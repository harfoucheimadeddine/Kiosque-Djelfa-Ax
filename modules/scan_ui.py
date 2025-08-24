import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import modules.db_utils as db_utils

def scan_product_window():
    def on_enter(event=None):
        barcode = entry_barcode.get()
        product = db_utils.get_item_by_barcode(barcode)
        if product:
            label_name.config(text=f"المنتج: {product['name']}")
            label_price.config(text=f"السعر: {product['price']} دج")
            label_qty.config(text=f"الكمية: {product['quantity']}")

            # Show image if exists
            if product["image_path"]:
                try:
                    img = Image.open(product["image_path"])
                    img = img.resize((120, 120))
                    photo = ImageTk.PhotoImage(img)
                    label_img.config(image=photo, text="")
                    label_img.image = photo
                except:
                    label_img.config(text="❌ خطأ في تحميل الصورة", image="")
            else:
                label_img.config(text="لا توجد صورة", image="")
        else:
            messagebox.showwarning("⚠️", "لم يتم العثور على المنتج")
        entry_barcode.delete(0, tk.END)

    window = tk.Toplevel()
    window.title("مسح المنتجات")
    window.geometry("400x400")

    tk.Label(window, text="امسح الباركود").pack()
    entry_barcode = tk.Entry(window)
    entry_barcode.pack()
    entry_barcode.bind("<Return>", on_enter)  # barcode scanner sends Enter

    label_name = tk.Label(window, text="")
    label_name.pack()

    label_price = tk.Label(window, text="")
    label_price.pack()

    label_qty = tk.Label(window, text="")
    label_qty.pack()

    label_img = tk.Label(window, text="")  # Image placeholder
    label_img.pack()

    window.mainloop()
