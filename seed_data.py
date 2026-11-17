import os
import random
from datetime import datetime, timedelta
from models import db, User, Category, Product, Order, OrderItem, ContactMessage

def seed_all_data():
    """Seeds the database with essential initial data if empty."""
    # 1. Seed Admin User
    admin = User.query.filter_by(email='admin@loozy.com').first()
    if not admin:
        admin = User(
            name='LOOZY Admin',
            email='admin@loozy.com',
            phone='+91 98765 43210',
            address='LOOZY Flagship Cafe, MG Road, Bangalore',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    # 2. Seed Demo Customer User
    customer = User.query.filter_by(email='customer@loozy.com').first()
    if not customer:
        customer = User(
            name='Aarav Sharma',
            email='customer@loozy.com',
            phone='+91 98123 45678',
            address='Flat 402, Green Glen Layout, Bellandur, Bangalore',
            is_admin=False
        )
        customer.set_password('customer123')
        db.session.add(customer)

    db.session.commit()

    # 3. Seed Categories
    categories_data = [
        {
            "name": "Fresh Juices",
            "slug": "fresh-juices",
            "description": "100% natural cold-pressed juices made from fresh handpicked seasonal fruits with no added sugar or preservatives.",
            "image_url": "https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-cup-straw",
            "display_order": 1
        },
        {
            "name": "Milkshakes",
            "slug": "milkshakes",
            "description": "Thick, creamy, decadent milkshakes loaded with rich flavors, dairy ice cream, and irresistible toppings.",
            "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-cup-hot-fill",
            "display_order": 2
        },
        {
            "name": "Burgers",
            "slug": "burgers",
            "description": "Juicy, mouth-watering gourmet burgers crafted with butter-toasted brioche buns, fresh crunch, and signature sauces.",
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-cake2",
            "display_order": 3
        },
        {
            "name": "Rolls",
            "slug": "rolls",
            "description": "Crispy, flaky, and warm paratha wraps packed with flavorful spiced fillings, crunchy veggies, and tangy house dips.",
            "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-box",
            "display_order": 4
        },
        {
            "name": "Sandwiches",
            "slug": "sandwiches",
            "description": "Artisan grilled and toasted sandwiches bursting with melted cheese, herb fillings, and farm-fresh ingredients.",
            "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-layers-half",
            "display_order": 5
        },
        {
            "name": "Snacks",
            "slug": "snacks",
            "description": "Crispy golden appetizers, loaded fries, cheesy bites, and savory treats perfect for pairing with your drinks.",
            "image_url": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=700&q=80",
            "icon": "bi-lightning-charge",
            "display_order": 6
        }
    ]

    category_map = {}
    for cat_data in categories_data:
        cat = Category.query.filter_by(slug=cat_data["slug"]).first()
        if not cat:
            cat = Category(**cat_data)
            db.session.add(cat)
            db.session.flush()
        category_map[cat.slug] = cat.id

    db.session.commit()

    # 4. Seed Products
    products_data = [
        # --- FRESH JUICES ---
        {
            "category_slug": "fresh-juices",
            "name": "Fresh Orange Bliss",
            "slug": "fresh-orange-bliss",
            "description": "Cold-pressed pure Valencia oranges packed with Vitamin C, natural zest, and zero added sugar. Clean and refreshing.",
            "price": 120.0,
            "image_url": "https://images.unsplash.com/photo-1613478223719-2ab802602423?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Beverage",
            "prep_time": "5-8 mins",
            "rating": 4.9
        },
        {
            "category_slug": "fresh-juices",
            "name": "Watermelon Mint Cooler",
            "slug": "watermelon-mint-cooler",
            "description": "Crisp juicy watermelon freshly muddled with fresh mint leaves, hint of lemon, and rock salt for the ultimate thirst quencher.",
            "price": 110.0,
            "image_url": "https://images.unsplash.com/photo-1589733955941-5eeaf752f6dd?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": False,
            "dietary_type": "Beverage",
            "prep_time": "5-8 mins",
            "rating": 4.8
        },
        {
            "category_slug": "fresh-juices",
            "name": "Green Detox Elixir",
            "slug": "green-detox-elixir",
            "description": "Revitalizing green juice made with Granny Smith apples, crisp cucumber, fresh spinach, celery, and ginger root.",
            "price": 150.0,
            "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Vegan",
            "prep_time": "6-10 mins",
            "rating": 4.7
        },
        {
            "category_slug": "fresh-juices",
            "name": "Pure Pomegranate Ruby",
            "slug": "pure-pomegranate-ruby",
            "description": "100% natural, antioxidant powerhouse squeezed fresh from ruby red pomegranates with no artificial additives.",
            "price": 160.0,
            "image_url": "https://images.unsplash.com/photo-1553530666-ba11a7da3888?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Beverage",
            "prep_time": "5-8 mins",
            "rating": 4.9
        },

        # --- MILKSHAKES ---
        {
            "category_slug": "milkshakes",
            "name": "Belgian Chocolate Decadence",
            "slug": "belgian-chocolate-decadence",
            "description": "Indulgent Belgian dark cocoa blended with rich dairy ice cream, chocolate fudge syrup, and topped with chocolate shavings.",
            "price": 180.0,
            "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "8-10 mins",
            "rating": 5.0
        },
        {
            "category_slug": "milkshakes",
            "name": "Strawberry Velvet Shake",
            "slug": "strawberry-velvet-shake",
            "description": "Fresh garden strawberries blended with creamy vanilla ice cream, whipped cream swirl, and pink sprinkles.",
            "price": 170.0,
            "image_url": "https://images.unsplash.com/photo-1579954115545-a95591f28bfc?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "8-10 mins",
            "rating": 4.8
        },
        {
            "category_slug": "milkshakes",
            "name": "Nutella Hazelnut Overload",
            "slug": "nutella-hazelnut-overload",
            "description": "Rich creamy hazelnut Nutella shake topped with roasted caramelized hazelnuts, waffle stick, and chocolate syrup.",
            "price": 210.0,
            "image_url": "https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10 mins",
            "rating": 4.9
        },
        {
            "category_slug": "milkshakes",
            "name": "Classic Oreo Cookies & Cream",
            "slug": "classic-oreo-cookies-and-cream",
            "description": "Crunchy Oreo cookies crushed and blended with chilled creamy milk and vanilla bean gelato, topped with cookie crumble.",
            "price": 160.0,
            "image_url": "https://images.unsplash.com/photo-1577805947697-89e18249d767?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "8 mins",
            "rating": 4.8
        },

        # --- BURGERS ---
        {
            "category_slug": "burgers",
            "name": "LOOZY Signature Crisp Burger",
            "slug": "loozy-signature-crisp-burger",
            "description": "Our chef's pride: double crispy vegetable patty, molten cheddar slice, crisp lettuce, gherkins, and house secret herb sauce in a brioche bun.",
            "price": 160.0,
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "12-15 mins",
            "rating": 4.9
        },
        {
            "category_slug": "burgers",
            "name": "Fiery Paneer Tikka Burger",
            "slug": "fiery-paneer-tikka-burger",
            "description": "Tender tandoori grilled paneer steak coated in spiced masala, pickled red onions, mint mayonnaise, and iceberg lettuce.",
            "price": 190.0,
            "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "12-15 mins",
            "rating": 4.8
        },
        {
            "category_slug": "burgers",
            "name": "Double Cheese Smasher",
            "slug": "double-cheese-smasher",
            "description": "Two hearty spiced patties layered with double molten American cheddar, caramelized onions, and smoky BBQ aioli.",
            "price": 220.0,
            "image_url": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "15 mins",
            "rating": 4.9
        },
        {
            "category_slug": "burgers",
            "name": "Crispy Herb & Mushroom Melt",
            "slug": "crispy-herb-and-mushroom-melt",
            "description": "Herb-crusted portobello and button mushrooms sautéed in garlic butter, topped with melted mozzarella and rocket leaves.",
            "price": 200.0,
            "image_url": "https://images.unsplash.com/photo-1582196016295-f8c8bd4b3e99?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "12-15 mins",
            "rating": 4.7
        },

        # --- ROLLS ---
        {
            "category_slug": "rolls",
            "name": "Paneer Makhani Kathi Roll",
            "slug": "paneer-makhani-kathi-roll",
            "description": "Marinated paneer chunks simmered in aromatic makhani gravy, rolled in a flaky layered paratha with spiced onion crunch.",
            "price": 150.0,
            "image_url": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10-12 mins",
            "rating": 4.9
        },
        {
            "category_slug": "rolls",
            "name": "Spicy Schezwan Veg Roll",
            "slug": "spicy-schezwan-veg-roll",
            "description": "Crispy seasoned vegetable fritters wok-tossed with spicy Schezwan sauce, bell peppers, scallions, and tangy slaw.",
            "price": 140.0,
            "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "10 mins",
            "rating": 4.6
        },
        {
            "category_slug": "rolls",
            "name": "Cheesy Corn & Jalapeno Roll",
            "slug": "cheesy-corn-and-jalapeno-roll",
            "description": "Golden sweet corn and spicy pickled jalapenos smothered in creamy cheese sauce, wrapped warm in a herb paratha.",
            "price": 160.0,
            "image_url": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10-12 mins",
            "rating": 4.8
        },
        {
            "category_slug": "rolls",
            "name": "Falafel & Garlic Hummus Wrap",
            "slug": "falafel-and-garlic-hummus-wrap",
            "description": "Crispy chickpea herb falafels nestled on smooth house garlic hummus, pickled gherkins, fresh mint, and tahini drizzle.",
            "price": 170.0,
            "image_url": "https://images.unsplash.com/photo-1529042410759-befb1204b468?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Vegan",
            "prep_time": "10 mins",
            "rating": 4.8
        },

        # --- SANDWICHES ---
        {
            "category_slug": "sandwiches",
            "name": "LOOZY Club Garden Grilled Sandwich",
            "slug": "loozy-club-garden-grilled-sandwich",
            "description": "Triple-decker toasted sandwich loaded with sliced cucumbers, tomatoes, spiced potatoes, cheddar melt, and cilantro chutney.",
            "price": 160.0,
            "image_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10-12 mins",
            "rating": 4.9
        },
        {
            "category_slug": "sandwiches",
            "name": "Paneer Tikka Focaccia Sandwich",
            "slug": "paneer-tikka-focaccia-sandwich",
            "description": "Handcrafted rosemary focaccia bread filled with charred cottage cheese, sun-dried tomatoes, and basil chipotle spread.",
            "price": 180.0,
            "image_url": "https://images.unsplash.com/photo-1553909489-cd47e0907980?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "12 mins",
            "rating": 4.7
        },
        {
            "category_slug": "sandwiches",
            "name": "Creamy Corn & Spinach Melt",
            "slug": "creamy-corn-and-spinach-melt",
            "description": "Sautéed baby spinach and sweet American corn folded in velvety white sauce, sandwiched and grilled with mozzarella.",
            "price": 150.0,
            "image_url": "https://images.unsplash.com/photo-1509722747041-616f39b57569?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10 mins",
            "rating": 4.8
        },
        {
            "category_slug": "sandwiches",
            "name": "Avocado Tomato Sourdough Toast",
            "slug": "avocado-tomato-sourdough-toast",
            "description": "Toasted sourdough loaf topped with chunky seasoned Hass avocado, cherry tomatoes, Danish feta, and toasted sesame seeds.",
            "price": 210.0,
            "image_url": "https://images.unsplash.com/photo-1588137378633-dea1336ce1e2?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "8-10 mins",
            "rating": 4.9
        },

        # --- SNACKS ---
        {
            "category_slug": "snacks",
            "name": "Cheesy Peri-Peri Loaded Fries",
            "slug": "cheesy-peri-peri-loaded-fries",
            "description": "Crisp golden skin-on potato fries dusted with piquant peri-peri seasoning and smothered in warm gooey cheddar sauce.",
            "price": 130.0,
            "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=700&q=80",
            "is_featured": True,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "8-10 mins",
            "rating": 4.9
        },
        {
            "category_slug": "snacks",
            "name": "Ultimate Nachos Grande",
            "slug": "ultimate-nachos-grande",
            "description": "Crispy Mexican tortilla chips layered with molten cheese, fresh pico de gallo, spicy sliced jalapenos, and sour cream.",
            "price": 170.0,
            "image_url": "https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": True,
            "dietary_type": "Veg",
            "prep_time": "10 mins",
            "rating": 4.8
        },
        {
            "category_slug": "snacks",
            "name": "Crispy Veg Spring Rolls (6 Pcs)",
            "slug": "crispy-veg-spring-rolls",
            "description": "Golden fried rolls stuffed with glass noodles, shredded cabbage, carrots, and mushrooms, served with spicy sweet chili dip.",
            "price": 140.0,
            "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Vegan",
            "prep_time": "10-12 mins",
            "rating": 4.7
        },
        {
            "category_slug": "snacks",
            "name": "Garlic Herb Bread with Cheese",
            "slug": "garlic-herb-bread-with-cheese",
            "description": "Artisan French baguette slices slathered with freshly churned garlic-parsley butter and baked until bubbly with mozzarella.",
            "price": 150.0,
            "image_url": "https://images.unsplash.com/photo-1619860860774-1e2e17343432?auto=format&fit=crop&w=700&q=80",
            "is_featured": False,
            "is_bestseller": False,
            "dietary_type": "Veg",
            "prep_time": "8-10 mins",
            "rating": 4.8
        }
    ]

    for prod_info in products_data:
        cat_slug = prod_info.pop("category_slug")
        cat_id = category_map.get(cat_slug)
        if cat_id:
            existing = Product.query.filter_by(slug=prod_info["slug"]).first()
            if not existing:
                prod = Product(category_id=cat_id, **prod_info)
                db.session.add(prod)

    db.session.commit()

    # 5. Seed Sample Contact Message
    if ContactMessage.query.count() == 0:
        sample_msg = ContactMessage(
            name='Priya Patel',
            email='priya.patel@example.com',
            phone='+91 98760 12345',
            subject='Inquiry regarding Catering for Birthday Party',
            message='Hello LOOZY team! We love your juices and burgers. We are planning a birthday gathering for 25 people next Saturday and would love to know if you offer bulk cafe catering packages. Thanks!',
            is_read=False
        )
        db.session.add(sample_msg)
        db.session.commit()

    # 6. Seed Sample Orders for Admin Dashboard Demo
    if Order.query.count() == 0:
        # Sample Order 1 (Completed)
        sample_prod1 = Product.query.filter_by(slug="loozy-signature-crisp-burger").first()
        sample_prod2 = Product.query.filter_by(slug="belgian-chocolate-decadence").first()
        sample_prod3 = Product.query.filter_by(slug="cheesy-peri-peri-loaded-fries").first()
        
        if sample_prod1 and sample_prod2 and sample_prod3:
            subtotal1 = (sample_prod1.price * 2) + sample_prod2.price + sample_prod3.price
            tax1 = round(subtotal1 * 0.05, 2)
            total1 = subtotal1 + tax1  # free delivery >= 499

            order1 = Order(
                order_number="LOOZY-20261110-8492",
                user_id=customer.id if customer else None,
                customer_name="Aarav Sharma",
                customer_email="customer@loozy.com",
                customer_phone="+91 98123 45678",
                delivery_address="Flat 402, Green Glen Layout, Bellandur, Bangalore",
                order_notes="Please provide extra napkins and spicy dip.",
                payment_method="Cash on Delivery",
                payment_status="Paid",
                order_status="Completed",
                subtotal=subtotal1,
                tax=tax1,
                delivery_fee=0.0,
                total_amount=total1,
                created_at=datetime.utcnow() - timedelta(days=2)
            )
            db.session.add(order1)
            db.session.flush()

            db.session.add(OrderItem(order_id=order1.id, product_id=sample_prod1.id, product_name=sample_prod1.name, product_price=sample_prod1.price, quantity=2, item_subtotal=sample_prod1.price*2))
            db.session.add(OrderItem(order_id=order1.id, product_id=sample_prod2.id, product_name=sample_prod2.name, product_price=sample_prod2.price, quantity=1, item_subtotal=sample_prod2.price))
            db.session.add(OrderItem(order_id=order1.id, product_id=sample_prod3.id, product_name=sample_prod3.name, product_price=sample_prod3.price, quantity=1, item_subtotal=sample_prod3.price))

            # Sample Order 2 (Preparing)
            subtotal2 = sample_prod1.price + sample_prod2.price
            tax2 = round(subtotal2 * 0.05, 2)
            delivery2 = 40.0
            total2 = subtotal2 + tax2 + delivery2

            order2 = Order(
                order_number="LOOZY-20261112-1029",
                user_id=None,
                customer_name="Sneha Rao",
                customer_email="sneha.rao@example.com",
                customer_phone="+91 99001 22334",
                delivery_address="Indiranagar 100ft Road, Bangalore",
                order_notes="Ring bell twice please.",
                payment_method="Pay at Counter",
                payment_status="Pending",
                order_status="Preparing",
                subtotal=subtotal2,
                tax=tax2,
                delivery_fee=delivery2,
                total_amount=total2,
                created_at=datetime.utcnow() - timedelta(hours=1)
            )
            db.session.add(order2)
            db.session.flush()

            db.session.add(OrderItem(order_id=order2.id, product_id=sample_prod1.id, product_name=sample_prod1.name, product_price=sample_prod1.price, quantity=1, item_subtotal=sample_prod1.price))
            db.session.add(OrderItem(order_id=order2.id, product_id=sample_prod2.id, product_name=sample_prod2.name, product_price=sample_prod2.price, quantity=1, item_subtotal=sample_prod2.price))

            db.session.commit()
    print("Seed data completed successfully!")
