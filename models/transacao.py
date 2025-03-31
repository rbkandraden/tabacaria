# models/transacao.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Transacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedor.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    quantidade = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    vendedor = db.relationship('Vendedor', backref='transacoes')
    item = db.relationship('Item', backref='transacoes')

    def __repr__(self):
        return f"<Transacao {self.id} - {self.quantidade} x {self.item.nome}>"

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def buscar_todas(cls):
        return cls.query.all()

    @classmethod
    def buscar_por_id(cls, id):
        return cls.query.get(id)

    def excluir(self):
        db.session.delete(self)
        db.session.commit()