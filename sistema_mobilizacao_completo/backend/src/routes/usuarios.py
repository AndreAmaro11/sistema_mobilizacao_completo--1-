from flask import Blueprint, request, jsonify
from src.models.mobilizacao import db, Usuario, Grupo
from src.routes.auth import token_required, admin_required

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('', methods=['GET'])
@token_required
@admin_required
def listar_usuarios(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        ativo = request.args.get('ativo', type=bool)
        grupo = request.args.get('grupo')
        
        query = Usuario.query
        
        if ativo is not None:
            query = query.filter(Usuario.ativo == ativo)
        
        if grupo:
            query = query.join(Usuario.grupos).filter(Grupo.nome == grupo)
        
        usuarios_paginated = query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'usuarios': [usuario.to_dict() for usuario in usuarios_paginated.items],
                'total': usuarios_paginated.total,
                'page': page,
                'limit': limit,
                'total_pages': usuarios_paginated.pages
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

@usuarios_bp.route('/<int:usuario_id>', methods=['GET'])
@token_required
@admin_required
def obter_usuario(current_user, usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Usuário não encontrado'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': usuario.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@usuarios_bp.route('', methods=['POST'])
@token_required
@admin_required
def criar_usuario(current_user):
    try:
        data = request.get_json()
        
        if not data or not data.get('nome') or not data.get('email') or not data.get('senha'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Nome, email e senha são obrigatórios'
                }
            }), 400
        
        # Verificar se email já existe
        existing_user = Usuario.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_ERROR',
                    'message': 'Email já cadastrado no sistema'
                }
            }), 422
        
        # Criar novo usuário
        usuario = Usuario(
            nome=data['nome'],
            email=data['email'],
            criado_por=current_user.id
        )
        usuario.set_senha(data['senha'])
        
        db.session.add(usuario)
        db.session.flush()  # Para obter o ID do usuário
        
        # Associar grupos
        grupos = data.get('grupos', [])
        for nome_grupo in grupos:
            grupo = Grupo.query.filter_by(nome=nome_grupo).first()
            if grupo:
                usuario.grupos.append(grupo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': usuario.to_dict()
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

@usuarios_bp.route('/<int:usuario_id>', methods=['PUT'])
@token_required
@admin_required
def atualizar_usuario(current_user, usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Usuário não encontrado'
                }
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'email' in data:
            # Verificar se novo email já existe
            if data['email'] != usuario.email:
                existing_user = Usuario.query.filter_by(email=data['email']).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'BUSINESS_RULE_ERROR',
                            'message': 'Email já cadastrado no sistema'
                        }
                    }), 422
            usuario.email = data['email']
        if 'ativo' in data:
            usuario.ativo = data['ativo']
        if 'senha' in data:
            usuario.set_senha(data['senha'])
        
        # Atualizar grupos
        if 'grupos' in data:
            usuario.grupos.clear()
            for nome_grupo in data['grupos']:
                grupo = Grupo.query.filter_by(nome=nome_grupo).first()
                if grupo:
                    usuario.grupos.append(grupo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': usuario.to_dict()
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

@usuarios_bp.route('/<int:usuario_id>', methods=['DELETE'])
@token_required
@admin_required
def deletar_usuario(current_user, usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Usuário não encontrado'
                }
            }), 404
        
        # Não permitir deletar o próprio usuário
        if usuario.id == current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_ERROR',
                    'message': 'Não é possível deletar o próprio usuário'
                }
            }), 422
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário deletado com sucesso'
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

# Rotas para grupos
@usuarios_bp.route('/grupos', methods=['GET'])
@token_required
def listar_grupos(current_user):
    try:
        grupos = Grupo.query.filter_by(ativo=True).all()
        
        return jsonify({
            'success': True,
            'data': [grupo.to_dict() for grupo in grupos]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@usuarios_bp.route('/grupos', methods=['POST'])
@token_required
@admin_required
def criar_grupo(current_user):
    try:
        data = request.get_json()
        
        if not data or not data.get('nome'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Nome do grupo é obrigatório'
                }
            }), 400
        
        # Verificar se nome já existe
        existing_group = Grupo.query.filter_by(nome=data['nome']).first()
        if existing_group:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'BUSINESS_RULE_ERROR',
                    'message': 'Nome do grupo já existe'
                }
            }), 422
        
        # Criar novo grupo
        grupo = Grupo(
            nome=data['nome'],
            descricao=data.get('descricao'),
            criado_por=current_user.id
        )
        
        db.session.add(grupo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': grupo.to_dict()
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

@usuarios_bp.route('/grupos/<int:grupo_id>', methods=['PUT'])
@token_required
@admin_required
def atualizar_grupo(current_user, grupo_id):
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
        
        # Atualizar campos
        if 'nome' in data:
            # Verificar se novo nome já existe
            if data['nome'] != grupo.nome:
                existing_group = Grupo.query.filter_by(nome=data['nome']).first()
                if existing_group:
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'BUSINESS_RULE_ERROR',
                            'message': 'Nome do grupo já existe'
                        }
                    }), 422
            grupo.nome = data['nome']
        if 'descricao' in data:
            grupo.descricao = data['descricao']
        if 'ativo' in data:
            grupo.ativo = data['ativo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': grupo.to_dict()
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

