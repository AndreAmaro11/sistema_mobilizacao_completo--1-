from src.models.mobilizacao import db, Usuario, Grupo
from datetime import datetime
from enum import Enum

class TipoPermissao(Enum):
    VISUALIZAR = 'visualizar'
    CRIAR = 'criar'
    EDITAR = 'editar'
    EXCLUIR = 'excluir'
    MOVER = 'mover'
    APROVAR = 'aprovar'
    REJEITAR = 'rejeitar'
    ADMINISTRAR = 'administrar'

class RecursoSistema(Enum):
    CARD = 'card'
    ETAPA = 'etapa'
    USUARIO = 'usuario'
    GRUPO = 'grupo'
    DASHBOARD = 'dashboard'
    RELATORIO = 'relatorio'
    CONFIGURACAO = 'configuracao'
    NOTIFICACAO = 'notificacao'

# Tabela de associação para permissões e grupos (many-to-many)
permissao_grupo = db.Table('permissao_grupo',
    db.Column('permissao_id', db.Integer, db.ForeignKey('permissoes.id'), primary_key=True),
    db.Column('grupo_id', db.Integer, db.ForeignKey('grupos.id'), primary_key=True),
    db.Column('data_associacao', db.DateTime, default=datetime.utcnow)
)

class Permissao(db.Model):
    __tablename__ = 'permissoes'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    criado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    grupos = db.relationship('Grupo', secondary=permissao_grupo, backref=db.backref('permissoes', lazy='dynamic'))
    
    def __init__(self, tipo, recurso, descricao=None, **kwargs):
        if isinstance(tipo, TipoPermissao):
            tipo = tipo.value
        if isinstance(recurso, RecursoSistema):
            recurso = recurso.value
            
        super().__init__(tipo=tipo, recurso=recurso, descricao=descricao, **kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'recurso': self.recurso,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class PermissaoEspecial(db.Model):
    __tablename__ = 'permissoes_especiais'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(50), nullable=False)
    recurso_id = db.Column(db.Integer)  # ID específico do recurso (ex: ID de uma etapa específica)
    concedido = db.Column(db.Boolean, default=True)  # True = conceder, False = negar explicitamente
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_expiracao = db.Column(db.DateTime)  # Opcional, para permissões temporárias
    concedido_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Relacionamentos
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    concessor = db.relationship('Usuario', foreign_keys=[concedido_por])
    
    def __init__(self, tipo, recurso, **kwargs):
        if isinstance(tipo, TipoPermissao):
            tipo = tipo.value
        if isinstance(recurso, RecursoSistema):
            recurso = recurso.value
            
        super().__init__(tipo=tipo, recurso=recurso, **kwargs)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'tipo': self.tipo,
            'recurso': self.recurso,
            'recurso_id': self.recurso_id,
            'concedido': self.concedido,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_expiracao': self.data_expiracao.isoformat() if self.data_expiracao else None,
            'concedido_por': self.concessor.nome if self.concessor else None
        }

class LogAcesso(db.Model):
    __tablename__ = 'log_acessos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo_operacao = db.Column(db.String(50), nullable=False)
    recurso = db.Column(db.String(50), nullable=False)
    recurso_id = db.Column(db.Integer)
    data_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    ip_origem = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    sucesso = db.Column(db.Boolean, default=True)
    detalhes = db.Column(db.Text)
    
    # Relacionamentos
    usuario = db.relationship('Usuario')
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario': self.usuario.nome if self.usuario else None,
            'tipo_operacao': self.tipo_operacao,
            'recurso': self.recurso,
            'recurso_id': self.recurso_id,
            'data_acesso': self.data_acesso.isoformat() if self.data_acesso else None,
            'ip_origem': self.ip_origem,
            'sucesso': self.sucesso,
            'detalhes': self.detalhes
        }

# Funções auxiliares para verificação de permissões
def verificar_permissao(usuario, tipo_permissao, recurso, recurso_id=None):
    """
    Verifica se um usuário tem uma permissão específica para um recurso.
    
    Args:
        usuario: Objeto Usuario
        tipo_permissao: String ou TipoPermissao
        recurso: String ou RecursoSistema
        recurso_id: ID opcional do recurso específico
        
    Returns:
        Boolean: True se tem permissão, False caso contrário
    """
    if usuario.is_admin():
        return True
    
    if isinstance(tipo_permissao, TipoPermissao):
        tipo_permissao = tipo_permissao.value
    if isinstance(recurso, RecursoSistema):
        recurso = recurso.value
    
    # Verificar permissões especiais (negações explícitas têm precedência)
    permissao_especial = PermissaoEspecial.query.filter_by(
        usuario_id=usuario.id,
        tipo=tipo_permissao,
        recurso=recurso
    ).first()
    
    if permissao_especial and permissao_especial.recurso_id == recurso_id:
        return permissao_especial.concedido
    
    # Verificar permissões por grupo
    for grupo in usuario.grupos:
        for permissao in grupo.permissoes:
            if permissao.tipo == tipo_permissao and permissao.recurso == recurso and permissao.ativo:
                return True
    
    return False

def registrar_acesso(usuario, tipo_operacao, recurso, recurso_id=None, ip_origem=None, 
                    user_agent=None, sucesso=True, detalhes=None):
    """
    Registra uma tentativa de acesso no log.
    
    Args:
        usuario: Objeto Usuario
        tipo_operacao: String ou TipoPermissao
        recurso: String ou RecursoSistema
        recurso_id: ID opcional do recurso específico
        ip_origem: Endereço IP de origem
        user_agent: User-Agent do navegador
        sucesso: Boolean indicando se o acesso foi bem-sucedido
        detalhes: Detalhes adicionais sobre o acesso
    """
    if isinstance(tipo_operacao, TipoPermissao):
        tipo_operacao = tipo_operacao.value
    if isinstance(recurso, RecursoSistema):
        recurso = recurso.value
    
    log = LogAcesso(
        usuario_id=usuario.id if usuario else None,
        tipo_operacao=tipo_operacao,
        recurso=recurso,
        recurso_id=recurso_id,
        ip_origem=ip_origem,
        user_agent=user_agent,
        sucesso=sucesso,
        detalhes=detalhes
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log

# Estender a classe Usuario com métodos de permissão
def tem_permissao(self, tipo_permissao, recurso, recurso_id=None):
    """
    Verifica se o usuário tem uma permissão específica.
    """
    return verificar_permissao(self, tipo_permissao, recurso, recurso_id)

def listar_permissoes(self):
    """
    Lista todas as permissões do usuário.
    """
    permissoes = set()
    
    # Permissões de grupo
    for grupo in self.grupos:
        for permissao in grupo.permissoes:
            if permissao.ativo:
                permissoes.add((permissao.tipo, permissao.recurso))
    
    # Permissões especiais (apenas as concedidas)
    permissoes_especiais = PermissaoEspecial.query.filter_by(
        usuario_id=self.id,
        concedido=True
    ).all()
    
    for pe in permissoes_especiais:
        permissoes.add((pe.tipo, pe.recurso))
    
    return list(permissoes)

# Adicionar os métodos à classe Usuario
Usuario.tem_permissao = tem_permissao
Usuario.listar_permissoes = listar_permissoes

