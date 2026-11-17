from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Backend validation
        if not name or len(name) < 2:
            flash('Please enter a valid full name (at least 2 characters).', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)
            
        if not email or not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)
            
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please login instead.', 'warning')
            return redirect(url_for('auth.login'))
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)
            
        if password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone, address=address)
            
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            is_admin=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash(f'Welcome to LOOZY, {name}! Your account has been created.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not email or not password:
            flash('Please provide both email and password.', 'warning')
            return render_template('login.html', email=email)
            
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)
            
        login_user(user, remember=remember)
        flash(f'Welcome back, {user.name}!', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
            
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
            
        return redirect(url_for('main.index'))
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully. See you soon at LOOZY!', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            
            if not name:
                flash('Name cannot be empty.', 'danger')
            else:
                current_user.name = name
                current_user.phone = phone
                current_user.address = address
                db.session.commit()
                flash('Your profile details have been updated successfully!', 'success')
                
        elif action == 'change_password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not current_user.check_password(old_password):
                flash('Current password is incorrect.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Your password has been changed successfully!', 'success')
                
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=current_user)
