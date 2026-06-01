from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from database import init_db, get_db, close_db
from controllers import AuthController, ProductController, CartController, InvoiceController


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_mapping(
        SECRET_KEY='t1enda_0nl1n3_segura_2026',
        DATABASE='tienda.db',
    )

    init_db(app)
    app.teardown_appcontext(close_db)

    @app.route('/')
    def home():
        if 'user' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            db = get_db()
            user = AuthController.authenticate(db, username, password)

            if user:
                session['user'] = user['username']
                session['is_admin'] = user['is_admin']
                session.setdefault('cart', {})
                flash('Bienvenido ' + user['username'], 'success')
                return redirect(url_for('dashboard'))

            flash('Usuario o contraseña incorrectos', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada con éxito', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    def dashboard():
        if 'user' not in session:
            return redirect(url_for('login'))

        db = get_db()
        category = request.args.get('category')
        products = ProductController.list_products(db, category)
        categories = ProductController.list_categories(db)
        cart_items, cart_total, _, _ = CartController.get_cart_summary(db, session.get('cart', {}))

        return render_template(
            'dashboard.html',
            user=session['user'],
            products=products,
            categories=categories,
            selected_category=category,
            cart_items=cart_items,
            cart_total=cart_total,
        )

    @app.route('/product/new', methods=['GET', 'POST'])
    def create_product():
        if 'user' not in session or not session.get('is_admin'):
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            form = request.form
            db = get_db()
            ProductController.add_product(db, form)
            flash('Producto agregado con éxito', 'success')
            return redirect(url_for('dashboard'))

        return render_template('product_form.html', product=None, action='Crear')

    @app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
    def edit_product(product_id):
        if 'user' not in session or not session.get('is_admin'):
            return redirect(url_for('dashboard'))

        db = get_db()
        product = ProductController.get_product(db, product_id)
        if not product:
            flash('Producto no encontrado', 'warning')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            ProductController.update_product(db, product_id, request.form)
            flash('Producto actualizado con éxito', 'success')
            return redirect(url_for('dashboard'))

        return render_template('product_form.html', product=product, action='Editar')

    @app.route('/product/delete/<int:product_id>', methods=['POST'])
    def delete_product(product_id):
        if 'user' not in session or not session.get('is_admin'):
            return redirect(url_for('dashboard'))

        db = get_db()
        ProductController.remove_product(db, product_id)
        flash('Producto eliminado correctamente', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/cart/add/<int:product_id>')
    def add_to_cart(product_id):
        if 'user' not in session:
            return redirect(url_for('login'))

        category = request.args.get('category')
        db = get_db()
        CartController.add_item(session, product_id)
        flash('Producto añadido al carrito', 'success')
        if category:
            return redirect(url_for('dashboard', category=category))
        return redirect(url_for('dashboard'))

    @app.route('/cart/remove/<int:product_id>', methods=['POST'])
    def remove_from_cart(product_id):
        if 'user' not in session:
            return redirect(url_for('login'))

        CartController.remove_item(session, product_id)
        flash('Producto eliminado del carrito', 'info')
        return redirect(url_for('cart'))

    @app.route('/cart/simulate', methods=['POST'])
    def simulate_payment():
        if 'user' not in session:
            return redirect(url_for('login'))

        if not session.get('cart'):
            flash('Agrega productos al carrito antes de simular el pago.', 'warning')
            return redirect(url_for('cart'))

        session['payment_simulated'] = True
        flash('Pago QR simulado correctamente. Ahora puedes descargar la factura.', 'success')
        return redirect(url_for('cart'))

    @app.route('/cart')
    def cart():
        if 'user' not in session:
            return redirect(url_for('login'))

        db = get_db()
        cart_items, cart_total, cart_cost_total, cart_profit_total = CartController.get_cart_summary(db, session.get('cart', {}))
        payment_simulated = session.get('payment_simulated', False)
        return render_template(
            'cart.html',
            cart_items=cart_items,
            cart_total=cart_total,
            cart_cost_total=cart_cost_total,
            cart_profit_total=cart_profit_total,
            payment_simulated=payment_simulated,
        )

    @app.route('/cart/checkout')
    def checkout():
        if 'user' not in session:
            return redirect(url_for('login'))

        if not session.get('payment_simulated'):
            flash('Primero simula el pago QR antes de descargar la factura.', 'warning')
            return redirect(url_for('cart'))

        db = get_db()
        cart_items, cart_total, cart_cost_total, cart_profit_total = CartController.get_cart_summary(db, session.get('cart', {}))
        if not cart_items:
            flash('El carrito está vacío', 'warning')
            return redirect(url_for('cart'))

        user = session['user']
        CartController.process_checkout(db, session.get('cart', {}))
        pdf_buffer = InvoiceController.generate_invoice(cart_items, cart_total, cart_cost_total, cart_profit_total, user)
        CartController.clear_cart(session)
        return send_file(
            pdf_buffer,
            download_name=f'factura_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            as_attachment=True,
            mimetype='application/pdf',
        )

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
