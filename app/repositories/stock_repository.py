
from decimal import Decimal, InvalidOperation

from app.extensions import get_db_connection
from app.patterns.strategies import StockMovementStrategyFactory


class StockRepository:
    """Репозиторій для створення складських операцій і зміни залишків."""

    def create_movement(
        self,
        product_id,
        movement_type,
        quantity,
        unit_price,
        notes=None,
        created_by=None,
    ):
        """Атомарно записує операцію та оновлює залишок товару."""
        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or product_id <= 0
        ):
            raise ValueError("Некоректний ID товару.")

        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            raise ValueError(
                "Кількість має бути цілим числом більше за нуль."
            )

        try:
            unit_price = Decimal(str(unit_price))

            if (
                not unit_price.is_finite()
                or unit_price < 0
                or unit_price > Decimal("9999999999.99")
                or unit_price.as_tuple().exponent < -2
            ):
                raise InvalidOperation

            unit_price = unit_price.quantize(Decimal("0.01"))

        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(
                "Некоректна ціна складської операції."
            ) from None

        strategy = StockMovementStrategyFactory.get_strategy(movement_type)

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id, quantity
                FROM products
                WHERE id = %s
                FOR UPDATE
                """,
                (product_id,),
            )
            product = cursor.fetchone()

            if product is None:
                raise ValueError("Товар не знайдено.")

            new_quantity = strategy.calculate_new_quantity(
                product["quantity"],
                quantity,
            )

            cursor.execute(
                """
                INSERT INTO stock_movements (
                    product_id,
                    movement_type,
                    quantity,
                    unit_price,
                    notes,
                    created_by
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    product_id,
                    movement_type,
                    quantity,
                    unit_price,
                    notes,
                    created_by,
                ),
            )
            movement_id = cursor.lastrowid

            cursor.execute(
                "UPDATE products SET quantity = %s WHERE id = %s",
                (new_quantity, product_id),
            )

            connection.commit()
            return movement_id

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
