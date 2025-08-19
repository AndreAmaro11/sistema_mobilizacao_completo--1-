from flask import Blueprint, request, jsonify, current_app
from src.models.mobilizacao import db, Notificacao, Usuario
from src.routes.auth import token_required, admin_required, permissao_required
from src.services.notificacao_service import NotificacaoService
from src.models.permissoes import TipoPermissao, RecursoSistema
from datetime import datetime

notificacoes_bp = Blueprint('notificacoes', __name__)

@notificacoes_bp.route('', methods=['GET'])
@token_required
def listar_notificacoes(current_user):
    """Lista notificações do usuário atual"""
    try:
        lidas = request.args.get('lidas', 'false').lower() == 'true'
        limite = request.args.get('limite', 50, type=int)
        
        notificacoes = NotificacaoService.listar_notificacoes_usuario(
            current_user.email,
            lidas=lidas,
            limite=limite
        )
        
        return jsonify({
            'success': True,
            'data': [notificacao.to_dict() for notificacao in notificacoes]
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar notificações: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/contagem', methods=['GET'])
@token_required
def contar_notificacoes(current_user):
    """Conta notificações não lidas do usuário atual"""
    try:
        contagem = NotificacaoService.contar_notificacoes_nao_lidas(current_user.email)
        
        return jsonify({
            'success': True,
            'data': {
                'nao_lidas': contagem
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao contar notificações: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/<int:notificacao_id>/ler', methods=['POST'])
@token_required
def marcar_como_lida(current_user, notificacao_id):
    """Marca uma notificação como lida"""
    try:
        # Verificar se a notificação pertence ao usuário
        notificacao = Notificacao.query.get(notificacao_id)
        
        if not notificacao:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Notificação não encontrada'
                }
            }), 404
        
        if notificacao.destinatario_email != current_user.email and not current_user.is_admin():
            return jsonify({
                'success': False,
                'error': {
                    'code': 'FORBIDDEN',
                    'message': 'Você não tem permissão para acessar esta notificação'
                }
            }), 403
        
        # Marcar como lida
        NotificacaoService.marcar_como_lida(notificacao_id, current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Notificação marcada como lida'
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/todas/ler', methods=['POST'])
@token_required
def marcar_todas_como_lidas(current_user):
    """Marca todas as notificações do usuário como lidas"""
    try:
        # Buscar todas as notificações não lidas do usuário
        notificacoes = Notificacao.query.filter_by(
            destinatario_email=current_user.email,
            lido=False
        ).all()
        
        # Marcar todas como lidas
        for notificacao in notificacoes:
            notificacao.lido = True
            notificacao.data_leitura = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(notificacoes)} notificações marcadas como lidas'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao marcar todas notificações como lidas: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/verificar-prazos', methods=['POST'])
@token_required
@permissao_required(TipoPermissao.ADMINISTRAR, RecursoSistema.NOTIFICACAO)
def verificar_prazos(current_user):
    """Executa verificação de prazos vencidos e próximos de vencer"""
    try:
        resultados = NotificacaoService.verificar_prazos_vencidos()
        
        return jsonify({
            'success': True,
            'data': resultados
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar prazos: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/verificar-inativos', methods=['POST'])
@token_required
@permissao_required(TipoPermissao.ADMINISTRAR, RecursoSistema.NOTIFICACAO)
def verificar_inativos(current_user):
    """Executa verificação de cards inativos"""
    try:
        resultados = NotificacaoService.verificar_cards_inativos()
        
        return jsonify({
            'success': True,
            'data': {
                'inativos': resultados
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar cards inativos: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/verificar-checklist', methods=['POST'])
@token_required
@permissao_required(TipoPermissao.ADMINISTRAR, RecursoSistema.NOTIFICACAO)
def verificar_checklist(current_user):
    """Executa verificação de itens de checklist pendentes"""
    try:
        resultados = NotificacaoService.verificar_checklist_pendentes()
        
        return jsonify({
            'success': True,
            'data': {
                'pendentes': resultados
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar checklist pendentes: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/processar-pendentes', methods=['POST'])
@token_required
@permissao_required(TipoPermissao.ADMINISTRAR, RecursoSistema.NOTIFICACAO)
def processar_pendentes(current_user):
    """Processa notificações pendentes de envio"""
    try:
        resultados = NotificacaoService.processar_notificacoes_pendentes()
        
        return jsonify({
            'success': True,
            'data': resultados
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao processar notificações pendentes: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@notificacoes_bp.route('/verificar-tudo', methods=['POST'])
@token_required
@permissao_required(TipoPermissao.ADMINISTRAR, RecursoSistema.NOTIFICACAO)
def verificar_tudo(current_user):
    """Executa todas as verificações de uma vez"""
    try:
        resultados = NotificacaoService.executar_verificacoes_periodicas()
        
        return jsonify({
            'success': True,
            'data': resultados
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao executar verificações: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

