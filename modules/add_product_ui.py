import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from modules import db_utils
import os
import shutil

ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def add_product_window(prefill_barcode=None):
    window = tk.Toplevel()
    window.title("➕ إضافة منتج جديد")
    window.geometry("400x750")

    tk.Label(window, text="اسم المنتج:", font=("Arial", 12)).pack(pady=5)
    entry_name = tk.Entry(window, font=("Arial", 12), width=30)
    entry_name.pack(pady=5)

    tk.Label(window, text="الحجم:", font=("Arial", 12)).pack(pady=5)
    entry_size = tk.Entry(window, font=("Arial", 12), width=30)
    entry_size.pack(pady=5)

    # --- Category selection ---
    tk.Label(window, text="الفئة:", font=("Arial", 12)).pack(pady=5)
    categories = db_utils.get_all_categories()
    category_name_to_id = {cat['name']: cat['id'] for cat in categories}
    category_names = list(category_name_to_id.keys())
    category_combo = ttk.Combobox(window, values=category_names, font=("Arial", 12), width=28, state="readonly")
    category_combo.pack(pady=5)

    def refresh_categories():
        cats = db_utils.get_all_categories()
        category_name_to_id.clear()
        names = []
        for cat in cats:
            category_name_to_id[cat['name']] = cat['id']
            names.append(cat['name'])
        category_combo['values'] = names

    def add_category_popup():
        popup = tk.Toplevel(window)
        popup.title("إضافة فئة جديدة")
        popup.geometry("300x150")
        tk.Label(popup, text="اسم الفئة:", font=("Arial", 12)).pack(pady=10)
        entry_cat = tk.Entry(popup, font=("Arial", 12), width=25)
        entry_cat.pack(pady=5)

        def save_cat():
            name = entry_cat.get().strip()
            if not name:
                messagebox.showerror("خطأ", "أدخل اسم الفئة")
                return
            db_utils.add_category(name)
            popup.destroy()
            refresh_categories()
            category_combo.set(name)

        tk.Button(popup, text="حفظ", command=save_cat, font=("Arial", 12), bg="green", fg="white").pack(pady=10)
        popup.mainloop()

    tk.Button(window, text="إضافة فئة جديدة", command=add_category_popup, font=("Arial", 12), bg="#f0ad4e").pack(pady=5)

    tk.Label(window, text="السعر:", font=("Arial", 12)).pack(pady=5)
    entry_price = tk.Entry(window, font=("Arial", 12), width=30)
    entry_price.pack(pady=5)

    tk.Label(window, text="الكمية:", font=("Arial", 12)).pack(pady=5)
    entry_quantity = tk.Entry(window, font=("Arial", 12), width=30)
    entry_quantity.pack(pady=5)

    # --- Barcode with scan button ---
    barcode_frame = tk.Frame(window)
    barcode_frame.pack(pady=5)
    tk.Label(barcode_frame, text="الباركود:", font=("Arial", 12)).pack(side=tk.LEFT)
    entry_barcode = tk.Entry(barcode_frame, font=("Arial", 12), width=18)
    entry_barcode.pack(side=tk.LEFT, padx=5)
    if prefill_barcode:
        entry_barcode.insert(0, prefill_barcode)

    def scan_barcode_popup():
        scan_win = tk.Toplevel(window)
        scan_win.title("امسح الباركود")
        scan_win.geometry("350x120")
        tk.Label(scan_win, text="رجاءً امسح الباركود الآن:", font=("Arial", 12)).pack(pady=10)
        scan_entry = tk.Entry(scan_win, font=("Arial", 14))
        scan_entry.pack(pady=10)
        scan_entry.focus_set()

        def on_scan(event=None):
            barcode = scan_entry.get().strip()
            if barcode:
                entry_barcode.delete(0, tk.END)
                entry_barcode.insert(0, barcode)
                scan_win.destroy()

        scan_entry.bind("<Return>", on_scan)
        scan_win.mainloop()

    tk.Button(barcode_frame, text="📷 امسح الباركود", command=scan_barcode_popup, font=("Arial", 11)).pack(side=tk.LEFT, padx=5)

    tk.Label(window, text="📷 صورة المنتج:", font=("Arial", 12)).pack(pady=5)
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
            lbl_image.config(text=f"✅ {filename}")

    btn_choose = tk.Button(window, text="اختر صورة", command=choose_image, font=("Arial", 12))
    btn_choose.pack(pady=5)
    lbl_image = tk.Label(window, text="لم يتم اختيار صورة", font=("Arial", 10))
    lbl_image.pack(pady=5)

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

    tk.Button(window, text="💾 حفظ المنتج", command=save_product, font=("Arial", 12), bg="green", fg="white").pack(pady=20)
    window.mainloop()