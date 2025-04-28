from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from database import get_db_connection
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    login_success = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود به سیستم فروش رستوران")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.title_label = QLabel("سیستم فروش رستوران")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.username_label = QLabel("نام کاربری:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری را وارد کنید")
        
        self.password_label = QLabel("رمز عبور:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("ورود")
        self.login_button.clicked.connect(self.authenticate)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
        
    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            )
            user = cursor.fetchone()
            
            if user:
                self.login_success.emit()
                from views.main_window import MainWindow
                self.main_window = MainWindow()
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است")