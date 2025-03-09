from app import create_app
from extensions import db
from models import User, Vendedor
from flask import current_app

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Criar admin padrão
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                role='admin'
            )
            admin_user.set_password('admin123')
            
            admin_vendedor = Vendedor(
                nome="Administrador",
                email="admin@empresa.com",
                telefone="(00) 00000-0000",
                user=admin_user
            )
            
            db.session.add(admin_user)
            db.session.add(admin_vendedor)
            db.session.commit()
        
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    init_db()