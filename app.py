from flask import Flask, redirect, url_for, render_template
import os
from extensions import db, bcrypt, login_manager, configure_extensions, migrate
from config import Config

def create_app():
    app = Flask(__name__)

    # Configurar o aplicativo com as configurações externas
    app.config.from_object(Config)

    # Configurar extensões
    configure_extensions(app)

    # Rota de debug para verificar arquivos estáticos
    @app.route('/debug-path')
    def debug_path():
        css_path = os.path.join(app.static_folder, 'css', 'styles.css')
        return f"""
        Static folder: {app.static_folder}<br>
        CSS path: {css_path}<br>
        Exists: {os.path.exists(css_path)}
        """

    with app.app_context():
        # Criar estrutura de diretórios necessários
        required_folders = [
            app.instance_path,  # Diretório da instância
            app.config['UPLOAD_FOLDER'],  # Diretório de uploads
            os.path.join(app.root_path, 'temp_uploads')  # Diretório temporário para uploads
        ]
        
        for folder in required_folders:
            os.makedirs(folder, exist_ok=True)  # Cria a pasta se não existir

        # Importar modelos para criação de tabelas
        from models import User, Produto, Venda, Pagamento
        
        # Criar todas as tabelas
        db.create_all()

        # Criar admin padrão se não existir
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                role='admin'
            )
            admin.set_password('admin123')  # Senha do admin
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
        return redirect(url_for('auth.login'))  # Redireciona para a página de login

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
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')