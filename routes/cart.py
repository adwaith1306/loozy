from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models import Product
from config import Config

cart_bp = Blueprint('cart', __name__)

def get_cart_summary():
    """Helper to calculate cart subtotal, taxes, delivery fee, and grand total."""
    cart = session.get('cart', {})
    items = []
    subtotal = 0.0
    total_quantity = 0
    
    for product_id_str, item in cart.items():
        qty = int(item.get('quantity', 1))
        price = float(item.get('price', 0.0))
        item_total = price * qty
        subtotal += item_total
        total_quantity += qty
        
        items.append({
            'product_id': int(product_id_str),
            'name': item.get('name'),
            'price': price,
            'image_url': item.get('image_url'),
            'category_name': item.get('category_name'),
            'dietary_type': item.get('dietary_type', 'Veg'),
            'quantity': qty,
            'item_total': item_total
        })
        
    tax = round(subtotal * Config.TAX_RATE, 2)
    
    if subtotal == 0:
        delivery_fee = 0.0
    elif subtotal >= Config.FREE_DELIVERY_THRESHOLD:
        delivery_fee = 0.0
    else:
        delivery_fee = Config.DELIVERY_FEE
        
    grand_total = round(subtotal + tax + delivery_fee, 2)
    amount_to_free_delivery = max(0.0, round(Config.FREE_DELIVERY_THRESHOLD - subtotal, 2))
    
    return {
        'cart_items': items,
        'items': items,
        'item_count': total_quantity,
        'unique_items': len(items),
        'subtotal': round(subtotal, 2),
        'tax': tax,
        'tax_rate_percent': int(Config.TAX_RATE * 100),
        'delivery_fee': delivery_fee,
        'free_delivery_threshold': Config.FREE_DELIVERY_THRESHOLD,
        'amount_to_free_delivery': amount_to_free_delivery,
        'is_free_delivery': (subtotal >= Config.FREE_DELIVERY_THRESHOLD and subtotal > 0),
        'grand_total': grand_total
    }

@cart_bp.route('/cart')
def view_cart():
    summary = get_cart_summary()
    return render_template('cart.html', cart_summary=summary)

@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not product.is_available:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'This item is currently out of stock.'}), 400
        flash('This item is currently out of stock.', 'warning')
        return redirect(request.referrer or url_for('products.menu'))
        
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
        
    if 'cart' not in session:
        session['cart'] = {}
        
    cart = session['cart']
    pid_str = str(product_id)
    
    if pid_str in cart:
        cart[pid_str]['quantity'] += quantity
    else:
        cart[pid_str] = {
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'category_name': product.category.name if product.category else 'Cafe Menu',
            'dietary_type': product.dietary_type,
            'quantity': quantity
        }
        
    session.modified = True
    summary = get_cart_summary()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'"{product.name}" added to cart!',
            'cart_count': summary['item_count'],
            'cart_subtotal': summary['subtotal'],
            'cart_total': summary['grand_total'],
            'product_name': product.name,
            'item_quantity': cart[pid_str]['quantity']
        })
        
    flash(f'"{product.name}" added to your cart!', 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))

@cart_bp.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    pid_str = str(product_id)
    cart = session.get('cart', {})
    
    if pid_str not in cart:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Item not in cart.'}), 404
        flash('Item not found in your cart.', 'warning')
        return redirect(url_for('cart.view_cart'))
        
    action = request.form.get('action')
    try:
        if action == 'increase':
            cart[pid_str]['quantity'] += 1
        elif action == 'decrease':
            cart[pid_str]['quantity'] -= 1
            if cart[pid_str]['quantity'] <= 0:
                del cart[pid_str]
        elif action == 'set':
            new_qty = int(request.form.get('quantity', 1))
            if new_qty > 0:
                cart[pid_str]['quantity'] = new_qty
            else:
                del cart[pid_str]
    except Exception:
        pass
        
    session.modified = True
    summary = get_cart_summary()
    
    item_subtotal = 0.0
    item_qty = 0
    if pid_str in cart:
        item_qty = cart[pid_str]['quantity']
        item_subtotal = cart[pid_str]['price'] * item_qty
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'item_quantity': item_qty,
            'item_subtotal': round(item_subtotal, 2),
            'cart_count': summary['item_count'],
            'subtotal': summary['subtotal'],
            'tax': summary['tax'],
            'delivery_fee': summary['delivery_fee'],
            'grand_total': summary['grand_total'],
            'is_removed': (pid_str not in cart)
        })
        
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    pid_str = str(product_id)
    cart = session.get('cart', {})
    
    removed_name = "Item"
    if pid_str in cart:
        removed_name = cart[pid_str].get('name', 'Item')
        del cart[pid_str]
        session.modified = True
        
    summary = get_cart_summary()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'"{removed_name}" removed from cart.',
            'cart_count': summary['item_count'],
            'subtotal': summary['subtotal'],
            'tax': summary['tax'],
            'delivery_fee': summary['delivery_fee'],
            'grand_total': summary['grand_total'],
            'is_empty': (summary['item_count'] == 0)
        })
        
    flash(f'"{removed_name}" was removed from your cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/cart/clear', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    session.modified = True
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))
