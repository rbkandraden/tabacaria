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
    
    # Relacionamento 1:1 com Vendedor (APENAS PARA USUÁRIOS DO TIPO VENDEDOR)
    vendedor = db.relationship('Vendedor', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    # Chave estrangeira para User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    user = db.relationship('User', back_populates='vendedor')
    
    # Relacionamento com Venda
    vendas = db.relationship('Venda', back_populates='vendedor')

class Produto(db.Model):
    __tablename__ = 'produto'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer)
    
    # Chave estrangeira para Vendedor
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'))
    vendedor = db.relationship('Vendedor', backref='produtos')

    @property
    def valor_total_estoque(self):
        return self.quantidade_estoque * self.preco_unitario

    def __repr__(self):
        return f'<Produto {self.nome}>'

class Venda(db.Model):
    __tablename__ = 'vendas'
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='pendente')
    
    # Chaves estrangeiras CORRETAS
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    
    # Relacionamentos CORRETOS
    vendedor = db.relationship('Vendedor', back_populates='vendas')
    produto = db.relationship('Produto', backref='vendas')
    pagamentos = db.relationship('Pagamento', back_populates='venda')

    def calcular_saldo(self):
        return float(self.valor_total) - float(self.valor_pago)

    def __repr__(self):
        return f'<Venda {self.id} - {self.produto.nome}>'

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    metodo = db.Column(db.String(50))
    observacao = db.Column(db.Text)
    
    # Chaves estrangeiras
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'), nullable=False)
    
    # Relacionamentos
    venda = db.relationship('Venda', back_populates='pagamentos')
    vendedor = db.relationship('Vendedor', backref='pagamentos')

    def __repr__(self):
        return f'<Pagamento {self.id} - R${self.valor}>'