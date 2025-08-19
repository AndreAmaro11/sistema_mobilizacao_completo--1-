import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.mobilizacao import db
from src.routes.auth import auth_bp
from src.routes.cards import cards_bp
from src.routes.etapas import etapas_bp
from src.routes.usuarios import usuarios_bp
from src.routes.dashboard import dashboard_bp
from src.routes.permissoes import permissoes_bp
from src.routes.notificacoes import notificacoes_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(cards_bp, url_prefix='/api/cards')
app.register_blueprint(etapas_bp, url_prefix='/api/etapas')
app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(permissoes_bp, url_prefix='/api/permissoes')
app.register_blueprint(notificacoes_bp, url_prefix='/api/notificacoes')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    # Criar dados iniciais se necessário
    from src.utils.seed_data import criar_dados_iniciais
    criar_dados_iniciais()
    
    # Inicializar permissões
    from src.utils.init_permissoes import inicializar_permissoes
    inicializar_permissoes()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
