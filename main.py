import tkinter as tk
from tkinter import ttk, messagebox, StringVar
from PIL import Image, ImageTk
import os
from modules.db_utils import (
    get_store, set_store, start_sale, finish_sale,
    get_all_items, get_all_categories, get_sales,
    get_item_by_barcode, add_sale_item, connect, update_item, delete_item
)
from modules.add_product_ui import add_product_window
from modules.scan_ui import scan_window

def show_product_image(image_path, product_name):
    """Display product image in a popup window"""
    if not image_path or not os.path.exists(image_path):
        messagebox.showinfo("صورة المنتج", "لا توجد صورة لهذا المنتج")
        return
    
    img_window = tk.Toplevel()
    img_window.title(f"صورة المنتج: {product_name}")
    img_window.geometry("400x400")
    
    try:
        # Load and resize image
        pil_image = Image.open(image_path)
        pil_image.thumbnail((350, 350), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(pil_image)
        
        # Display image
        img_label = tk.Label(img_window, image=photo)
        img_label.image = photo  # Keep a reference
        img_label.pack(pady=20)
        
        # Product name label
        name_label = tk.Label(img_window, text=product_name, font=("Arial", 14, "bold"))
        name_label.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("خطأ", f"لا يمكن عرض الصورة: {str(e)}")
        img_window.destroy()
def create_sales_table(parent, sales_data, search_var=None):
    # Search bar
    search_frame = ttk.Frame(parent)
    search_frame.pack(fill=tk.X, padx=10, pady=(10,0))
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(search_frame, text="بحث", style="Accent.TButton", command=lambda: reload_table()).pack(side=tk.LEFT)
    ttk.Separator(parent, orient="horizontal").pack(fill=tk.X, padx=10, pady=5)

    # Table
    table = ttk.Treeview(parent, columns=("datetime", "product_name", "size", "category_name", "price", "quantity", "total"), show="headings", height=18)
    for col, txt in zip(table["columns"], 
        ("التاريخ والوقت", "المنتج", "الحجم", "الفئة", "السعر", "الكمية", "المجموع")):
        table.heading(col, text=txt)
        table.column(col, anchor="center")
    table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def reload_table():
        table.delete(*table.get_children())
        filter_str = search_var.get() if search_var else ""
        for sale in sales_data():
            if filter_str and filter_str not in sale["product_name"]:
                continue
            table.insert("", "end", values=(
                sale["datetime"],
                sale["product_name"],
                sale["size"],
                sale["category_name"],
                sale["price"],
                sale["quantity"],
                sale["total"]
            ))
    reload_table()
    return table

def edit_item_popup(item_id, reload_callback):
    # Get fresh item data from database
    conn = connect()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    
    if not item:
        messagebox.showerror("خطأ", "لم يتم العثور على المنتج")
        return
    
    win = tk.Toplevel()
    win.title("تعديل المنتج")
    win.geometry("450x600")
    
    # Product name
    tk.Label(win, text="اسم المنتج:", font=("Arial", 12)).pack(pady=5)
    name_var = tk.StringVar(value=item["name"])
    name_entry = tk.Entry(win, textvariable=name_var, font=("Arial", 12), width=30)
    name_entry.pack(pady=5)
    
    # Size
    tk.Label(win, text="الحجم:", font=("Arial", 12)).pack(pady=5)
    size_var = tk.StringVar(value=item["size"])
    size_entry = tk.Entry(win, textvariable=size_var, font=("Arial", 12), width=30)
    size_entry.pack(pady=5)
    
    # Price
    tk.Label(win, text="السعر:", font=("Arial", 12)).pack(pady=5)
    price_var = tk.DoubleVar(value=item["price"])
    price_entry = tk.Entry(win, textvariable=price_var, font=("Arial", 12), width=30)
    price_entry.pack(pady=5)
    
    # Quantity
    tk.Label(win, text="الكمية:", font=("Arial", 12)).pack(pady=5)
    qty_var = tk.IntVar(value=item["quantity"])
    qty_entry = tk.Entry(win, textvariable=qty_var, font=("Arial", 12), width=30)
    qty_entry.pack(pady=5)
    
    # Barcode
    tk.Label(win, text="الباركود:", font=("Arial", 12)).pack(pady=5)
    barcode_var = tk.StringVar(value=item["barcode"] or "")
    barcode_entry = tk.Entry(win, textvariable=barcode_var, font=("Arial", 12), width=30)
    barcode_entry.pack(pady=5)
    
    # Image section
    tk.Label(win, text="صورة المنتج:", font=("Arial", 12)).pack(pady=5)
    image_frame = tk.Frame(win)
    image_frame.pack(pady=5)
    
    def view_current_image():
        show_product_image(item["image_path"], item["name"])
    
    def change_image():
        from tkinter import filedialog
        import shutil
        file_path = filedialog.askopenfilename(
            title="اختر صورة جديدة",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            # Copy to assets directory
            filename = os.path.basename(file_path)
            dest_path = os.path.join("assets", filename)
            os.makedirs("assets", exist_ok=True)
            shutil.copy(file_path, dest_path)
            
            # Update database
            conn = connect()
            cur = conn.cursor()
            cur.execute("UPDATE items SET image_path = %s WHERE id = %s", (dest_path, item["id"]))
            conn.commit()
            cur.close()
            conn.close()
            
            item["image_path"] = dest_path
            messagebox.showinfo("تم", "تم تحديث صورة المنتج")
    
    if item["image_path"] and os.path.exists(item["image_path"]):
        tk.Button(image_frame, text="عرض الصورة الحالية", command=view_current_image, 
                 font=("Arial", 11), bg="#17a2b8", fg="white").pack(side=tk.LEFT, padx=5)
    
    tk.Button(image_frame, text="تغيير الصورة", command=change_image, 
             font=("Arial", 11), bg="#ffc107").pack(side=tk.LEFT, padx=5)
    
    def save():
        # Update all fields
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            UPDATE items SET name = %s, size = %s, price = %s, quantity = %s, barcode = %s 
            WHERE id = %s
        """, (name_var.get(), size_var.get(), price_var.get(), qty_var.get(), 
              barcode_var.get(), item["id"]))
        conn.commit()
        cur.close()
        conn.close()
        win.destroy()
        reload_callback()
        messagebox.showinfo("تم", "تم تحديث المنتج بنجاح")
    
    ttk.Button(win, text="حفظ التعديلات", command=save, style="Accent.TButton").pack(pady=10)
    win.mainloop()

def enhanced_inventory_tab(notebook):
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text="المخزون")
    
    # Title
    title_label = ttk.Label(tab, text="إدارة المخزون", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, pady=(0,10))
    
    # Search section
    search_var = StringVar()
    search_frame = ttk.Frame(tab)
    search_frame.grid(row=1, column=0, sticky="ew", pady=5)
    ttk.Label(search_frame, text="البحث:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0,5))
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Arial", 12), width=30)
    search_entry.pack(side=tk.LEFT, padx=(0,5))
    ttk.Button(search_frame, text="بحث", style="Accent.TButton", 
        command=lambda: load_products(search_var.get())).pack(side=tk.LEFT)
    ttk.Button(search_frame, text="إعادة تحميل", style="Accent.TButton", 
        command=lambda: load_products()).pack(side=tk.LEFT, padx=(5,0))
    
    ttk.Separator(tab, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=5)

    columns = ("id", "name", "size", "category", "price", "quantity", "barcode", "image")
    product_table = ttk.Treeview(tab, columns=columns, show="headings", height=20)
    for col, txt in zip(columns, ("ID", "المنتج", "الحجم", "الفئة", "السعر", "الكمية", "الباركود", "صورة")):
        product_table.heading(col, text=txt)
        product_table.column(col, anchor="center")
    
    # Hide ID column
    product_table.column("id", width=0, stretch=False)
    product_table.heading("id", text="")
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=product_table.yview)
    product_table.configure(yscrollcommand=scrollbar.set)
    product_table.grid(row=3, column=0, sticky="nsew", padx=(5,0), pady=5)
    scrollbar.grid(row=3, column=1, sticky="ns", pady=5)
    
    tab.grid_rowconfigure(3, weight=1)
    tab.grid_columnconfigure(0, weight=1)

    def load_products(query=""):
        product_table.delete(*product_table.get_children())
        products = get_all_items()
        categories = {cat['id']: cat['name'] for cat in get_all_categories()}
        for item in products:
            if query and query not in item["name"]:
                continue
            has_image = "✅" if item["image_path"] and os.path.exists(item["image_path"]) else "❌"
            product_table.insert(
                "", "end",
                values=(
                    item["id"], 
                    item["name"], 
                    item["size"], 
                    categories.get(item["category_id"], ""), 
                    item["price"], 
                    item["quantity"], 
                    item["barcode"],
                    has_image
                )
            )
    
    def view_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        product_name = vals[1]
        
        # Get image path from database
        conn = connect()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT image_path FROM items WHERE id = %s", (item_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            show_product_image(result["image_path"], product_name)
    
    def edit_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        edit_item_popup(item_id, load_products)

    def delete_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        item_name = vals[1]
        if messagebox.askyesno("تأكيد الحذف", f"هل تريد حذف المنتج '{item_name}' نهائياً؟\nسيتم حذف المنتج وصورته من النظام."):
            delete_item(item_id)
            load_products()
            messagebox.showinfo("تم", f"تم حذف المنتج '{item_name}' وصورته بنجاح")

    action_frame = ttk.Frame(tab)
    action_frame.grid(row=4, column=0, pady=10)
    ttk.Button(action_frame, text="👁️ عرض الصورة", command=view_selected_item, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
    ttk.Button(action_frame, text="تعديل المنتج", command=edit_selected_item, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
    ttk.Button(action_frame, text="حذف المنتج", command=delete_selected_item, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
    
    def add_new_product():
        add_product_window()
        load_products()  # Refresh the inventory after adding
    
    ttk.Button(tab, text="➕ إضافة منتج جديد", command=add_new_product, style="Accent.TButton", width=20).grid(row=5, column=0, pady=10)
    load_products()
    return tab

def edit_sale_item_popup(item, refresh_callback):
    win = tk.Toplevel()
    win.title("تعديل عنصر البيع")
    win.geometry("400x300")
    tk.Label(win, text="المنتج:", font=("Arial", 12)).pack(pady=10)
    tk.Label(win, text=item["name"], font=("Arial", 13, "bold")).pack()
    price_var = tk.DoubleVar(value=item["price"])
    price_entry = tk.Entry(win, textvariable=price_var, font=("Arial", 12))
    price_entry.pack(pady=5)
    qty_var = tk.IntVar(value=item["quantity"])
    qty_entry = tk.Entry(win, textvariable=qty_var, font=("Arial", 12))
    qty_entry.pack(pady=5)
    def save():
        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE sale_items SET price = %s, quantity = %s WHERE id = %s",
                    (price_var.get(), qty_var.get(), item["id"]))
        conn.commit()
        cur.close()
        conn.close()
        win.destroy()
        refresh_callback()
        messagebox.showinfo("تم", "تم تعديل عنصر البيع بنجاح")
    ttk.Button(win, text="حفظ التعديلات", command=save, style="Accent.TButton").pack(pady=10)
    win.mainloop()

def delete_sale_item_action(item_id, refresh_callback):
    if messagebox.askyesno("تأكيد", "هل تريد حذف هذا العنصر من البيع؟"):
        conn = connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM sale_items WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        conn.close()
        refresh_callback()
        messagebox.showinfo("تم", "تم حذف عنصر البيع بنجاح")

def enhanced_current_sale_tab(notebook, store):
    tab = ttk.Frame(notebook, padding=10)
    notebook.add(tab, text="المبيعات الحالية")

    sale_id = [start_sale(store["id"])]

    # Current sale table
    current_sale_label = ttk.Label(tab, text="سلة البيع الحالية", font=("Arial", 14, "bold"))
    current_sale_label.pack(pady=(0,5))
    current_sale_table = ttk.Treeview(tab, columns=("name", "price", "qty", "total"), show="headings", height=10)
    for col, txt in zip(("name", "price", "qty", "total"), ("المنتج", "السعر", "الكمية", "المجموع")):
        current_sale_table.heading(col, text=txt)
        current_sale_table.column(col, anchor="center")
    current_sale_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    btn_frame = ttk.Frame(tab)
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="📷 مسح منتج", width=18,
        style="Accent.TButton",
        command=lambda: scan_window(current_sale_table, sale_id[0])).pack(side=tk.LEFT, padx=8)
    ttk.Button(btn_frame, text="➕ إضافة منتج يدويًا", width=18,
        command=lambda: add_product_window(), style="Accent.TButton").pack(side=tk.LEFT, padx=8)

    def finish_current_sale():
        total = 0
        for row in current_sale_table.get_children():
            total += float(current_sale_table.item(row)["values"][3])
        finish_sale(sale_id[0], total)
        messagebox.showinfo("تم", f"تم إنهاء البيع بمجموع {total} د.ح")
        current_sale_table.delete(*current_sale_table.get_children())
        sale_id[0] = start_sale(store["id"])
        refresh_latest_sale()
        status_var.set("تم إنهاء البيع.")

    ttk.Button(btn_frame, text="💾 إنهاء البيع", width=18, command=finish_current_sale, style="Accent.TButton").pack(side=tk.LEFT, padx=8)

    # Latest sale section
    ttk.Separator(tab, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)
    latest_label = ttk.Label(tab, text="آخر عملية بيع مكتملة", font=("Arial", 13, "bold"))
    latest_label.pack(pady=(5,2))
    latest_sale_table = ttk.Treeview(tab, columns=("id", "name", "price", "qty", "total"), show="headings", height=5)
    for col, txt in zip(("id", "name", "price", "qty", "total"), ("", "المنتج", "السعر", "الكمية", "المجموع")):
        latest_sale_table.heading(col, text=txt)
        latest_sale_table.column(col, anchor="center")
    latest_sale_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def refresh_latest_sale():
        latest_sale_table.delete(*latest_sale_table.get_children())
        conn = connect()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT si.id, i.name, si.price, si.quantity, (si.price * si.quantity) AS total
            FROM sale_items si
            JOIN items i ON si.item_id = i.id
            WHERE si.sale_id = (
                SELECT id FROM sales WHERE total_price > 0 ORDER BY date DESC LIMIT 1
            )
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for item in rows:
            latest_sale_table.insert("", "end", values=(item['id'], item['name'], item['price'], item['quantity'], item['total']))
    refresh_latest_sale()

    def edit_selected_sale_item():
        selected = latest_sale_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر عنصرًا أولاً")
            return
        vals = latest_sale_table.item(selected)["values"]
        item_id = vals[0]
        conn = connect()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT si.*, i.name FROM sale_items si JOIN items i ON si.item_id = i.id WHERE si.id = %s", (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        if item:
            edit_sale_item_popup(item, refresh_latest_sale)

    def delete_selected_sale_item():
        selected = latest_sale_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر عنصرًا أولاً")
            return
        vals = latest_sale_table.item(selected)["values"]
        item_id = vals[0]
        delete_sale_item_action(item_id, refresh_latest_sale)

    action_frame2 = ttk.Frame(tab)
    action_frame2.pack(pady=5)
    ttk.Button(action_frame2, text="تعديل عنصر البيع", command=edit_selected_sale_item, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
    ttk.Button(action_frame2, text="حذف عنصر البيع", command=delete_selected_sale_item, style="Accent.TButton").pack(side=tk.LEFT, padx=5)

    return tab

def main():
    root = tk.Tk()
    root.title("📊 نظام المبيعات")
    root.geometry("1350x950")
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Accent.TButton", font=("Arial", 12), foreground="#fff", background="#0078D7")
    style.configure("TLabel", font=("Arial", 12))
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

    global status_var
    status_var = StringVar()
    status_bar = ttk.Label(root, textvariable=status_var, relief="sunken", anchor="w", font=("Arial", 11), background="#eee")
    status_bar.pack(side="bottom", fill="x")
    status_var.set("جاهز")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=7, pady=7)

    # --- Inventory Tab ---
    enhanced_inventory_tab(notebook)

    # --- Store Logic ---
    store = get_store()
    if not store:
        def create_store():
            win = tk.Toplevel()
            win.title("إعداد المتجر")
            win.geometry("400x300")
            ttk.Label(win, text="اسم المتجر:", font=("Arial", 12)).pack(pady=10)
            name_entry = ttk.Entry(win, font=("Arial", 12))
            name_entry.pack(pady=5)
            ttk.Label(win, text="الموقع:", font=("Arial", 12)).pack(pady=5)
            loc_entry = ttk.Entry(win, font=("Arial", 12))
            loc_entry.pack(pady=5)
            ttk.Label(win, text="رقم التواصل:", font=("Arial", 12)).pack(pady=5)
            contact_entry = ttk.Entry(win, font=("Arial", 12))
            contact_entry.pack(pady=5)
            def save_store():
                set_store(
                    name_entry.get(),
                    loc_entry.get(),
                    contact_entry.get()
                )
                messagebox.showinfo("نجاح", "تم حفظ معلومات المتجر")
                win.destroy()
            ttk.Button(win, text="حفظ", command=save_store, style="Accent.TButton").pack(pady=15)
            win.mainloop()
        create_store()
        store = get_store()

    # --- Current Sale Tab ---
    enhanced_current_sale_tab(notebook, store)

    # --- Today's Sales Tab ---
    today_tab = ttk.Frame(notebook, padding=10)
    notebook.add(today_tab, text="مبيعات اليوم")
    today_sales_var = StringVar()
    create_sales_table(today_tab, lambda: get_sales('today'), today_sales_var)

    # --- This Week's Sales Tab ---
    week_tab = ttk.Frame(notebook, padding=10)
    notebook.add(week_tab, text="مبيعات الأسبوع")
    week_sales_var = StringVar()
    create_sales_table(week_tab, lambda: get_sales('week'), week_sales_var)

    # --- Total Sales Tab ---
    all_tab = ttk.Frame(notebook, padding=10)
    notebook.add(all_tab, text="إجمالي المبيعات")
    all_sales_var = StringVar()
    create_sales_table(all_tab, lambda: get_sales('all'), all_sales_var)

    root.mainloop()

if __name__ == "__main__":
    main()