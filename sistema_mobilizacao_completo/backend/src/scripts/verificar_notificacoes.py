#!/usr/bin/env python3
"""
Script para executar verificações periódicas de notificações.
Este script deve ser executado periodicamente (ex: via cron) para verificar prazos,
cards inativos, checklist pendentes e enviar notificações.
"""

import os
import sys
import logging
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'notificacoes.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def executar_verificacoes():
    """Executa todas as verificações periódicas"""
    from flask import Flask
    from src.models.mobilizacao import db
    from src.services.notificacao_service import NotificacaoService
    
    # Criar aplicação Flask temporária
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        logger.info("Iniciando verificações periódicas...")
        inicio = datetime.now()
        
        try:
            # Executar todas as verificações
            resultados = NotificacaoService.executar_verificacoes_periodicas()
            
            # Registrar resultados
            logger.info(f"Verificações concluídas em {(datetime.now() - inicio).total_seconds():.2f} segundos")
            logger.info(f"Resultados: {resultados}")
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro ao executar verificações: {str(e)}")
            return None

if __name__ == '__main__':
    executar_verificacoes()

