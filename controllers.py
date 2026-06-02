import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from models import (
    get_user_by_username,
    get_products,
    get_categories,
    get_product_by_id,
    create_product,
    update_product,
    delete_product,
    decrease_stock,
)

class AuthController:
    @staticmethod
    def authenticate(db, username, password):
        user = get_user_by_username(db, username)
        if user and user.password == password:
            return {'id': user.id, 'username': user.username, 'is_admin': user.is_admin}
        return None


class ProductController:
    @staticmethod
    def list_products(db, category=None):
        return get_products(db, category)

    @staticmethod
    def list_categories(db):
        return get_categories(db)

    @staticmethod
    def add_product(db, form):
        create_product(
            db,
            form.get('name', '').strip(),
            form.get('category', '').strip(),
            form.get('cost', 0),
            form.get('stock', 0),
            form.get('description', '').strip(),
        )

    @staticmethod
    def get_product(db, product_id):
        return get_product_by_id(db, product_id)

    @staticmethod
    def update_product(db, product_id, form):
        update_product(
            db,
            product_id,
            form.get('name', '').strip(),
            form.get('category', '').strip(),
            form.get('cost', 0),
            form.get('stock', 0),
            form.get('description', '').strip(),
        )

    @staticmethod
    def remove_product(db, product_id):
        delete_product(db, product_id)


class CartController:
    @staticmethod
    def add_item(session, product_id):
        cart = session.setdefault('cart', {})
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        session['cart'] = cart
        session['payment_simulated'] = False

    @staticmethod
    def remove_item(session, product_id):
        cart = session.get('cart', {})
        cart.pop(str(product_id), None)
        session['cart'] = cart
        session['payment_simulated'] = False

    @staticmethod
    def clear_cart(session):
        session['cart'] = {}
        session['payment_simulated'] = False

    @staticmethod
    def get_cart_summary(db, cart):
        items = []
        total = 0.0
        total_cost = 0.0
        total_profit = 0.0
        for product_id, quantity in cart.items():
            product = get_product_by_id(db, int(product_id))
            if not product:
                continue
            product_cost = product['cost']
            product_price = product['price']
            product_total = product_price * quantity
            item_total_cost = product_cost * quantity
            item_total_profit = (product_price - product_cost) * quantity
            profit_pct = round(((product_price - product_cost) / product_cost * 100), 2) if product_cost else 0.0
            items.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'cost': product_cost,
                'price': product_price,
                'quantity': quantity,
                'total': round(product_total, 2),
                'total_cost': round(item_total_cost, 2),
                'total_profit': round(item_total_profit, 2),
                'profit_pct': profit_pct,
            })
            total += product_total
            total_cost += item_total_cost
            total_profit += item_total_profit
        return items, round(total, 2), round(total_cost, 2), round(total_profit, 2)

    @staticmethod
    def process_checkout(db, cart):
        for product_id, quantity in cart.items():
            decrease_stock(db, int(product_id), quantity)


class InvoiceController:
    @staticmethod
    def generate_invoice(cart_items, cart_total, cart_cost_total, cart_profit_total, username):
        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=28,
            rightMargin=28,
            topMargin=28,
            bottomMargin=28,
        )
        story = []

        title_style = ParagraphStyle('Title', fontSize=18, leading=24, spaceAfter=12)
        normal_style = ParagraphStyle('Normal', fontSize=11, leading=14)
        heading_style = ParagraphStyle('Heading', fontSize=13, leading=16, spaceAfter=8, textColor=colors.HexColor('#003366'))

        story.append(Paragraph('Factura de Compra', title_style))
        story.append(Paragraph(f'Cliente: {username}', normal_style))
        story.append(Spacer(1, 8))

        table_data = [['Producto', 'Categoría', 'Cantidad', 'Costo', 'Precio', 'Ganancia', 'Subtotal']]
        for item in cart_items:
            table_data.append([
                item['name'],
                item['category'],
                str(item['quantity']),
                f'${item['cost']:.2f}',
                f'${item['price']:.2f}',
                f'${item['total_profit']:.2f} ({item['profit_pct']:.0f}%)',
                f'${item['total']:.2f}',
            ])

        table_data.append(['', '', '', '', '', 'Subtotal', f'${cart_total:.2f}'])
        table_data.append(['', '', '', '', 'Costo total', f'${cart_cost_total:.2f}'])
        table_data.append(['', '', '', '', 'Ganancia total', f'${cart_profit_total:.2f}'])
        table = Table(table_data, colWidths=[50*mm, 30*mm, 15*mm, 20*mm, 20*mm, 25*mm, 20*mm], hAlign='LEFT')
        table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (-1, -2), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f1fb')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ])
        )
        story.append(table)
        story.append(Spacer(1, 12))
        story.append(Paragraph('Gracias por su compra. Estamos comprometidos con la calidad y la experiencia de usuario.', normal_style))

        document.build(story)
        buffer.seek(0)
        return buffer
