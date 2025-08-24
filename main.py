import tkinter as tk
from tkinter import ttk
import modules.db_utils as db_utils
from modules.add_product_ui import add_product_window

from modules.scan_ui import scan_window

def main():
    root = tk.Tk()
    root.title("📊 نظام المبيعات")
    root.geometry("800x600")

    # Sales table
    sale_table = ttk.Treeview(root, columns=("name", "price", "qty", "total"), show="headings")
    sale_table.heading("name", text="المنتج")
    sale_table.heading("price", text="السعر")
    sale_table.heading("qty", text="الكمية")
    sale_table.heading("total", text="المجموع")
    sale_table.pack(fill=tk.BOTH, expand=True, pady=20)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="➕ إضافة منتج", width=15, command=add_product_window).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="📷 مسح منتج", width=15, command=lambda: scan_window(sale_table)).pack(side=tk.LEFT, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
