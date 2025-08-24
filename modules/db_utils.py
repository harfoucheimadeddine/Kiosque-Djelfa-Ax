import mysql.connector
from datetime import datetime

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'kiosque_db'
}

def connect():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**MYSQL_CONFIG)

# ----------- Categories -----------
def add_category(name):
    """Adds a new category."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_categories():
    """Returns all categories as a list of dicts."""
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    cur.close()
    conn.close()
    return categories

# ----------- Store -----------
def get_store():
    """Returns store information (first row only)."""
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM store LIMIT 1")
    store = cur.fetchone()
    cur.close()
    conn.close()
    return store

def set_store(name, location, contact):
    """Sets store information."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO store (name, location, contact) VALUES (%s, %s, %s)", (name, location, contact))
    conn.commit()
    cur.close()
    conn.close()

# ----------- Items -----------
def add_item(name, size, category_id, price, quantity, barcode=None, image_path=None):
    """Adds a new item/product."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO items (name, size, category_id, price, quantity, barcode, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (name, size, category_id, price, quantity, barcode, image_path))
    conn.commit()
    cur.close()
    conn.close()

def get_item_by_barcode(barcode):
    """Finds item by barcode."""
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM items WHERE barcode = %s", (barcode,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return item

def update_item(item_id, price=None, quantity=None, image_path=None):
    """Updates item fields by id."""
    conn = connect()
    cur = conn.cursor()
    updates = []
    values = []

    if price is not None:
        updates.append("price = %s")
        values.append(price)
    if quantity is not None:
        updates.append("quantity = %s")
        values.append(quantity)
    if image_path is not None:
        updates.append("image_path = %s")
        values.append(image_path)

    if not updates:
        cur.close()
        conn.close()
        return

    values.append(item_id)
    cur.execute(f"UPDATE items SET {', '.join(updates)} WHERE id = %s", values)
    conn.commit()
    cur.close()
    conn.close()

def get_all_items():
    """Returns all items/products as a list of dicts."""
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    conn.close()
    return items

def delete_item(item_id):
    """Deletes an item by id."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cur.close()
    conn.close()

# ----------- Sales & Sale Items -----------
def start_sale(store_id):
    """Creates a new sale and returns its id."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO sales (store_id, total_price) VALUES (%s, %s)", (store_id, 0))
    sale_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return sale_id

def add_sale_item(sale_id, item_id, quantity, price):
    """Adds an item to a sale."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sale_items (sale_id, item_id, quantity, price)
        VALUES (%s, %s, %s, %s)
    """, (sale_id, item_id, quantity, price))
    conn.commit()
    cur.close()
    conn.close()

def finish_sale(sale_id, total_price):
    """Finishes the sale and updates the total price."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("UPDATE sales SET total_price = %s WHERE id = %s", (total_price, sale_id))
    conn.commit()
    cur.close()
    conn.close()

def get_sales_summary(period="all"):
    """Returns total sales amount for the selected period."""
    conn = connect()
    cur = conn.cursor()
    if period == "today":
        cur.execute("SELECT SUM(total_price) FROM sales WHERE DATE(date) = CURDATE()")
    elif period == "week":
        cur.execute("SELECT SUM(total_price) FROM sales WHERE YEARWEEK(date, 1) = YEARWEEK(CURDATE(), 1)")
    else:  # all time
        cur.execute("SELECT SUM(total_price) FROM sales")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result if result else 0

def get_last_sale_items():
    """Returns the last sale item with product info."""
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT si.*, i.name, i.image_path FROM sale_items si
        JOIN items i ON si.item_id = i.id
        ORDER BY si.id DESC
        LIMIT 1
    """)
    item = cur.fetchone()
    cur.close()
    conn.close()
    return item

def get_sales(period="all"):
    """
    Returns full sales item list for period.
    Each row: {
        'datetime', 'product_name', 'size', 'category_name', 'price', 'quantity', 'total'
    }
    """
    conn = connect()
    cur = conn.cursor(dictionary=True)
    where_clause = ""
    params = []
    if period == "today":
        where_clause = "WHERE DATE(s.date) = CURDATE()"
    elif period == "week":
        where_clause = "WHERE YEARWEEK(s.date, 1) = YEARWEEK(CURDATE(), 1)"
    # else: all, no where clause

    query = f"""
        SELECT
            s.date AS datetime,
            i.name AS product_name,
            i.size,
            c.name AS category_name,
            si.price,
            si.quantity,
            (si.price * si.quantity) AS total
        FROM sale_items si
        JOIN sales s ON si.sale_id = s.id
        JOIN items i ON si.item_id = i.id
        JOIN categories c ON i.category_id = c.id
        {where_clause}
        ORDER BY s.date DESC
    """
    cur.execute(query, params)
    sales = cur.fetchall()
    cur.close()
    conn.close()
    return sales