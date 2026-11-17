import os
import uuid
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, Category, Product, Order, OrderItem, ContactMessage

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in with an administrator account to access this section.', 'warning')
            return redirect(url_for('admin.login', next=request.url))
        if not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def handle_image_upload(request_file, fallback_url=None):
    if request_file and request_file.filename != '':
        if allowed_file(request_file.filename):
            ext = request_file.filename.rsplit('.', 1)[1].lower()
            filename = f"prod_{uuid.uuid4().hex[:10]}.{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            request_file.save(upload_path)
            return f"/static/uploads/{filename}"
        else:
            flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP, GIF.', 'warning')
    return fallback_url

# --- ADMIN AUTH ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_admin:
                login_user(user)
                flash(f'Admin access granted. Welcome back, {user.name}!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('This account does not have administrator privileges.', 'danger')
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')
            
    return render_template('admin/login.html')

# --- DASHBOARD OVERVIEW ---
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0
    total_customers = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    
    # Status breakdown
    orders_pending = Order.query.filter_by(order_status='Pending').count()
    orders_confirmed = Order.query.filter_by(order_status='Confirmed').count()
    orders_preparing = Order.query.filter_by(order_status='Preparing').count()
    orders_ready = Order.query.filter_by(order_status='Ready').count()
    orders_completed = Order.query.filter_by(order_status='Completed').count()
    orders_cancelled = Order.query.filter_by(order_status='Cancelled').count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(7).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    stats = {
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'total_customers': total_customers,
        'total_products': total_products,
        'unread_messages': unread_messages,
        'status_counts': {
            'Pending': orders_pending,
            'Confirmed': orders_confirmed,
            'Preparing': orders_preparing,
            'Ready': orders_ready,
            'Completed': orders_completed,
            'Cancelled': orders_cancelled
        }
    }
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_orders=recent_orders,
        recent_messages=recent_messages
    )

# --- PRODUCT MANAGEMENT ---
@admin_bp.route('/products')
@admin_required
def products():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('q', '').strip()
    
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
        
    products_list = query.order_by(Product.category_id.asc(), Product.name.asc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    
    return render_template(
        'admin/products.html',
        products=products_list,
        categories=categories,
        current_cat=category_id,
        search_query=search
    )

@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    categories = Category.query.order_by(Category.name.asc()).all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        description = request.form.get('description', '').strip()
        image_url_input = request.form.get('image_url', '').strip()
        dietary_type = request.form.get('dietary_type', 'Veg')
        prep_time = request.form.get('prep_time', '10-15 mins')
        
        is_featured = bool(request.form.get('is_featured'))
        is_bestseller = bool(request.form.get('is_bestseller'))
        is_available = bool(request.form.get('is_available', True))
        
        if not name or not category_id or price is None or price < 0:
            flash('Please provide a valid product name, category, and positive price.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)
            
        slug = secure_filename(name.lower().replace(' ', '-'))
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        # Image handling
        uploaded_file = request.files.get('image_file')
        final_image_url = handle_image_upload(uploaded_file, fallback_url=image_url_input)
        
        if not final_image_url:
            final_image_url = "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=700&q=80"
            
        product = Product(
            name=name,
            slug=slug,
            category_id=category_id,
            price=price,
            description=description,
            image_url=final_image_url,
            dietary_type=dietary_type,
            prep_time=prep_time,
            is_featured=is_featured,
            is_bestseller=is_bestseller,
            is_available=is_available
        )
        db.session.add(product)
        db.session.commit()
        
        flash(f'Product "{product.name}" added successfully to the menu!', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name.asc()).all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id', type=int)
        price = request.form.get('price', type=float)
        description = request.form.get('description', '').strip()
        image_url_input = request.form.get('image_url', '').strip()
        dietary_type = request.form.get('dietary_type', 'Veg')
        prep_time = request.form.get('prep_time', '10-15 mins')
        
        is_featured = bool(request.form.get('is_featured'))
        is_bestseller = bool(request.form.get('is_bestseller'))
        is_available = bool(request.form.get('is_available'))
        
        if not name or not category_id or price is None or price < 0:
            flash('Please provide valid product details.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)
            
        uploaded_file = request.files.get('image_file')
        final_image_url = handle_image_upload(uploaded_file, fallback_url=image_url_input or product.image_url)
        
        product.name = name
        product.category_id = category_id
        product.price = price
        product.description = description
        product.image_url = final_image_url
        product.dietary_type = dietary_type
        product.prep_time = prep_time
        product.is_featured = is_featured
        product.is_bestseller = is_bestseller
        product.is_available = is_available
        
        db.session.commit()
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    prod_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{prod_name}" has been removed from menu.', 'info')
    return redirect(url_for('admin.products'))

# --- CATEGORY MANAGEMENT ---
@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            image_url = request.form.get('image_url', '').strip()
            icon = request.form.get('icon', 'bi-cup-hot').strip()
            
            if not name:
                flash('Category name is required.', 'danger')
            else:
                slug = secure_filename(name.lower().replace(' ', '-'))
                if Category.query.filter_by(slug=slug).first():
                    flash('A category with this name already exists.', 'warning')
                else:
                    cat = Category(
                        name=name,
                        slug=slug,
                        description=description,
                        image_url=image_url or "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=700&q=80",
                        icon=icon,
                        display_order=Category.query.count() + 1
                    )
                    db.session.add(cat)
                    db.session.commit()
                    flash(f'Category "{name}" created successfully!', 'success')
                    
        elif action == 'edit':
            cat_id = request.form.get('category_id', type=int)
            cat = Category.query.get_or_404(cat_id)
            name = request.form.get('name', '').strip()
            if name:
                cat.name = name
                cat.description = request.form.get('description', '').strip()
                cat.image_url = request.form.get('image_url', '').strip() or cat.image_url
                cat.icon = request.form.get('icon', 'bi-cup-hot').strip()
                db.session.commit()
                flash(f'Category "{name}" updated successfully!', 'success')
                
        elif action == 'delete':
            cat_id = request.form.get('category_id', type=int)
            cat = Category.query.get_or_404(cat_id)
            if cat.products:
                flash(f'Cannot delete category "{cat.name}" because it contains {len(cat.products)} active products. Move or delete products first.', 'warning')
            else:
                db.session.delete(cat)
                db.session.commit()
                flash(f'Category "{cat.name}" deleted successfully.', 'info')
                
        return redirect(url_for('admin.categories'))
        
    categories_list = Category.query.order_by(Category.display_order.asc(), Category.name.asc()).all()
    return render_template('admin/categories.html', categories=categories_list)

# --- ORDERS MANAGEMENT ---
@admin_bp.route('/orders')
@admin_required
def orders():
    status = request.args.get('status', 'all').strip()
    search = request.args.get('q', '').strip()
    
    query = Order.query
    if status and status != 'all':
        query = query.filter_by(order_status=status)
    if search:
        query = query.filter(
            (Order.order_number.ilike(f"%{search}%")) |
            (Order.customer_name.ilike(f"%{search}%")) |
            (Order.customer_phone.ilike(f"%{search}%"))
        )
        
    orders_list = query.order_by(Order.created_at.desc()).all()
    statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled']
    
    return render_template('admin/orders.html', orders=orders_list, current_status=status, statuses=statuses, search_query=search)

@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('order_status')
    payment_status = request.form.get('payment_status')
    
    valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Completed', 'Cancelled']
    if new_status in valid_statuses:
        order.order_status = new_status
        if new_status == 'Completed':
            order.payment_status = 'Paid'
            
    if payment_status in ['Pending', 'Paid', 'Failed']:
        order.payment_status = payment_status
        
    db.session.commit()
    flash(f'Order #{order.order_number} status updated to "{order.order_status}".', 'success')
    return redirect(request.referrer or url_for('admin.orders'))

# --- CONTACT MESSAGES ---
@admin_bp.route('/messages')
@admin_required
def messages():
    messages_list = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages_list)

@admin_bp.route('/messages/<int:message_id>/toggle-read', methods=['POST'])
@admin_required
def toggle_message_read(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    msg.is_read = not msg.is_read
    db.session.commit()
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
@admin_required
def delete_message(message_id):
    msg = ContactMessage.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'info')
    return redirect(url_for('admin.messages'))
