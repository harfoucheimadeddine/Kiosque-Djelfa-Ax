import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules import db_utils
import os
import shutil

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
    card = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
    card.pack(fill="x", padx=10, pady=5)
    
    if title:
        title_frame = tk.Frame(card, bg='#ffffff')
        title_frame.pack(fill="x", padx=padding, pady=(padding, 10))
        title_label = tk.Label(title_frame, text=title, font=("Segoe UI", 14, "bold"), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(anchor="w")
    
    content_frame = tk.Frame(card, bg='#ffffff')
    content_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))
    
    return content_frame

def add_product_window(parent=None, prefill_barcode=None):
    """Create modern add product window"""
    if parent is None:
        window = tk.Tk()
        window.title("➕ إضافة منتج جديد")
        window.geometry("500x800")
        window.configure(bg='#f8fafc')
    else:
        window = create_modal_window(parent, "➕ إضافة منتج جديد", 500, 800)
    
    ASSETS_DIR = "assets"
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Header
    header_frame = tk.Frame(window, bg='#f8fafc')
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(header_frame, text="إضافة منتج جديد", font=("Segoe UI", 18, "bold"), 
            bg='#f8fafc', fg='#1e293b').pack(anchor="w")
    tk.Label(header_frame, text="املأ جميع البيانات المطلوبة لإضافة المنتج", 
            font=("Segoe UI", 10), bg='#f8fafc', fg='#64748b').pack(anchor="w", pady=(5, 0))
    # Main form card
    form_card = create_modern_card(window, "بيانات المنتج الأساسية")
    
    # Product name
    tk.Label(form_card, text="اسم المنتج *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_name = tk.Entry(form_card, font=("Segoe UI", 11), width=35, relief='solid', bd=1)
    entry_name.pack(fill="x", pady=(0, 15))

    # Size
    tk.Label(form_card, text="الحجم", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_size = tk.Entry(form_card, font=("Segoe UI", 11), width=35, relief='solid', bd=1)
    entry_size.pack(fill="x", pady=(0, 15))

    # Category selection
    tk.Label(form_card, text="الفئة *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    categories = db_utils.get_all_categories()
    category_name_to_id = {cat['name']: cat['id'] for cat in categories}
    category_names = list(category_name_to_id.keys())
    
    category_frame = tk.Frame(form_card, bg='#ffffff')
    category_frame.pack(fill="x", pady=(0, 15))
    
    category_combo = ttk.Combobox(category_frame, values=category_names, font=("Segoe UI", 11), 
                                 width=25, state="readonly")
    category_combo.pack(side="left", fill="x", expand=True)

    def refresh_categories():
        cats = db_utils.get_all_categories()
        category_name_to_id.clear()
        names = []
        for cat in cats:
            category_name_to_id[cat['name']] = cat['id']
            names.append(cat['name'])
        category_combo['values'] = names

    def add_category_popup():
        popup = create_modal_window(window, "إضافة فئة جديدة", 350, 200)
        
        popup_card = create_modern_card(popup, "فئة جديدة")
        
        tk.Label(popup_card, text="اسم الفئة:", font=("Segoe UI", 11, "bold"), 
                bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
        entry_cat = tk.Entry(popup_card, font=("Segoe UI", 11), width=25, relief='solid', bd=1)
        entry_cat.pack(fill="x", pady=(0, 15))

        def save_cat():
            name = entry_cat.get().strip()
            if not name:
                messagebox.showerror("خطأ", "أدخل اسم الفئة")
                return
            db_utils.add_category(name)
            popup.destroy()
            refresh_categories()
            category_combo.set(name)

        btn_frame = tk.Frame(popup_card, bg='#ffffff')
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="💾 حفظ", command=save_cat, font=("Segoe UI", 11, "bold"), 
                 bg="#10b981", fg="white", relief='flat', padx=20, pady=8).pack(side="right")

    tk.Button(category_frame, text="➕ فئة جديدة", command=add_category_popup, 
             font=("Segoe UI", 10), bg="#f59e0b", fg="white", relief='flat', 
             padx=15, pady=5).pack(side="right", padx=(10, 0))

    # Price and quantity
    price_qty_frame = tk.Frame(form_card, bg='#ffffff')
    price_qty_frame.pack(fill="x", pady=(0, 15))
    
    # Price
    price_frame = tk.Frame(price_qty_frame, bg='#ffffff')
    price_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
    tk.Label(price_frame, text="السعر (د.ح) *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_price = tk.Entry(price_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_price.pack(fill="x")

    # Quantity
    qty_frame = tk.Frame(price_qty_frame, bg='#ffffff')
    qty_frame.pack(side="right", fill="x", expand=True)
    tk.Label(qty_frame, text="الكمية *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_quantity = tk.Entry(qty_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_quantity.pack(fill="x")

    # Barcode card
    barcode_card = create_modern_card(window, "الباركود")
    
    barcode_input_frame = tk.Frame(barcode_card, bg='#ffffff')
    barcode_input_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(barcode_input_frame, text="رقم الباركود", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    
    barcode_entry_frame = tk.Frame(barcode_input_frame, bg='#ffffff')
    barcode_entry_frame.pack(fill="x")
    
    entry_barcode = tk.Entry(barcode_entry_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_barcode.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    if prefill_barcode:
        entry_barcode.insert(0, prefill_barcode)

    def scan_barcode_popup():
        scan_win = create_modal_window(window, "مسح الباركود", 400, 200)
        
        scan_card = create_modern_card(scan_win, "امسح الباركود")
        
        tk.Label(scan_card, text="رجاءً امسح الباركود الآن:", font=("Segoe UI", 12), 
                bg='#ffffff', fg='#1e293b').pack(pady=(0, 10))
        scan_entry = tk.Entry(scan_card, font=("Segoe UI", 14), relief='solid', bd=1)
        scan_entry.pack(fill="x", pady=(0, 15))
        scan_entry.focus_set()

        def on_scan(event=None):
            barcode = scan_entry.get().strip()
            if barcode:
                entry_barcode.delete(0, tk.END)
                entry_barcode.insert(0, barcode)
                scan_win.destroy()

        scan_entry.bind("<Return>", on_scan)

    tk.Button(barcode_entry_frame, text="📷 مسح", command=scan_barcode_popup, 
             font=("Segoe UI", 10), bg="#2563eb", fg="white", relief='flat', 
             padx=15, pady=8).pack(side="right")

    # Image card
    image_card = create_modern_card(window, "📷 صورة المنتج")
    
    image_path_var = tk.StringVar()
    
    def choose_image():
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(ASSETS_DIR, filename)
            shutil.copy(file_path, dest_path)
            image_path_var.set(dest_path)
            lbl_image.config(text=f"✅ تم اختيار: {filename}", fg="#10b981")

    image_btn_frame = tk.Frame(image_card, bg='#ffffff')
    image_btn_frame.pack(fill="x", pady=(0, 10))
    
    tk.Button(image_btn_frame, text="📁 اختيار صورة", command=choose_image, 
             font=("Segoe UI", 11), bg="#64748b", fg="white", relief='flat', 
             padx=20, pady=8).pack(side="left")
    
    lbl_image = tk.Label(image_card, text="لم يتم اختيار صورة", font=("Segoe UI", 10), 
                        bg='#ffffff', fg='#64748b')
    lbl_image.pack(anchor="w")

    # Save button
    button_frame = tk.Frame(window, bg='#f8fafc')
    button_frame.pack(fill="x", padx=20, pady=20)
    
    def save_product():
        name = entry_name.get()
        size = entry_size.get()
        category_name = category_combo.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        barcode = entry_barcode.get()
        image_path = image_path_var.get() if image_path_var.get() else None

        if not name or not price or not quantity or not category_name:
            messagebox.showerror("خطأ", "يجب ملء جميع الحقول المطلوبة")
            return

        try:
            category_id = category_name_to_id[category_name]
            db_utils.add_item(
                name,
                size,
                category_id,
                float(price),
                int(quantity),
                barcode,
                image_path
            )
            messagebox.showinfo("نجاح", "✅ تم إضافة المنتج بنجاح")
            window.destroy()
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ {e}")

    tk.Button(button_frame, text="💾 حفظ المنتج", command=save_product, 
             font=("Segoe UI", 12, "bold"), bg="#10b981", fg="white", relief='flat', 
             padx=30, pady=12).pack(side="right")
    
    tk.Button(button_frame, text="❌ إلغاء", command=window.destroy, 
             font=("Segoe UI", 11), bg="#ef4444", fg="white", relief='flat', 
             padx=20, pady=12).pack(side="right", padx=(0, 10))
    
    if parent is None:
        window.mainloop()import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules import db_utils
import os
import shutil

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
    card = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
    card.pack(fill="x", padx=10, pady=5)
    
    if title:
        title_frame = tk.Frame(card, bg='#ffffff')
        title_frame.pack(fill="x", padx=padding, pady=(padding, 10))
        title_label = tk.Label(title_frame, text=title, font=("Segoe UI", 14, "bold"), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(anchor="w")
    
    content_frame = tk.Frame(card, bg='#ffffff')
    content_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))
    
    return content_frame

def add_product_window(parent=None, prefill_barcode=None):
    """Create modern add product window"""
    if parent is None:
        window = tk.Tk()
        window.title("➕ إضافة منتج جديد")
        window.geometry("500x800")
        window.configure(bg='#f8fafc')
    else:
        window = create_modal_window(parent, "➕ إضافة منتج جديد", 500, 800)
    
    ASSETS_DIR = "assets"
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # Header
    header_frame = tk.Frame(window, bg='#f8fafc')
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(header_frame, text="إضافة منتج جديد", font=("Segoe UI", 18, "bold"), 
            bg='#f8fafc', fg='#1e293b').pack(anchor="w")
    tk.Label(header_frame, text="املأ جميع البيانات المطلوبة لإضافة المنتج", 
            font=("Segoe UI", 10), bg='#f8fafc', fg='#64748b').pack(anchor="w", pady=(5, 0))
    # Main form card
    form_card = create_modern_card(window, "بيانات المنتج الأساسية")
    
    # Product name
    tk.Label(form_card, text="اسم المنتج *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_name = tk.Entry(form_card, font=("Segoe UI", 11), width=35, relief='solid', bd=1)
    entry_name.pack(fill="x", pady=(0, 15))

    # Size
    tk.Label(form_card, text="الحجم", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_size = tk.Entry(form_card, font=("Segoe UI", 11), width=35, relief='solid', bd=1)
    entry_size.pack(fill="x", pady=(0, 15))

    # Category selection
    tk.Label(form_card, text="الفئة *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    categories = db_utils.get_all_categories()
    category_name_to_id = {cat['name']: cat['id'] for cat in categories}
    category_names = list(category_name_to_id.keys())
    
    category_frame = tk.Frame(form_card, bg='#ffffff')
    category_frame.pack(fill="x", pady=(0, 15))
    
    category_combo = ttk.Combobox(category_frame, values=category_names, font=("Segoe UI", 11), 
                                 width=25, state="readonly")
    category_combo.pack(side="left", fill="x", expand=True)

    def refresh_categories():
        cats = db_utils.get_all_categories()
        category_name_to_id.clear()
        names = []
        for cat in cats:
            category_name_to_id[cat['name']] = cat['id']
            names.append(cat['name'])
        category_combo['values'] = names

    def add_category_popup():
        popup = create_modal_window(window, "إضافة فئة جديدة", 350, 200)
        
        popup_card = create_modern_card(popup, "فئة جديدة")
        
        tk.Label(popup_card, text="اسم الفئة:", font=("Segoe UI", 11, "bold"), 
                bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
        entry_cat = tk.Entry(popup_card, font=("Segoe UI", 11), width=25, relief='solid', bd=1)
        entry_cat.pack(fill="x", pady=(0, 15))

        def save_cat():
            name = entry_cat.get().strip()
            if not name:
                messagebox.showerror("خطأ", "أدخل اسم الفئة")
                return
            db_utils.add_category(name)
            popup.destroy()
            refresh_categories()
            category_combo.set(name)

        btn_frame = tk.Frame(popup_card, bg='#ffffff')
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="💾 حفظ", command=save_cat, font=("Segoe UI", 11, "bold"), 
                 bg="#10b981", fg="white", relief='flat', padx=20, pady=8).pack(side="right")

    tk.Button(category_frame, text="➕ فئة جديدة", command=add_category_popup, 
             font=("Segoe UI", 10), bg="#f59e0b", fg="white", relief='flat', 
             padx=15, pady=5).pack(side="right", padx=(10, 0))

    # Price and quantity
    price_qty_frame = tk.Frame(form_card, bg='#ffffff')
    price_qty_frame.pack(fill="x", pady=(0, 15))
    
    # Price
    price_frame = tk.Frame(price_qty_frame, bg='#ffffff')
    price_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
    tk.Label(price_frame, text="السعر (د.ح) *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_price = tk.Entry(price_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_price.pack(fill="x")

    # Quantity
    qty_frame = tk.Frame(price_qty_frame, bg='#ffffff')
    qty_frame.pack(side="right", fill="x", expand=True)
    tk.Label(qty_frame, text="الكمية *", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    entry_quantity = tk.Entry(qty_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_quantity.pack(fill="x")

    # Barcode card
    barcode_card = create_modern_card(window, "الباركود")
    
    barcode_input_frame = tk.Frame(barcode_card, bg='#ffffff')
    barcode_input_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(barcode_input_frame, text="رقم الباركود", font=("Segoe UI", 11, "bold"), 
            bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
    
    barcode_entry_frame = tk.Frame(barcode_input_frame, bg='#ffffff')
    barcode_entry_frame.pack(fill="x")
    
    entry_barcode = tk.Entry(barcode_entry_frame, font=("Segoe UI", 11), relief='solid', bd=1)
    entry_barcode.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    if prefill_barcode:
        entry_barcode.insert(0, prefill_barcode)

    def scan_barcode_popup():
        scan_win = create_modal_window(window, "مسح الباركود", 400, 200)
        
        scan_card = create_modern_card(scan_win, "امسح الباركود")
        
        tk.Label(scan_card, text="رجاءً امسح الباركود الآن:", font=("Segoe UI", 12), 
                bg='#ffffff', fg='#1e293b').pack(pady=(0, 10))
        scan_entry = tk.Entry(scan_card, font=("Segoe UI", 14), relief='solid', bd=1)
        scan_entry.pack(fill="x", pady=(0, 15))
        scan_entry.focus_set()

        def on_scan(event=None):
            barcode = scan_entry.get().strip()
            if barcode:
                entry_barcode.delete(0, tk.END)
                entry_barcode.insert(0, barcode)
                scan_win.destroy()

        scan_entry.bind("<Return>", on_scan)

    tk.Button(barcode_entry_frame, text="📷 مسح", command=scan_barcode_popup, 
             font=("Segoe UI", 10), bg="#2563eb", fg="white", relief='flat', 
             padx=15, pady=8).pack(side="right")

    # Image card
    image_card = create_modern_card(window, "📷 صورة المنتج")
    
    image_path_var = tk.StringVar()
    
    def choose_image():
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(ASSETS_DIR, filename)
            shutil.copy(file_path, dest_path)
            image_path_var.set(dest_path)
            lbl_image.config(text=f"✅ تم اختيار: {filename}", fg="#10b981")

    image_btn_frame = tk.Frame(image_card, bg='#ffffff')
    image_btn_frame.pack(fill="x", pady=(0, 10))
    
    tk.Button(image_btn_frame, text="📁 اختيار صورة", command=choose_image, 
             font=("Segoe UI", 11), bg="#64748b", fg="white", relief='flat', 
             padx=20, pady=8).pack(side="left")
    
    lbl_image = tk.Label(image_card, text="لم يتم اختيار صورة", font=("Segoe UI", 10), 
                        bg='#ffffff', fg='#64748b')
    lbl_image.pack(anchor="w")

    # Save button
    button_frame = tk.Frame(window, bg='#f8fafc')
    button_frame.pack(fill="x", padx=20, pady=20)
    
    def save_product():
        name = entry_name.get()
        size = entry_size.get()
        category_name = category_combo.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        barcode = entry_barcode.get()
        image_path = image_path_var.get() if image_path_var.get() else None

        if not name or not price or not quantity or not category_name:
            messagebox.showerror("خطأ", "يجب ملء جميع الحقول المطلوبة")
            return

        try:
            category_id = category_name_to_id[category_name]
            db_utils.add_item(
                name,
                size,
                category_id,
                float(price),
                int(quantity),
                barcode,
                image_path
            )
            messagebox.showinfo("نجاح", "✅ تم إضافة المنتج بنجاح")
            window.destroy()
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ {e}")

    tk.Button(button_frame, text="💾 حفظ المنتج", command=save_product, 
             font=("Segoe UI", 12, "bold"), bg="#10b981", fg="white", relief='flat', 
             padx=30, pady=12).pack(side="right")
    
    tk.Button(button_frame, text="❌ إلغاء", command=window.destroy, 
             font=("Segoe UI", 11), bg="#ef4444", fg="white", relief='flat', 
             padx=20, pady=12).pack(side="right", padx=(0, 10))
    
    if parent is None:
        window.mainloop()