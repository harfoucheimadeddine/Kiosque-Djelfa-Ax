import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
import tkinter as tk
from modules.add_product_ui import add_product_window
from modules.scan_ui import scan_product_window

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("نظام المبيعات")
        self.setGeometry(200, 100, 900, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --- Totals section ---
        totals_layout = QHBoxLayout()
        self.label_today = QLabel("إجمالي اليوم: 0 د.ج")
        self.label_week = QLabel("إجمالي هذا الأسبوع: 0 د.ج")
        self.label_all_time = QLabel("إجمالي الكل: 0 د.ج")

        for label in [self.label_today, self.label_week, self.label_all_time]:
            label.setStyleSheet("font-size: 16px; font-weight: bold;")
            totals_layout.addWidget(label)

        main_layout.addLayout(totals_layout)

        # --- Current Sale Table ---
        self.sale_table = QTableWidget()
        self.sale_table.setColumnCount(4)
        self.sale_table.setHorizontalHeaderLabels(["المنتج", "السعر", "الكمية", "الإجمالي"])
        main_layout.addWidget(QLabel("القائمة الحالية للبيع"))
        main_layout.addWidget(self.sale_table)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("إضافة منتج")
        self.btn_remove = QPushButton("حذف منتج")
        self.btn_finish = QPushButton("إنهاء البيع")

        for btn in [self.btn_add, self.btn_remove, self.btn_finish]:
            btn.setStyleSheet("font-size: 14px; padding: 6px;")
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)

        # --- Stock Table ---
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels(["المنتج", "الفئة", "الحجم", "السعر", "الكمية"])
        main_layout.addWidget(QLabel("جدول المخزون"))
        main_layout.addWidget(self.stock_table)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main_menu():
    root = tk.Tk()
    root.title("نظام الكشك")
    root.geometry("400x300")

    tk.Button(root, text="➕ إضافة منتج", command=add_product_window).pack(pady=10)
    tk.Button(root, text="📷 مسح منتج", command=scan_product_window).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_menu()
