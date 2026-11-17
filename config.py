import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'loozy-cafe-super-secret-key-2026-fresh-happy')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "loozy.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg', 'gif'}
    
    # Store settings
    STORE_NAME = "LOOZY"
    STORE_TAGLINE = "Fresh Taste, Happy Moments"
    CURRENCY_SYMBOL = "₹"
    DELIVERY_FEE = 40.0
    FREE_DELIVERY_THRESHOLD = 499.0 
    TAX_RATE = 0.05  # 5% GST
