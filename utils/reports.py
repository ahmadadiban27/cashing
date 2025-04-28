from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton, 
                            QDateEdit, QLabel, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QAbstractTableModel, QDate, QModelIndex
from PyQt5.QtGui import QColor
from database import get_db_connection

class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("سیستم گزارش‌گیری")
        self.setMinimumSize(1200, 800)
        
        layout = QVBoxLayout()
        
        # بخش فیلتر تاریخ
        self.setup_date_filter(layout)
        
        # دکمه‌های گزارش
        self.setup_report_buttons(layout)
        
        # جدول نمایش نتایج
        self.setup_results_table(layout)
        
        # بخش جمع‌های پایانی
        self.setup_summary_section(layout)
        
        self.setLayout(layout)

    def setup_date_filter(self, layout):
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("بازه زمانی گزارش:"))
        date_layout.addWidget(QLabel("از:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("تا:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        layout.addLayout(date_layout)

    def setup_report_buttons(self, layout):
        btn_layout = QHBoxLayout()
        
        self.sales_report_btn = self.create_report_button("گزارش فروش", self.generate_sales_report)
        self.products_report_btn = self.create_report_button("گزارش محصولات", self.generate_products_report)
        self.tables_report_btn = self.create_report_button("گزارش میزها", self.generate_tables_report)
        
        btn_layout.addWidget(self.sales_report_btn)
        btn_layout.addWidget(self.products_report_btn)
        btn_layout.addWidget(self.tables_report_btn)
        
        layout.addLayout(btn_layout)

    def setup_results_table(self, layout):
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setStyleSheet("""
            QTableView {
                font-size: 12px;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #607D8B;
                color: white;
                padding: 5px;
            }
        """)
        layout.addWidget(self.table_view)

    def setup_summary_section(self, layout):
        self.summary_layout = QHBoxLayout()
        
        self.total_sales_label = QLabel("جمع کل فروش: ")
        self.total_sales_label.setStyleSheet("font-weight: bold; color: #2E7D32; font-size: 14px;")
        
        self.pending_sales_label = QLabel("جمع تسویه نشده: ")
        self.pending_sales_label.setStyleSheet("font-weight: bold; color: #D32F2F; font-size: 14px;")
        
        self.summary_layout.addWidget(self.total_sales_label)
        self.summary_layout.addWidget(self.pending_sales_label)
        self.summary_layout.addStretch()
        
        layout.addLayout(self.summary_layout)

    def create_report_button(self, text, callback):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #455A64;
                color: white;
                padding: 8px 15px;
                min-width: 120px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def generate_sales_report(self):
        try:
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # گزارش فروشهای تسویه شده
                cursor.execute("""
                    SELECT 
                        o.id as order_id,
                        t.number as table_number,
                        o.start_time,
                        o.total_amount,
                        GROUP_CONCAT(p.name || ' (' || oi.quantity || ')', ', ') as items
                    FROM orders o
                    JOIN tables t ON o.table_id = t.id
                    JOIN order_items oi ON o.id = oi.order_id
                    JOIN products p ON oi.product_id = p.id
                    WHERE date(o.start_time) BETWEEN ? AND ?
                    AND o.status = 'closed'
                    GROUP BY o.id
                    ORDER BY o.start_time
                """, (start, end))
                
                sales_data = cursor.fetchall()
                headers = ['شماره سفارش', 'میز', 'تاریخ', 'مبلغ کل', 'آیتم‌ها']
                
                # محاسبه جمع کل فروش
                cursor.execute("""
                    SELECT SUM(total_amount) as total_sales
                    FROM orders
                    WHERE date(start_time) BETWEEN ? AND ?
                    AND status = 'closed'
                """, (start, end))
                total_sales = cursor.fetchone()['total_sales'] or 0
                
                # محاسبه جمع تسویه نشده
                cursor.execute("""
                    SELECT SUM(total_amount) as pending_sales
                    FROM orders
                    WHERE date(start_time) BETWEEN ? AND ?
                    AND status = 'open'
                """, (start, end))
                pending_sales = cursor.fetchone()['pending_sales'] or 0
                
                # نمایش نتایج
                self.display_results(sales_data, headers)
                self.update_summary(total_sales, pending_sales)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش فروش:\n{str(e)}")

    def generate_products_report(self):
        try:
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        p.name as product_name,
                        SUM(oi.quantity) as total_quantity,
                        SUM(oi.quantity * oi.price_at_order) as total_sales,
                        p.production_location
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    JOIN orders o ON oi.order_id = o.id
                    WHERE date(o.start_time) BETWEEN ? AND ?
                    AND o.status = 'closed'
                    GROUP BY p.id
                    ORDER BY total_sales DESC
                """, (start, end))
                
                products_data = cursor.fetchall()
                headers = ['نام محصول', 'تعداد فروش', 'جمع فروش', 'محل تولید']
                
                # نمایش نتایج
                self.display_results(products_data, headers)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش محصولات:\n{str(e)}")

    def generate_tables_report(self):
        try:
            start = self.start_date.date().toString("yyyy-MM-dd")
            end = self.end_date.date().toString("yyyy-MM-dd")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        t.number as table_number,
                        COUNT(o.id) as order_count,
                        SUM(o.total_amount) as total_sales,
                        AVG(o.total_amount) as average_sale
                    FROM orders o
                    JOIN tables t ON o.table_id = t.id
                    WHERE date(o.start_time) BETWEEN ? AND ?
                    AND o.status = 'closed'
                    GROUP BY t.id
                    ORDER BY total_sales DESC
                """, (start, end))
                
                tables_data = cursor.fetchall()
                headers = ['شماره میز', 'تعداد سفارش', 'جمع فروش', 'میانگین فروش']
                
                # نمایش نتایج
                self.display_results(tables_data, headers)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش میزها:\n{str(e)}")

    def update_summary(self, total_sales, pending_sales):
        """به‌روزرسانی بخش جمع‌های پایانی"""
        self.total_sales_label.setText(f"جمع کل فروش: {total_sales:,} تومان")
        self.pending_sales_label.setText(f"جمع تسویه نشده: {pending_sales:,} تومان")

    def display_results(self, data, headers):
        model = ReportTableModel(data, headers)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()

class ReportTableModel(QAbstractTableModel):
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.BackgroundRole and index.column() in [2, 3]:  # رنگ برای ستون‌های مالی
            return QColor(220, 255, 220)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None