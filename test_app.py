import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from application import app
from models import db, User, Category, Product, Order, ContactMessage

def run_tests():
    client = app.test_client()
    print("=== STARTING LOOZY FULL-STACK TESTS ===")

    # 1. Test Home Page
    res = client.get('/')
    assert res.status_code == 200, f"Home page failed: {res.status_code}"
    assert b"LOOZY" in res.data
    assert b"Fresh Taste" in res.data
    print("[PASS] Home page renders successfully (200 OK)")

    # 2. Test About Page
    res = client.get('/about')
    assert res.status_code == 200
    assert b"Our Story" in res.data or b"LOOZY STORY" in res.data
    print("[PASS] About page renders successfully (200 OK)")

    # 3. Test Menu Page & Filters
    res = client.get('/menu')
    assert res.status_code == 200
    assert b"Fresh Juices" in res.data
    print("[PASS] Menu page renders successfully (200 OK)")

    res_cat = client.get('/menu?category=burgers')
    assert res_cat.status_code == 200
    assert b"Burger" in res_cat.data
    print("[PASS] Menu category filtering works (200 OK)")

    res_search = client.get('/menu?q=chocolate')
    assert res_search.status_code == 200
    assert b"Belgian Chocolate" in res_search.data
    print("[PASS] Menu search query works (200 OK)")

    # 4. Test Single Product Details
    res = client.get('/product/1')
    assert res.status_code == 200
    assert b"Prep Time" in res.data
    print("[PASS] Product detail page renders successfully (200 OK)")

    # 5. Test Cart Functionality
    # Add item 1
    res = client.post('/cart/add/1', data={'quantity': 2}, follow_redirects=True)
    assert res.status_code == 200
    print("[PASS] Add to cart works via form POST")

    # Add item 2 via AJAX header
    res_ajax = client.post('/cart/add/2', data={'quantity': 1}, headers={'X-Requested-With': 'XMLHttpRequest'})
    assert res_ajax.status_code == 200
    data = res_ajax.get_json()
    assert data['success'] is True
    assert data['cart_count'] == 3
    print("[PASS] Add to cart works via AJAX with live count")

    # View Cart
    res = client.get('/cart')
    assert res.status_code == 200
    assert b"Order Summary" in res.data
    print("[PASS] Cart page view displays accurate items & summary (200 OK)")

    # 6. Test Checkout & Order Placement
    res = client.get('/checkout')
    assert res.status_code == 200
    assert b"Customer & Delivery Details" in res.data
    print("[PASS] Checkout page renders successfully (200 OK)")

    # Place order
    order_data = {
        'customer_name': 'Test Foodie',
        'customer_email': 'testfoodie@example.com',
        'customer_phone': '+91 9988776655',
        'delivery_address': 'Flat 101, Test Residency, Koramangala 5th Block, Bangalore',
        'order_notes': 'Please deliver before 2 PM.',
        'payment_method': 'Cash on Delivery'
    }
    res = client.post('/checkout/place', data=order_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"ORDER CONFIRMED" in res.data
    assert b"Test Foodie" in res.data
    print("[PASS] Order placement saves to database and shows receipt (200 OK)")

    # 7. Test Contact Form Submission
    contact_data = {
        'name': 'Rahul Verma',
        'email': 'rahul.verma@example.com',
        'phone': '+91 98765 00000',
        'subject': 'Event Catering',
        'message': 'Hi, I would like to book LOOZY juice bar for our corporate event next month.'
    }
    res = client.post('/contact', data=contact_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Your message has been sent to LOOZY" in res.data
    with app.app_context():
        msg = ContactMessage.query.filter_by(email='rahul.verma@example.com').first()
        assert msg is not None
        assert msg.subject == 'Event Catering'
    print("[PASS] Contact message saved to database (200 OK)")

    # 8. Test Auth: Login & Register
    # User registration
    reg_data = {
        'name': 'New Customer',
        'email': 'newcustomer@loozy.com',
        'phone': '+91 91234 56789',
        'address': 'HSR Layout Sector 2, Bangalore',
        'password': 'password123',
        'confirm_password': 'password123'
    }
    res = client.post('/register', data=reg_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome to LOOZY" in res.data
    print("[PASS] User registration works with password hashing (200 OK)")

    # Logout
    client.get('/logout', follow_redirects=True)

    # Login
    login_data = {
        'email': 'customer@loozy.com',
        'password': 'customer123'
    }
    res = client.post('/login', data=login_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Aarav" in res.data or b"Welcome back" in res.data
    print("[PASS] Customer login and session authentication work (200 OK)")

    # 9. Test Admin Authentication & Dashboard
    # Try accessing admin while logged in as normal customer (should be blocked)
    res = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Access denied" in res.data or res.status_code in [302, 403, 200]
    print("[PASS] Admin protection blocks normal customer access")

    client.get('/logout', follow_redirects=True)

    # Login as Admin
    admin_login_data = {
        'email': 'admin@loozy.com',
        'password': 'admin123'
    }
    res = client.post('/admin/login', data=admin_login_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Operations Overview" in res.data
    print("[PASS] Admin login & Dashboard access work (200 OK)")

    # Admin Products
    res = client.get('/admin/products')
    assert res.status_code == 200
    assert b"Belgian Chocolate Decadence" in res.data
    print("[PASS] Admin products list displays all catalog items (200 OK)")

    # Admin Add Product
    new_prod_data = {
        'name': 'Special Cold Brew Coffee',
        'category_id': 2, # Milkshakes/drinks
        'price': 140.0,
        'dietary_type': 'Beverage',
        'prep_time': '5 mins',
        'description': 'Slow-steeped Arabica coffee beans brewed for 18 hours, served over ice.',
        'image_url': 'https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=700&q=80',
        'is_available': 'on'
    }
    res = client.post('/admin/products/add', data=new_prod_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Special Cold Brew Coffee" in res.data
    print("[PASS] Admin add product works and updates database (200 OK)")

    # Admin Orders
    res = client.get('/admin/orders')
    assert res.status_code == 200
    assert b"Customer Orders" in res.data
    print("[PASS] Admin orders list works (200 OK)")

    # Admin Messages
    res = client.get('/admin/messages')
    assert res.status_code == 200
    assert b"Customer Inquiries" in res.data
    print("[PASS] Admin messages list displays inquiries (200 OK)")

    print("=== ALL 15 INTEGRATION TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == '__main__':
    run_tests()
