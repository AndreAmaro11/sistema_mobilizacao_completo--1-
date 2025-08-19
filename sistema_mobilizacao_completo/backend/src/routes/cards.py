from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.mobilizacao import db, CardMobilizacao, ChecklistCard, EtapaProcesso, Usuario
from src.routes.auth import token_required
from sqlalchemy import or_, and_

cards_bp = Blueprint('cards', __name__)

@cards_bp.route('', methods=['GET'])
@token_required
def listar_cards(current_user):
    try:
        # Parâmetros de filtro
        etapa_id = request.args.get('etapa_id', type=int)
        status = request.args.get('status')
        responsavel = request.args.get('responsavel')
        prazo_vencido = request.args.get('prazo_vencido', type=bool)
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Construir query
        query = CardMobilizacao.query
        
        if etapa_id:
            query = query.filter(CardMobilizacao.etapa_atual_id == etapa_id)
        
        if status:
            query = query.filter(CardMobilizacao.status_etapa == status)
        
        if responsavel:
            query = query.filter(CardMobilizacao.responsavel_atual == responsavel)
        
        if prazo_vencido:
            query = query.filter(CardMobilizacao.prazo_etapa < datetime.utcnow())
        
        # Paginação
        cards_paginated = query.paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        # Contar cards por etapa
        cards_por_etapa = {}
        etapas = EtapaProcesso.query.filter_by(ativo=True).all()
        for etapa in etapas:
            count = CardMobilizacao.query.filter_by(etapa_atual_id=etapa.id).count()
            cards_por_etapa[str(etapa.id)] = count
        
        return jsonify({
            'success': True,
            'data': {
                'cards': [card.to_dict() for card in cards_paginated.items],
                'total': cards_paginated.total,
                'page': page,
                'limit': limit,
                'total_pages': cards_paginated.pages,
                'por_etapa': cards_por_etapa
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('/<int:card_id>', methods=['GET'])
@token_required
def obter_card(current_user, card_id):
    try:
        card = CardMobilizacao.query.get(card_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Card não encontrado'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': card.to_dict(incluir_detalhes=True)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('', methods=['POST'])
@token_required
def criar_card(current_user):
    try:
        # Verificar se usuário pode criar cards
        if not current_user.pode_criar_cards():
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Usuário não tem permissão para criar cards'
                }
            }), 403
        
        data = request.get_json()
        
        if not data or not data.get('nome_colaborador'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Nome do colaborador é obrigatório'
                }
            }), 400
        
        # Verificar se CPF já existe (se fornecido)
        if data.get('cpf'):
            existing_card = CardMobilizacao.query.filter_by(cpf=data['cpf']).first()
            if existing_card:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'BUSINESS_RULE_ERROR',
                        'message': 'CPF já cadastrado no sistema'
                    }
                }), 422
        
        # Obter primeira etapa do processo
        primeira_etapa = EtapaProcesso.query.filter_by(ativo=True).order_by(EtapaProcesso.ordem).first()
        
        if not primeira_etapa:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_ERROR',
                    'message': 'Nenhuma etapa ativa encontrada no processo'
                }
            }), 422
        
        # Criar novo card
        card = CardMobilizacao(
            nome_colaborador=data['nome_colaborador'],
            cpf=data.get('cpf'),
            cargo=data.get('cargo'),
            salario=data.get('salario'),
            centro_custo=data.get('centro_custo'),
            data_admissao=datetime.strptime(data['data_admissao'], '%Y-%m-%d').date() if data.get('data_admissao') else None,
            etapa_atual_id=primeira_etapa.id,
            observacoes=data.get('observacoes'),
            criado_por=current_user.id,
            atualizado_por=current_user.id
        )
        
        db.session.add(card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': card.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('/<int:card_id>', methods=['PUT'])
@token_required
def atualizar_card(current_user, card_id):
    try:
        card = CardMobilizacao.query.get(card_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Card não encontrado'
                }
            }), 404
        
        # Verificar permissão para editar a etapa atual
        if not current_user.pode_editar_etapa(card.etapa_atual_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Usuário não tem permissão para editar esta etapa'
                }
            }), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'nome_colaborador' in data:
            card.nome_colaborador = data['nome_colaborador']
        if 'cargo' in data:
            card.cargo = data['cargo']
        if 'salario' in data:
            card.salario = data['salario']
        if 'centro_custo' in data:
            card.centro_custo = data['centro_custo']
        if 'data_admissao' in data and data['data_admissao']:
            card.data_admissao = datetime.strptime(data['data_admissao'], '%Y-%m-%d').date()
        if 'status_etapa' in data:
            card.status_etapa = data['status_etapa']
        if 'observacoes' in data:
            card.observacoes = data['observacoes']
        
        card.atualizado_por = current_user.id
        card.ultima_atualizacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': card.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('/<int:card_id>/mover', methods=['PUT'])
@token_required
def mover_card(current_user, card_id):
    try:
        card = CardMobilizacao.query.get(card_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Card não encontrado'
                }
            }), 404
        
        data = request.get_json()
        etapa_destino_id = data.get('etapa_destino_id')
        motivo = data.get('motivo')
        
        if not etapa_destino_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Etapa de destino é obrigatória'
                }
            }), 400
        
        # Verificar se etapa de destino existe
        etapa_destino = EtapaProcesso.query.get(etapa_destino_id)
        if not etapa_destino or not etapa_destino.ativo:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Etapa de destino não encontrada ou inativa'
                }
            }), 404
        
        # Verificar permissão para etapa atual e destino
        if not current_user.pode_editar_etapa(card.etapa_atual_id) or not current_user.pode_editar_etapa(etapa_destino_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Usuário não tem permissão para mover entre essas etapas'
                }
            }), 403
        
        # Mover card
        card.mover_para_etapa(etapa_destino_id, current_user.id, motivo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': card.to_dict(),
            'message': 'Card movido com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('/<int:card_id>/checklist/<int:item_id>', methods=['PUT'])
@token_required
def atualizar_checklist_item(current_user, card_id, item_id):
    try:
        card = CardMobilizacao.query.get(card_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Card não encontrado'
                }
            }), 404
        
        # Verificar permissão para editar a etapa atual
        if not current_user.pode_editar_etapa(card.etapa_atual_id):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Usuário não tem permissão para editar esta etapa'
                }
            }), 403
        
        checklist_item = ChecklistCard.query.filter_by(
            card_id=card_id, 
            id=item_id
        ).first()
        
        if not checklist_item:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Item do checklist não encontrado'
                }
            }), 404
        
        data = request.get_json()
        
        if 'concluido' in data:
            checklist_item.concluido = data['concluido']
            if data['concluido']:
                checklist_item.data_conclusao = datetime.utcnow()
                checklist_item.concluido_por = current_user.id
            else:
                checklist_item.data_conclusao = None
                checklist_item.concluido_por = None
        
        if 'observacoes' in data:
            checklist_item.observacoes = data['observacoes']
        
        card.ultima_atualizacao = datetime.utcnow()
        card.atualizado_por = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'item_id': item_id,
                'concluido': checklist_item.concluido,
                'data_conclusao': checklist_item.data_conclusao.isoformat() if checklist_item.data_conclusao else None,
                'concluido_por': current_user.nome if checklist_item.concluido else None,
                'checklist_progresso': card.get_progresso_checklist()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@cards_bp.route('/<int:card_id>', methods=['DELETE'])
@token_required
def deletar_card(current_user, card_id):
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Apenas administradores podem deletar cards'
                }
            }), 403
        
        card = CardMobilizacao.query.get(card_id)
        
        if not card:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Card não encontrado'
                }
            }), 404
        
        db.session.delete(card)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Card deletado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

