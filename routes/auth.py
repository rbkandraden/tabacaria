from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm
from models import User
from extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.dashboard'))
        else:
            flash('Usuário ou senha incorretos', 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != 'admin':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registro realizado com sucesso!', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro no registro: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)

# Nova rota para o painel administrativo
@bp.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('dashboard.dashboard'))
    
        return render_template('admin/panel.html')