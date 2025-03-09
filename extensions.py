from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate  # Nova importação

# Inicialização das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()  # Instância do Migrate

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', set())

def configure_extensions(app):
    """Configura todas as extensões do Flask"""
    # Configuração do SQLAlchemy
    db.init_app(app)
    
    # Configuração do Bcrypt
    bcrypt.init_app(app)
    
    # Configuração do Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Configuração do Flask-Migrate
    migrate.init_app(app, db)  # Configuração importante
    
    # Carregador de usuário
    @login_manager.user_loader
    def load_user(user_id):
        from models import User  # Importação local para evitar circular imports
        return User.query.get(int(user_id))