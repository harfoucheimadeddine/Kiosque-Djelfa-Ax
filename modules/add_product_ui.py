import tkinter as tk
from tkinter import filedialog, messagebox
import modules.db_utils as db_utils

def add_product_window():
    def choose_image():
        file_path = filedialog.askopenfilename(
            title="اختر صورة المنتج",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            entry_image.delete(0, tk.END)
            entry_image.insert(0, file_path)

    def save_product():
        name = entry_name.get()
        size = entry_size.get()
        category_id = combo_category.get()
        price = entry_price.get()
        quantity = entry_quantity.get()
        barcode = entry_barcode.get()
        image_path = entry_image.get()

        if not (name and size and category_id and price and quantity and barcode):
            messagebox.showwarning("⚠️", "من فضلك املأ جميع الخانات")
            return

        try:
            db_utils.add_item(
                name, size, int(category_id), float(price), int(quantity), barcode, image_path
            )
            messagebox.showinfo("✅", "تم إضافة المنتج بنجاح!")
            window.destroy()
        except Exception as e:
            messagebox.showerror("❌ خطأ", str(e))

    window = tk.Toplevel()
    window.title("إضافة منتج")
    window.geometry("400x500")

    tk.Label(window, text="اسم المنتج").pack()
    entry_name = tk.Entry(window)
    entry_name.pack()

    tk.Label(window, text="الحجم").pack()
    entry_size = tk.Entry(window)
    entry_size.pack()

    tk.Label(window, text="التصنيف (ID)").pack()
    combo_category = tk.Entry(window)  # later: replace with dropdown
    combo_category.pack()

    tk.Label(window, text="السعر").pack()
    entry_price = tk.Entry(window)
    entry_price.pack()

    tk.Label(window, text="الكمية").pack()
    entry_quantity = tk.Entry(window)
    entry_quantity.pack()

    tk.Label(window, text="الباركود").pack()
    entry_barcode = tk.Entry(window)
    entry_barcode.pack()

    tk.Label(window, text="صورة المنتج").pack()
    entry_image = tk.Entry(window)
    entry_image.pack()
    tk.Button(window, text="اختر صورة", command=choose_image).pack()

    tk.Button(window, text="💾 حفظ", command=save_product).pack(pady=10)

    window.mainloop()
