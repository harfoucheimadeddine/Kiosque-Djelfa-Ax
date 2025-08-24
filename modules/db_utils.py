import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database connection
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="kiosque_db"
    )

# ------------------- Categories -------------------
def add_category(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Category '{name}' added!")

def get_all_categories():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return categories

# ------------------- Items -------------------
def add_item(name, size, category_id, price, quantity, barcode, image_path=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (name, size, category_id, price, quantity, barcode, image_path, date_added)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, size, category_id, price, quantity, barcode, image_path, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"🆕 Item '{name}' added with image {image_path}")

def get_item_by_barcode(barcode):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items WHERE barcode = %s", (barcode,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()
    return item

def update_item(item_id, price=None, quantity=None, image_path=None):
    conn = create_connection()
    cursor = conn.cursor()

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

    values.append(item_id)

    cursor.execute(f"""
        UPDATE items
        SET {", ".join(updates)}
        WHERE id = %s
    """, values)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"🔄 Item {item_id} updated!")

def get_all_items():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def delete_item(item_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"❌ Item {item_id} deleted!")

# ------------------- Sales -------------------
def record_sale(item_id, quantity, total_price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sales (item_id, quantity, total_price, sale_date)
        VALUES (%s, %s, %s, %s)
    """, (item_id, quantity, total_price, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"💰 Sale recorded for item {item_id} ({quantity} pcs)")

def get_sales_summary(period="all"):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    if period == "today":
        cursor.execute("SELECT SUM(total_price) AS total FROM sales WHERE DATE(sale_date) = CURDATE()")
    elif period == "week":
        cursor.execute("SELECT SUM(total_price) AS total FROM sales WHERE YEARWEEK(sale_date, 1) = YEARWEEK(CURDATE(), 1)")
    else:  # all time
        cursor.execute("SELECT SUM(total_price) AS total FROM sales")

    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
