from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from functools import wraps
from models import db, User

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('routes.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(name=name).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('Logged in successfully!', 'success')
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('Please fill out all fields.', 'error')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter((User.name == name) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists.', 'error')
            return redirect(url_for('auth.register'))
        
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('routes.index'))