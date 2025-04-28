from database import get_db_connection

class Table:
    @staticmethod
    def create_table(number):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tables (number) VALUES (?)",
                (number,)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_all_tables():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables ORDER BY number")
            return cursor.fetchall()

    @staticmethod
    def get_table_by_id(table_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables WHERE id = ?", (table_id,))
            return cursor.fetchone()