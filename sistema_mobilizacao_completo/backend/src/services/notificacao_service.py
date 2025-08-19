from src.models.mobilizacao import db, Notificacao, CardMobilizacao, EtapaProcesso, Usuario
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificacaoService:
    """
    Serviço para gerenciar notificações e alertas do sistema.
    """
    
    @staticmethod
    def verificar_prazos_vencidos():
        """
        Verifica cards com prazos vencidos ou próximos de vencer e gera notificações.
        """
        hoje = datetime.utcnow().date()
        
        # Cards com prazo vencido
        cards_vencidos = CardMobilizacao.query.filter(
            CardMobilizacao.prazo_etapa < datetime.utcnow(),
            CardMobilizacao.status_etapa != 'FINALIZADO'
        ).all()
        
        # Cards com prazo próximo de vencer (2 dias)
        prazo_alerta = datetime.utcnow() + timedelta(days=2)
        cards_vencendo = CardMobilizacao.query.filter(
            CardMobilizacao.prazo_etapa <= prazo_alerta,
            CardMobilizacao.prazo_etapa >= datetime.utcnow(),
            CardMobilizacao.status_etapa != 'FINALIZADO'
        ).all()
        
        # Gerar notificações para cards vencidos
        for card in cards_vencidos:
            NotificacaoService.criar_notificacao_prazo_vencido(card)
        
        # Gerar notificações para cards próximos de vencer
        for card in cards_vencendo:
            NotificacaoService.criar_notificacao_prazo_vencendo(card)
        
        return {
            'vencidos': len(cards_vencidos),
            'vencendo': len(cards_vencendo)
        }
    
    @staticmethod
    def verificar_cards_inativos():
        """
        Verifica cards sem atividade recente e gera notificações.
        """
        cards_inativos = []
        
        # Buscar todas as etapas com configuração de alerta de inatividade
        etapas = EtapaProcesso.query.filter(
            EtapaProcesso.dias_alerta_inatividade > 0,
            EtapaProcesso.ativo == True
        ).all()
        
        for etapa in etapas:
            # Calcular data limite para inatividade
            data_limite = datetime.utcnow() - timedelta(days=etapa.dias_alerta_inatividade)
            
            # Buscar cards inativos nesta etapa
            cards = CardMobilizacao.query.filter(
                CardMobilizacao.etapa_atual_id == etapa.id,
                CardMobilizacao.ultima_atualizacao < data_limite,
                CardMobilizacao.status_etapa != 'FINALIZADO'
            ).all()
            
            # Gerar notificações para cards inativos
            for card in cards:
                NotificacaoService.criar_notificacao_card_inativo(card)
                cards_inativos.append(card)
        
        return len(cards_inativos)
    
    @staticmethod
    def verificar_checklist_pendentes():
        """
        Verifica cards com itens obrigatórios de checklist pendentes e gera notificações.
        """
        cards_com_pendencias = []
        
        # Buscar todos os cards ativos
        cards = CardMobilizacao.query.filter(
            CardMobilizacao.status_etapa != 'FINALIZADO'
        ).all()
        
        for card in cards:
            # Verificar se tem itens obrigatórios pendentes
            itens_obrigatorios = [item for item in card.checklist_items 
                                if item.checklist_etapa.obrigatorio and not item.concluido]
            
            if itens_obrigatorios:
                NotificacaoService.criar_notificacao_checklist_pendente(card, len(itens_obrigatorios))
                cards_com_pendencias.append(card)
        
        return len(cards_com_pendencias)
    
    @staticmethod
    def criar_notificacao_prazo_vencido(card):
        """
        Cria uma notificação para um card com prazo vencido.
        """
        # Verificar se já existe notificação recente (últimas 24h)
        notificacao_existente = Notificacao.query.filter(
            Notificacao.tipo == 'PRAZO_VENCIDO',
            Notificacao.card_id == card.id,
            Notificacao.data_criacao >= datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if notificacao_existente:
            return notificacao_existente
        
        # Criar nova notificação
        notificacao = Notificacao(
            tipo='PRAZO_VENCIDO',
            titulo=f'Prazo vencido: {card.nome_colaborador}',
            mensagem=f'O prazo para conclusão da etapa "{card.etapa_atual.nome}" do colaborador {card.nome_colaborador} venceu em {card.prazo_etapa.strftime("%d/%m/%Y")}.',
            destinatario_email=card.responsavel_atual,
            card_id=card.id,
            etapa_id=card.etapa_atual_id
        )
        
        db.session.add(notificacao)
        db.session.commit()
        
        # Tentar enviar email
        NotificacaoService.enviar_email_notificacao(notificacao)
        
        return notificacao
    
    @staticmethod
    def criar_notificacao_prazo_vencendo(card):
        """
        Cria uma notificação para um card com prazo próximo de vencer.
        """
        # Verificar se já existe notificação recente (últimas 24h)
        notificacao_existente = Notificacao.query.filter(
            Notificacao.tipo == 'PRAZO_VENCENDO',
            Notificacao.card_id == card.id,
            Notificacao.data_criacao >= datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if notificacao_existente:
            return notificacao_existente
        
        # Calcular dias restantes
        dias_restantes = (card.prazo_etapa - datetime.utcnow()).days + 1
        
        # Criar nova notificação
        notificacao = Notificacao(
            tipo='PRAZO_VENCENDO',
            titulo=f'Prazo próximo: {card.nome_colaborador}',
            mensagem=f'O prazo para conclusão da etapa "{card.etapa_atual.nome}" do colaborador {card.nome_colaborador} vence em {dias_restantes} dias ({card.prazo_etapa.strftime("%d/%m/%Y")}).',
            destinatario_email=card.responsavel_atual,
            card_id=card.id,
            etapa_id=card.etapa_atual_id
        )
        
        db.session.add(notificacao)
        db.session.commit()
        
        # Tentar enviar email
        NotificacaoService.enviar_email_notificacao(notificacao)
        
        return notificacao
    
    @staticmethod
    def criar_notificacao_card_inativo(card):
        """
        Cria uma notificação para um card inativo.
        """
        # Verificar se já existe notificação recente (últimas 24h)
        notificacao_existente = Notificacao.query.filter(
            Notificacao.tipo == 'CARD_INATIVO',
            Notificacao.card_id == card.id,
            Notificacao.data_criacao >= datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if notificacao_existente:
            return notificacao_existente
        
        # Calcular dias de inatividade
        dias_inativo = (datetime.utcnow() - card.ultima_atualizacao).days
        
        # Criar nova notificação
        notificacao = Notificacao(
            tipo='CARD_INATIVO',
            titulo=f'Card inativo: {card.nome_colaborador}',
            mensagem=f'O card do colaborador {card.nome_colaborador} está sem atualizações há {dias_inativo} dias na etapa "{card.etapa_atual.nome}".',
            destinatario_email=card.responsavel_atual,
            card_id=card.id,
            etapa_id=card.etapa_atual_id
        )
        
        db.session.add(notificacao)
        db.session.commit()
        
        # Tentar enviar email
        NotificacaoService.enviar_email_notificacao(notificacao)
        
        return notificacao
    
    @staticmethod
    def criar_notificacao_checklist_pendente(card, qtd_pendentes):
        """
        Cria uma notificação para um card com itens obrigatórios de checklist pendentes.
        """
        # Verificar se já existe notificação recente (últimas 24h)
        notificacao_existente = Notificacao.query.filter(
            Notificacao.tipo == 'CHECKLIST_PENDENTE',
            Notificacao.card_id == card.id,
            Notificacao.data_criacao >= datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if notificacao_existente:
            return notificacao_existente
        
        # Criar nova notificação
        notificacao = Notificacao(
            tipo='CHECKLIST_PENDENTE',
            titulo=f'Checklist pendente: {card.nome_colaborador}',
            mensagem=f'O card do colaborador {card.nome_colaborador} possui {qtd_pendentes} itens obrigatórios pendentes na etapa "{card.etapa_atual.nome}".',
            destinatario_email=card.responsavel_atual,
            card_id=card.id,
            etapa_id=card.etapa_atual_id
        )
        
        db.session.add(notificacao)
        db.session.commit()
        
        # Tentar enviar email
        NotificacaoService.enviar_email_notificacao(notificacao)
        
        return notificacao
    
    @staticmethod
    def criar_notificacao_movimentacao(card, etapa_origem, etapa_destino, usuario):
        """
        Cria uma notificação para movimentação de card entre etapas.
        """
        # Criar nova notificação para o responsável da etapa de destino
        notificacao = Notificacao(
            tipo='CARD_MOVIDO',
            titulo=f'Card movido: {card.nome_colaborador}',
            mensagem=f'O card do colaborador {card.nome_colaborador} foi movido da etapa "{etapa_origem.nome}" para "{etapa_destino.nome}" por {usuario.nome}.',
            destinatario_email=etapa_destino.dono_email,
            card_id=card.id,
            etapa_id=etapa_destino.id
        )
        
        db.session.add(notificacao)
        db.session.commit()
        
        # Tentar enviar email
        NotificacaoService.enviar_email_notificacao(notificacao)
        
        return notificacao
    
    @staticmethod
    def enviar_email_notificacao(notificacao):
        """
        Tenta enviar um email para a notificação.
        """
        # Em ambiente de desenvolvimento, apenas simular o envio
        if os.environ.get('FLASK_ENV') == 'development':
            logger.info(f"[SIMULAÇÃO DE EMAIL] Para: {notificacao.destinatario_email}, Assunto: {notificacao.titulo}")
            logger.info(f"[SIMULAÇÃO DE EMAIL] Mensagem: {notificacao.mensagem}")
            
            # Marcar como enviado
            notificacao.enviado = True
            notificacao.data_envio = datetime.utcnow()
            db.session.commit()
            return True
        
        # Em produção, tentar enviar email real
        try:
            # Configurações de email (devem vir de variáveis de ambiente em produção)
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
            smtp_port = int(os.environ.get('SMTP_PORT', 587))
            smtp_user = os.environ.get('SMTP_USER', 'user@example.com')
            smtp_password = os.environ.get('SMTP_PASSWORD', 'password')
            from_email = os.environ.get('FROM_EMAIL', 'sistema@mobilizacao.com.br')
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = notificacao.destinatario_email
            msg['Subject'] = notificacao.titulo
            
            # Adicionar corpo do email
            corpo_email = f"""
            <html>
            <body>
                <h2>{notificacao.titulo}</h2>
                <p>{notificacao.mensagem}</p>
                <p>Esta é uma notificação automática do Sistema de Mobilização.</p>
                <p>Para mais detalhes, acesse o sistema.</p>
            </body>
            </html>
            """
            msg.attach(MIMEText(corpo_email, 'html'))
            
            # Conectar ao servidor SMTP e enviar
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            
            # Marcar como enviado
            notificacao.enviado = True
            notificacao.data_envio = datetime.utcnow()
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            
            # Registrar erro
            notificacao.enviado = False
            notificacao.tentativas_envio += 1
            notificacao.erro_envio = str(e)
            db.session.commit()
            
            return False
    
    @staticmethod
    def processar_notificacoes_pendentes():
        """
        Processa notificações pendentes de envio.
        """
        # Buscar notificações não enviadas com menos de 5 tentativas
        notificacoes = Notificacao.query.filter(
            Notificacao.enviado == False,
            Notificacao.tentativas_envio < 5
        ).all()
        
        enviadas = 0
        falhas = 0
        
        for notificacao in notificacoes:
            if NotificacaoService.enviar_email_notificacao(notificacao):
                enviadas += 1
            else:
                falhas += 1
        
        return {
            'processadas': len(notificacoes),
            'enviadas': enviadas,
            'falhas': falhas
        }
    
    @staticmethod
    def marcar_como_lida(notificacao_id, usuario_id):
        """
        Marca uma notificação como lida.
        """
        notificacao = Notificacao.query.get(notificacao_id)
        
        if not notificacao:
            return False
        
        notificacao.lido = True
        notificacao.data_leitura = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def listar_notificacoes_usuario(email, lidas=False, limite=50):
        """
        Lista notificações para um usuário específico.
        """
        query = Notificacao.query.filter_by(destinatario_email=email)
        
        if not lidas:
            query = query.filter_by(lido=False)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Notificacao.data_criacao.desc())
        
        # Limitar resultados
        query = query.limit(limite)
        
        return query.all()
    
    @staticmethod
    def contar_notificacoes_nao_lidas(email):
        """
        Conta notificações não lidas para um usuário.
        """
        return Notificacao.query.filter_by(
            destinatario_email=email,
            lido=False
        ).count()
    
    @staticmethod
    def executar_verificacoes_periodicas():
        """
        Executa todas as verificações periódicas de uma vez.
        """
        resultados = {
            'prazos': NotificacaoService.verificar_prazos_vencidos(),
            'inativos': NotificacaoService.verificar_cards_inativos(),
            'checklist': NotificacaoService.verificar_checklist_pendentes(),
            'pendentes': NotificacaoService.processar_notificacoes_pendentes()
        }
        
        return resultados

