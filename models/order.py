from database import get_db_connection

class Order:
    @staticmethod
    def create_order(table_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (table_id) VALUES (?)",
                (table_id,))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_current_order(table_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM orders WHERE table_id = ? AND status = 'open'",
                (table_id,))
            return cursor.fetchone()

    @staticmethod
    def close_order(order_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE orders 
                SET status = 'closed', end_time = CURRENT_TIMESTAMP 
                WHERE id = ?""",
                (order_id,))
            conn.commit()