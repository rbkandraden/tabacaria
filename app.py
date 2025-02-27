from flask import Flask, redirect, url_for
import os
from extensions import db, configure_extensions

def create_app():
    app = Flask(__name__)
    
    # Configurações essenciais
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-key-123'),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(app.instance_path, 'wayne_security.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'},
        'UPLOAD_FOLDER': os.path.join(app.root_path, 'static', 'uploads'),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB
    })

    # Configurar extensões
    configure_extensions(app)

    # Garantir estrutura de pastas
    with app.app_context():
        # Criar pastas necessárias
        required_folders = [
            app.instance_path,
            app.config['UPLOAD_FOLDER'],
            os.path.join(app.root_path, 'temp_uploads')
        ]
        
        for folder in required_folders:
            os.makedirs(folder, exist_ok=True)

        # Inicializar banco de dados
        from models import User, Item
        db.create_all()

        # Registrar blueprints
        from routes.auth import bp as auth_bp
        from routes.dashboard import dashboard_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Rota principal
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)