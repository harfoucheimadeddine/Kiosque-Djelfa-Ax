import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import StringVar
import os
import shutil
from PIL import Image, ImageTk
from modules.db_utils import *
from modules.add_product_ui import add_product_window
from modules.scan_ui import scan_window

def setup_modern_theme():
    """Configure modern theme with clean colors and typography"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Modern color palette
    colors = {
        'primary': '#2563eb',      # Modern blue
        'primary_hover': '#1d4ed8',
        'secondary': '#64748b',    # Slate gray
        'success': '#10b981',      # Emerald green
        'warning': '#f59e0b',      # Amber
        'danger': '#ef4444',       # Red
        'surface': '#ffffff',      # White
        'background': '#f8fafc',   # Light gray
        'text': '#1e293b',         # Dark slate
        'text_muted': '#64748b',   # Muted text
        'border': '#e2e8f0',       # Light border
        'accent': '#8b5cf6'        # Purple accent
    }
    
    # Configure button styles
    style.configure("Primary.TButton",
                   font=("Segoe UI", 11, "bold"),
                   foreground="white",
                   background=colors['primary'],
                   borderwidth=0,
                   focuscolor="none",
                   padding=(20, 12))
    
    style.map("Primary.TButton",
             background=[('active', colors['primary_hover']),
                        ('pressed', colors['primary_hover'])])
    
    style.configure("Success.TButton",
                   font=("Segoe UI", 10, "bold"),
                   foreground="white",
                   background=colors['success'],
                   borderwidth=0,
                   focuscolor="none",
                   padding=(16, 10))
    
    style.configure("Danger.TButton",
                   font=("Segoe UI", 10, "bold"),
                   foreground="white",
                   background=colors['danger'],
                   borderwidth=0,
                   focuscolor="none",
                   padding=(16, 10))
    
    style.configure("Secondary.TButton",
                   font=("Segoe UI", 10),
                   foreground=colors['text'],
                   background=colors['surface'],
                   borderwidth=1,
                   focuscolor="none",
                   padding=(16, 10))
    
    # Configure labels
    style.configure("Heading.TLabel",
                   font=("Segoe UI", 18, "bold"),
                   foreground=colors['text'],
                   background=colors['background'])
    
    style.configure("Subheading.TLabel",
                   font=("Segoe UI", 14, "bold"),
                   foreground=colors['text'],
                   background=colors['background'])
    
    style.configure("Body.TLabel",
                   font=("Segoe UI", 11),
                   foreground=colors['text'],
                   background=colors['background'])
    
    style.configure("Muted.TLabel",
                   font=("Segoe UI", 10),
                   foreground=colors['text_muted'],
                   background=colors['background'])
    
    # Configure treeview
    style.configure("Modern.Treeview",
                   font=("Segoe UI", 10),
                   background=colors['surface'],
                   foreground=colors['text'],
                   fieldbackground=colors['surface'],
                   borderwidth=0,
                   rowheight=35)
    
    style.configure("Modern.Treeview.Heading",
                   font=("Segoe UI", 11, "bold"),
                   background=colors['background'],
                   foreground=colors['text'],
                   borderwidth=0,
                   padding=(10, 15))
    
    # Configure notebook
    style.configure("Modern.TNotebook",
                   background=colors['background'],
                   borderwidth=0,
                   tabmargins=[0, 0, 0, 0])
    
    style.configure("Modern.TNotebook.Tab",
                   font=("Segoe UI", 11, "bold"),
                   padding=(20, 15),
                   background=colors['surface'],
                   foreground=colors['text_muted'],
                   borderwidth=0)
    
    style.map("Modern.TNotebook.Tab",
             background=[('selected', colors['primary']),
                        ('active', colors['background'])],
             foreground=[('selected', 'white'),
                        ('active', colors['text'])])
    
    # Configure frames
    style.configure("Card.TFrame",
                   background=colors['surface'],
                   borderwidth=1,
                   relief="solid")
    
    style.configure("Modern.TFrame",
                   background=colors['background'],
                   borderwidth=0)
    
    return colors

def create_modal_window(parent, title, width=400, height=300):
    """Create a modern modal window that stays on top of parent"""
    window = tk.Toplevel(parent)
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.configure(bg='#f8fafc')
    
    # Make it modal
    window.transient(parent)
    window.grab_set()
    
    # Center on parent
    parent.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")
    
    # Focus and bring to front
    window.focus_force()
    window.lift()
    window.attributes('-topmost', True)
    window.after(100, lambda: window.attributes('-topmost', False))
    
    return window

def create_modern_card(parent, title=None, padding=20):
    """Create a modern card-style frame"""
    card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
    
    if title:
        title_label = ttk.Label(card, text=title, style="Subheading.TLabel")
        title_label.pack(anchor="w", pady=(0, 15))
    
    return card

def create_sales_table(parent, get_data_func, total_var):
    """Create a modern sales table with summary"""
    # Header card
    header_card = create_modern_card(parent, padding=15)
    header_card.pack(fill="x", pady=(0, 20))
    
    # Summary section
    summary_frame = ttk.Frame(header_card, style="Modern.TFrame")
    summary_frame.pack(fill="x")
    
    ttk.Label(summary_frame, text="📊 ملخص المبيعات", style="Subheading.TLabel").pack(side="left")
    
    total_label = ttk.Label(summary_frame, textvariable=total_var, style="Heading.TLabel")
    total_label.pack(side="right")
    
    # Table card
    table_card = create_modern_card(parent, padding=15)
    table_card.pack(fill="both", expand=True)
    
    # Table
    columns = ("datetime", "product", "size", "category", "price", "qty", "total")
    headers = ("التاريخ والوقت", "المنتج", "الحجم", "الفئة", "السعر", "الكمية", "المجموع")
    
    table = ttk.Treeview(table_card, columns=columns, show="headings", style="Modern.Treeview", height=15)
    
    for col, header in zip(columns, headers):
        table.heading(col, text=header)
        table.column(col, anchor="center", width=120)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    
    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def refresh_data():
        table.delete(*table.get_children())
        data = get_data_func()
        total = 0
        for row in data:
            table.insert("", "end", values=(
                row['datetime'].strftime("%Y-%m-%d %H:%M"),
                row['product_name'],
                row['size'] or '-',
                row['category_name'],
                f"{row['price']:.2f} د.ح",
                row['quantity'],
                f"{row['total']:.2f} د.ح"
            ))
            total += row['total']
        total_var.set(f"{total:.2f} د.ح")
    
    # Refresh button
    refresh_btn = ttk.Button(header_card, text="🔄 تحديث", command=refresh_data, style="Secondary.TButton")
    refresh_btn.pack(side="right", padx=(10, 0))
    
    refresh_data()
    return table

def enhanced_inventory_tab(notebook, main_window):
    """Create modern inventory management tab"""
    tab = ttk.Frame(notebook, style="Modern.TFrame", padding=20)
    notebook.add(tab, text="📦 إدارة المخزون")
    
    # Header
    header_card = create_modern_card(tab, "إدارة المخزون", 20)
    header_card.pack(fill="x", pady=(0, 20))
    
    # Search section
    search_frame = ttk.Frame(header_card, style="Modern.TFrame")
    search_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Label(search_frame, text="🔍 البحث:", style="Body.TLabel").pack(side="left", padx=(0, 10))
    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 11), width=30)
    search_entry.pack(side="left", padx=(0, 10))
    
    # Add product button
    add_btn = ttk.Button(search_frame, text="➕ إضافة منتج جديد", 
                        style="Primary.TButton")
    add_btn.pack(side="right")
    
    # Table card
    table_card = create_modern_card(tab, padding=15)
    table_card.pack(fill="both", expand=True, pady=(0, 20))
    
    # Product table
    columns = ("id", "name", "size", "category", "price", "quantity", "barcode", "image")
    headers = ("", "اسم المنتج", "الحجم", "الفئة", "السعر", "الكمية", "الباركود", "صورة")
    
    product_table = ttk.Treeview(table_card, columns=columns, show="headings", style="Modern.Treeview", height=12)
    
    for col, header in zip(columns, headers):
        product_table.heading(col, text=header)
        if col == "id":
            product_table.column(col, width=0, stretch=False)
        elif col == "image":
            product_table.column(col, width=60, anchor="center")
        else:
            product_table.column(col, anchor="center", width=120)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=product_table.yview)
    product_table.configure(yscrollcommand=scrollbar.set)
    
    product_table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def load_products():
        product_table.delete(*product_table.get_children())
        items = get_all_items()
        categories = {cat['id']: cat['name'] for cat in get_all_categories()}
        
        for item in items:
            category_name = categories.get(item['category_id'], 'غير محدد')
            image_status = "✅" if item.get('image_path') else "❌"
            
            product_table.insert("", "end", values=(
                item['id'],
                item['name'],
                item['size'] or '-',
                category_name,
                f"{item['price']:.2f} د.ح",
                item['quantity'],
                item['barcode'] or '-',
                image_status
            ))
    
    def view_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        item_name = vals[1]
        
        conn = connect()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        
        if not item or not item.get('image_path') or not os.path.exists(item['image_path']):
            messagebox.showinfo("تنبيه", "لا توجد صورة لهذا المنتج")
            return
        
        # Create modern image viewer
        img_window = create_modal_window(main_window, f"صورة المنتج: {item_name}", 500, 600)
        
        # Header
        header_frame = ttk.Frame(img_window, style="Modern.TFrame")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text=item_name, style="Subheading.TLabel").pack()
        ttk.Label(header_frame, text=f"السعر: {item['price']:.2f} د.ح | الكمية: {item['quantity']}", 
                 style="Muted.TLabel").pack(pady=(5, 0))
        
        # Image
        try:
            img = Image.open(item['image_path'])
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(img_window, image=photo, bg='#f8fafc')
            img_label.image = photo
            img_label.pack(pady=20)
        except Exception as e:
            ttk.Label(img_window, text=f"خطأ في تحميل الصورة: {e}", style="Muted.TLabel").pack(pady=50)
    
    def edit_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        
        conn = connect()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()
        
        if not item:
            messagebox.showerror("خطأ", "المنتج غير موجود")
            return
        
        # Create modern edit window
        edit_window = create_modal_window(main_window, f"تعديل المنتج: {item['name']}", 500, 700)
        
        # Header
        header_card = create_modern_card(edit_window, "تعديل بيانات المنتج", 20)
        header_card.pack(fill="x", padx=20, pady=(20, 10))
        
        # Form
        form_card = create_modern_card(edit_window, padding=20)
        form_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Form fields
        fields = [
            ("اسم المنتج:", item['name']),
            ("الحجم:", item['size'] or ''),
            ("السعر:", str(item['price'])),
            ("الكمية:", str(item['quantity'])),
            ("الباركود:", item['barcode'] or '')
        ]
        
        entries = {}
        for i, (label, value) in enumerate(fields):
            ttk.Label(form_card, text=label, style="Body.TLabel").grid(row=i, column=0, sticky="w", pady=8, padx=(0, 10))
            entry = ttk.Entry(form_card, font=("Segoe UI", 11), width=25)
            entry.insert(0, value)
            entry.grid(row=i, column=1, sticky="ew", pady=8)
            entries[label] = entry
        
        form_card.columnconfigure(1, weight=1)
        
        # Image section
        image_frame = ttk.Frame(form_card, style="Modern.TFrame")
        image_frame.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=15)
        
        ttk.Label(image_frame, text="📷 صورة المنتج:", style="Body.TLabel").pack(anchor="w")
        
        image_path_var = StringVar(value=item.get('image_path', ''))
        current_image_label = ttk.Label(image_frame, 
                                       text=f"الصورة الحالية: {os.path.basename(item['image_path'])}" if item.get('image_path') else "لا توجد صورة",
                                       style="Muted.TLabel")
        current_image_label.pack(anchor="w", pady=(5, 10))
        
        def choose_new_image():
            file_path = filedialog.askopenfilename(
                title="اختر صورة جديدة",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
            )
            if file_path:
                filename = os.path.basename(file_path)
                dest_path = os.path.join("assets", filename)
                os.makedirs("assets", exist_ok=True)
                shutil.copy(file_path, dest_path)
                image_path_var.set(dest_path)
                current_image_label.config(text=f"صورة جديدة: {filename}")
        
        ttk.Button(image_frame, text="اختيار صورة جديدة", command=choose_new_image, 
                  style="Secondary.TButton").pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(edit_window, style="Modern.TFrame")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def save_changes():
            try:
                name = entries["اسم المنتج:"].get().strip()
                size = entries["الحجم:"].get().strip()
                price = float(entries["السعر:"].get())
                quantity = int(entries["الكمية:"].get())
                barcode = entries["الباركود:"].get().strip()
                
                if not name:
                    messagebox.showerror("خطأ", "اسم المنتج مطلوب")
                    return
                
                conn = connect()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE items SET name = %s, size = %s, price = %s, quantity = %s, 
                    barcode = %s, image_path = %s WHERE id = %s
                """, (name, size, price, quantity, barcode, image_path_var.get(), item_id))
                conn.commit()
                cur.close()
                conn.close()
                
                messagebox.showinfo("نجاح", "تم تحديث المنتج بنجاح")
                edit_window.destroy()
                load_products()
                
            except ValueError:
                messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {e}")
        
        ttk.Button(button_frame, text="💾 حفظ التغييرات", command=save_changes, 
                  style="Success.TButton").pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text="❌ إلغاء", command=edit_window.destroy, 
                  style="Secondary.TButton").pack(side="right")
    
    def delete_selected_item():
        selected = product_table.focus()
        if not selected:
            messagebox.showinfo("تنبيه", "اختر منتجًا أولاً")
            return
        
        vals = product_table.item(selected)["values"]
        item_id = vals[0]
        item_name = vals[1]
        
        if messagebox.askyesno("تأكيد الحذف", 
                              f"هل تريد حذف المنتج '{item_name}' نهائياً؟\nسيتم حذف المنتج وصورته من النظام.",
                              icon='warning'):
            delete_item(item_id)
            load_products()
            messagebox.showinfo("تم", f"تم حذف المنتج '{item_name}' وصورته بنجاح")
    
    def add_new_product():
        add_product_window(main_window)
        load_products()
    
    # Connect add button
    add_btn.config(command=add_new_product)
    
    # Action buttons
    action_card = create_modern_card(tab, padding=15)
    action_card.pack(fill="x")
    
    action_frame = ttk.Frame(action_card, style="Modern.TFrame")
    action_frame.pack()
    
    ttk.Button(action_frame, text="👁️ عرض الصورة", command=view_selected_item, 
              style="Secondary.TButton").pack(side="left", padx=5)
    ttk.Button(action_frame, text="✏️ تعديل المنتج", command=edit_selected_item, 
              style="Secondary.TButton").pack(side="left", padx=5)
    ttk.Button(action_frame, text="🗑️ حذف المنتج", command=delete_selected_item, 
              style="Danger.TButton").pack(side="left", padx=5)
    ttk.Button(action_frame, text="🔄 إعادة تحميل", command=load_products, 
              style="Secondary.TButton").pack(side="left", padx=5)
    
    # Search functionality
    def filter_products(*args):
        search_term = search_var.get().lower()
        if not search_term:
            load_products()
            return
        
        product_table.delete(*product_table.get_children())
        items = get_all_items()
        categories = {cat['id']: cat['name'] for cat in get_all_categories()}
        
        for item in items:
            if (search_term in item['name'].lower() or 
                search_term in (item['barcode'] or '').lower() or
                search_term in categories.get(item['category_id'], '').lower()):
                
                category_name = categories.get(item['category_id'], 'غير محدد')
                image_status = "✅" if item.get('image_path') else "❌"
                
                product_table.insert("", "end", values=(
                    item['id'],
                    item['name'],
                    item['size'] or '-',
                    category_name,
                    f"{item['price']:.2f} د.ح",
                    item['quantity'],
                    item['barcode'] or '-',
                    image_status
                ))
    
    search_var.trace('w', filter_products)
    
    load_products()
    return tab

def enhanced_current_sale_tab(notebook, store, main_window):
    """Create modern current sale tab"""
    tab = ttk.Frame(notebook, style="Modern.TFrame", padding=20)
    notebook.add(tab, text="💰 المبيعات الحالية")
    
    sale_id = [start_sale(store["id"])]
    
    # Header
    header_card = create_modern_card(tab, "نقطة البيع", 20)
    header_card.pack(fill="x", pady=(0, 20))
    
    # Quick actions
    actions_frame = ttk.Frame(header_card, style="Modern.TFrame")
    actions_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Button(actions_frame, text="📷 مسح منتج", style="Primary.TButton",
              command=lambda: scan_window(current_sale_table, sale_id[0], main_window)).pack(side="left", padx=(0, 10))
    ttk.Button(actions_frame, text="➕ إضافة منتج يدويًا", style="Secondary.TButton",
              command=lambda: add_product_window(main_window)).pack(side="left", padx=(0, 10))
    
    # Current sale card
    sale_card = create_modern_card(tab, "سلة البيع الحالية", 15)
    sale_card.pack(fill="both", expand=True, pady=(0, 20))
    
    # Current sale table
    current_sale_table = ttk.Treeview(sale_card, columns=("name", "price", "qty", "total"), 
                                     show="headings", style="Modern.Treeview", height=8)
    
    headers = ("المنتج", "السعر", "الكمية", "المجموع")
    for col, header in zip(("name", "price", "qty", "total"), headers):
        current_sale_table.heading(col, text=header)
        current_sale_table.column(col, anchor="center", width=150)
    
    current_sale_table.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Sale total and finish
    total_frame = ttk.Frame(tab, style="Modern.TFrame")
    total_frame.pack(fill="x", pady=(0, 20))
    
    total_card = create_modern_card(total_frame, padding=20)
    total_card.pack(fill="x")
    
    total_label = ttk.Label(total_card, text="المجموع: 0.00 د.ح", style="Heading.TLabel")
    total_label.pack(side="left")
    
    def update_total():
        total = 0
        for row in current_sale_table.get_children():
            total += float(current_sale_table.item(row)["values"][3])
        total_label.config(text=f"المجموع: {total:.2f} د.ح")
    
    def finish_current_sale():
        total = 0
        for row in current_sale_table.get_children():
            total += float(current_sale_table.item(row)["values"][3])
        
        if total == 0:
            messagebox.showwarning("تنبيه", "لا توجد منتجات في السلة")
            return
        
        finish_sale(sale_id[0], total)
        messagebox.showinfo("تم", f"تم إنهاء البيع بمجموع {total:.2f} د.ح")
        current_sale_table.delete(*current_sale_table.get_children())
        sale_id[0] = start_sale(store["id"])
        update_total()
        refresh_latest_sale()
    
    ttk.Button(total_card, text="💾 إنهاء البيع", command=finish_current_sale, 
              style="Success.TButton").pack(side="right")
    
    # Latest sale section
    latest_card = create_modern_card(tab, "آخر عملية بيع مكتملة", 15)
    latest_card.pack(fill="both", expand=True)
    
    latest_sale_table = ttk.Treeview(latest_card, columns=("id", "name", "price", "qty", "total"), 
                                    show="headings", style="Modern.Treeview", height=6)
    
    headers = ("", "المنتج", "السعر", "الكمية", "المجموع")
    for col, header in zip(("id", "name", "price", "qty", "total"), headers):
        latest_sale_table.heading(col, text=header)
        if col == "id":
            latest_sale_table.column(col, width=0, stretch=False)
        else:
            latest_sale_table.column(col, anchor="center", width=120)
    
    latest_sale_table.pack(fill="both", expand=True, padx=10, pady=10)
    
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
            latest_sale_table.insert("", "end", values=(
                item['id'], item['name'], f"{item['price']:.2f} د.ح", 
                item['quantity'], f"{item['total']:.2f} د.ح"
            ))
    
    refresh_latest_sale()
    
    # Bind update total to table changes
    def on_sale_change(*args):
        update_total()
    
    current_sale_table.bind('<<TreeviewSelect>>', on_sale_change)
    
    return tab

def create_store_setup_window(main_window):
    """Create modern store setup window"""
    setup_window = create_modal_window(main_window, "إعداد المتجر", 500, 400)
    
    # Header
    header_card = create_modern_card(setup_window, "إعداد معلومات المتجر", 20)
    header_card.pack(fill="x", padx=20, pady=(20, 10))
    
    ttk.Label(header_card, text="يرجى إدخال معلومات المتجر لبدء استخدام النظام", 
             style="Muted.TLabel").pack()
    
    # Form
    form_card = create_modern_card(setup_window, padding=20)
    form_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    fields = [
        ("اسم المتجر:", ""),
        ("الموقع:", ""),
        ("رقم التواصل:", "")
    ]
    
    entries = {}
    for i, (label, value) in enumerate(fields):
        ttk.Label(form_card, text=label, style="Body.TLabel").grid(row=i, column=0, sticky="w", pady=12, padx=(0, 15))
        entry = ttk.Entry(form_card, font=("Segoe UI", 11), width=25)
        entry.insert(0, value)
        entry.grid(row=i, column=1, sticky="ew", pady=12)
        entries[label] = entry
    
    form_card.columnconfigure(1, weight=1)
    
    # Buttons
    button_frame = ttk.Frame(setup_window, style="Modern.TFrame")
    button_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    def save_store():
        name = entries["اسم المتجر:"].get().strip()
        location = entries["الموقع:"].get().strip()
        contact = entries["رقم التواصل:"].get().strip()
        
        if not name:
            messagebox.showerror("خطأ", "اسم المتجر مطلوب")
            return
        
        set_store(name, location, contact)
        messagebox.showinfo("نجاح", "تم حفظ معلومات المتجر بنجاح")
        setup_window.destroy()
    
    ttk.Button(button_frame, text="💾 حفظ", command=save_store, 
              style="Primary.TButton").pack(side="right")

def main():
    # Create main window
    root = tk.Tk()
    root.title("🏪 كشك الجلفة - أكسا | نظام إدارة المبيعات")
    root.geometry("1400x900")
    root.configure(bg='#f8fafc')
    
    # Setup modern theme
    colors = setup_modern_theme()
    
    # Status bar
    status_var = StringVar()
    status_frame = ttk.Frame(root, style="Modern.TFrame")
    status_frame.pack(side="bottom", fill="x")
    
    status_bar = ttk.Label(status_frame, textvariable=status_var, style="Muted.TLabel", 
                          padding=(10, 8))
    status_bar.pack(side="left")
    
    # App info
    app_info = ttk.Label(status_frame, text="كشك الجلفة - أكسا © 2024", 
                        style="Muted.TLabel", padding=(10, 8))
    app_info.pack(side="right")
    
    status_var.set("🟢 النظام جاهز")
    
    # Main content
    main_frame = ttk.Frame(root, style="Modern.TFrame", padding=10)
    main_frame.pack(fill="both", expand=True)
    
    # Header
    header_frame = ttk.Frame(main_frame, style="Modern.TFrame")
    header_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(header_frame, text="🏪 كشك الجلفة - أكسا", style="Heading.TLabel").pack(side="left")
    ttk.Label(header_frame, text="نظام إدارة المبيعات المتطور", style="Muted.TLabel").pack(side="left", padx=(15, 0))
    
    # Notebook
    notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
    notebook.pack(fill="both", expand=True)
    
    # Store setup
    store = get_store()
    if not store:
        create_store_setup_window(root)
        store = get_store()
    
    # Create tabs
    enhanced_inventory_tab(notebook, root)
    enhanced_current_sale_tab(notebook, store, root)
    
    # Sales report tabs
    today_tab = ttk.Frame(notebook, style="Modern.TFrame", padding=20)
    notebook.add(today_tab, text="📊 مبيعات اليوم")
    today_sales_var = StringVar()
    create_sales_table(today_tab, lambda: get_sales('today'), today_sales_var)
    
    week_tab = ttk.Frame(notebook, style="Modern.TFrame", padding=20)
    notebook.add(week_tab, text="📈 مبيعات الأسبوع")
    week_sales_var = StringVar()
    create_sales_table(week_tab, lambda: get_sales('week'), week_sales_var)
    
    all_tab = ttk.Frame(notebook, style="Modern.TFrame", padding=20)
    notebook.add(all_tab, text="📋 إجمالي المبيعات")
    all_sales_var = StringVar()
    create_sales_table(all_tab, lambda: get_sales('all'), all_sales_var)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()