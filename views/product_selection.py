from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                            QDialogButtonBox, QInputDialog, QListWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt
from database import get_db_connection  # اضافه کردن این import

class ProductSelectionWindow(QWidget):
    product_added = pyqtSignal()
    
    def __init__(self, table_id):
        super().__init__()
        self.table_id = table_id
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """تنظیمات رابط کاربری پنجره انتخاب محصول"""
        self.setWindowTitle("انتخاب محصول")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        self.product_list = QListWidget()
        self.product_list.itemDoubleClicked.connect(self.add_selected_product)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.add_selected_product)
        buttons.rejected.connect(self.close)
        
        layout.addWidget(self.product_list)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def load_products(self):
        """بارگذاری لیست محصولات از دیتابیس"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.price, c.name as category
                FROM products p
                JOIN categories c ON p.category_id = c.id
                ORDER BY c.display_order, p.name
            """)
            
            for product in cursor.fetchall():
                item_text = (
                    f"{product['category']} - {product['name']}\n"
                    f"{product['price']:,} تومان"
                )
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, product['id'])
                self.product_list.addItem(item)

    def add_selected_product(self):
        """افزودن محصول انتخاب شده به سفارش"""
        current_item = self.product_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "خطا", "لطفاً یک محصول را انتخاب کنید")
            return
            
        product_id = current_item.data(Qt.UserRole)
        quantity, ok = QInputDialog.getInt(
            self, "تعداد", "تعداد را وارد کنید:", 1, 1, 100, 1
        )
        
        if ok and quantity > 0:
            self.save_order_item(product_id, quantity)
            self.product_added.emit()
            self.close()

    def save_order_item(self, product_id, quantity):
        """ذخیره آیتم سفارش در دیتابیس"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # دریافت اطلاعات محصول
            cursor.execute(
                "SELECT name, price, production_location FROM products WHERE id = ?",
                (product_id,)
            )
            product = cursor.fetchone()
            
            # دریافت یا ایجاد سفارش
            cursor.execute(
                "SELECT id FROM orders WHERE table_id = ? AND status = 'open'",
                (self.table_id,)
            )
            order = cursor.fetchone()
            
            if order:
                # افزودن به سفارش موجود
                cursor.execute(
                    """INSERT INTO order_items 
                    (order_id, product_id, quantity, price_at_order, production_location)
                    VALUES (?, ?, ?, ?, ?)""",
                    (order['id'], product_id, quantity, product['price'], product['production_location'])
                )
                
                # محاسبه جمع کل
                cursor.execute(
                    "SELECT SUM(quantity * price_at_order) AS total FROM order_items WHERE order_id = ?",
                    (order['id'],)
                )
                total = cursor.fetchone()['total'] or 0
                
                # بروزرسانی جمع کل سفارش
                cursor.execute(
                    "UPDATE orders SET total_amount = ? WHERE id = ?",
                    (total, order['id'])
                )
                
                conn.commit()