from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Venda
from forms import VendaForm
from datetime import datetime

vendas_bp = Blueprint('vendas', __name__, template_folder='../templates/vendas')

@vendas_bp.route('/')
@login_required
def listar_vendas():
    vendas = db.session.query(
        Venda,
        Venda.produto.has(nome='produto_nome'),
        Venda.vendedor.has(username='vendedor_nome')
    ).all()
    
    return render_template('lista.html', vendas=vendas)

@vendas_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova_venda():
    form = VendaForm()
    
    if form.validate_on_submit():
        try:
            nova_venda = Venda(
                produto_id=form.produto.data,
                vendedor_id=form.vendedor.data,
                quantidade=form.quantidade.data,
                preco_unitario=form.preco_unitario.data,
                valor_recebido=form.valor_recebido.data,
                data_venda=datetime.utcnow()
            )
            
            db.session.add(nova_venda)
            db.session.commit()
            flash('Venda registrada com sucesso!', 'success')
            return redirect(url_for('vendas.listar_vendas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar venda: {str(e)}', 'danger')
    
    return render_template('nova.html', form=form)

@vendas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_venda(id):
    venda = Venda.query.get_or_404(id)
    form = VendaForm(obj=venda)
    
    if form.validate_on_submit():
        try:
            venda.produto_id = form.produto.data
            venda.vendedor_id = form.vendedor.data
            venda.quantidade = form.quantidade.data
            venda.preco_unitario = form.preco_unitario.data
            venda.valor_recebido = form.valor_recebido.data
            
            db.session.commit()
            flash('Venda atualizada com sucesso!', 'success')
            return redirect(url_for('vendas.listar_vendas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar venda: {str(e)}', 'danger')
    
    return render_template('editar.html', form=form, venda=venda)

@vendas_bp.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_venda(id):
    venda = Venda.query.get_or_404(id)
    
    try:
        db.session.delete(venda)
        db.session.commit()
        flash('Venda excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir venda: {str(e)}', 'danger')
    
    return redirect(url_for('vendas.listar_vendas'))