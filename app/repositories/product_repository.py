
from app.extensions import get_db_connection
from app.models.product import Product


class ProductRepository:
    """Репозиторій для роботи з товарами."""

    def get_all(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, sku, description, quantity,
                       min_quantity, price, supplier_id,
                       created_at, updated_at
                FROM products
                ORDER BY name ASC
            """)

            rows = cursor.fetchall()
            return [
                Product.from_dict(row).to_dict()
                for row in rows
            ]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_by_id(self, product_id):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, sku, description, quantity,
                       min_quantity, price, supplier_id,
                       created_at, updated_at
                FROM products
                WHERE id = %s
            """, (product_id,))

            row = cursor.fetchone()
            return Product.from_dict(row).to_dict() if row else None

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def count_all(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            return cursor.fetchone()[0]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_total_quantity(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT COALESCE(SUM(quantity), 0) FROM products"
            )
            return cursor.fetchone()[0]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_low_stock(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, sku, quantity, min_quantity
                FROM products
                WHERE quantity <= min_quantity
                ORDER BY quantity ASC, name ASC
            """)

            rows = cursor.fetchall()
            products = [
                Product.from_dict(row)
                for row in rows
            ]

            return [
                {
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "quantity": product.quantity,
                    "min_quantity": product.min_quantity,
                }
                for product in products
            ]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def create(self, data):
        """Створює товар із заданим сервісом початковим залишком."""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO products (
                    name, sku, description, quantity,
                    min_quantity, price, supplier_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["name"],
                data["sku"],
                data.get("description") or None,
                data["quantity"],
                data["min_quantity"],
                data["price"],
                data.get("supplier_id") or None,
            ))

            connection.commit()
            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def update(self, product_id, data):
        """Оновлює дані товару, не змінюючи quantity."""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE products
                SET name = %s,
                    sku = %s,
                    description = %s,
                    min_quantity = %s,
                    price = %s,
                    supplier_id = %s
                WHERE id = %s
            """, (
                data["name"],
                data["sku"],
                data.get("description") or None,
                data["min_quantity"],
                data["price"],
                data.get("supplier_id") or None,
                product_id,
            ))

            cursor.execute(
                "SELECT id FROM products WHERE id = %s",
                (product_id,),
            )
            exists = cursor.fetchone() is not None

            connection.commit()
            return exists

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def delete(self, product_id):
        """Видаляє товар, якщо це дозволяє база даних."""
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM products WHERE id = %s",
                (product_id,),
            )

            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
