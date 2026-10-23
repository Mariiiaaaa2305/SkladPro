
from app.extensions import get_db_connection


class DocumentRepository:
    """Репозиторій для роботи з документами та їхніми позиціями."""

    def create(self, document_data, items):
        """Зберігає документ і всі його позиції в одній транзакції."""

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()

            # Перевіряємо існування всіх товарів до створення документа.
            for item in items:
                cursor.execute(
                    "SELECT id FROM products WHERE id = %s",
                    (item["product_id"],),
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        f"Товар з ID {item['product_id']} не знайдений."
                    )

            cursor.execute(
                """
                INSERT INTO documents (
                    document_number, document_type, contractor_id,
                    supplier_id, created_by, total_amount, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    document_data["document_number"],
                    document_data["document_type"],
                    document_data["contractor_id"],
                    document_data["supplier_id"],
                    document_data["created_by"],
                    document_data["total_amount"],
                    document_data["notes"],
                ),
            )

            document_id = cursor.lastrowid

            for item in items:
                cursor.execute(
                    """
                    INSERT INTO document_items (
                        document_id, product_id, quantity, unit_price
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        document_id,
                        item["product_id"],
                        item["quantity"],
                        item["unit_price"],
                    ),
                )

            connection.commit()
            return document_id

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_all(self, limit=100):
        """Повертає список документів."""

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, document_number, document_type,
                       contractor_id, supplier_id, created_by,
                       total_amount, notes, created_at
                FROM documents
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_by_id(self, document_id):
        """Повертає документ разом із його позиціями або None."""

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id, document_number, document_type,
                       contractor_id, supplier_id, created_by,
                       total_amount, notes, created_at
                FROM documents
                WHERE id = %s
                """,
                (document_id,),
            )

            document = cursor.fetchone()

            if document is None:
                return None

            cursor.execute(
                """
                SELECT di.product_id, p.name AS product_name, p.sku,
                       di.quantity, di.unit_price,
                       di.quantity * di.unit_price AS line_total
                FROM document_items di
                JOIN products p ON p.id = di.product_id
                WHERE di.document_id = %s
                ORDER BY di.id
                """,
                (document_id,),
            )

            document["items"] = cursor.fetchall()
            return document

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
