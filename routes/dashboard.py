from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from flask_login import login_required
from datetime import datetime
from extensions import db, allowed_file
from models import Item
from ocr_processor import OCRProcessor

dashboard_bp = Blueprint('dashboard', __name__)

TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@dashboard_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_itens': Item.query.count(),
        'itens_abaixo_minimo': Item.query.filter(Item.quantidade_atual < Item.quantidade_minima).count(),
        'itens_para_repor': Item.query.filter(Item.quantidade_atual <= Item.quantidade_minima * 1.1).count()
    }
    return render_template('dashboard.html', **stats)

@dashboard_bp.route('/estoque')
@login_required
def estoque():
    return render_template('estoque.html', 
        itens=Item.query.order_by(Item.nome).all()
    )

@dashboard_bp.route('/adicionar_item', methods=['GET', 'POST'])
@login_required
def adicionar_item():
    if request.method == 'POST':
        try:
            novo_item = Item(
                nome=request.form['nome'],
                quantidade_minima=float(request.form['quantidade_minima']),
                quantidade_atual=float(request.form['quantidade_atual']),
                unidade=request.form['unidade']
            )
            db.session.add(novo_item)
            db.session.commit()
            flash('Item adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar item: {str(e)}', 'danger')
    return render_template('adicionar_item.html')

@dashboard_bp.route('/editar_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        try:
            item.nome = request.form['nome']
            item.quantidade_minima = float(request.form['quantidade_minima'])
            item.quantidade_atual = float(request.form['quantidade_atual'])
            item.unidade = request.form['unidade']
            db.session.commit()
            flash('Item atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    return render_template('editar_item.html', item=item)

@dashboard_bp.route('/remover_item/<int:item_id>', methods=['POST'])
@login_required
def remover_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash('Item removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover item: {str(e)}', 'danger')
    return redirect(url_for('dashboard.estoque'))

@dashboard_bp.route('/atualizar_estoque/<int:item_id>', methods=['POST'])
@login_required
def atualizar_estoque(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        nova_quantidade = request.form.get('quantidade_atual')
        if nova_quantidade:
            item.quantidade_atual = float(nova_quantidade)
            item.data_atualizacao = datetime.utcnow()
            db.session.commit()
            flash('Estoque atualizado com sucesso!', 'success')
        else:
            flash('Valor de estoque inválido.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar estoque: {str(e)}', 'danger')
    return redirect(url_for('dashboard.estoque'))

@dashboard_bp.route('/upload_tabela', methods=['POST'])
@login_required
def upload_tabela():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado', 'danger')
        return redirect(url_for('dashboard.estoque'))

    file = request.files['file']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('dashboard.estoque'))

    if not allowed_file(file.filename):
        flash('Formato de arquivo não permitido', 'danger')
        return redirect(url_for('dashboard.estoque'))

    try:
        upload_folder = os.path.join(current_app.root_path, 'temp_uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        ocr = OCRProcessor(TESSERACT_PATH)
        df = ocr.process_inventory_table(filepath)

        if df.empty:
            flash('Nenhum dado válido detectado na tabela', 'warning')
            return redirect(url_for('dashboard.estoque'))

        atualizados = 0
        novos_itens = 0

        try:
            for _, row in df.iterrows():
                item = Item.query.filter_by(nome=row['nome']).first()

                if item:
                    item.quantidade_minima = row['quantidade_minima']
                    item.quantidade_atual = row['quantidade_atual']
                    item.unidade = row['unidade']
                    item.data_atualizacao = datetime.utcnow()
                    atualizados += 1
                else:
                    novo_item = Item(
                        nome=row['nome'],
                        quantidade_minima=row['quantidade_minima'],
                        quantidade_atual=row['quantidade_atual'],
                        unidade=row['unidade'],
                        data_atualizacao=datetime.utcnow()
                    )
                    db.session.add(novo_item)
                    novos_itens += 1

            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao atualizar/inserir dados: {e}", exc_info=True)
            flash(f'Erro ao processar itens: {str(e)}', 'danger')
            return redirect(url_for('dashboard.estoque'))

        os.remove(filepath)
        
        flash(
            f'Tabela processada! Itens detectados: {len(df)} | '
            f'Atualizados: {atualizados} | Novos: {novos_itens}', 
            'success'
        )

    except Exception as e:
        flash(f'Erro no processamento: {str(e)}', 'danger')
        current_app.logger.error(f'Erro no upload: {str(e)}', exc_info=True)
        
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

    return redirect(url_for('dashboard.estoque'))

@dashboard_bp.route('/upload_foto', methods=['POST'])
@login_required
def upload_foto():
    if 'foto' not in request.files:
        flash('Nenhum arquivo enviado', 'error')
        return redirect(url_for('dashboard.estoque'))
    
    file = request.files['foto']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('dashboard.estoque'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            filename
        )
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        flash('Foto enviada com sucesso', 'success')
    else:
        flash('Tipo de arquivo não permitido', 'error')
    
    return redirect(url_for('dashboard.estoque'))