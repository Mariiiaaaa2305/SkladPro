from app.extensions import get_db_connection


class ReportRepository:
    """Репозиторій SQL-запитів для складських звітів."""

    def get_stock_balance_rows(self, next_day):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.sku,
                    p.quantity AS current_quantity,
                    p.min_quantity,
                    p.price,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN sm.movement_type = 'receipt'
                                    THEN sm.quantity
                                WHEN sm.movement_type IN (
                                    'shipment', 'write_off'
                                )
                                    THEN -sm.quantity
                                ELSE 0
                            END
                        ),
                        0
                    ) AS movements_after_date
                FROM products p
                LEFT JOIN stock_movements sm
                    ON sm.product_id = p.id
                    AND sm.created_at >= %s
                GROUP BY
                    p.id,
                    p.name,
                    p.sku,
                    p.quantity,
                    p.min_quantity,
                    p.price
                ORDER BY p.name
                """,
                (next_day,),
            )
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_stock_movement_rows(
        self,
        date_from=None,
        date_to=None,
        product_id=None,
        movement_type=None,
    ):
        conditions = []
        params = []

        if date_from is not None:
            conditions.append("sm.created_at >= %s")
            params.append(date_from)

        if date_to is not None:
            conditions.append("sm.created_at < %s")
            params.append(date_to)

        if product_id is not None:
            conditions.append("sm.product_id = %s")
            params.append(product_id)

        if movement_type is not None:
            conditions.append("sm.movement_type = %s")
            params.append(movement_type)

        where_clause = (
            "WHERE " + " AND ".join(conditions)
            if conditions
            else ""
        )

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                f"""
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
                {where_clause}
                ORDER BY sm.created_at DESC, sm.id DESC
                """,
                tuple(params),
            )
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_stock_valuation_rows(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    p.id,
                    p.name,
                    p.sku,
                    p.quantity,
                    p.price,
                    p.quantity * p.price AS total_value
                FROM products p
                ORDER BY p.name
                """
            )
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
