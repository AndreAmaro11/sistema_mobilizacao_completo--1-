from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from src.models.mobilizacao import db, Usuario

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'error': {'code': 'INVALID_TOKEN', 'message': 'Token malformado'}}), 401
        
        if not token:
            return jsonify({'success': False, 'error': {'code': 'MISSING_TOKEN', 'message': 'Token de acesso requerido'}}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['user_id'])
            if not current_user or not current_user.ativo:
                return jsonify({'success': False, 'error': {'code': 'INVALID_USER', 'message': 'Usuário inválido ou inativo'}}), 401
                
            # Registrar acesso
            try:
                from src.models.permissoes import registrar_acesso
                registrar_acesso(
                    current_user,
                    'acessar',
                    request.endpoint.split('.')[-1] if request.endpoint else 'desconhecido',
                    None,
                    request.remote_addr,
                    request.user_agent.string if request.user_agent else None,
                    True,
                    f"Método: {request.method}, Endpoint: {request.endpoint}"
                )
            except ImportError:
                pass  # Ignorar se o módulo de permissões não estiver disponível
                
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': {'code': 'EXPIRED_TOKEN', 'message': 'Token expirado'}}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': {'code': 'INVALID_TOKEN', 'message': 'Token inválido'}}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': {'code': 'FORBIDDEN', 'message': 'Acesso negado - privilégios de administrador requeridos'}}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('senha'):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Email e senha são obrigatórios'
                }
            }), 400
        
        usuario = Usuario.query.filter_by(email=data['email']).first()
        
        if not usuario or not usuario.check_senha(data['senha']):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Email ou senha inválidos'
                }
            }), 401
        
        if not usuario.ativo:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INACTIVE_USER',
                    'message': 'Usuário inativo'
                }
            }), 401
        
        # Atualizar último acesso
        usuario.data_ultimo_acesso = datetime.utcnow()
        db.session.commit()
        
        # Gerar token JWT
        token = jwt.encode({
            'user_id': usuario.id,
            'email': usuario.email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'usuario': usuario.to_dict(),
                'expires_in': 86400  # 24 horas em segundos
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

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    try:
        # Gerar novo token
        token = jwt.encode({
            'user_id': current_user.id,
            'email': current_user.email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'expires_in': 86400
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

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # Em uma implementação real, você poderia adicionar o token a uma blacklist
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso'
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'success': True,
        'data': current_user.to_dict()
    })



def permissao_required(tipo_permissao, recurso, recurso_id_param=None):
    """
    Decorador para verificar se o usuário tem uma permissão específica.
    
    Args:
        tipo_permissao: String ou TipoPermissao
        recurso: String ou RecursoSistema
        recurso_id_param: Nome do parâmetro da URL que contém o ID do recurso (opcional)
    """
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            try:
                from src.models.permissoes import verificar_permissao, registrar_acesso, TipoPermissao, RecursoSistema
                
                # Obter ID do recurso se especificado
                recurso_id = None
                if recurso_id_param and recurso_id_param in kwargs:
                    recurso_id = kwargs[recurso_id_param]
                
                # Verificar permissão
                if not verificar_permissao(current_user, tipo_permissao, recurso, recurso_id):
                    # Registrar tentativa de acesso não autorizado
                    registrar_acesso(
                        current_user,
                        tipo_permissao,
                        recurso,
                        recurso_id,
                        request.remote_addr,
                        request.user_agent.string if request.user_agent else None,
                        False,
                        f"Acesso negado: {request.method} {request.endpoint}"
                    )
                    
                    return jsonify({
                        'success': False,
                        'error': {
                            'code': 'FORBIDDEN',
                            'message': 'Acesso negado - Permissão insuficiente'
                        }
                    }), 403
                
                # Registrar acesso bem-sucedido
                registrar_acesso(
                    current_user,
                    tipo_permissao,
                    recurso,
                    recurso_id,
                    request.remote_addr,
                    request.user_agent.string if request.user_agent else None,
                    True,
                    f"Acesso permitido: {request.method} {request.endpoint}"
                )
                
                return f(current_user, *args, **kwargs)
                
            except ImportError:
                # Se o módulo de permissões não estiver disponível, apenas continuar
                return f(current_user, *args, **kwargs)
                
        return decorated
    return decorator

