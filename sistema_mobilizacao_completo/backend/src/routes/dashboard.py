from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from src.models.mobilizacao import db, CardMobilizacao, EtapaProcesso, HistoricoMovimentacao
from src.routes.auth import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/indicadores', methods=['GET'])
@token_required
def obter_indicadores(current_user):
    try:
        # Parâmetros de filtro
        periodo = request.args.get('periodo', '30d')
        centro_custo = request.args.get('centro_custo')
        
        # Calcular data de início baseada no período
        data_inicio = None
        if periodo == '7d':
            data_inicio = datetime.utcnow() - timedelta(days=7)
        elif periodo == '30d':
            data_inicio = datetime.utcnow() - timedelta(days=30)
        elif periodo == '90d':
            data_inicio = datetime.utcnow() - timedelta(days=90)
        elif periodo == '1y':
            data_inicio = datetime.utcnow() - timedelta(days=365)
        
        # Query base para cards
        cards_query = CardMobilizacao.query
        if centro_custo:
            cards_query = cards_query.filter(CardMobilizacao.centro_custo == centro_custo)
        
        # Resumo geral
        total_cards = cards_query.count()
        cards_em_andamento = cards_query.filter(CardMobilizacao.status_etapa != 'FINALIZADO').count()
        cards_finalizados = cards_query.filter(CardMobilizacao.status_etapa == 'FINALIZADO').count()
        
        # Cards atrasados (prazo vencido)
        agora = datetime.utcnow()
        cards_atrasados = cards_query.filter(
            and_(
                CardMobilizacao.prazo_etapa < agora,
                CardMobilizacao.status_etapa != 'FINALIZADO'
            )
        ).count()
        
        # Cards vencendo (próximos 2 dias)
        limite_vencendo = agora + timedelta(days=2)
        cards_vencendo = cards_query.filter(
            and_(
                CardMobilizacao.prazo_etapa.between(agora, limite_vencendo),
                CardMobilizacao.status_etapa != 'FINALIZADO'
            )
        ).count()
        
        # Cards por etapa
        etapas = EtapaProcesso.query.filter_by(ativo=True).order_by(EtapaProcesso.ordem).all()
        por_etapa = []
        
        for etapa in etapas:
            etapa_query = cards_query.filter(CardMobilizacao.etapa_atual_id == etapa.id)
            
            total_etapa = etapa_query.count()
            nao_iniciado = etapa_query.filter(CardMobilizacao.status_etapa == 'NAO_INICIADO').count()
            em_andamento = etapa_query.filter(CardMobilizacao.status_etapa == 'EM_ANDAMENTO').count()
            finalizado = etapa_query.filter(CardMobilizacao.status_etapa == 'FINALIZADO').count()
            atrasados_etapa = etapa_query.filter(
                and_(
                    CardMobilizacao.prazo_etapa < agora,
                    CardMobilizacao.status_etapa != 'FINALIZADO'
                )
            ).count()
            
            por_etapa.append({
                'etapa': etapa.nome,
                'total': total_etapa,
                'nao_iniciado': nao_iniciado,
                'em_andamento': em_andamento,
                'finalizado': finalizado,
                'atrasados': atrasados_etapa
            })
        
        # Tempo médio por etapa (baseado no histórico)
        tempo_medio_etapas = []
        for etapa in etapas:
            historico_query = HistoricoMovimentacao.query.filter(
                HistoricoMovimentacao.etapa_origem_id == etapa.id
            )
            
            if data_inicio:
                historico_query = historico_query.filter(
                    HistoricoMovimentacao.data_movimentacao >= data_inicio
                )
            
            tempo_medio = db.session.query(
                func.avg(HistoricoMovimentacao.tempo_permanencia_dias)
            ).filter(
                HistoricoMovimentacao.etapa_origem_id == etapa.id
            ).scalar()
            
            tempo_medio_etapas.append({
                'etapa': etapa.nome,
                'tempo_medio_dias': round(float(tempo_medio), 1) if tempo_medio else 0,
                'prazo_configurado': etapa.prazo_dias
            })
        
        # Cards por responsável
        cards_por_responsavel = db.session.query(
            CardMobilizacao.responsavel_atual,
            func.count(CardMobilizacao.id).label('total'),
            func.sum(
                func.case(
                    [(and_(CardMobilizacao.prazo_etapa < agora, 
                          CardMobilizacao.status_etapa != 'FINALIZADO'), 1)],
                    else_=0
                )
            ).label('atrasados')
        ).filter(
            CardMobilizacao.responsavel_atual.isnot(None)
        ).group_by(CardMobilizacao.responsavel_atual).all()
        
        responsaveis_list = []
        for responsavel, total, atrasados in cards_por_responsavel:
            responsaveis_list.append({
                'responsavel': responsavel,
                'total': total,
                'atrasados': atrasados or 0
            })
        
        # Tendências (baseadas no período)
        tendencias = {}
        if data_inicio:
            cards_criados_periodo = cards_query.filter(
                CardMobilizacao.data_criacao >= data_inicio
            ).count()
            
            cards_finalizados_periodo = HistoricoMovimentacao.query.join(
                EtapaProcesso, HistoricoMovimentacao.etapa_destino_id == EtapaProcesso.id
            ).filter(
                and_(
                    HistoricoMovimentacao.data_movimentacao >= data_inicio,
                    EtapaProcesso.ordem == db.session.query(func.max(EtapaProcesso.ordem)).scalar()
                )
            ).count()
            
            # Tempo médio do processo completo
            tempo_medio_processo = db.session.query(
                func.avg(
                    func.julianday(HistoricoMovimentacao.data_movimentacao) - 
                    func.julianday(CardMobilizacao.data_criacao)
                )
            ).join(
                CardMobilizacao, HistoricoMovimentacao.card_id == CardMobilizacao.id
            ).join(
                EtapaProcesso, HistoricoMovimentacao.etapa_destino_id == EtapaProcesso.id
            ).filter(
                and_(
                    HistoricoMovimentacao.data_movimentacao >= data_inicio,
                    EtapaProcesso.ordem == db.session.query(func.max(EtapaProcesso.ordem)).scalar()
                )
            ).scalar()
            
            tendencias = {
                'cards_criados_periodo': cards_criados_periodo,
                'cards_finalizados_periodo': cards_finalizados_periodo,
                'tempo_medio_processo': round(float(tempo_medio_processo), 1) if tempo_medio_processo else 0
            }
        
        return jsonify({
            'success': True,
            'data': {
                'resumo': {
                    'total_cards': total_cards,
                    'cards_em_andamento': cards_em_andamento,
                    'cards_finalizados': cards_finalizados,
                    'cards_atrasados': cards_atrasados,
                    'cards_vencendo': cards_vencendo
                },
                'por_etapa': por_etapa,
                'tempo_medio_etapas': tempo_medio_etapas,
                'cards_por_responsavel': responsaveis_list,
                'tendencias': tendencias
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

@dashboard_bp.route('/cards-atrasados', methods=['GET'])
@token_required
def listar_cards_atrasados(current_user):
    try:
        agora = datetime.utcnow()
        
        # Cards com prazo vencido
        cards_vencidos = CardMobilizacao.query.filter(
            and_(
                CardMobilizacao.prazo_etapa < agora,
                CardMobilizacao.status_etapa != 'FINALIZADO'
            )
        ).all()
        
        # Cards vencendo (próximos 2 dias)
        limite_vencendo = agora + timedelta(days=2)
        cards_vencendo = CardMobilizacao.query.filter(
            and_(
                CardMobilizacao.prazo_etapa.between(agora, limite_vencendo),
                CardMobilizacao.status_etapa != 'FINALIZADO'
            )
        ).all()
        
        resultado = []
        
        # Adicionar cards vencidos
        for card in cards_vencidos:
            dias_atraso = (agora - card.prazo_etapa).days
            resultado.append({
                'id': card.id,
                'nome_colaborador': card.nome_colaborador,
                'etapa_atual': card.etapa_atual.nome if card.etapa_atual else '',
                'responsavel_atual': card.responsavel_atual,
                'prazo_etapa': card.prazo_etapa.isoformat() if card.prazo_etapa else None,
                'dias_atraso': dias_atraso,
                'status_prazo': 'VENCIDO'
            })
        
        # Adicionar cards vencendo
        for card in cards_vencendo:
            dias_restantes = (card.prazo_etapa - agora).days
            resultado.append({
                'id': card.id,
                'nome_colaborador': card.nome_colaborador,
                'etapa_atual': card.etapa_atual.nome if card.etapa_atual else '',
                'responsavel_atual': card.responsavel_atual,
                'prazo_etapa': card.prazo_etapa.isoformat() if card.prazo_etapa else None,
                'dias_restantes': dias_restantes,
                'status_prazo': 'VENCENDO'
            })
        
        # Ordenar por urgência (vencidos primeiro, depois por prazo)
        resultado.sort(key=lambda x: (
            0 if x['status_prazo'] == 'VENCIDO' else 1,
            x.get('dias_atraso', 0) if x['status_prazo'] == 'VENCIDO' else -x.get('dias_restantes', 0)
        ), reverse=True)
        
        return jsonify({
            'success': True,
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erro interno do servidor'
            }
        }), 500

@dashboard_bp.route('/estatisticas-periodo', methods=['GET'])
@token_required
def obter_estatisticas_periodo(current_user):
    try:
        # Parâmetros
        dias = request.args.get('dias', 30, type=int)
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Cards criados por dia
        cards_por_dia = db.session.query(
            func.date(CardMobilizacao.data_criacao).label('data'),
            func.count(CardMobilizacao.id).label('total')
        ).filter(
            CardMobilizacao.data_criacao >= data_inicio
        ).group_by(
            func.date(CardMobilizacao.data_criacao)
        ).order_by('data').all()
        
        # Cards finalizados por dia (baseado no histórico)
        ultima_etapa_ordem = db.session.query(func.max(EtapaProcesso.ordem)).scalar()
        
        cards_finalizados_por_dia = db.session.query(
            func.date(HistoricoMovimentacao.data_movimentacao).label('data'),
            func.count(HistoricoMovimentacao.id).label('total')
        ).join(
            EtapaProcesso, HistoricoMovimentacao.etapa_destino_id == EtapaProcesso.id
        ).filter(
            and_(
                HistoricoMovimentacao.data_movimentacao >= data_inicio,
                EtapaProcesso.ordem == ultima_etapa_ordem
            )
        ).group_by(
            func.date(HistoricoMovimentacao.data_movimentacao)
        ).order_by('data').all()
        
        # Converter para formato de resposta
        criados_dict = {str(data): total for data, total in cards_por_dia}
        finalizados_dict = {str(data): total for data, total in cards_finalizados_por_dia}
        
        # Gerar série temporal completa
        serie_temporal = []
        data_atual = data_inicio.date()
        data_fim = datetime.utcnow().date()
        
        while data_atual <= data_fim:
            data_str = str(data_atual)
            serie_temporal.append({
                'data': data_str,
                'cards_criados': criados_dict.get(data_str, 0),
                'cards_finalizados': finalizados_dict.get(data_str, 0)
            })
            data_atual += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'data': {
                'periodo_dias': dias,
                'serie_temporal': serie_temporal
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

