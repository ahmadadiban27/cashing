import sys
import os
from PyQt5.QtWidgets import QApplication
from auth import LoginWindow
from database import initialize_database

def main():
    # ایجاد دایرکتوری‌های لازم
    os.makedirs('assets/images', exist_ok=True)
    
    # مقداردهی اولیه دیتابیس
    initialize_database()
    
    app = QApplication(sys.argv)
    
    # ایجاد پنجره ورود
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()