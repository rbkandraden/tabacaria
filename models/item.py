# models/item.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Item {self.nome}>"

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def buscar_todos(cls):
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id):
        return cls.query.get(id)

    def atualizar(self, nome=None, descricao=None, preco=None, quantidade_estoque=None):
        if nome:
            self.nome = nome
        if descricao:
            self.descricao = descricao
        if preco:
            self.preco = preco
        if quantidade_estoque:
            self.quantidade_estoque = quantidade_estoque
        db.session.commit()

    def excluir(self):
        db.session.delete(self)
        db.session.commit()