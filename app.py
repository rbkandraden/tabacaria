from flask import Flask, redirect, url_for, render_template
import os
from extensions import db, bcrypt, login_manager, configure_extensions, migrate

def create_app():
    app = Flask(__name__)
    
    # Configurações principais
    app.config.update({
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-key-123'),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(app.instance_path, 'tabacaria.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': os.path.join(app.root_path, 'static', 'uploads'),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'gif'}
    })

    # Configurar extensões
    configure_extensions(app)

    with app.app_context():
        # Criar estrutura de diretórios
        required_folders = [
            app.instance_path,
            app.config['UPLOAD_FOLDER'],
            os.path.join(app.root_path, 'temp_uploads')
        ]
        
        for folder in required_folders:
            os.makedirs(folder, exist_ok=True)

        # Importar modelos para criação de tabelas (ATUALIZADO)
        from models import User, Produto, Venda, Pagamento
        
        # Criar todas as tabelas
        db.create_all()

        # Criar admin padrão se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            try:
                db.session.commit()
                print("✅ Admin padrão criado com sucesso!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao criar admin: {str(e)}")

        # Registrar blueprints
        from routes.auth import bp as auth_bp
        from routes.dashboard import bp as dashboard_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Rotas básicas
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Manipuladores de erro
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)