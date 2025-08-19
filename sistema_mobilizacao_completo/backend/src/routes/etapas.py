from flask import Blueprint, request, jsonify
from src.models.mobilizacao import db, EtapaProcesso, ChecklistEtapa, Grupo
from src.routes.auth import token_required, admin_required

etapas_bp = Blueprint('etapas', __name__)

@etapas_bp.route('', methods=['GET'])
@token_required
def listar_etapas(current_user):
    try:
        etapas = EtapaProcesso.query.filter_by(ativo=True).order_by(EtapaProcesso.ordem).all()
        
        return jsonify({
            'success': True,
            'data': [etapa.to_dict() for etapa in etapas]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@etapas_bp.route('/<int:etapa_id>', methods=['GET'])
@token_required
def obter_etapa(current_user, etapa_id):
    try:
        etapa = EtapaProcesso.query.get(etapa_id)
        
        if not etapa:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Etapa não encontrada'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': etapa.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@etapas_bp.route('', methods=['POST'])
@token_required
@admin_required
def criar_etapa(current_user):
    try:
        data = request.get_json()
        
        if not data or not data.get('nome') or not data.get('dono_email'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Nome e dono da etapa são obrigatórios'
                }
            }), 400
        
        # Verificar se ordem já existe
        ordem = data.get('ordem')
        if ordem:
            existing_etapa = EtapaProcesso.query.filter_by(ordem=ordem).first()
            if existing_etapa:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'BUSINESS_RULE_ERROR',
                        'message': 'Já existe uma etapa com esta ordem'
                    }
                }), 422
        else:
            # Se não fornecida, usar próxima ordem disponível
            max_ordem = db.session.query(db.func.max(EtapaProcesso.ordem)).scalar() or 0
            ordem = max_ordem + 1
        
        # Criar nova etapa
        etapa = EtapaProcesso(
            nome=data['nome'],
            descricao=data.get('descricao'),
            ordem=ordem,
            prazo_dias=data.get('prazo_dias', 5),
            dias_alerta_inatividade=data.get('dias_alerta_inatividade', 3),
            dono_email=data['dono_email']
        )
        
        db.session.add(etapa)
        db.session.flush()  # Para obter o ID da etapa
        
        # Associar grupos permitidos
        grupos_permitidos = data.get('grupos_permitidos', [])
        for nome_grupo in grupos_permitidos:
            grupo = Grupo.query.filter_by(nome=nome_grupo).first()
            if grupo:
                etapa.grupos_permitidos.append(grupo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': etapa.to_dict()
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

@etapas_bp.route('/<int:etapa_id>', methods=['PUT'])
@token_required
@admin_required
def atualizar_etapa(current_user, etapa_id):
    try:
        etapa = EtapaProcesso.query.get(etapa_id)
        
        if not etapa:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Etapa não encontrada'
                }
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            etapa.nome = data['nome']
        if 'descricao' in data:
            etapa.descricao = data['descricao']
        if 'prazo_dias' in data:
            etapa.prazo_dias = data['prazo_dias']
        if 'dias_alerta_inatividade' in data:
            etapa.dias_alerta_inatividade = data['dias_alerta_inatividade']
        if 'dono_email' in data:
            etapa.dono_email = data['dono_email']
        if 'ativo' in data:
            etapa.ativo = data['ativo']
        
        # Atualizar grupos permitidos
        if 'grupos_permitidos' in data:
            etapa.grupos_permitidos.clear()
            for nome_grupo in data['grupos_permitidos']:
                grupo = Grupo.query.filter_by(nome=nome_grupo).first()
                if grupo:
                    etapa.grupos_permitidos.append(grupo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': etapa.to_dict()
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

@etapas_bp.route('/<int:etapa_id>/checklist', methods=['GET'])
@token_required
def listar_checklist_etapa(current_user, etapa_id):
    try:
        etapa = EtapaProcesso.query.get(etapa_id)
        
        if not etapa:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Etapa não encontrada'
                }
            }), 404
        
        checklist_items = ChecklistEtapa.query.filter_by(
            etapa_id=etapa_id, 
            ativo=True
        ).order_by(ChecklistEtapa.ordem).all()
        
        return jsonify({
            'success': True,
            'data': [item.to_dict() for item in checklist_items]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@etapas_bp.route('/<int:etapa_id>/checklist', methods=['POST'])
@token_required
@admin_required
def criar_checklist_item(current_user, etapa_id):
    try:
        etapa = EtapaProcesso.query.get(etapa_id)
        
        if not etapa:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Etapa não encontrada'
                }
            }), 404
        
        data = request.get_json()
        
        if not data or not data.get('tarefa'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Tarefa é obrigatória'
                }
            }), 400
        
        # Obter próxima ordem
        max_ordem = db.session.query(db.func.max(ChecklistEtapa.ordem)).filter_by(etapa_id=etapa_id).scalar() or 0
        ordem = data.get('ordem', max_ordem + 1)
        
        # Criar item do checklist
        checklist_item = ChecklistEtapa(
            etapa_id=etapa_id,
            tarefa=data['tarefa'],
            descricao=data.get('descricao'),
            obrigatorio=data.get('obrigatorio', True),
            ordem=ordem
        )
        
        db.session.add(checklist_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': checklist_item.to_dict()
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

@etapas_bp.route('/<int:etapa_id>/checklist/<int:item_id>', methods=['PUT'])
@token_required
@admin_required
def atualizar_checklist_item(current_user, etapa_id, item_id):
    try:
        checklist_item = ChecklistEtapa.query.filter_by(
            id=item_id, 
            etapa_id=etapa_id
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
        
        # Atualizar campos
        if 'tarefa' in data:
            checklist_item.tarefa = data['tarefa']
        if 'descricao' in data:
            checklist_item.descricao = data['descricao']
        if 'obrigatorio' in data:
            checklist_item.obrigatorio = data['obrigatorio']
        if 'ordem' in data:
            checklist_item.ordem = data['ordem']
        if 'ativo' in data:
            checklist_item.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': checklist_item.to_dict()
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

@etapas_bp.route('/<int:etapa_id>/checklist/<int:item_id>', methods=['DELETE'])
@token_required
@admin_required
def deletar_checklist_item(current_user, etapa_id, item_id):
    try:
        checklist_item = ChecklistEtapa.query.filter_by(
            id=item_id, 
            etapa_id=etapa_id
        ).first()
        
        if not checklist_item:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Item do checklist não encontrado'
                }
            }), 404
        
        db.session.delete(checklist_item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item do checklist deletado com sucesso'
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

