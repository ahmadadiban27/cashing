from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument
from datetime import datetime

def print_receipt(order_data, include_prices=True):
    printer = QPrinter()
    print_dialog = QPrintDialog(printer)
    
    if print_dialog.exec_() == QPrintDialog.Accepted:
        doc = QTextDocument()
        
        # ساخت هدر HTML
        html = """
        <html>
        <body>
            <h1 align="center">رسید فروش</h1>
            <p align="center">رستوران نمونه</p>
            <hr>
            <p>شماره سفارش: {order_id}</p>
            <p>میز: {table_id}</p>
            <p>تاریخ: {date_time}</p>
            <hr>
            <table width="100%" border="1">
                <tr>
                    <th>نام محصول</th>
                    <th>تعداد</th>
        """.format(
            order_id=order_data['order_id'],
            table_id=order_data['table_id'],
            date_time=datetime.now().strftime('%Y/%m/%d %H:%M')
        )
        
        # اضافه کردن ستون‌های قیمت اگر نیاز باشد
        if include_prices:
            html += "<th>قیمت</th><th>جمع</th>"
        
        html += "</tr>"
        
        # اضافه کردن آیتم‌ها
        for item in order_data['items']:
            html += """
                <tr>
                    <td>{name}</td>
                    <td align="center">{quantity}</td>
            """.format(
                name=item['name'],
                quantity=item['quantity']
            )
            
            if include_prices:
                html += """
                    <td align="right">{price:,}</td>
                    <td align="right">{total:,}</td>
                """.format(
                    price=item['price'],
                    total=item['quantity'] * item['price']
                )
            
            html += "</tr>"
        
        # اضافه کردن جمع کل
        html += """
            </table>
            <hr>
        """
        
        if include_prices:
            html += """
            <p align="right">جمع کل: {total:,} تومان</p>
            """.format(total=order_data['total'])
        
        html += """
            <p align="center">با تشکر از خرید شما</p>
        </body>
        </html>
        """
        
        doc.setHtml(html)
        doc.print_(printer)

def print_kitchen_order(table_id, product_name, quantity, production_location, notes=""):
    """چاپ رسید آشپزخانه با فرمت بهبود یافته"""
    printer = QPrinter()
    print_dialog = QPrintDialog(printer)
    
    if print_dialog.exec_() == QPrintDialog.Accepted:
        doc = QTextDocument()
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; font-size: 14px; }}
                h1 {{ color: #d9534f; text-align: center; }}
                h2 {{ color: #5bc0de; text-align: center; }}
                .info {{ margin: 10px 0; }}
                .product {{ font-weight: bold; font-size: 16px; }}
                .notes {{ font-style: italic; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>سفارش آشپزخانه</h1>
            <h2>{production_location}</h2>
            <div class="info">
                <p><strong>میز:</strong> {table_id}</p>
                <p><strong>زمان:</strong> {datetime.now().strftime('%Y/%m/%d %H:%M')}</p>
            </div>
            <hr>
            <div class="product">{product_name} × {quantity}</div>
            <div class="notes">توضیحات: {notes}</div>
            <hr>
            <p style="text-align: center; margin-top: 20px;">لطفاً با دقت تهیه شود</p>
        </body>
        </html>
        """
        
        doc.setHtml(html)
        doc.print_(printer)
def print_report(title, headers, data):
    printer = QPrinter()
    print_dialog = QPrintDialog(printer)
    
    if print_dialog.exec_() == QPrintDialog.Accepted:
        doc = QTextDocument()
        
        html = f"""
        <html>
        <body>
            <h1 align="center">{title}</h1>
            <p align="center">{datetime.now().strftime('%Y/%m/%d %H:%M')}</p>
            <hr>
            <table width="100%" border="1">
                <tr>
                    {"".join(f"<th>{h}</th>" for h in headers)}
                </tr>
        """
        
        for row in data:
            html += "<tr>" + "".join(f"<td>{str(col)}</td>" for col in row) + "</tr>"
        
        html += """
            </table>
        </body>
        </html>
        """
        
        doc.setHtml(html)
        doc.print_(printer)