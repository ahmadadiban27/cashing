from database import get_db_connection

class Product:
    @staticmethod
    def create_product(name, category_id, price, production_location):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO products 
                (name, category_id, price, production_location) 
                VALUES (?, ?, ?, ?)""",
                (name, category_id, price, production_location))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_products_by_category(category_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE category_id = ? ORDER BY name",
                (category_id,))
            return cursor.fetchall()

    @staticmethod
    def update_product(product_id, name, price, production_location):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE products 
                SET name = ?, price = ?, production_location = ? 
                WHERE id = ?""",
                (name, price, production_location, product_id))
            conn.commit()