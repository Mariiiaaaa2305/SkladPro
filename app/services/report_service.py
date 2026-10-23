from datetime import date, datetime, time, timedelta
from decimal import Decimal

from app.models.stock_movement import StockMovement
from app.repositories.report_repository import ReportRepository


class ReportService:
    """Сервіс формування складських звітів."""

    def __init__(self, repository=None):
        self.repository = repository or ReportRepository()

    @staticmethod
    def _as_date(value):
        """Перетворює дату або рядок у date."""
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))

    def get_stock_balance(self, report_date=None):
        """Відновлює залишки на кінець вибраної дати."""
        target_date = self._as_date(report_date or date.today())
        next_day = datetime.combine(
            target_date + timedelta(days=1),
            time.min,
        )

        rows = self.repository.get_stock_balance_rows(next_day)

        for row in rows:
            quantity_at_date = (
                int(row["current_quantity"])
                - int(row["movements_after_date"])
            )
            price = Decimal(str(row["price"] or 0))
            row["quantity_at_date"] = quantity_at_date
            row["value_at_date"] = price * quantity_at_date

        return rows

    def get_stock_movements(
        self,
        date_from=None,
        date_to=None,
        product_id=None,
        movement_type=None,
    ):
        """Повертає рух товарів за обраними фільтрами."""
        start_datetime = None
        end_datetime = None
        parsed_product_id = None

        if date_from:
            start_datetime = datetime.combine(
                self._as_date(date_from),
                time.min,
            )

        if date_to:
            end_datetime = datetime.combine(
                self._as_date(date_to) + timedelta(days=1),
                time.min,
            )

        if product_id is not None and product_id != "":
            try:
                parsed_product_id = int(product_id)
            except (TypeError, ValueError):
                raise ValueError("Некоректний ID товару.") from None

            if parsed_product_id <= 0:
                raise ValueError("ID товару має бути додатним числом.")

        if movement_type:
            if movement_type not in StockMovement.VALID_TYPES:
                raise ValueError("Некоректний тип складської операції.")
        else:
            movement_type = None

        return self.repository.get_stock_movement_rows(
            date_from=start_datetime,
            date_to=end_datetime,
            product_id=parsed_product_id,
            movement_type=movement_type,
        )

    def get_stock_valuation(self):
        """Оцінює поточну вартість запасів за ціною товару."""
        rows = self.repository.get_stock_valuation_rows()

        total_value = sum(
            (
                Decimal(str(row["total_value"] or 0))
                for row in rows
            ),
            Decimal("0.00"),
        )

        return {
            "items": rows,
            "total_value": total_value,
        }
