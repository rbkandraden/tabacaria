from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[
        DataRequired(),
        Length(min=4, max=50)
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6)
    ])

class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[
        DataRequired(),
        Length(min=4, max=50)
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirmar Senha', validators=[
        DataRequired(),
        EqualTo('password', message='Senhas devem ser iguais')
    ])
    role = SelectField('Função', choices=[
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor')
    ], validators=[DataRequired()])

class RetiradaForm(FlaskForm):
    vendedor = SelectField('Vendedor', coerce=int, validators=[DataRequired()])
    produto = SelectField('Produto', coerce=int, validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', validators=[
        DataRequired(),
        NumberRange(min=1, message='Quantidade mínima: 1')
    ])

class PagamentoForm(FlaskForm):
    venda = SelectField('Venda Pendente', coerce=int, validators=[DataRequired()])
    valor = DecimalField('Valor do Pagamento', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.01, message='Valor mínimo: R$ 0.01')
    ])
    metodo = SelectField('Método de Pagamento', choices=[
        ('dinheiro', 'Dinheiro'),
        ('cartao', 'Cartão'),
        ('pix', 'PIX')
    ], validators=[DataRequired()])

class ProdutoForm(FlaskForm):
    nome = StringField('Nome do Produto', validators=[DataRequired()])
    quantidade = IntegerField('Estoque Inicial', validators=[
        DataRequired(),
        NumberRange(min=0, message="Valor mínimo: 0")
    ])
    preco = DecimalField('Preço Unitário', places=2, validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Valor mínimo: R$ 0.01")
    ])
    submit = SubmitField('Salvar')

class VendedorForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired()])
    submit = SubmitField('Salvar Vendedor')