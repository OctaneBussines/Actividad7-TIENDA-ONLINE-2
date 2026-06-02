from dataclasses import asdict, dataclass


@dataclass
class Product:
    id: int
    name: str
    category: str
    cost: float
    price: float
    stock: int
    description: str


@dataclass
class User:
    id: int
    username: str
    password: str
    is_admin: bool


def row_to_product(row):
    if not row:
        return None
    cost = row['cost']
    if cost == 0 and row['price'] is not None:
        cost = round(row['price'] / 1.2, 2)
    sale_price = round(cost * 1.2, 2)
    return Product(
        id=row['id'],
        name=row['name'],
        category=row['category'],
        cost=cost,
        price=sale_price,
        stock=row['stock'],
        description=row['description'] or '',
    )


def row_to_user(row):
    if not row:
        return None
    return User(
        id=row['id'],
        username=row['username'],
        password=row['password'],
        is_admin=bool(row['is_admin']),
    )


def get_user_by_username(db, username):
    cursor = db.execute('SELECT * FROM users WHERE username = ?', (username,))
    return row_to_user(cursor.fetchone())


def get_products(db, category=None):
    excluded = ('Moda', 'Accesorios')
    if category:
        cursor = db.execute(
            'SELECT * FROM products WHERE category = ? AND category NOT IN (?, ?) ORDER BY name',
            (category, *excluded),
        )
    else:
        cursor = db.execute(
            'SELECT * FROM products WHERE category NOT IN (?, ?) ORDER BY category, name',
            excluded,
        )
    return [asdict(row_to_product(row)) for row in cursor.fetchall()]


def get_product_by_id(db, product_id):
    cursor = db.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = cursor.fetchone()
    return asdict(row_to_product(row)) if row else None


def get_categories(db):
    excluded = ('Moda', 'Accesorios')
    cursor = db.execute(
        'SELECT DISTINCT category FROM products WHERE category NOT IN (?, ?) ORDER BY category',
        excluded,
    )
    return [row['category'] for row in cursor.fetchall()]


def create_product(db, name, category, cost, stock, description):
    price = round(float(cost) * 1.2, 2)
    db.execute(
        'INSERT INTO products (name, category, cost, price, stock, description) VALUES (?, ?, ?, ?, ?, ?)',
        (name, category, float(cost), price, int(stock), description),
    )
    db.commit()


def update_product(db, product_id, name, category, cost, stock, description):
    price = round(float(cost) * 1.2, 2)
    db.execute(
        '''
        UPDATE products
        SET name = ?, category = ?, cost = ?, price = ?, stock = ?, description = ?
        WHERE id = ?
        ''',
        (name, category, float(cost), price, int(stock), description, product_id),
    )
    db.commit()


def delete_product(db, product_id):
    db.execute('DELETE FROM products WHERE id = ?', (product_id,))
    db.commit()


def decrease_stock(db, product_id, quantity):
    db.execute(
        'UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?',
        (quantity, product_id, quantity),
    )
    db.commit()
    cursor = db.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
    result = cursor.fetchone()
    return result['stock'] if result else -1
