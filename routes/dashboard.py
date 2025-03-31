from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Vendedor, Produto, Venda, Pagamento, db
from forms import RetiradaForm, PagamentoForm, ProdutoForm, VendedorForm
from sqlalchemy.orm import joinedload

bp = Blueprint('dashboard', __name__)

def get_dashboard_stats():
    """Retorna estatísticas gerais do dashboard"""
    return {
        'total_produtos': Produto.query.count(),
        'vendas_pendentes': Venda.query.filter_by(status='pendente').count(),
        'saldo_total': db.session.query(
            db.func.sum(Venda.valor_total - Venda.valor_pago)
        ).scalar() or 0.0,
        'total_estoque': db.session.query(
            db.func.sum(Produto.quantidade_estoque * Produto.preco_unitario)
        ).scalar() or 0.0,
        'categorias_labels': [],
        'categorias_values': [],
        'vendedores_labels': [],
        'vendedores_values': []
    }

@bp.route('/')
@login_required
def dashboard():
    try:
        stats = get_dashboard_stats()
        return render_template('dashboard/dashboard.html', **stats)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return render_template('dashboard/dashboard.html')

@bp.route('/vendedores')
@login_required
def vendedores():
    try:
        vendedores = Vendedor.query.order_by(Vendedor.nome).all()
        stats = get_dashboard_stats()
        return render_template('dashboard/vendedores.html',
                             vendedores=vendedores,
                             total_estoque=stats['total_estoque'])
    except Exception as e:
        flash(f'Erro ao carregar vendedores: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@bp.route('/estoque')
@login_required
def estoque():
    try:
        produtos = Produto.query.order_by(Produto.nome).all()
        stats = get_dashboard_stats()
        return render_template('dashboard/estoque.html',
                            produtos=produtos,
                            total_estoque=stats['total_estoque'])
    except Exception as e:
        flash(f'Erro ao carregar estoque: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@bp.route('/estatisticas')
@login_required
def estatisticas():
    try:
        stats = get_dashboard_stats()
        print(f"DEBUG - Total Estoque: {stats['total_estoque']}")  # Log de debug
        print(f"DEBUG - Total Produtos: {stats['total_produtos']}")  # Log de debug
        return render_template('dashboard/estatisticas.html',
                            total_estoque=stats['total_estoque'],
                            total_produtos=stats['total_produtos'])
    except Exception as e:
        import traceback
        traceback.print_exc()  # Imprime o stack trace completo
        flash(f'Erro detalhado: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@bp.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    form = ProdutoForm()
    try:
        if form.validate_on_submit():
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
    try:
        if request.method == 'POST':
            produto.nome = request.form['nome']
            db.session.commit()
            flash('Item atualizado!', 'success')
            return redirect(url_for('dashboard.estoque'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    return render_template('dashboard/editar_item.html', produto=produto)

@bp.route('/estoque/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    try:
        produto = Produto.query.get_or_404(id)
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
    try:
        form.vendedor.choices = [(u.id, u.username) for u in User.query.filter(User.role.in_(['vendedor', 'funcionario']))]
        form.produto.choices = [(p.id, f"{p.nome} (Estoque: {p.quantidade_estoque})") for p in Produto.query.all()]

        if form.validate_on_submit():
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
    try:
        if form.validate_on_submit():
            novo_vendedor = Vendedor(nome=form.nome.data)
            db.session.add(novo_vendedor)
            db.session.commit()
            flash('Vendedor cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {str(e)}', 'danger')
    return render_template('dashboard/adicionar_vendedor.html', form=form)

@bp.route('/pagamento', methods=['GET', 'POST'])
@login_required
def pagamento():
    form = PagamentoForm()
    try:
        vendas_pendentes = Venda.query.filter_by(status='pendente').all()
        form.venda.choices = [(v.id, f"Venda #{v.id} - Saldo: R$ {v.calcular_saldo():.2f}") for v in vendas_pendentes]

        if form.validate_on_submit():
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
    try:
        vendas = Venda.query.order_by(Venda.data_venda.desc()).all()
        pagamentos = Pagamento.query.order_by(Pagamento.data_pagamento.desc()).all()
        stats = get_dashboard_stats()
        return render_template('dashboard/transacoes.html',
                            vendas=vendas,
                            pagamentos=pagamentos,
                            total_estoque=stats['total_estoque'])
    except Exception as e:
        flash(f'Erro ao carregar transações: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@bp.route('/estoque/tabela')
@login_required
def estoque_tabela():
    try:
        produtos = Produto.query.order_by(Produto.nome).all()
        stats = get_dashboard_stats()
        return render_template('dashboard/estoque_tabela.html',
                            produtos=produtos,
                            total_estoque=stats['total_estoque'])
    except Exception as e:
        flash(f'Erro ao carregar tabela de estoque: {str(e)}', 'danger')
        return redirect(url_for('dashboard.dashboard'))