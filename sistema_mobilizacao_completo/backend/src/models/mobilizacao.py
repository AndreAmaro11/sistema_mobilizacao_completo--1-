from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()

# Tabela de associação para usuários e grupos (many-to-many)
usuario_grupo = db.Table('usuario_grupo',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupos.id'), primary_key=True),
    db.Column('data_associacao', db.DateTime, default=datetime.utcnow)
)

# Tabela de associação para etapas e grupos (many-to-many)
etapa_grupo = db.Table('etapa_grupo',
    db.Column('etapa_id', db.Integer, db.ForeignKey('etapas_processo.id'), primary_key=True),
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupos.id'), primary_key=True),
    db.Column('data_associacao', db.DateTime, default=datetime.utcnow)
)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_ultimo_acesso = db.Column(db.DateTime)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    grupos = db.relationship('Grupo', secondary=usuario_grupo, back_populates='usuarios')
    cards_criados = db.relationship('CardMobilizacao', foreign_keys='CardMobilizacao.criado_por', back_populates='criador')
    cards_atualizados = db.relationship('CardMobilizacao', foreign_keys='CardMobilizacao.atualizado_por', back_populates='atualizador')
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def is_admin(self):
        return any(grupo.nome == 'Administrador' for grupo in self.grupos)
    
    def pode_criar_cards(self):
        return self.is_admin() or any(grupo.nome == 'Requisição' for grupo in self.grupos)
    
    def pode_editar_etapa(self, etapa_id):
        etapa = EtapaProcesso.query.get(etapa_id)
        if not etapa:
            return False
        return self.is_admin() or any(grupo in etapa.grupos_permitidos for grupo in self.grupos)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'grupos': [grupo.nome for grupo in self.grupos],
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_ultimo_acesso': self.data_ultimo_acesso.isoformat() if self.data_ultimo_acesso else None
        }

class Grupo(db.Model):
    __tablename__ = 'grupos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', secondary=usuario_grupo, back_populates='grupos')
    etapas_permitidas = db.relationship('EtapaProcesso', secondary=etapa_grupo, back_populates='grupos_permitidos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'total_usuarios': len(self.usuarios),
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class EtapaProcesso(db.Model):
    __tablename__ = 'etapas_processo'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, unique=True, nullable=False)
    prazo_dias = db.Column(db.Integer, nullable=False, default=5)
    dias_alerta_inatividade = db.Column(db.Integer, default=3)
    dono_email = db.Column(db.String(150), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    grupos_permitidos = db.relationship('Grupo', secondary=etapa_grupo, back_populates='etapas_permitidas')
    checklist_items = db.relationship('ChecklistEtapa', back_populates='etapa', cascade='all, delete-orphan')
    cards = db.relationship('CardMobilizacao', back_populates='etapa_atual')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ordem': self.ordem,
            'prazo_dias': self.prazo_dias,
            'dias_alerta_inatividade': self.dias_alerta_inatividade,
            'dono_email': self.dono_email,
            'ativo': self.ativo,
            'grupos_permitidos': [grupo.nome for grupo in self.grupos_permitidos],
            'checklist': [item.to_dict() for item in self.checklist_items if item.ativo]
        }

class ChecklistEtapa(db.Model):
    __tablename__ = 'checklist_etapas'
    
    id = db.Column(db.Integer, primary_key=True)
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapas_processo.id'), nullable=False)
    tarefa = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    obrigatorio = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    etapa = db.relationship('EtapaProcesso', back_populates='checklist_items')
    checklist_cards = db.relationship('ChecklistCard', back_populates='checklist_etapa')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tarefa': self.tarefa,
            'descricao': self.descricao,
            'obrigatorio': self.obrigatorio,
            'ordem': self.ordem,
            'ativo': self.ativo
        }

class CardMobilizacao(db.Model):
    __tablename__ = 'cards_mobilizacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_colaborador = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    cargo = db.Column(db.String(100))
    salario = db.Column(db.Numeric(10, 2))
    centro_custo = db.Column(db.String(50))
    data_admissao = db.Column(db.Date)
    etapa_atual_id = db.Column(db.Integer, db.ForeignKey('etapas_processo.id'), nullable=False)
    status_etapa = db.Column(db.String(20), default='NAO_INICIADO')
    data_entrada_etapa = db.Column(db.DateTime, default=datetime.utcnow)
    prazo_etapa = db.Column(db.DateTime)
    responsavel_atual = db.Column(db.String(150))
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    etapa_atual = db.relationship('EtapaProcesso', back_populates='cards')
    criador = db.relationship('Usuario', foreign_keys=[criado_por], back_populates='cards_criados')
    atualizador = db.relationship('Usuario', foreign_keys=[atualizado_por], back_populates='cards_atualizados')
    checklist_items = db.relationship('ChecklistCard', back_populates='card', cascade='all, delete-orphan')
    historico = db.relationship('HistoricoMovimentacao', back_populates='card', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calcular_prazo_etapa()
        self.criar_checklist_inicial()
    
    def calcular_prazo_etapa(self):
        if self.etapa_atual:
            self.prazo_etapa = self.data_entrada_etapa + timedelta(days=self.etapa_atual.prazo_dias)
            self.responsavel_atual = self.etapa_atual.dono_email
    
    def criar_checklist_inicial(self):
        if self.etapa_atual and not self.checklist_items:
            for item_etapa in self.etapa_atual.checklist_items:
                if item_etapa.ativo:
                    checklist_card = ChecklistCard(
                        card_id=self.id,
                        checklist_etapa_id=item_etapa.id,
                        concluido=False
                    )
                    self.checklist_items.append(checklist_card)
    
    def mover_para_etapa(self, nova_etapa_id, usuario_id, motivo=None):
        etapa_anterior = self.etapa_atual_id
        self.etapa_atual_id = nova_etapa_id
        self.status_etapa = 'NAO_INICIADO'
        self.data_entrada_etapa = datetime.utcnow()
        self.atualizado_por = usuario_id
        self.ultima_atualizacao = datetime.utcnow()
        
        # Recalcular prazo
        self.calcular_prazo_etapa()
        
        # Registrar no histórico
        historico = HistoricoMovimentacao(
            card_id=self.id,
            etapa_origem_id=etapa_anterior,
            etapa_destino_id=nova_etapa_id,
            usuario_id=usuario_id,
            motivo=motivo
        )
        self.historico.append(historico)
        
        # Criar novo checklist
        self.criar_checklist_para_nova_etapa()
    
    def criar_checklist_para_nova_etapa(self):
        # Remove checklist da etapa anterior
        ChecklistCard.query.filter_by(card_id=self.id).delete()
        
        # Cria checklist para nova etapa
        if self.etapa_atual:
            for item_etapa in self.etapa_atual.checklist_items:
                if item_etapa.ativo:
                    checklist_card = ChecklistCard(
                        card_id=self.id,
                        checklist_etapa_id=item_etapa.id,
                        concluido=False
                    )
                    self.checklist_items.append(checklist_card)
    
    def get_status_prazo(self):
        if not self.prazo_etapa:
            return 'NO_PRAZO'
        
        agora = datetime.utcnow()
        if agora > self.prazo_etapa:
            return 'VENCIDO'
        elif agora > (self.prazo_etapa - timedelta(days=2)):
            return 'VENCENDO'
        else:
            return 'NO_PRAZO'
    
    def get_progresso_checklist(self):
        total = len(self.checklist_items)
        concluidos = len([item for item in self.checklist_items if item.concluido])
        percentual = (concluidos / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'concluidos': concluidos,
            'percentual': round(percentual, 1)
        }
    
    def pode_finalizar_etapa(self):
        obrigatorios = [item for item in self.checklist_items 
                       if item.checklist_etapa.obrigatorio]
        return all(item.concluido for item in obrigatorios)
    
    def to_dict(self, incluir_detalhes=False):
        base_dict = {
            'id': self.id,
            'nome_colaborador': self.nome_colaborador,
            'cpf': self.cpf,
            'cargo': self.cargo,
            'salario': float(self.salario) if self.salario else None,
            'centro_custo': self.centro_custo,
            'data_admissao': self.data_admissao.isoformat() if self.data_admissao else None,
            'etapa_atual': self.etapa_atual.to_dict() if self.etapa_atual else None,
            'status_etapa': self.status_etapa,
            'data_entrada_etapa': self.data_entrada_etapa.isoformat() if self.data_entrada_etapa else None,
            'prazo_etapa': self.prazo_etapa.isoformat() if self.prazo_etapa else None,
            'responsavel_atual': self.responsavel_atual,
            'status_prazo': self.get_status_prazo(),
            'checklist_progresso': self.get_progresso_checklist(),
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
        
        if incluir_detalhes:
            base_dict.update({
                'checklist': [item.to_dict() for item in self.checklist_items],
                'historico': [h.to_dict() for h in self.historico]
            })
        
        return base_dict

class ChecklistCard(db.Model):
    __tablename__ = 'checklist_card'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards_mobilizacao.id'), nullable=False)
    checklist_etapa_id = db.Column(db.Integer, db.ForeignKey('checklist_etapas.id'), nullable=False)
    concluido = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.DateTime)
    concluido_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    card = db.relationship('CardMobilizacao', back_populates='checklist_items')
    checklist_etapa = db.relationship('ChecklistEtapa', back_populates='checklist_cards')
    usuario_conclusao = db.relationship('Usuario')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tarefa': self.checklist_etapa.tarefa if self.checklist_etapa else '',
            'descricao': self.checklist_etapa.descricao if self.checklist_etapa else '',
            'obrigatorio': self.checklist_etapa.obrigatorio if self.checklist_etapa else True,
            'concluido': self.concluido,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'concluido_por': self.usuario_conclusao.nome if self.usuario_conclusao else None,
            'observacoes': self.observacoes
        }

class HistoricoMovimentacao(db.Model):
    __tablename__ = 'historico_movimentacao'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards_mobilizacao.id'), nullable=False)
    etapa_origem_id = db.Column(db.Integer, db.ForeignKey('etapas_processo.id'))
    etapa_destino_id = db.Column(db.Integer, db.ForeignKey('etapas_processo.id'), nullable=False)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    motivo = db.Column(db.Text)
    tempo_permanencia_dias = db.Column(db.Integer)
    status_origem = db.Column(db.String(20))
    status_destino = db.Column(db.String(20), default='NAO_INICIADO')
    
    # Relacionamentos
    card = db.relationship('CardMobilizacao', back_populates='historico')
    etapa_origem = db.relationship('EtapaProcesso', foreign_keys=[etapa_origem_id])
    etapa_destino = db.relationship('EtapaProcesso', foreign_keys=[etapa_destino_id])
    usuario = db.relationship('Usuario')
    
    def to_dict(self):
        return {
            'id': self.id,
            'etapa_origem': self.etapa_origem.nome if self.etapa_origem else None,
            'etapa_destino': self.etapa_destino.nome if self.etapa_destino else None,
            'data_movimentacao': self.data_movimentacao.isoformat() if self.data_movimentacao else None,
            'usuario': self.usuario.nome if self.usuario else None,
            'motivo': self.motivo,
            'tempo_permanencia_dias': self.tempo_permanencia_dias,
            'status_origem': self.status_origem,
            'status_destino': self.status_destino
        }

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    destinatario_email = db.Column(db.String(150), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards_mobilizacao.id'))
    etapa_id = db.Column(db.Integer, db.ForeignKey('etapas_processo.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_envio = db.Column(db.DateTime)
    enviado = db.Column(db.Boolean, default=False)
    lido = db.Column(db.Boolean, default=False)
    data_leitura = db.Column(db.DateTime)
    tentativas_envio = db.Column(db.Integer, default=0)
    erro_envio = db.Column(db.Text)
    
    # Relacionamentos
    card = db.relationship('CardMobilizacao')
    etapa = db.relationship('EtapaProcesso')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensagem': self.mensagem,
            'card_id': self.card_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'lido': self.lido,
            'data_leitura': self.data_leitura.isoformat() if self.data_leitura else None
        }

