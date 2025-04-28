from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QScrollArea, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QTime
from PyQt5.QtGui import QColor
from database import get_db_connection
from views.table_window import TableWindow
from views.settings_window import SettingsWindow
from utils.reports import ReportWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.source_table = None
        self.moving_table = False
        self.setup_ui()
        self.setup_timer()
        self.load_tables()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_tables_display)
        self.timer.start(1000)  # به‌روزرسانی هر 1 ثانیه
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(1000)  # به‌روزرسانی هر 1 ثانیه
        self.update_timer.start()
    def setup_ui(self):
        """تنظیمات اولیه رابط کاربری"""
        self.setWindowTitle("سیستم فروش رستوران - صفحه اصلی")
        self.setMinimumSize(1024, 768)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # ایجاد هدر با دکمه‌ها
        header = QHBoxLayout()  # <-- این خط را اضافه کنید
        
        self.title_label = QLabel("وضعیت میزها")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # ایجاد دکمه‌ها
        self.move_table_btn = self.create_button("جابجایی میز", self.initiate_table_move)
        self.settings_btn = self.create_button("تنظیمات", self.open_settings)
        self.report_btn = self.create_button("گزارش‌گیری", self.open_reports)
        self.subscription_btn = self.create_button("اشتراک‌ها", self.open_subscription_window)  # <-- دکمه جدید
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.move_table_btn)
        header.addWidget(self.subscription_btn)  # <-- اضافه کردن دکمه اشتراک‌ها
        header.addWidget(self.report_btn)
        header.addWidget(self.settings_btn)
        
        main_layout.addLayout(header)
        
        # ایجاد ناحیه اسکرول برای میزها
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.tables_container = QWidget()
        self.tables_layout = QGridLayout()
        self.tables_layout.setSpacing(20)
        self.tables_container.setLayout(self.tables_layout)
        
        scroll.setWidget(self.tables_container)
        main_layout.addWidget(scroll)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
            
    def setup_header(self, parent_layout):
        """ایجاد هدر با دکمه‌های کنترلی"""
        header = QHBoxLayout()
        
        self.title_label = QLabel("وضعیت میزها")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        # ایجاد دکمه‌ها
        self.move_table_btn = self.create_button("جابجایی میز", self.initiate_table_move)
        self.settings_btn = self.create_button("تنظیمات", self.open_settings)
        self.report_btn = self.create_button("گزارش‌گیری", self.open_reports)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.move_table_btn)
        header.addWidget(self.report_btn)
        header.addWidget(self.settings_btn)
        
        parent_layout.addLayout(header)

    def setup_tables_area(self, parent_layout):
        """ایجاد ناحیه نمایش میزها"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.tables_container = QWidget()
        self.tables_layout = QGridLayout()
        self.tables_layout.setSpacing(20)
        self.tables_container.setLayout(self.tables_layout)
        
        scroll.setWidget(self.tables_container)
        parent_layout.addWidget(scroll)

    def setup_timer(self):
        """تنظیم تایمر برای به روزرسانی خودکار"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_tables_display)
        self.update_timer.start(1000)  # به روزرسانی هر 1 ثانیه

    def create_button(self, text, callback):
        """ایجاد دکمه با استایل یکسان"""
        btn = QPushButton(text)
        btn.setFixedSize(120, 40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #5D6D7E;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #6D7B8D;
            }
        """)
        btn.clicked.connect(callback)
        return btn
    def load_tables(self):
        """بارگذاری و نمایش میزها"""
        self.clear_tables_layout()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables ORDER BY number")
            tables = cursor.fetchall()
            
            self.display_tables(tables)

    def clear_tables_layout(self):
        """پاک کردن میزهای قبلی"""
        for i in reversed(range(self.tables_layout.count())): 
            self.tables_layout.itemAt(i).widget().setParent(None)

    def display_tables(self, tables):
        """نمایش میزها در صفحه"""
        row, col = 0, 0
        max_cols = 4
        
        for table in tables:
            table_widget = self.create_table_widget(table)
            self.tables_layout.addWidget(table_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_table_widget(self, table):
        """ایجاد ویجت میز با نمایش اطلاعات"""
        widget = QWidget()
        widget.setObjectName(f"table_{table['id']}")  # شناسه منحصر به فرد
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # دکمه میز
        table_btn = QPushButton(f"میز {table['number']}")
        table_btn.setObjectName("table_button")  # نام برای دسترسی آسان
        table_btn.setFixedSize(180, 60)
        table_btn.setStyleSheet(self.get_table_style(table['status']))
        table_btn.clicked.connect(lambda: self.handle_table_click(table))
        
        # لیبل اطلاعات سفارش
        info_label = QLabel()
        info_label.setObjectName("info_label")  # نام برای دسترسی آسان
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333;
                background-color: rgba(255, 255, 255, 150);
                border-radius: 5px;
                padding: 2px;
            }
        """)
        
        layout.addWidget(table_btn)
        layout.addWidget(info_label)
        
        # ذخیره داده‌های میز در ویجت
        widget.table_data = table
        
        # به‌روزرسانی اولیه اطلاعات
        self.update_table_info(widget)
        
        return widget

    def update_table_widget(self, widget):
        """به‌روزرسانی اطلاعات میز"""
        table = widget.table_data
        
        if table['status'] == 'occupied':
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT start_time, total_amount FROM orders WHERE id = ?",
                    (table['current_order_id'],)
                )
                order = cursor.fetchone()
                
                if order:
                    # نمایش مبلغ و زمان
                    elapsed_time = self.calculate_elapsed_time(order['start_time'])
                    widget.findChild(QLabel).setText(
                        f"{order['total_amount']:,} تومان\n"
                        f"{elapsed_time}"
                    )
                    widget.findChild(QLabel).show()

    def initiate_table_move(self):
        """شروع فرآیند جابجایی میز"""
        if not hasattr(self, 'source_table') or self.source_table is None:
            QMessageBox.information(self, "جابجایی میز", 
                "لطفاً ابتدا میز مبدأ (میز دارای سفارش) را انتخاب کنید")
            return

        # اطمینان از وجود سفارش در میز مبدأ
        if 'current_order_id' not in self.source_table or self.source_table['current_order_id'] is None:
            QMessageBox.warning(self, "خطا", "میز انتخاب شده فاقد سفارش فعال است")
            return

        reply = QMessageBox.question(
            self,
            "تأیید جابجایی",
            f"آیا می‌خواهید سفارش میز {self.source_table['number']} را به میز دیگری منتقل کنید؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.moving_table = True
            QMessageBox.information(
                self,
                "انتخاب میز مقصد",
                f"لطفاً میز مقصد (میز خالی) را برای انتقال سفارش از میز {self.source_table['number']} انتخاب کنید"
            )

    def get_table_style(self, status):
        """استایل دکمه میز بر اساس وضعیت"""
        if status == 'occupied':
            return """
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                }
            """
        return """
            QPushButton {
                background-color: #51CF66;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }
        """

    def update_tables_display(self):
        """به‌روزرسانی نمایش تمام میزها"""
        for i in range(self.tables_layout.count()):
            widget = self.tables_layout.itemAt(i).widget()
            if hasattr(widget, 'table_data'):
                # ایجاد یک کپی جدید از داده‌های میز
                table_data = dict(widget.table_data)
                
                # به‌روزرسانی داده‌های میز از دیتابیس
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT status, current_order_id FROM tables WHERE id=?",
                        (table_data['id'],)
                    )
                    updated_data = cursor.fetchone()
                    if updated_data:
                        table_data['status'] = updated_data['status']
                        table_data['current_order_id'] = updated_data['current_order_id']
                
                # به‌روزرسانی داده‌های ویجت
                widget.table_data = table_data
                
                # به‌روزرسانی نمایش
                self.update_table_info(widget)

    def update_table_info(self, widget):
        """به‌روزرسانی اطلاعات نمایشی یک میز خاص"""
        table = widget.table_data
        info_label = widget.findChild(QLabel, "info_label")
        
        if table['status'] == 'occupied':
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT start_time, total_amount FROM orders WHERE id = ?",
                    (table['current_order_id'],)
                )
                order = cursor.fetchone()
                
                if order:
                    try:
                        # تبدیل زمان شروع به QDateTime
                        start_time = QDateTime.fromString(order['start_time'], "yyyy-MM-dd HH:mm:ss")
                        if not start_time.isValid():
                            start_time = QDateTime.currentDateTime()
                        
                        # محاسبه زمان سپری شده
                        elapsed_sec = start_time.secsTo(QDateTime.currentDateTime())
                        elapsed_sec = max(0, elapsed_sec)  # جلوگیری از مقادیر منفی
                        
                        # قالب‌بندی زمان
                        hours = elapsed_sec // 3600
                        minutes = (elapsed_sec % 3600) // 60
                        seconds = elapsed_sec % 60
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                        
                        # نمایش اطلاعات
                        info_label.setText(
                            f"{order['total_amount']:,} تومان\n"
                            f"زمان: {time_str}"
                        )
                        info_label.show()
                        
                    except Exception as e:
                        print(f"خطا در به‌روزرسانی میز {table['number']}: {str(e)}")
                        info_label.hide()
        else:
            info_label.hide()

    def format_elapsed_time(self, seconds):
        """قالب‌بندی زمان به صورت HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def handle_table_click(self, table):
        """مدیریت کلیک روی میز با بررسی وضعیت"""
        if hasattr(self, 'moving_table') and self.moving_table:
            self.complete_table_move(table)
            return
        
        # ایجاد یک کپی قابل تغییر از داده‌های میز
        table_data = dict(table)
        
        # به‌روزرسانی وضعیت میز از دیتابیس
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT status, current_order_id FROM tables WHERE id=?",
                (table_data['id'],)
            )
            updated_status = cursor.fetchone()
            if updated_status:
                table_data['status'] = updated_status['status']
                table_data['current_order_id'] = updated_status['current_order_id']
        
        if table_data['status'] == 'empty':
            self.create_new_order(table_data)
        else:
            self.source_table = table_data
            self.open_table_window(table_data, mode='view')
        
    def move_table(self):
        """جابجایی سفارش بین میزها"""
        if not self.source_table:
            return
            
        self.moving_table = True
        QMessageBox.information(self, "جابجایی میز",
            f"حالا میز مقصد را انتخاب کنید (سفارش از میز {self.source_table['number']} منتقل می‌شود)")
        
            
    def create_new_order(self, table):
        """ایجاد سفارش جدید با به‌روزرسانی کامل وضعیت"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # زمان فعلی با فرمت صحیح
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            # ایجاد سفارش جدید
            cursor.execute(
                "INSERT INTO orders (table_id, start_time) VALUES (?, ?)",
                (table['id'], current_time)
            )
            order_id = cursor.lastrowid
            
            # به‌روزرسانی وضعیت میز در دیتابیس
            cursor.execute(
                "UPDATE tables SET status='occupied', current_order_id=? WHERE id=?",
                (order_id, table['id'])
            )
            conn.commit()
        
        # به‌روزرسانی فوری رابط کاربری
        self.refresh_table_widget(table['id'], order_id)
        
        self.open_table_window(table, mode='new')
    def refresh_table_widget(self, table_id, order_id):
        """به‌روزرسانی ویجت میز پس از تغییر وضعیت"""
        for i in range(self.tables_layout.count()):
            widget = self.tables_layout.itemAt(i).widget()
            if hasattr(widget, 'table_data') and widget.table_data['id'] == table_id:
                # به‌روزرسانی داده‌های ویجت
                widget.table_data['status'] = 'occupied'
                widget.table_data['current_order_id'] = order_id
                
                # به‌روزرسانی ظاهر میز
                table_btn = widget.findChild(QPushButton, "table_button")
                table_btn.setStyleSheet(self.get_table_style('occupied'))
                
                # نمایش اطلاعات سفارش
                self.update_table_info(widget)
                break    
    def open_table_window(self, table, mode):
        """باز کردن پنجره سفارشات میز"""
        self.table_window = TableWindow(table['id'], mode)
        self.table_window.order_closed.connect(self.load_tables)
        self.table_window.show()
        self.table_window.raise_()  # پنجره را به جلو بیاورد
    def open_settings(self):
        """باز کردن پنجره تنظیمات"""
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_reports(self):
        """باز کردن پنجره گزارش‌گیری"""
        self.report_window = ReportWindow()
        self.report_window.show()
    
    # def complete_table_move(self, target_table):
    #     """تکمیل فرآیند جابجایی میز"""
    #     if target_table['status'] != 'empty':
    #         QMessageBox.warning(self, "خطا", "میز مقصد باید خالی باشد")
    #         self.moving_table = False
    #         return
    def get_table_style(self, status):
        """استایل دینامیک برای میزها بر اساس وضعیت"""
        if status == 'occupied':
            return """
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    border: 2px solid #D32F2F;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #51CF66;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    border: 2px solid #388E3C;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
            """
    def complete_table_move(self, target_table):
        if not self.source_table:
            return
        if target_table['status'] != 'empty':
            QMessageBox.warning(self, "خطا", "میز مقصد باید خالی باشد")
            return
            
            
            
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # انتقال سفارش
            cursor.execute(
                "UPDATE orders SET table_id = ? WHERE id = ?",
                (target_table['id'], self.source_table['current_order_id'])
            )
            
            # به‌روزرسانی میز مبدأ
            cursor.execute(
                "UPDATE tables SET status = 'empty', current_order_id = NULL WHERE id = ?",
                (self.source_table['id'],)
            )
            
            # به‌روزرسانی میز مقصد
            cursor.execute(
                "UPDATE tables SET status = 'occupied', current_order_id = ? WHERE id = ?",
                (self.source_table['current_order_id'], target_table['id'])
            )
            
            conn.commit()
            
        self.moving_table = False
        self.load_tables()
        QMessageBox.information(self, "انجام شد", 
            f"سفارش با موفقیت از میز {self.source_table['number']} به میز {target_table['number']} منتقل شد")
        
    def open_subscription_window(self):
        from views.subscription_window import SubscriptionWindow
        self.sub_window = SubscriptionWindow()
        self.sub_window.show()