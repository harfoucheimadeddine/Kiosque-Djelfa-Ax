import sqlite3
import os
from datetime import datetime

# Database file path (inside "database" folder)
DB_PATH = os.path.join("database", "kiosque.db")


# ------------------- Connection -------------------
def connect():
    return sqlite3.connect(DB_PATH)


def create_tables():
    """Create required tables if they don't exist"""
    conn = connect()
    cur = conn.cursor()

    # Categories table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # Items table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        size TEXT,
        category_id INTEGER,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        barcode TEXT UNIQUE,
        image_path TEXT,
        date_added TEXT,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # Sales table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        sale_date TEXT,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    """)

    conn.commit()
    conn.close()


# ------------------- Categories -------------------
def add_category(name):
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def get_all_categories():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    conn.close()
    return categories


# ------------------- Items -------------------
def add_item(name, size, category_id, price, quantity, barcode=None, image_path=None):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO items (name, size, category_id, price, quantity, barcode, image_path, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, size, category_id, price, quantity, barcode, image_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_item_by_barcode(barcode):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE barcode = ?", (barcode,))
    item = cur.fetchone()
    conn.close()
    return item


def update_item(item_id, price=None, quantity=None, image_path=None):
    conn = connect()
    cur = conn.cursor()

    updates = []
    values = []

    if price is not None:
        updates.append("price = ?")
        values.append(price)
    if quantity is not None:
        updates.append("quantity = ?")
        values.append(quantity)
    if image_path is not None:
        updates.append("image_path = ?")
        values.append(image_path)

    values.append(item_id)

    cur.execute(f"""
        UPDATE items
        SET {", ".join(updates)}
        WHERE id = ?
    """, values)

    conn.commit()
    conn.close()


def get_all_items():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    conn.close()
    return items


def delete_item(item_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


# ------------------- Sales -------------------
def record_sale(item_id, quantity, total_price):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sales (item_id, quantity, total_price, sale_date)
        VALUES (?, ?, ?, ?)
    """, (item_id, quantity, total_price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def get_sales_summary(period="all"):
    conn = connect()
    cur = conn.cursor()

    if period == "today":
        cur.execute("SELECT SUM(total_price) FROM sales WHERE DATE(sale_date) = DATE('now')")
    elif period == "week":
        cur.execute("SELECT SUM(total_price) FROM sales WHERE strftime('%W', sale_date) = strftime('%W', 'now')")
    else:  # all time
        cur.execute("SELECT SUM(total_price) FROM sales")

    result = cur.fetchone()[0]
    conn.close()
    return result if result else 0


# ------------------- Init -------------------
# Ensure database + tables exist when importing
os.makedirs("database", exist_ok=True)
create_tables()
