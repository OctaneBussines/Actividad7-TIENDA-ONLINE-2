import sqlite3
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0
            )
            '''
        )
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                cost REAL NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                description TEXT
            )
            '''
        )
        db.commit()

        try:
            cursor.execute('ALTER TABLE products ADD COLUMN cost REAL NOT NULL DEFAULT 0.0')
            db.commit()
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute('ALTER TABLE products ADD COLUMN price REAL NOT NULL DEFAULT 0.0')
            db.commit()
        except sqlite3.OperationalError:
            pass

        cursor.execute('SELECT COUNT(1) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                ('admin', 'admin123', 1),
            )
            cursor.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                ('cliente', 'cliente123', 0),
            )
            db.commit()

        cursor.execute('SELECT COUNT(1) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_base = [
                ('Auriculares inalámbricos', 'Audio', 38.25, 18, 'Auriculares Bluetooth con cancelación de ruido.'),
                ('Smartwatch', 'Wearables', 100.00, 12, 'Smartwatch con monitoreo de salud y notificaciones.'),
                ('Mouse ergonómico', 'Computación', 29.79, 22, 'Mouse con diseño cómodo y programación de botones.'),
            ]
            sample_products = [
                (name, category, cost, round(cost * 1.2, 2), stock, description)
                for name, category, cost, stock, description in sample_base
            ]
            cursor.executemany(
                'INSERT INTO products (name, category, cost, price, stock, description) VALUES (?, ?, ?, ?, ?, ?)',
                sample_products,
            )
            db.commit()

        cursor.execute('UPDATE products SET cost = ROUND(price / 1.2, 2) WHERE cost = 0 AND price IS NOT NULL')
        db.commit()

        cursor.execute('UPDATE products SET price = ROUND(cost * 1.2, 2) WHERE price = 0 AND cost > 0')
        db.commit()

        cursor.execute("DELETE FROM products WHERE category IN ('Moda', 'Accesorios')")
        db.commit()
