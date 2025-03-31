# models/vendedor.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Vendedor {self.nome}>"

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def buscar_todos(cls):
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id):
        return cls.query.get(id)

    def atualizar(self, nome=None, email=None, senha=None):
        if nome:
            self.nome = nome
        if email:
            self.email = email
        if senha:
            self.senha = senha
        db.session.commit()

    def excluir(self):
        db.session.delete(self)
        db.session.commit()