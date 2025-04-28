from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QPushButton, QListWidget, QListWidgetItem, 
                            QLineEdit, QLabel, QMessageBox, QInputDialog,
                            QDoubleSpinBox, QComboBox)
from database import get_db_connection
from models.table import Table
from models.category import Category
from models.product import Product

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تنظیمات سیستم")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        
        # تب میزها
        self.tables_tab = QWidget()
        self.setup_tables_tab()
        self.tabs.addTab(self.tables_tab, "مدیریت میزها")
        
        # تب دسته‌بندی‌ها
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tabs.addTab(self.categories_tab, "دسته‌بندی‌ها")
        
        # تب محصولات
        self.products_tab = QWidget()
        self.setup_products_tab()
        self.tabs.addTab(self.products_tab, "محصولات")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def setup_tables_tab(self):
        layout = QVBoxLayout()
        
        # لیست میزها
        self.tables_list = QListWidget()
        self.load_tables()
        
        # دکمه‌های مدیریت
        btn_layout = QHBoxLayout()
        
        self.add_table_btn = QPushButton("افزودن میز")
        self.add_table_btn.clicked.connect(self.add_table)
        
        self.remove_table_btn = QPushButton("حذف میز")
        self.remove_table_btn.clicked.connect(self.remove_table)
        
        btn_layout.addWidget(self.add_table_btn)
        btn_layout.addWidget(self.remove_table_btn)
        
        layout.addWidget(self.tables_list)
        layout.addLayout(btn_layout)
        
        self.tables_tab.setLayout(layout)
    
    def load_tables(self):
        self.tables_list.clear()
        tables = Table.get_all_tables()
        
        for table in tables:
            item = QListWidgetItem(f"میز شماره {table['number']}")
            item.setData(1, table['id'])
            self.tables_list.addItem(item)
    
    def add_table(self):
        number, ok = QInputDialog.getInt(
            self, "افزودن میز", "شماره میز را وارد کنید:", 1, 1, 1000, 1
        )
        
        if ok:
            Table.create_table(number)
            self.load_tables()
    
    def remove_table(self):
        selected_items = self.tables_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "خطا", "لطفاً یک میز را انتخاب کنید")
            return
            
        item = selected_items[0]
        table_id = item.data(1)
        
        reply = QMessageBox.question(
            self, 'حذف میز', 
            'آیا از حذف این میز اطمینان دارید؟',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tables WHERE id = ?", (table_id,))
                conn.commit()
                self.load_tables()
    
    def setup_categories_tab(self):
        layout = QVBoxLayout()
        
        # لیست دسته‌بندی‌ها
        self.categories_list = QListWidget()
        self.load_categories()
        
        # فرم ویرایش
        form_layout = QVBoxLayout()
        
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("نام دسته‌بندی")
        
        self.category_order_input = QLineEdit()
        self.category_order_input.setPlaceholderText("ترتیب نمایش")
        
        btn_layout = QHBoxLayout()
        
        self.add_category_btn = QPushButton("افزودن")
        self.add_category_btn.clicked.connect(self.add_category)
        
        self.update_category_btn = QPushButton("بروزرسانی")
        self.update_category_btn.clicked.connect(self.update_category)
        
        btn_layout.addWidget(self.add_category_btn)
        btn_layout.addWidget(self.update_category_btn)
        
        form_layout.addWidget(QLabel("نام دسته‌بندی:"))
        form_layout.addWidget(self.category_name_input)
        form_layout.addWidget(QLabel("ترتیب نمایش:"))
        form_layout.addWidget(self.category_order_input)
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(self.categories_list)
        layout.addLayout(form_layout)
        
        self.categories_tab.setLayout(layout)
    
    def load_categories(self):
        self.categories_list.clear()
        categories = Category.get_all_categories()
        
        for category in categories:
            item = QListWidgetItem(f"{category['name']} (ترتیب: {category['display_order']})")
            item.setData(1, category['id'])
            self.categories_list.addItem(item)
    
    def add_category(self):
        name = self.category_name_input.text()
        order = self.category_order_input.text()
        
        if not name or not order:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
            
        try:
            order = int(order)
            Category.create_category(name, order)
            self.load_categories()
            self.category_name_input.clear()
            self.category_order_input.clear()
        except ValueError:
            QMessageBox.warning(self, "خطا", "ترتیب نمایش باید عدد باشد")
    
    def update_category(self):
        selected_items = self.categories_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "خطا", "لطفاً یک دسته‌بندی را انتخاب کنید")
            return
            
        item = selected_items[0]
        category_id = item.data(1)
        name = self.category_name_input.text()
        order = self.category_order_input.text()
        
        if not name or not order:
            QMessageBox.warning(self, "خطا", "لطفاً تمام فیلدها را پر کنید")
            return
            
        try:
            order = int(order)
            Category.update_category(category_id, name, order)
            self.load_categories()
            self.category_name_input.clear()
            self.category_order_input.clear()
        except ValueError:
            QMessageBox.warning(self, "خطا", "ترتیب نمایش باید عدد باشد")
    
    def setup_products_tab(self):
        layout = QVBoxLayout()
        
        # لیست محصولات
        self.products_list = QListWidget()
        
        # فیلتر دسته‌بندی
        self.category_filter = QComboBox()
        self.load_category_filter()
        self.category_filter.currentIndexChanged.connect(self.load_products)
        
        # فرم ویرایش
        form_layout = QVBoxLayout()
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("نام محصول")
        
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setPrefix("قیمت: ")
        self.product_price_input.setSuffix(" تومان")
        self.product_price_input.setMinimum(0)
        self.product_price_input.setMaximum(1000000)
        
        self.product_location_input = QComboBox()
        self.product_location_input.addItems(["آشپزخانه اصلی", "آشپزخانه سرد", "کافه", "سالادبار"])
        
        btn_layout = QHBoxLayout()
        
        self.add_product_btn = QPushButton("افزودن")
        self.add_product_btn.clicked.connect(self.add_product)
        
        self.update_product_btn = QPushButton("بروزرسانی")
        self.update_product_btn.clicked.connect(self.update_product)
        
        btn_layout.addWidget(self.add_product_btn)
        btn_layout.addWidget(self.update_product_btn)
        
        form_layout.addWidget(QLabel("دسته‌بندی:"))
        form_layout.addWidget(self.category_filter)
        form_layout.addWidget(QLabel("نام محصول:"))
        form_layout.addWidget(self.product_name_input)
        form_layout.addWidget(QLabel("قیمت:"))
        form_layout.addWidget(self.product_price_input)
        form_layout.addWidget(QLabel("محل تولید:"))
        form_layout.addWidget(self.product_location_input)
        form_layout.addLayout(btn_layout)
        
        layout.addWidget(self.products_list)
        layout.addLayout(form_layout)
        
        self.products_tab.setLayout(layout)
        self.load_products()
    
    def load_category_filter(self):
        self.category_filter.clear()
        categories = Category.get_all_categories()
        self.category_filter.addItem("همه دسته‌بندی‌ها", 0)
        
        for category in categories:
            self.category_filter.addItem(category['name'], category['id'])
    # در متد load_products تغییرات زیر را اعمال کنید:

    def load_products(self):
        """بارگذاری محصولات بر اساس دسته‌بندی انتخاب شده"""
        self.products_list.clear()
        category_id = self.category_filter.currentData()
        
        if category_id == 0:  # همه دسته‌بندی‌ها
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.name, p.price, p.production_location, c.name as category_name
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY c.display_order, p.name
                """)
                # تبدیل به لیست معمولی
                products = [dict(row) for row in cursor.fetchall()]
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.id, p.name, p.price, p.production_location
                    FROM products p
                    WHERE p.category_id = ?
                    ORDER BY p.name
                """, (category_id,))
                products = [dict(row) for row in cursor.fetchall()]
                
                # اضافه کردن نام دسته‌بندی
                cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
                category_name = cursor.fetchone()['name']
                
                for product in products:
                    product['category_name'] = category_name
        
        # نمایش محصولات
        for product in products:
            item_text = (
                f"{product['name']} - {product['category_name']}\n"
                f"قیمت: {product['price']:,} تومان - محل تولید: {product['production_location']}"
            )
            item = QListWidgetItem(item_text)
            item.setData(1, product['id'])
            self.products_list.addItem(item)
    
    def add_product(self):
        name = self.product_name_input.text()
        price = self.product_price_input.value()
        location = self.product_location_input.currentText()
        category_id = self.category_filter.currentData()
        
        if not name or category_id == 0:
            QMessageBox.warning(self, "خطا", "لطفاً نام محصول و دسته‌بندی را انتخاب کنید")
            return
            
        Product.create_product(name, category_id, price, location)
        self.load_products()
        self.product_name_input.clear()
        self.product_price_input.setValue(0)
    
    def update_product(self):
        selected_items = self.products_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "خطا", "لطفاً یک محصول را انتخاب کنید")
            return
            
        item = selected_items[0]
        product_id = item.data(1)
        name = self.product_name_input.text()
        price = self.product_price_input.value()
        location = self.product_location_input.currentText()
        
        if not name:
            QMessageBox.warning(self, "خطا", "لطفاً نام محصول را وارد کنید")
            return
            
        Product.update_product(product_id, name, price, location)
        self.load_products()
        self.product_name_input.clear()
        self.product_price_input.setValue(0)