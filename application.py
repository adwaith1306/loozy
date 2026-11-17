import os
from flask import Flask, render_template, session
from flask_login import LoginManager
from config import Config
from models import db, User, Category
from seed_data import seed_all_data

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_context():
        cart = session.get('cart', {})
        cart_count = sum(item.get('quantity', 1) for item in cart.values())
        categories = Category.query.order_by(Category.display_order.asc()).all()
        return {
            'cart_count': cart_count,
            'nav_categories': categories,
            'STORE_NAME': Config.STORE_NAME,
            'STORE_TAGLINE': Config.STORE_TAGLINE,
            'CURRENCY_SYMBOL': Config.CURRENCY_SYMBOL,
            'FREE_DELIVERY_THRESHOLD': Config.FREE_DELIVERY_THRESHOLD,
            'DELIVERY_FEE': Config.DELIVERY_FEE
        }

    # Custom Error Pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto database setup and seed
    with app.app_context():
        db.create_all()
        # Seed initial categories, menu items, and admin user if empty
        if Category.query.count() == 0 or User.query.filter_by(is_admin=True).count() == 0:
            seed_all_data()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
