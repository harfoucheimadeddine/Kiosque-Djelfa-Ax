import tkinter as tk
from tkinter import messagebox
import modules.db_utils as db_utils

def scan_window(sale_table):
    def on_enter(event=None):
        code = entry_barcode.get().strip()
        item = db_utils.get_item_by_barcode(code)

        if not item:
            messagebox.showerror("❌ خطأ", "المنتج غير موجود!")
            entry_barcode.delete(0, tk.END)
            return

        if item["quantity"] <= 0:
            messagebox.showwarning("⚠️", "الكمية غير كافية في المخزون")
            return

        total_price = item["price"]

        # Add to sale table
        sale_table.insert("", "end", values=(item["name"], item["price"], 1, total_price))

        # Decrease stock
        db_utils.update_item(item["id"], quantity=item["quantity"] - 1)

        # Record sale
        db_utils.record_sale(item["id"], 1, total_price)

        messagebox.showinfo("✅", f"تمت إضافة {item['name']} للبيع")
        entry_barcode.delete(0, tk.END)

    window = tk.Toplevel()
    window.title("📷 مسح الباركود")
    window.geometry("400x200")

    tk.Label(window, text="امسح الباركود هنا:").pack(pady=10)
    entry_barcode = tk.Entry(window, font=("Arial", 14))
    entry_barcode.pack(pady=10)

    entry_barcode.bind("<Return>", on_enter)  # scanner usually presses Enter

    window.mainloop()
