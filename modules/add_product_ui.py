import tkinter as tk
from tkinter import filedialog, messagebox
from modules import db_utils

def add_product_window():
    window = tk.Toplevel()
    window.title("➕ إضافة منتج جديد")
    window.geometry("400x500")

    # Labels + Entry fields
    tk.Label(window, text="اسم المنتج:").pack(pady=5)
    entry_name = tk.Entry(window, width=30)
    entry_name.pack(pady=5)

    tk.Label(window, text="الحجم:").pack(pady=5)
    entry_size = tk.Entry(window, width=30)
    entry_size.pack(pady=5)

    tk.Label(window, text="الفئة (ID):").pack(pady=5)
    entry_category = tk.Entry(window, width=30)
    entry_category.pack(pady=5)

    tk.Label(window, text="السعر:").pack(pady=5)
    entry_price = tk.Entry(window, width=30)
    entry_price.pack(pady=5)

    tk.Label(window, text="الكمية:").pack(pady=5)
    entry_quantity = tk.Entry(window, width=30)
    entry_quantity.pack(pady=5)

    tk.Label(window, text="الباركود:").pack(pady=5)
    entry_barcode = tk.Entry(window, width=30)
    entry_barcode.pack(pady=5)

    # Image upload
    tk.Label(window, text="📷 صورة المنتج:").pack(pady=5)
    image_path_var = tk.StringVar()

    def choose_image():
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            image_path_var.set(file_path)
            lbl_image.config(text=f"✅ {file_path.split('/')[-1]}")

    btn_choose = tk.Button(window, text="اختر صورة", command=choose_image)
    btn_choose.pack(pady=5)

    lbl_image = tk.Label(window, text="لم يتم اختيار صورة")
    lbl_image.pack(pady=5)

    # Save product
    def save_product():
        name = entry_name.get()
        size = entry_size.get()
        category_id = entry_category.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        barcode = entry_barcode.get()
        image_path = image_path_var.get() if image_path_var.get() else None

        if not name or not price or not quantity:
            messagebox.showerror("خطأ", "يجب ملء جميع الحقول المطلوبة")
            return

        try:
            db_utils.add_item(
                name,
                size,
                int(category_id) if category_id else None,
                float(price),
                int(quantity),
                barcode,
                image_path
            )
            messagebox.showinfo("نجاح", "✅ تم إضافة المنتج بنجاح")
            window.destroy()
        except Exception as e:
            messagebox.showerror("خطأ", f"❌ {e}")

    tk.Button(window, text="💾 حفظ المنتج", command=save_product, bg="green", fg="white").pack(pady=20)

    window.mainloop()
