
from app.extensions import get_db_connection
from app.models.stock_movement import StockMovement


class MovementRepository:
    """Запити до бази даних для історії складських операцій."""

    def get_all(self, limit=100, product_id=None, movement_type=None):
        """Повертає історію операцій із необов'язковими фільтрами."""
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 1000
        ):
            raise ValueError("Ліміт має бути від 1 до 1000.")

        conditions = []
        params = []

        if product_id is not None:
            if (
                not isinstance(product_id, int)
                or isinstance(product_id, bool)
                or product_id <= 0
            ):
                raise ValueError("Некоректний ID товару.")

            conditions.append("sm.product_id = %s")
            params.append(product_id)

        allowed_types = StockMovement.VALID_TYPES

        if movement_type is not None:
            if movement_type not in allowed_types:
                raise ValueError("Невідомий тип складської операції.")

            conditions.append("sm.movement_type = %s")
            params.append(movement_type)

        query = """
            SELECT
                sm.id,
                sm.product_id,
                p.name AS product_name,
                p.sku,
                sm.movement_type,
                sm.quantity,
                sm.unit_price,
                sm.notes,
                sm.created_by,
                sm.created_at
            FROM stock_movements sm
            JOIN products p ON p.id = sm.product_id
        """

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY sm.created_at DESC, sm.id DESC LIMIT %s"
        params.append(limit)

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, tuple(params))

            return [
                StockMovement.from_dict(row).to_dict()
                for row in cursor.fetchall()
            ]

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_by_id(self, movement_id):
        """Повертає одну операцію за ID або None."""
        if (
            not isinstance(movement_id, int)
            or isinstance(movement_id, bool)
            or movement_id <= 0
        ):
            raise ValueError("Некоректний ID складської операції.")

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    sm.id,
                    sm.product_id,
                    p.name AS product_name,
                    p.sku,
                    sm.movement_type,
                    sm.quantity,
                    sm.unit_price,
                    sm.notes,
                    sm.created_by,
                    sm.created_at
                FROM stock_movements sm
                JOIN products p ON p.id = sm.product_id
                WHERE sm.id = %s
                """,
                (movement_id,),
            )

            row = cursor.fetchone()
            return StockMovement.from_dict(row).to_dict() if row else None

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
