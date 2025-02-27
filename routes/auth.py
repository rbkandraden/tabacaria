from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import LoginForm, RegisterForm
from functools import wraps


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)

            print(f"Usuário logado: {user.username}, Role: {user.role}")  # Debug

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    # Adicionar um campo para a role no formulário (supondo que você tenha esse campo na classe do formulário)
    if form.validate_on_submit():
        role = form.role.data if form.role.data else 'funcionario' 

        new_user = User(username=form.username.data, role=role)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            user_role = current_user.role.lower() 
            expected_role = role.lower() 

            print(f"Usuário logado: {current_user.username}, Role: {user_role}, Esperado: {expected_role}")  # Debug

            # Verificar se o usuário é admin
            if user_role != expected_role and user_role != "admin":
                flash("Acesso negado!", "danger")
                return redirect(url_for("auth.login"))  

            return f(*args, **kwargs)
        return wrapped_function
    return decorator


@bp.route("/admin_panel")
@login_required
@role_required("administrador")
def admin_panel():
    return render_template("admin_panel.html")

@bp.route("/gerente_panel")
@login_required
@role_required("gerente")
def gerente_panel():
    return render_template("gerente_panel.html")