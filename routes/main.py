from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db, Category, Product, ContactMessage
import re

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    categories = Category.query.order_by(Category.display_order).all()
    featured_products = Product.query.filter_by(is_featured=True, is_available=True).limit(6).all()
    bestseller_products = Product.query.filter_by(is_bestseller=True, is_available=True).limit(6).all()
    
    testimonials = [
        {
            "name": "Ananya Roy",
            "role": "Food Blogger & Regular Customer",
            "rating": 5,
            "comment": "LOOZY has the best shakes and burgers in town! The Belgian Chocolate Decadence shake is to die for, and their buns are always fresh and pillowy.",
            "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80"
        },
        {
            "name": "Rohan Mehta",
            "role": "College Student",
            "rating": 5,
            "comment": "Our gang hangs out at LOOZY every evening after classes. Super affordable, vibrant light-green vibe, quick service, and the Peri-Peri fries are absolute fire!",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"
        },
        {
            "name": "Sneha Iyer",
            "role": "Fitness Enthusiast",
            "rating": 5,
            "comment": "Cold-pressed juices with zero added sugar are hard to find at cafes. LOOZY's Green Detox and Orange Bliss juices are genuinely natural and super refreshing.",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
        }
    ]
    
    special_offers = [
        {
            "title": "Combo Fiesta",
            "badge": "Flat 20% OFF",
            "subtitle": "Burger + Shake + Fries",
            "description": "Get LOOZY Signature Crisp Burger with Belgian Shake & Peri-Peri Fries at a special combo price.",
            "code": "LOOZYCOMBO",
            "bg_color": "#E8F5E9"
        },
        {
            "title": "Fresh Morning Boost",
            "badge": "Buy 1 Get 1 @ 50%",
            "subtitle": "Cold-Pressed Juices",
            "description": "Order any 2 cold-pressed juices before 12 PM and get 50% discount on the second juice.",
            "code": "JUICEBOOST",
            "bg_color": "#D8F3DC"
        }
    ]

    return render_template(
        'index.html',
        categories=categories,
        featured_products=featured_products,
        bestsellers=bestseller_products,
        testimonials=testimonials,
        special_offers=special_offers
    )

@main_bp.route('/about')
def about():
    stats = [
        {"count": "15,000+", "label": "Happy Foodies Served"},
        {"count": "25+", "label": "Signature Recipes"},
        {"count": "100%", "label": "Fresh & Preservative-Free"},
        {"count": "4.9 ★", "label": "Customer Average Rating"}
    ]
    
    values = [
        {
            "icon": "bi-heart-pulse-fill",
            "title": "Uncompromised Freshness",
            "desc": "We squeeze real fresh fruits per order and never use premixes, syrups, or harmful artificial chemicals."
        },
        {
            "icon": "bi-award-fill",
            "title": "Chef-Crafted Flavors",
            "desc": "Each burger, sandwich, and roll recipe is perfected with house-made sauces and premium ingredients."
        },
        {
            "icon": "bi-emoji-smile-fill",
            "title": "Youthful & Welcoming",
            "desc": "LOOZY is designed as a cheerful hangout where friends bond over delicious bites and happy memories."
        },
        {
            "icon": "bi-shield-check",
            "title": "Top-Tier Hygiene",
            "desc": "Cleanliness and food safety are our utmost priority. Every order is prepared in a pristine kitchen."
        }
    ]
    
    return render_template('about.html', stats=stats, values=values)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation
        if not name or len(name) < 2:
            flash('Please enter your full name.', 'danger')
            return render_template('contact.html', name=name, email=email, phone=phone, subject=subject, message=message)
            
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email or not re.match(email_pattern, email):
            flash('Please provide a valid email address.', 'danger')
            return render_template('contact.html', name=name, email=email, phone=phone, subject=subject, message=message)
            
        if not subject:
            flash('Please select or specify a subject for your inquiry.', 'danger')
            return render_template('contact.html', name=name, email=email, phone=phone, subject=subject, message=message)
            
        if not message or len(message) < 10:
            flash('Please enter your message (at least 10 characters).', 'danger')
            return render_template('contact.html', name=name, email=email, phone=phone, subject=subject, message=message)
            
        contact_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message
        )
        db.session.add(contact_msg)
        db.session.commit()
        
        flash('Thank you! Your message has been sent to LOOZY. Our cafe manager will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('contact.html')
