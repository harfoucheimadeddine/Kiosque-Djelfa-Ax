import tkinter as tk
from tkinter import ttk, messagebox
from modules.db_utils import get_item_by_barcode, add_sale_item

def scan_window(current_sale_table, sale_id):
    def on_scan():
        barcode = barcode_var.get().strip()
        if not barcode:
            messagebox.showwarning("تنبيه", "الرجاء إدخال أو مسح الباركود.")
            return
        item = get_item_by_barcode(barcode)
        win.grab_release()
        win.destroy()
        if item:
            # Found: ask if user wants to add with database price or custom price
            def on_add(price=None):
                quantity = 1
                used_price = price if price is not None else item['price']
                add_sale_item(sale_id, item['id'], quantity, used_price)
                total = used_price * quantity
                current_sale_table.insert("", "end", values=(item['name'], used_price, quantity, total))
                messagebox.showinfo("تم", f"تمت إضافة المنتج '{item['name']}' إلى السلة.")
            add_win = tk.Toplevel()
            add_win.title("تأكيد إضافة المنتج")
            add_win.geometry("350x220")
            ttk.Label(add_win, text=f"تم العثور على المنتج: {item['name']}", font=("Arial", 13, "bold")).pack(pady=10)
            ttk.Label(add_win, text=f"السعر المخزن: {item['price']} د.ح").pack(pady=5)
            ttk.Button(add_win, text="إضافة بالسعر المخزن", style="Accent.TButton",
                       command=lambda: [on_add(), add_win.destroy()]).pack(pady=7)
            price_var = tk.DoubleVar(value=item['price'])
            price_frame = ttk.Frame(add_win)
            price_frame.pack(pady=5)
            ttk.Label(price_frame, text="أو أدخل سعر مخصص: ").pack(side=tk.LEFT, padx=3)
            price_entry = ttk.Entry(price_frame, textvariable=price_var, width=10)
            price_entry.pack(side=tk.LEFT)
            ttk.Button(add_win, text="إضافة بالسعر المدخل", style="Accent.TButton",
                       command=lambda: [on_add(price_var.get()), add_win.destroy()]).pack(pady=7)
            ttk.Button(add_win, text="إلغاء", command=add_win.destroy).pack(pady=5)
            add_win.transient(current_sale_table)
            add_win.grab_set()
            add_win.focus()
        else:
            # Not found: ask if user wants to add to stock
            def on_accept():
                messagebox.showinfo("تحويل", "سيتم تحويلك لإضافة المنتج الجديد.")
                from modules.add_product_ui import add_product_window
                add_product_window(prefill_barcode=barcode)
            def on_decline():
                messagebox.showinfo("تنبيه", "الباركود غير موجود. لم تتم إضافة المنتج.")
            not_found_win = tk.Toplevel()
            not_found_win.title("الباركود غير موجود")
            not_found_win.geometry("350x180")
            ttk.Label(not_found_win, text=f"الباركود '{barcode}' غير موجود في المخزون.", font=("Arial", 13, "bold")).pack(pady=10)
            ttk.Label(not_found_win, text="هل تريد إضافته إلى المخزون؟").pack(pady=5)
            btns = ttk.Frame(not_found_win)
            btns.pack(pady=10)
            ttk.Button(btns, text="نعم، إضافة", style="Accent.TButton",
                command=lambda: [not_found_win.destroy(), on_accept()]).pack(side=tk.LEFT, padx=10)
            ttk.Button(btns, text="لا، تجاهل", command=lambda: [not_found_win.destroy(), on_decline()]).pack(side=tk.LEFT, padx=10)
            not_found_win.transient(current_sale_table)
            not_found_win.grab_set()
            not_found_win.focus()

    win = tk.Toplevel()
    win.title("مسح الباركود")
    win.geometry("350x170")
    ttk.Label(win, text="مسح أو إدخال الباركود:", font=("Arial", 12)).pack(pady=15)
    barcode_var = tk.StringVar()
    barcode_entry = ttk.Entry(win, textvariable=barcode_var, font=("Arial", 13), width=20)
    barcode_entry.pack(pady=5)
    barcode_entry.focus()
    ttk.Button(win, text="تأكيد", style="Accent.TButton", command=on_scan).pack(pady=12)
    win.transient(current_sale_table)
    win.grab_set()
    win.focus()