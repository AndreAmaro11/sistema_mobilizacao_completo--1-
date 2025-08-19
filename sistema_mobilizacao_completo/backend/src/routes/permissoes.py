from flask import Blueprint, request, jsonify
from src.models.mobilizacao import db, Usuario, Grupo
from src.models.permissoes import (
    Permissao, PermissaoEspecial, LogAcesso, 
    TipoPermissao, RecursoSistema, 
    verificar_permissao, registrar_acesso
)
from src.routes.auth import token_required, admin_required
from datetime import datetime

permissoes_bp = Blueprint('permissoes', __name__)

@permissoes_bp.route('', methods=['GET'])
@token_required
@admin_required
def listar_permissoes(current_user):
    """Lista todas as permissões do sistema"""
    try:
        permissoes = Permissao.query.all()
        
        return jsonify({
            'success': True,
            'data': [permissao.to_dict() for permissao in permissoes]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@permissoes_bp.route('/tipos', methods=['GET'])
@token_required
def listar_tipos_permissoes(current_user):
    """Lista todos os tipos de permissões disponíveis"""
    try:
        tipos = [tipo.value for tipo in TipoPermissao]
        recursos = [recurso.value for recurso in RecursoSistema]
        
        return jsonify({
            'success': True,
            'data': {
                'tipos': tipos,
                'recursos': recursos
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

@permissoes_bp.route('/grupos/<int:grupo_id>', methods=['GET'])
@token_required
@admin_required
def listar_permissoes_grupo(current_user, grupo_id):
    """Lista todas as permissões de um grupo específico"""
    try:
        grupo = Grupo.query.get(grupo_id)
        
        if not grupo:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Grupo não encontrado'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'grupo': grupo.nome,
                'permissoes': [permissao.to_dict() for permissao in grupo.permissoes]
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

@permissoes_bp.route('/grupos/<int:grupo_id>', methods=['PUT'])
@token_required
@admin_required
def atualizar_permissoes_grupo(current_user, grupo_id):
    """Atualiza as permissões de um grupo"""
    try:
        grupo = Grupo.query.get(grupo_id)
        
        if not grupo:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Grupo não encontrado'
                }
            }), 404
        
        data = request.get_json()
        
        if not data or 'permissoes_ids' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Lista de IDs de permissões é obrigatória'
                }
            }), 400
        
        # Limpar permissões atuais
        grupo.permissoes.clear()
        
        # Adicionar novas permissões
        for permissao_id in data['permissoes_ids']:
            permissao = Permissao.query.get(permissao_id)
            if permissao:
                grupo.permissoes.append(permissao)
        
        db.session.commit()
        
        # Registrar no log
        registrar_acesso(
            current_user, 
            TipoPermissao.EDITAR, 
            RecursoSistema.GRUPO, 
            grupo_id,
            detalhes=f"Atualização de permissões do grupo {grupo.nome}"
        )
        
        return jsonify({
            'success': True,
            'data': {
                'grupo': grupo.nome,
                'permissoes': [permissao.to_dict() for permissao in grupo.permissoes]
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

@permissoes_bp.route('/especiais', methods=['GET'])
@token_required
@admin_required
def listar_permissoes_especiais(current_user):
    """Lista todas as permissões especiais"""
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        
        query = PermissaoEspecial.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        permissoes_especiais = query.all()
        
        return jsonify({
            'success': True,
            'data': [pe.to_dict() for pe in permissoes_especiais]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@permissoes_bp.route('/especiais', methods=['POST'])
@token_required
@admin_required
def criar_permissao_especial(current_user):
    """Cria uma nova permissão especial para um usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('usuario_id') or not data.get('tipo') or not data.get('recurso'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Usuário, tipo e recurso são obrigatórios'
                }
            }), 400
        
        # Verificar se usuário existe
        usuario = Usuario.query.get(data['usuario_id'])
        if not usuario:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Usuário não encontrado'
                }
            }), 404
        
        # Verificar se tipo e recurso são válidos
        try:
            tipo = TipoPermissao(data['tipo'])
            recurso = RecursoSistema(data['recurso'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Tipo ou recurso inválido'
                }
            }), 400
        
        # Verificar se já existe permissão especial para este usuário/tipo/recurso/recurso_id
        permissao_existente = PermissaoEspecial.query.filter_by(
            usuario_id=data['usuario_id'],
            tipo=data['tipo'],
            recurso=data['recurso'],
            recurso_id=data.get('recurso_id')
        ).first()
        
        if permissao_existente:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_ERROR',
                    'message': 'Já existe uma permissão especial para este usuário/tipo/recurso'
                }
            }), 422
        
        # Criar nova permissão especial
        permissao_especial = PermissaoEspecial(
            usuario_id=data['usuario_id'],
            tipo=data['tipo'],
            recurso=data['recurso'],
            recurso_id=data.get('recurso_id'),
            concedido=data.get('concedido', True),
            data_expiracao=datetime.fromisoformat(data['data_expiracao']) if data.get('data_expiracao') else None,
            concedido_por=current_user.id
        )
        
        db.session.add(permissao_especial)
        db.session.commit()
        
        # Registrar no log
        registrar_acesso(
            current_user, 
            TipoPermissao.CRIAR, 
            RecursoSistema.PERMISSAO, 
            permissao_especial.id,
            detalhes=f"Criação de permissão especial para {usuario.nome}"
        )
        
        return jsonify({
            'success': True,
            'data': permissao_especial.to_dict()
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

@permissoes_bp.route('/especiais/<int:permissao_id>', methods=['DELETE'])
@token_required
@admin_required
def remover_permissao_especial(current_user, permissao_id):
    """Remove uma permissão especial"""
    try:
        permissao_especial = PermissaoEspecial.query.get(permissao_id)
        
        if not permissao_especial:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Permissão especial não encontrada'
                }
            }), 404
        
        usuario_nome = permissao_especial.usuario.nome if permissao_especial.usuario else "Desconhecido"
        
        db.session.delete(permissao_especial)
        db.session.commit()
        
        # Registrar no log
        registrar_acesso(
            current_user, 
            TipoPermissao.EXCLUIR, 
            RecursoSistema.PERMISSAO, 
            permissao_id,
            detalhes=f"Remoção de permissão especial de {usuario_nome}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Permissão especial removida com sucesso'
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

@permissoes_bp.route('/verificar', methods=['POST'])
@token_required
def verificar_permissao_usuario(current_user):
    """Verifica se o usuário atual tem uma permissão específica"""
    try:
        data = request.get_json()
        
        if not data or not data.get('tipo') or not data.get('recurso'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Tipo e recurso são obrigatórios'
                }
            }), 400
        
        # Verificar permissão
        tem_permissao = current_user.tem_permissao(
            data['tipo'],
            data['recurso'],
            data.get('recurso_id')
        )
        
        return jsonify({
            'success': True,
            'data': {
                'tem_permissao': tem_permissao
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

@permissoes_bp.route('/minhas', methods=['GET'])
@token_required
def listar_minhas_permissoes(current_user):
    """Lista todas as permissões do usuário atual"""
    try:
        permissoes = current_user.listar_permissoes()
        
        # Obter permissões especiais
        permissoes_especiais = PermissaoEspecial.query.filter_by(
            usuario_id=current_user.id
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'permissoes': permissoes,
                'permissoes_especiais': [pe.to_dict() for pe in permissoes_especiais]
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

@permissoes_bp.route('/logs', methods=['GET'])
@token_required
@admin_required
def listar_logs_acesso(current_user):
    """Lista logs de acesso"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        usuario_id = request.args.get('usuario_id', type=int)
        tipo_operacao = request.args.get('tipo_operacao')
        recurso = request.args.get('recurso')
        sucesso = request.args.get('sucesso', type=bool)
        
        query = LogAcesso.query
        
        if usuario_id:
            query = query.filter_by(usuario_id=usuario_id)
        
        if tipo_operacao:
            query = query.filter_by(tipo_operacao=tipo_operacao)
        
        if recurso:
            query = query.filter_by(recurso=recurso)
        
        if sucesso is not None:
            query = query.filter_by(sucesso=sucesso)
        
        # Ordenar por data de acesso (mais recente primeiro)
        query = query.order_by(LogAcesso.data_acesso.desc())
        
        # Paginação
        logs_paginated = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs_paginated.items],
                'total': logs_paginated.total,
                'page': page,
                'limit': limit,
                'total_pages': logs_paginated.pages
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

