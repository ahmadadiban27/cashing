from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem,
                            QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from database import get_db_connection
from utils.printer import print_receipt, print_kitchen_order

class TableWindow(QWidget):
    order_closed = pyqtSignal()
    
    def __init__(self, table_id, mode='view'):
        super().__init__()
        self.table_id = table_id
        self.mode = mode  # 'new' یا 'view'
        self.order_id = None
        self.setup_ui()
        self.load_order_details()

    def setup_ui(self):
        """تنظیمات اولیه رابط کاربری"""
        self.setWindowTitle(f"میز {self.table_id}")
        self.setMinimumSize(800, 600)
        
        main_layout = QVBoxLayout()
        
        # بخش هدر
        self.setup_header(main_layout)
        
        # لیست سفارشات
        self.setup_order_list(main_layout)
        
        # دکمه‌های عملیاتی
        self.setup_action_buttons(main_layout)
        
        self.setLayout(main_layout)

    def setup_header(self, parent_layout):
        """ایجاد هدر با اطلاعات میز"""
        header = QHBoxLayout()
        
        self.table_label = QLabel(f"میز شماره {self.table_id}")
        self.table_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """)
        
        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setStyleSheet("""
            font-size: 18px;
            color: #2B8A3E;
        """)
        
        header.addWidget(self.table_label)
        header.addStretch()
        header.addWidget(self.total_label)
        
        parent_layout.addLayout(header)

    def setup_order_list(self, parent_layout):
        """ایجاد لیست سفارشات"""
        self.order_list = QListWidget()
        self.order_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                background-color: #fff;
                alternate-background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.order_list.setAlternatingRowColors(True)
        parent_layout.addWidget(self.order_list)

    def setup_action_buttons(self, parent_layout):
        """تنظیم دکمه‌های عملیاتی"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        if self.mode == 'view':
            # حالت مشاهده سفارش موجود
            self.print_kitchen_btn = self.create_action_button(
                "چاپ آشپزخانه", 
                "#FF9800", 
                self.print_kitchen_order
            )
            self.print_customer_btn = self.create_action_button(
                "چاپ فاکتور", 
                "#2196F3", 
                self.print_customer_receipt
            )
            self.edit_btn = self.create_action_button(
                "ویرایش", 
                "#FFC107", 
                self.enable_editing
            )
            self.checkout_btn = self.create_action_button(
                "تسویه", 
                "#F44336", 
                self.checkout_table
            )
            
            btn_layout.addWidget(self.print_kitchen_btn)
            btn_layout.addWidget(self.print_customer_btn)
            btn_layout.addWidget(self.edit_btn)
            btn_layout.addWidget(self.checkout_btn)
        else:
            # حالت سفارش جدید
            self.add_product_btn = self.create_action_button(
                "افزودن محصول", 
                "#4CAF50", 
                self.add_product
            )
            self.finish_order_btn = self.create_action_button(
                "اتمام سفارش", 
                "#009688", 
                self.finish_order
            )
            
            btn_layout.addWidget(self.add_product_btn)
            btn_layout.addWidget(self.finish_order_btn)
        
        parent_layout.addLayout(btn_layout)

    def create_action_button(self, text, color, callback):
        """ایجاد دکمه عملیاتی با استایل یکسان"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def darken_color(self, hex_color, factor=0.8):
        """تیره کردن رنگ برای افکت hover"""
        # ... پیاده‌سازی تبدیل رنگ HEX به RGB و تیره کردن ...

    def load_order_details(self):
        """بارگذاری سفارشات میز"""
        self.order_list.clear()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # دریافت سفارش فعال
            cursor.execute(
                "SELECT id, total_amount FROM orders WHERE table_id = ? AND status = 'open'",
                (self.table_id,)
            )
            order = cursor.fetchone()
            
            if order:
                self.order_id = order['id']
                self.total_label.setText(f"جمع کل: {order['total_amount']:,} تومان")
                
                # دریافت آیتم‌های سفارش
                cursor.execute("""
                    SELECT p.name, oi.quantity, oi.price_at_order
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = ?
                """, (self.order_id,))
                
                for item in cursor.fetchall():
                    item_text = (
                        f"{item['name']} - "
                        f"{item['quantity']} عدد - "
                        f"{item['price_at_order']:,} تومان"
                    )
                    QListWidgetItem(item_text, self.order_list)

    def add_product(self):
        """افزودن محصول جدید به سفارش"""
        # پیاده‌سازی پنجره انتخاب محصول
        from views.product_selection import ProductSelectionWindow
        self.product_window = ProductSelectionWindow(self.table_id)
        self.product_window.product_added.connect(self.load_order_details)
        self.product_window.show()

    def print_kitchen_order(self):
        """چاپ سفارش برای آشپزخانه با ذکر میز جدید"""
        if not self.order_id:
            return
            
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_id FROM orders WHERE id = ?", (self.order_id,))
            current_table_id = cursor.fetchone()['table_id']
            
            cursor.execute("SELECT number FROM tables WHERE id = ?", (current_table_id,))
            table_number = cursor.fetchone()['number']
            
            cursor.execute("""
                SELECT p.name, oi.quantity, oi.production_location
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            """, (self.order_id,))
            
            for item in cursor.fetchall():
                print_kitchen_order(
                    table_id=table_number,
                    product_name=item['name'],
                    quantity=item['quantity'],
                    production_location=item['production_location']
                )

    def print_customer_receipt(self):
        """چاپ فاکتور برای مشتری"""
        if not self.order_id:
            return
            
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.start_time, o.total_amount,
                       p.name, oi.quantity, oi.price_at_order
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.id = ?
            """, (self.order_id,))
            
            items = cursor.fetchall()
            if items:
                order_data = {
                    'table_id': self.table_id,
                    'order_id': items[0]['id'],
                    'date_time': items[0]['start_time'],
                    'items': [{
                        'name': item['name'],
                        'quantity': item['quantity'],
                        'price': item['price_at_order']
                    } for item in items],
                    'total': items[0]['total_amount']
                }
                print_receipt(order_data, include_prices=True)

    def enable_editing(self):
        """فعال کردن حالت ویرایش سفارش"""
        self.mode = 'edit'
        self.setup_action_buttons(self.layout())

    def finish_order(self):
        """اتمام سفارش جدید"""
        if not self.order_list.count():
            QMessageBox.warning(self, "خطا", "هیچ محصولی به سفارش اضافه نشده است")
            return
            
        self.close()

    def checkout_table(self):
        """تسویه حساب و آزاد کردن میز"""
        reply = QMessageBox.question(
            self, 'تسویه میز',
            'آیا از تسویه این میز اطمینان دارید؟',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # بستن سفارش
                cursor.execute("""
                    UPDATE orders 
                    SET status = 'closed', end_time = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (self.order_id,))
                
                # آزاد کردن میز
                cursor.execute("""
                    UPDATE tables 
                    SET status = 'empty', current_order_id = NULL 
                    WHERE id = ?
                """, (self.table_id,))
                
                conn.commit()
                self.order_closed.emit()
                self.close()
                    
    def setup_checkout_section(self):
        """بخش تسویه حساب با امکان پرداخت نسیه"""
        self.checkout_layout = QHBoxLayout()
        
        self.payment_type = QComboBox()
        self.payment_type.addItems(["نقدی", "نسیه"])
        self.payment_type.currentTextChanged.connect(self.update_payment_ui)
        
        self.customer_combo = QComboBox()
        self.load_customers()
        
        self.checkout_btn = QPushButton("تسویه حساب")
        self.checkout_btn.clicked.connect(self.process_checkout)
        
        self.checkout_layout.addWidget(QLabel("نوع پرداخت:"))
        self.checkout_layout.addWidget(self.payment_type)
        self.checkout_layout.addWidget(QLabel("مشتری:"))
        self.checkout_layout.addWidget(self.customer_combo)
        self.checkout_layout.addWidget(self.checkout_btn)
        
        self.layout().addLayout(self.checkout_layout)

    def update_payment_ui(self, payment_type):
        """به‌روزرسانی UI بر اساس نوع پرداخت"""
        if payment_type == "نسیه":
            self.checkout_btn.setText("ثبت نسیه")
        else:
            self.checkout_btn.setText("تسویه حساب")

    def load_customers(self):
        """بارگذاری لیست مشتریان دارای اعتبار"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name FROM customers 
                WHERE is_active = 1 AND credit_limit > balance
                ORDER BY name
            """)
            for customer in cursor.fetchall():
                self.customer_combo.addItem(customer['name'], customer['id'])

    def process_checkout(self):
        """پردازش تسویه حساب با در نظر گرفتن نوع پرداخت"""
        payment_type = self.payment_type.currentText()
        customer_id = self.customer_combo.currentData()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if payment_type == "نسیه":
                # بررسی اعتبار مشتری
                cursor.execute("""
                    SELECT credit_limit, balance FROM customers 
                    WHERE id = ?
                """, (customer_id,))
                customer = cursor.fetchone()
                
                if self.order_total > (customer['credit_limit'] - customer['balance']):
                    QMessageBox.warning(self, "خطا", "اعتبار مشتری کافی نیست")
                    return
                
                # به‌روزرسانی مانده حساب مشتری
                cursor.execute("""
                    UPDATE customers SET balance = balance + ? 
                    WHERE id = ?
                """, (self.order_total, customer_id))
            
            # ثبت پرداخت در دیتابیس
            cursor.execute("""
                UPDATE orders 
                SET status = 'closed', 
                    end_time = CURRENT_TIMESTAMP,
                    payment_type = ?,
                    customer_id = ?
                WHERE id = ?
            """, (payment_type, customer_id, self.order_id))
            
            conn.commit()
        
        self.order_closed.emit()
        self.close()