from database import get_db_connection

class Category:
    @staticmethod
    def create_category(name, display_order):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, display_order) VALUES (?, ?)",
                (name, display_order))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_all_categories():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY display_order")
            return cursor.fetchall()

    @staticmethod
    def update_category(category_id, name, display_order):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET name = ?, display_order = ? WHERE id = ?",
                (name, display_order, category_id))
            conn.commit()