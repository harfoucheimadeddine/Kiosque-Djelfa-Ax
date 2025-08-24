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