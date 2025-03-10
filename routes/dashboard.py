from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Vendedor, Produto, Venda, Pagamento, db
from forms import RetiradaForm, PagamentoForm, ProdutoForm, VendedorForm

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_produtos': Produto.query.count(),
        'vendas_pendentes': Venda.query.filter_by(status='pendente').count(),
        'saldo_total': db.session.query(db.func.sum(Venda.valor_total - Venda.valor_pago)).scalar() or 0.0
    }
    return render_template('dashboard/dashboard.html', **stats)

@bp.route('/estoque')
@login_required
def estoque():
    produtos = Produto.query.order_by(Produto.nome).all()
    total_estoque = db.session.query(
        db.func.sum(Produto.quantidade_estoque * Produto.preco_unitario)
    ).scalar() or 0.0
    return render_template('dashboard/estoque.html', produtos=produtos, total_estoque=total_estoque)

@bp.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        try:
            produto = Produto(
                nome=form.nome.data,
                quantidade_estoque=form.quantidade.data,
                preco_unitario=form.preco.data
            )
            db.session.add(produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    return render_template('dashboard/adicionar_item.html', form=form)

@bp.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        try:
            produto.nome = request.form['nome']
            produto.quantidade_estoque = int(request.form['estoque'])
            produto.preco_unitario = float(request.form['preco'])
            db.session.commit()
            flash('Produto atualizado!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    return render_template('dashboard/editar_produto.html', produto=produto)

@bp.route('/estoque/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    try:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    return redirect(url_for('dashboard.estoque'))

@bp.route('/retirada', methods=['GET', 'POST'])
@login_required
def retirada():
    form = RetiradaForm()
    form.vendedor.choices = [(u.id, u.username) for u in User.query.filter(User.role.in_(['vendedor', 'funcionario']))]
    form.produto.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Produto.query.all()]
    
    if form.validate_on_submit():
        try:
            produto = Produto.query.get(form.produto.data)
            vendedor = User.query.get(form.vendedor.data)
            
            if produto.quantidade_estoque < form.quantidade.data:
                flash('Estoque insuficiente!', 'danger')
                return redirect(url_for('dashboard.retirada'))
            
            valor_total = form.quantidade.data * float(produto.preco_unitario)
            
            nova_venda = Venda(
                quantidade=form.quantidade.data,
                preco_unitario=produto.preco_unitario,
                valor_total=valor_total,
                vendedor_id=vendedor.id,
                produto_id=produto.id,
                status='pendente'
            )
            
            produto.quantidade_estoque -= form.quantidade.data
            
            db.session.add(nova_venda)
            db.session.commit()
            flash('Retirada registrada com sucesso!', 'success')
            return redirect(url_for('dashboard.transacoes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('dashboard/retirada.html', form=form)

@bp.route('/adicionar_vendedor', methods=['GET', 'POST'])
@login_required
def adicionar_vendedor():
    form = VendedorForm()
    
    if form.validate_on_submit():
        try:
            novo_vendedor = Vendedor(
                nome=form.nome.data,
            )
            db.session.add(novo_vendedor)
            db.session.commit()
            flash('Vendedor cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))  # Correção aplicada aqui
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('dashboard/adicionar_vendedor.html', form=form)

@bp.route('/pagamento', methods=['GET', 'POST'])
@login_required
def pagamento():
    form = PagamentoForm()
    vendas_pendentes = Venda.query.filter_by(status='pendente').all()
    form.venda.choices = [(v.id, f"Venda #{v.id} - Saldo: R$ {v.calcular_saldo():.2f}") for v in vendas_pendentes]
    
    if form.validate_on_submit():
        try:
            venda = Venda.query.get(form.venda.data)
            valor_pagamento = form.valor.data
            
            if valor_pagamento > venda.calcular_saldo():
                flash('Valor excede o saldo pendente!', 'danger')
                return redirect(url_for('dashboard.pagamento'))
            
            novo_pagamento = Pagamento(
                valor=valor_pagamento,
                metodo=form.metodo.data,
                venda_id=venda.id,
                vendedor_id=venda.vendedor_id
            )
            
            venda.valor_pago += valor_pagamento
            if venda.valor_pago >= venda.valor_total:
                venda.status = 'pago'
            
            db.session.add(novo_pagamento)
            db.session.commit()
            flash('Pagamento registrado com sucesso!', 'success')
            return redirect(url_for('dashboard.transacoes'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
    
    return render_template('dashboard/pagamento.html', form=form)

@bp.route('/transacoes')
@login_required
def transacoes():
    vendas = Venda.query.order_by(Venda.data_venda.desc()).all()
    pagamentos = Pagamento.query.order_by(Pagamento.data_pagamento.desc()).all()
    total_estoque = db.session.query(
        db.func.sum(Produto.quantidade_estoque * Produto.preco_unitario)
    ).scalar() or 0.0
    return render_template('dashboard/transacoes.html',
                         vendas=vendas,
                         pagamentos=pagamentos,
                         total_estoque=total_estoque)



