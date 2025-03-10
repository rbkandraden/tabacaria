from app import create_app
from extensions import db
from models import User, Vendedor

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                role='admin'
            )
            admin.set_password('admin123')
            
            vendedor_admin = Vendedor(
                nome="Administrador",
                user=admin
            )
            
            db.session.add(admin)
            db.session.add(vendedor_admin)
            db.session.commit()

if __name__ == "__main__":
    init_db()