import random
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from models import db, Order, OrderItem, Product
from routes.cart import get_cart_summary

orders_bp = Blueprint('orders', __name__)

def generate_order_number():
    date_str = datetime.utcnow().strftime('%Y%m%d')
    rand_suffix = ''.join(random.choices('0123456789', k=4))
    return f"LOOZY-{date_str}-{rand_suffix}"

@orders_bp.route('/checkout', methods=['GET'])
def checkout():
    cart_summary = get_cart_summary()
    if cart_summary['item_count'] == 0:
        flash('Your cart is empty. Add some delicious items before checkout!', 'warning')
        return redirect(url_for('products.menu'))
        
    return render_template('checkout.html', cart_summary=cart_summary)

@orders_bp.route('/checkout/place', methods=['POST'])
def place_order():
    cart_summary = get_cart_summary()
    if cart_summary['item_count'] == 0:
        flash('Your cart is empty. Cannot place an order.', 'warning')
        return redirect(url_for('products.menu'))
        
    name = request.form.get('customer_name', '').strip()
    email = request.form.get('customer_email', '').strip().lower()
    phone = request.form.get('customer_phone', '').strip()
    address = request.form.get('delivery_address', '').strip()
    order_notes = request.form.get('order_notes', '').strip()
    payment_method = request.form.get('payment_method', 'Cash on Delivery').strip()
    
    # Backend Validation
    errors = []
    if not name or len(name) < 2:
        errors.append('Please provide a valid full name.')
    if not phone or len(phone) < 8:
        errors.append('Please provide a valid phone number (at least 8-10 digits).')
    if not address or len(address) < 5:
        errors.append('Please provide a complete delivery address.')
    if not email:
        errors.append('Please provide an email address for order confirmation.')
        
    if errors:
        for err in errors:
            flash(err, 'danger')
        return render_template('checkout.html', cart_summary=cart_summary,
                               customer_name=name, customer_email=email,
                               customer_phone=phone, delivery_address=address,
                               order_notes=order_notes, payment_method=payment_method)
                               
    order_number = generate_order_number()
    while Order.query.filter_by(order_number=order_number).first():
        order_number = generate_order_number()
        
    user_id = current_user.id if current_user.is_authenticated else None
    
    order = Order(
        order_number=order_number,
        user_id=user_id,
        customer_name=name,
        customer_email=email,
        customer_phone=phone,
        delivery_address=address,
        order_notes=order_notes,
        payment_method=payment_method,
        payment_status="Paid" if payment_method == "UPI / Digital" else "Pending",
        order_status="Confirmed",
        subtotal=cart_summary['subtotal'],
        tax=cart_summary['tax'],
        delivery_fee=cart_summary['delivery_fee'],
        total_amount=cart_summary['grand_total']
    )
    db.session.add(order)
    db.session.flush() # obtain order.id
    
    for item in cart_summary.get('cart_items', []):
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            product_name=item['name'],
            product_price=item['price'],
            quantity=item['quantity'],
            item_subtotal=item['item_total']
        )
        db.session.add(order_item)
        
    db.session.commit()
    
    # Clear cart
    session.pop('cart', None)
    session.modified = True
    
    flash(f'Awesome! Your order #{order.order_number} has been placed successfully!', 'success')
    return redirect(url_for('orders.order_confirmation', order_number=order.order_number))

@orders_bp.route('/order/confirmation/<order_number>')
def order_confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_confirmation.html', order=order)

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

@orders_bp.route('/order/track', methods=['GET', 'POST'])
def track_order():
    order_number = request.args.get('order_number') or request.form.get('order_number')
    order = None
    searched = False
    
    if order_number:
        searched = True
        order_number = order_number.strip().upper()
        order = Order.query.filter_by(order_number=order_number).first()
        if not order:
            flash(f'No order found matching "{order_number}". Please double check your order number.', 'warning')
            
    return render_template('track_order.html', order=order, searched=searched, query_num=order_number)
