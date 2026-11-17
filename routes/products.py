from flask import Blueprint, render_template, request, jsonify, abort
from models import db, Category, Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/menu')
def menu():
    category_slug = request.args.get('category', 'all').strip()
    search_query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort', 'default').strip()
    
    categories = Category.query.order_by(Category.display_order).all()
    
    query = Product.query.filter_by(is_available=True)
    
    selected_category = None
    if category_slug and category_slug != 'all':
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)
            
    if search_query:
        search_filter = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(search_filter)) | 
            (Product.description.ilike(search_filter))
        )
        
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort_by == 'bestseller':
        query = query.order_by(Product.is_bestseller.desc(), Product.name.asc())
    else:
        query = query.order_by(Product.category_id.asc(), Product.is_featured.desc(), Product.name.asc())
        
    products = query.all()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify({
            'success': True,
            'count': len(products),
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'slug': p.slug,
                    'price': p.price,
                    'description': p.description,
                    'image_url': p.image_url,
                    'category_id': p.category_id,
                    'category_name': p.category.name,
                    'category_slug': p.category.slug,
                    'is_featured': p.is_featured,
                    'is_bestseller': p.is_bestseller,
                    'dietary_type': p.dietary_type,
                    'prep_time': p.prep_time,
                    'rating': p.rating
                } for p in products
            ]
        })
        
    return render_template(
        'menu.html',
        categories=categories,
        products=products,
        current_category=category_slug,
        selected_category=selected_category,
        search_query=search_query,
        sort_by=sort_by
    )

@products_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_available == True
    ).limit(4).all()
    
    return render_template('product_detail.html', product=product, related_products=related_products)
