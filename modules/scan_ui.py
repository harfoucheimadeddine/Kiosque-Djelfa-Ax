import tkinter as tk
from tkinter import ttk, messagebox
from modules.db_utils import get_item_by_barcode, add_sale_item

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
    card.pack(fill="x", padx=15, pady=10)
    
    if title:
        title_frame = tk.Frame(card, bg='#ffffff')
        title_frame.pack(fill="x", padx=padding, pady=(padding, 10))
        title_label = tk.Label(title_frame, text=title, font=("Segoe UI", 14, "bold"), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(anchor="w")
    
    content_frame = tk.Frame(card, bg='#ffffff')
    content_frame.pack(fill="both", expand=True, padx=padding, pady=(0, padding))
    
    return content_frame

def scan_window(current_sale_table, sale_id, parent=None):
    """Create modern barcode scanning window"""
    def on_scan():
        barcode = barcode_var.get().strip()
        if not barcode:
            messagebox.showwarning("تنبيه", "الرجاء إدخال أو مسح الباركود")
            return
        
        item = get_item_by_barcode(barcode)
        win.destroy()
        
        if item:
            # Product found - show modern confirmation dialog
            def on_add(price=None):
                quantity = 1
                used_price = price if price is not None else item['price']
                add_sale_item(sale_id, item['id'], quantity, used_price)
                total = used_price * quantity
                current_sale_table.insert("", "end", values=(item['name'], used_price, quantity, total))
                messagebox.showinfo("تم", f"تمت إضافة المنتج '{item['name']}' إلى السلة")
            
            # Create modern confirmation window
            add_win = create_modal_window(parent or win, "تأكيد إضافة المنتج", 450, 350)
            
            # Header
            header_frame = tk.Frame(add_win, bg='#f8fafc')
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(header_frame, text="✅ تم العثور على المنتج", 
                    font=("Segoe UI", 16, "bold"), bg='#f8fafc', fg='#10b981').pack()
            
            # Product info card
            info_card = create_modern_card(add_win, "معلومات المنتج")
            
            tk.Label(info_card, text=f"المنتج: {item['name']}", font=("Segoe UI", 12, "bold"), 
                    bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
            tk.Label(info_card, text=f"السعر المخزن: {item['price']:.2f} د.ح", 
                    font=("Segoe UI", 11), bg='#ffffff', fg='#64748b').pack(anchor="w", pady=(0, 15))
            
            # Default price button
            tk.Button(info_card, text="✅ إضافة بالسعر المخزن", 
                     command=lambda: [on_add(), add_win.destroy()],
                     font=("Segoe UI", 11, "bold"), bg="#10b981", fg="white", 
                     relief='flat', padx=20, pady=10).pack(fill="x", pady=(0, 15))
            
            # Custom price section
            tk.Label(info_card, text="أو أدخل سعر مخصص:", font=("Segoe UI", 11, "bold"), 
                    bg='#ffffff', fg='#1e293b').pack(anchor="w", pady=(0, 5))
            
            price_frame = tk.Frame(info_card, bg='#ffffff')
            price_frame.pack(fill="x", pady=(0, 15))
            
            price_var = tk.DoubleVar(value=item['price'])
            price_entry = tk.Entry(price_frame, textvariable=price_var, font=("Segoe UI", 11), 
                                  relief='solid', bd=1, width=15)
            price_entry.pack(side="left", padx=(0, 10))
            
            tk.Label(price_frame, text="د.ح", font=("Segoe UI", 11), 
                    bg='#ffffff', fg='#64748b').pack(side="left")
            
            tk.Button(info_card, text="💰 إضافة بالسعر المخصص", 
                     command=lambda: [on_add(price_var.get()), add_win.destroy()],
                     font=("Segoe UI", 11, "bold"), bg="#2563eb", fg="white", 
                     relief='flat', padx=20, pady=10).pack(fill="x", pady=(0, 10))
            
            # Cancel button
            tk.Button(info_card, text="❌ إلغاء", command=add_win.destroy,
                     font=("Segoe UI", 11), bg="#ef4444", fg="white", 
                     relief='flat', padx=20, pady=8).pack(fill="x")
            
        else:
            # Product not found - show modern add to stock dialog
            def on_accept():
                add_win.destroy()
                from modules.add_product_ui import add_product_window
                add_product_window(parent or win, prefill_barcode=barcode)
                
            def on_decline():
                add_win.destroy()
                messagebox.showinfo("تنبيه", "الباركود غير موجود. لم تتم إضافة المنتج")
            
            # Create modern not found window
            add_win = create_modal_window(parent or win, "الباركود غير موجود", 450, 300)
            
            # Header
            header_frame = tk.Frame(add_win, bg='#f8fafc')
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            tk.Label(header_frame, text="❌ الباركود غير موجود", 
                    font=("Segoe UI", 16, "bold"), bg='#f8fafc', fg='#ef4444').pack()
            
            # Info card
            info_card = create_modern_card(add_win, "إضافة منتج جديد")
            
            tk.Label(info_card, text=f"الباركود '{barcode}' غير موجود في المخزون", 
                    font=("Segoe UI", 12), bg='#ffffff', fg='#1e293b').pack(pady=(0, 10))
            tk.Label(info_card, text="هل تريد إضافته إلى المخزون؟", 
                    font=("Segoe UI", 11), bg='#ffffff', fg='#64748b').pack(pady=(0, 20))
            
            # Buttons
            button_frame = tk.Frame(info_card, bg='#ffffff')
            button_frame.pack(fill="x")
            
            tk.Button(button_frame, text="✅ نعم، إضافة منتج جديد", command=on_accept,
                     font=("Segoe UI", 11, "bold"), bg="#10b981", fg="white", 
                     relief='flat', padx=20, pady=10).pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            tk.Button(button_frame, text="❌ لا، تجاهل", command=on_decline,
                     font=("Segoe UI", 11), bg="#ef4444", fg="white", 
                     relief='flat', padx=20, pady=10).pack(side="right", fill="x", expand=True, padx=(5, 0))

    # Create main scan window
    win = create_modal_window(parent, "مسح الباركود", 400, 250)
    
    # Header
    header_frame = tk.Frame(win, bg='#f8fafc')
    header_frame.pack(fill="x", padx=20, pady=(20, 10))
    
    tk.Label(header_frame, text="📷 مسح الباركود", font=("Segoe UI", 16, "bold"), 
            bg='#f8fafc', fg='#1e293b').pack()
    
    # Input card
    input_card = create_modern_card(win, "أدخل أو امسح الباركود")
    
    barcode_var = tk.StringVar()
    barcode_entry = tk.Entry(input_card, textvariable=barcode_var, font=("Segoe UI", 14), 
                            relief='solid', bd=1, justify='center')
    barcode_entry.pack(fill="x", pady=(0, 15))
    barcode_entry.focus()
    
    # Scan button
    tk.Button(input_card, text="🔍 تأكيد المسح", command=on_scan,
             font=("Segoe UI", 12, "bold"), bg="#2563eb", fg="white", 
             relief='flat', padx=30, pady=12).pack()
    
    # Bind Enter key
    barcode_entry.bind('<Return>', lambda e: on_scan())