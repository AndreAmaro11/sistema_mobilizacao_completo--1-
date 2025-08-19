"""
Configurações de produção para o Sistema de Mobilização.
Este arquivo contém configurações específicas para o ambiente de produção.
"""

import os
import secrets
from datetime import timedelta

# Configurações de segurança
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Configurações de banco de dados
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', 
    f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_recycle': 1800,
    'pool_pre_ping': True
}

# Configurações de CORS
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')

# Configurações de cache
CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 300

# Configurações de logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = os.environ.get('LOG_FILE', 'app.log')

# Configurações de email
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.example.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'user@example.com')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'password')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'sistema@mobilizacao.com.br')

# Configurações de notificações
NOTIFICACOES_VERIFICACAO_INTERVALO = int(os.environ.get('NOTIFICACOES_VERIFICACAO_INTERVALO', 3600))  # 1 hora
NOTIFICACOES_MAX_TENTATIVAS = int(os.environ.get('NOTIFICACOES_MAX_TENTATIVAS', 5))

# Configurações de segurança adicionais
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SAMESITE = 'Lax'

# Configurações de rate limiting
RATELIMIT_ENABLED = True
RATELIMIT_DEFAULT = "100/hour;1000/day"
RATELIMIT_STORAGE_URL = "memory://"

# Configurações de upload de arquivos
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

# Configurações de timeout
REQUEST_TIMEOUT = 60  # segundos

