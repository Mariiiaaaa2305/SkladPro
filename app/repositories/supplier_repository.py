
from app.extensions import get_db_connection
from app.models.supplier import Supplier


class SupplierRepository:
    """Репозиторій для роботи з постачальниками."""

    def get_all(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, contact_person, phone,
                       email, address, created_at
                FROM suppliers
                ORDER BY name ASC
            """)

            rows = cursor.fetchall()
            return [
                Supplier.from_dict(row).to_dict()
                for row in rows
            ]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_by_id(self, supplier_id):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, contact_person, phone,
                       email, address, created_at
                FROM suppliers
                WHERE id = %s
            """, (supplier_id,))

            row = cursor.fetchone()
            return Supplier.from_dict(row).to_dict() if row else None

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def create(self, data):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO suppliers (
                    name, contact_person, phone, email, address
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["name"],
                data.get("contact_person") or None,
                data.get("phone") or None,
                data.get("email") or None,
                data.get("address") or None,
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

    def update(self, supplier_id, data):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE suppliers
                SET name = %s,
                    contact_person = %s,
                    phone = %s,
                    email = %s,
                    address = %s
                WHERE id = %s
            """, (
                data["name"],
                data.get("contact_person") or None,
                data.get("phone") or None,
                data.get("email") or None,
                data.get("address") or None,
                supplier_id,
            ))

            cursor.execute(
                "SELECT id FROM suppliers WHERE id = %s",
                (supplier_id,),
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

    def delete(self, supplier_id):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM suppliers WHERE id = %s",
                (supplier_id,),
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
