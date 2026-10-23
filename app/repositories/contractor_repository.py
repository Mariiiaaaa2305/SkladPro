
from app.extensions import get_db_connection
from app.models.contractor import Contractor


class ContractorRepository:
    """Репозиторій для роботи з контрагентами."""

    def get_all(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, contractor_type, phone,
                       email, address, created_at
                FROM contractors
                ORDER BY name ASC
            """)

            return [
                Contractor.from_dict(row).to_dict()
                for row in cursor.fetchall()
            ]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_by_id(self, contractor_id):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, name, contractor_type, phone,
                       email, address, created_at
                FROM contractors
                WHERE id = %s
            """, (contractor_id,))

            row = cursor.fetchone()
            return Contractor.from_dict(row).to_dict() if row else None

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
