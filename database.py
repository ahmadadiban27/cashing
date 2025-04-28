import sqlite3
from contextlib import contextmanager

DATABASE_PATH = 'restaurant.db'

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL,
            status TEXT DEFAULT 'empty',
            current_order_id INTEGER
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_order INTEGER
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            production_location TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            start_time TEXT DEFAULT CURRENT_TIMESTAMP,
            end_time TEXT,
            status TEXT DEFAULT 'open',
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (table_id) REFERENCES tables(id)
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_order REAL NOT NULL,
            production_location TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password) 
        VALUES ('admin', 'admin123')
        ''')
        

        # ایجاد جدول مشتریان و اشتراک‌ها
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            credit_limit REAL DEFAULT 0,
            balance REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            remaining_amount REAL NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        ''')
        
        # اضافه کردن فیلد customer_id به سفارشات
        try:
            cursor.execute('ALTER TABLE orders ADD COLUMN customer_id INTEGER')
        except sqlite3.OperationalError:
            pass  # اگر فیلد قبلاً وجود داشته باشد
        
        conn.commit()