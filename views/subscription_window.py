from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QDateEdit, QComboBox)
from PyQt5.QtCore import QDate
from database import get_db_connection

class SubscriptionWindow(QWidget):
    def __init__(self, customer_id=None):
        super().__init__()
        self.customer_id = customer_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("مدیریت اشتراک")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # فیلدهای اطلاعات مشتری
        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.credit_limit = QLineEdit()
        
        # فیلدهای اشتراک
        self.start_date = QDateEdit(QDate.currentDate())
        self.end_date = QDateEdit(QDate.currentDate().addMonths(1))
        self.total_amount = QLineEdit()
        self.payment_type = QComboBox()
        self.payment_type.addItems(["نقدی", "نسیه"])
        
        # دکمه‌ها
        btn_save = QPushButton("ذخیره اشتراک")
        btn_save.clicked.connect(self.save_subscription)
        
        # چیدمان
        layout.addWidget(QLabel("نام مشتری:"))
        layout.addWidget(self.customer_name)
        layout.addWidget(QLabel("شماره تلفن:"))
        layout.addWidget(self.customer_phone)
        layout.addWidget(QLabel("سقف اعتبار:"))
        layout.addWidget(self.credit_limit)
        layout.addWidget(QLabel("تاریخ شروع:"))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel("تاریخ پایان:"))
        layout.addWidget(self.end_date)
        layout.addWidget(QLabel("مبلغ کل:"))
        layout.addWidget(self.total_amount)
        layout.addWidget(QLabel("نوع پرداخت:"))
        layout.addWidget(self.payment_type)
        layout.addWidget(btn_save)
        
        self.setLayout(layout)
    
    def save_subscription(self):
        # ذخیره اطلاعات اشتراک در دیتابیس
        pass