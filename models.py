from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='funcionario')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    vendedor = db.relationship('Vendedor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', back_populates='vendedor')
    vendas = db.relationship('Venda', back_populates='vendedor')

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    quantidade_estoque = db.Column(db.Integer)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=True)
    vendedor = db.relationship('Vendedor', backref='produtos')

    @property
    def valor_total_estoque(self):
        return self.quantidade_estoque * self.preco_unitario

class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='pendente')
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    vendedor = db.relationship('Vendedor', back_populates='vendas')
    produto = db.relationship('Produto', backref='vendas')
    pagamentos = db.relationship('Pagamento', back_populates='venda')

    def calcular_saldo(self):
        return float(self.valor_total) - float(self.valor_pago)

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    metodo = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    venda = db.relationship('Venda', back_populates='pagamentos')
    vendedor = db.relationship('Vendedor', backref='pagamentos')