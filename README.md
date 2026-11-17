# LOOZY – Full-Stack Modern Cafe Website

> **Brand Tagline**: *"Fresh Taste, Happy Moments"*  
> **Business Model**: Cafe / Fast Food / Juice Shop  
> **Brand Palette**: Fresh Light Green (`#A8D5A2`, `#E8F5E9`), Dark Forest Green (`#245C36`), Clean White (`#FFFFFF`)

LOOZY is a complete, modern, responsive, and fully functional full-stack web application designed for a trendy cafe. It bridges a customer-facing digital ordering storefront with a real-time administrative operations portal.

---

## 🌟 Key Features

### 🛍️ Customer Experience
- **Interactive Home Page**:
  - Hero banner with brand imagery, floating quick-stats badges, and direct call-to-actions.
  - Category showcase (Fresh Juices, Milkshakes, Burgers, Rolls, Sandwiches, Snacks).
  - Featured specialties and trending bestsellers.
  - Special offers and discount promo cards.
  - Real customer testimonials and brand value pillars.
- **Dynamic Menu Page**:
  - Live in-browser instant search across product titles and descriptions.
  - One-click category filtering without page reloads.
  - Sorting by Price (Low to High, High to Low), Top Ratings, and Bestsellers.
  - Dietary badges (*Veg*, *Vegan*, *Beverage*), preparation times, and prices in Indian Rupees (₹).
  - AJAX-powered *"Add to Cart"* with interactive toast feedback and navbar counter pulse.
- **Product Detail View**:
  - High-resolution imagery, detailed dietary notes, ingredients highlight, and related items.
- **Shopping Cart**:
  - Dynamic quantity increment/decrement with instant subtotal and tax calculation.
  - Item removal with smooth animations.
  - Automatic delivery fee calculation (FREE delivery on orders over ₹499).
- **Streamlined Checkout**:
  - Customer contact details and address capture.
  - Kitchen instructions / delivery notes.
  - Payment options: Cash on Delivery (COD), Pay at Cafe Counter, UPI / Digital QR.
  - Direct database persistence of orders and order items.
- **Real-Time Order Confirmation & Tracking**:
  - Printable receipt invoice.
  - Multi-stage kitchen status tracker (*Pending* ➔ *Confirmed* ➔ *Preparing* ➔ *Ready* ➔ *Completed*).
- **Customer Authentication & Account**:
  - Session-based login, secure password hashing (Werkzeug), profile management, and complete past order history.
- **Contact Us & Map**:
  - Inquiries form connected to the database with server-side validation.
  - Google Maps embed placeholder, cafe timings, and contact cards.

### 🛡️ Administrative Portal
- **Protected Admin Routes**: Strict `@admin_required` access control.
- **Dashboard Analytics**:
  - Total sales revenue counter.
  - Total orders placed.
  - Menu catalog count and registered customer metrics.
  - Live kitchen status breakdown counters (*Pending*, *Preparing*, *Ready*, etc.).
  - Recent orders quick-table and recent contact messages.
- **Menu Management**:
  - View full product catalog with category filters and search.
  - Add new products with file upload or external image URL.
  - Edit pricing, description, dietary classification, and availability toggle.
  - Safe deletion of menu products.
- **Category Management**:
  - Create, edit, and safely delete menu categories.
- **Order Processing & Status Updates**:
  - Live dropdown to transition order status (*Pending*, *Confirmed*, *Preparing*, *Ready*, *Completed*, *Cancelled*).
  - Detailed invoice view with printable receipt.
- **Inquiry Management**:
  - View customer messages, toggle read/unread status, and delete messages.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Google Fonts (Outfit & Plus Jakarta Sans) |
| **Backend** | Python 3.13+, Flask 3.1 Framework |
| **Database** | SQLite, SQLAlchemy ORM, Flask-SQLAlchemy |
| **Security** | Werkzeug Password Hashing (`generate_password_hash`, `check_password_hash`), Flask-Login Session Management |
| **Deployment** | Gunicorn, Procfile, Environment Variable Configuration |

---

## 📂 Project Directory Structure

```text
loozy/
├── application.py         # Application factory, blueprint registrations & startup
├── config.py              # Application settings, database URI, thresholds
├── models.py              # SQLAlchemy models (User, Category, Product, Order, OrderItem, ContactMessage)
├── seed_data.py           # Auto-seeder with 24 realistic products & demo accounts
├── requirements.txt       # Python dependencies
├── Procfile               # Production WSGI process definition
├── .env.example           # Environment variables template
├── README.md              # Project documentation
│
├── routes/                # Modular Flask Blueprints
│   ├── __init__.py
│   ├── auth.py            # User registration, login, logout, profile
│   ├── main.py            # Home, About, Contact
│   ├── products.py        # Menu, live filtering, product detail
│   ├── cart.py            # Cart view, AJAX add/update/remove
│   ├── orders.py          # Checkout, order confirmation, tracking, order history
│   └── admin.py           # Admin login, analytics, product/order/message management
│
├── static/
│   ├── css/
│   │   └── style.css      # Custom cafe brand styling (Light Green & White)
│   ├── js/
│   │   └── script.js      # AJAX cart, toast notifications, search filter
│   ├── images/            # Cafe branding assets
│   └── uploads/           # Uploaded product images
│
└── templates/
    ├── base.html          # Global header, navbar, footer, toast container
    ├── index.html         # Hero, categories, featured, bestsellers, offers, reviews
    ├── about.html         # Cafe story, mission, vision, values, stats
    ├── menu.html          # Interactive menu, category tabs, live search
    ├── product_detail.html# Single product view, dietary info, related items
    ├── cart.html          # Cart table, quantity controls, price breakdown
    ├── checkout.html      # Address form, payment options, order review
    ├── order_confirmation.html # Receipt, step tracker, printable bill
    ├── my_orders.html     # Customer past orders
    ├── track_order.html   # Public order tracker
    ├── login.html         # Customer login
    ├── register.html      # Customer signup
    ├── profile.html       # Customer profile & password management
    ├── contact.html       # Contact form, location, hours, map
    ├── errors/
    │   ├── 404.html       # Custom 404 Not Found page
    │   └── 500.html       # Custom 500 Server Error page
    └── admin/
        ├── admin_base.html# Admin sidebar & layout
        ├── login.html     # Admin login screen
        ├── dashboard.html # Analytics, revenue, status breakdown
        ├── products.html  # Product table & management
        ├── product_form.html # Add / Edit product form
        ├── categories.html# Category manager
        ├── orders.html    # Order list & status updater
        ├── order_detail.html # Printable invoice & customer details
        └── messages.html  # Customer inquiries manager
```

---

## 🚀 Getting Started & Local Execution

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Navigate to the Project Directory
```bash
cd "C:\Users\user\.gemini\antigravity\scratch\loozy"
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python application.py
```

The database tables are **automatically created and seeded** with:
- 6 Categories (*Fresh Juices*, *Milkshakes*, *Burgers*, *Rolls*, *Sandwiches*, *Snacks*)
- 24 Realistic Menu Items with high-res food photography, pricing in ₹, and descriptions
- Admin and Customer test accounts
- Sample orders and contact inquiries

### 5. Access the Website
Open your browser and navigate to:
- **Customer Storefront**: `http://localhost:5000`
- **Menu Page**: `http://localhost:5000/menu`
- **Admin Dashboard**: `http://localhost:5000/admin/login`

---

## 🔑 Pre-Seeded Test Credentials

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@loozy.com` | `admin123` | Full Admin Dashboard & Operations |
| **Customer** | `customer@loozy.com` | `customer123` | Ordering, Cart, Order History |

*Note: You can also register a new customer account anytime via the "Sign Up" page.*

---

## 🧪 Testing Guide

1. **Browse & Search**:
   - Go to `http://localhost:5000/menu`
   - Use the category tabs (*Fresh Juices*, *Burgers*, etc.) to filter items.
   - Type `"Burger"` or `"Chocolate"` into the search bar for live instant filtering.
2. **Add to Cart**:
   - Click **Add** on any product card.
   - Notice the toast confirmation and the pulsating navbar cart count badge.
3. **Cart & Quantity**:
   - Go to the Cart page.
   - Use the `+` and `-` buttons to adjust quantities; watch subtotal and grand total update automatically without full page refresh.
4. **Checkout**:
   - Click "Proceed to Checkout".
   - Enter your name, phone, and delivery address.
   - Choose "Cash on Delivery" or "Pay at Counter".
   - Click "Place Order" to receive your unique Order Number (e.g. `LOOZY-20261112-XXXX`).
5. **Admin Operations**:
   - Log in at `http://localhost:5000/admin/login` using `admin@loozy.com` / `admin123`.
   - View revenue and order statistics.
   - Update order status to *"Preparing"*, *"Ready"*, or *"Completed"*.
   - Add a new product or edit existing items with image upload support.
