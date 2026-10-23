
from decimal import Decimal, InvalidOperation

from app.repositories.product_repository import ProductRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.movement_repository import MovementRepository
from app.patterns.observers import StockSubject, LowStockObserver
from app.services.notification_service import NotificationService


class InventoryService:
    """Сервіс керування товарами та складськими операціями."""

    def __init__(self):
        self.product_repository = ProductRepository()
        self.stock_repository = StockRepository()
        self.movement_repository = MovementRepository()

        # Підключаємо Observer для сповіщень про низький залишок.
        self.stock_subject = StockSubject()
        self.notification_service = NotificationService()
        self.stock_subject.subscribe(
            LowStockObserver(self.notification_service)
        )

    def get_dashboard_statistics(self):
        """Повертає статистику для головної сторінки."""
        return {
            "total_products": self.product_repository.count_all(),
            "total_quantity": self.product_repository.get_total_quantity(),
            "low_stock_products": self.product_repository.get_low_stock(),
        }

    def get_low_stock_products(self):
        """Повертає товари з низьким залишком."""
        return self.product_repository.get_low_stock()

    def get_all_products(self):
        """Повертає всі товари."""
        return self.product_repository.get_all()

    def get_product(self, product_id):
        """Повертає товар за ID."""
        return self.product_repository.get_by_id(product_id)

    def get_stock_movements(
        self, limit=100, product_id=None, movement_type=None
    ):
        """Повертає історію складських операцій."""
        return self.movement_repository.get_all(
            limit=limit,
            product_id=product_id,
            movement_type=movement_type,
        )

    def get_stock_movement(self, movement_id):
        """Повертає одну складську операцію."""
        return self.movement_repository.get_by_id(movement_id)

    def create_stock_movement(
        self,
        product_id,
        movement_type,
        quantity,
        unit_price,
        notes=None,
        created_by=None,
    ):
        """Створює складську операцію та перевіряє залишок."""
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

        movement_id = self.stock_repository.create_movement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            unit_price=unit_price,
            notes=notes,
            created_by=created_by,
        )

        product = self.product_repository.get_by_id(product_id)

        if product is not None:
            self._notify_stock_status(product)

        return movement_id

    def _notify_stock_status(self, product):
        """Передає актуальний залишок спостерігачам."""
        self.stock_subject.notify(
            product_id=product["id"],
            product_name=product["name"],
            quantity=product["quantity"],
            min_quantity=product["min_quantity"],
        )

    def validate_product_data(self, form):
        """Перевіряє та нормалізує дані форми товару."""
        errors = []

        name = form.get("name", "").strip()
        sku = form.get("sku", "").strip()
        description = form.get("description", "").strip()

        if not name:
            errors.append("Вкажіть назву товару.")
        elif len(name) > 150:
            errors.append(
                "Назва товару не може перевищувати 150 символів."
            )

        if not sku:
            errors.append("Вкажіть артикул товару.")
        elif len(sku) > 80:
            errors.append(
                "Артикул не може перевищувати 80 символів."
            )

        # Перевіряємо поле, якщо воно передане.
        # Створення товару нижче примусово встановлює залишок у 0,
        # а під час редагування фактичний залишок не змінюється.
        quantity_raw = form.get("quantity", "0")

        try:
            quantity = int(quantity_raw)
            if quantity < 0:
                raise ValueError
        except (TypeError, ValueError):
            quantity = 0
            errors.append(
                "Кількість має бути цілим числом не менше нуля."
            )

        try:
            min_quantity = int(form.get("min_quantity", "5"))
            if min_quantity < 0:
                raise ValueError
        except (TypeError, ValueError):
            min_quantity = 5
            errors.append(
                "Мінімальний залишок має бути цілим числом не менше нуля."
            )

        try:
            price = Decimal(str(form.get("price", "")))

            if (
                not price.is_finite()
                or price < 0
                or price > Decimal("9999999999.99")
                or price.as_tuple().exponent < -2
            ):
                raise InvalidOperation

            price = price.quantize(Decimal("0.01"))

        except (InvalidOperation, TypeError, ValueError):
            price = Decimal("0.00")
            errors.append(
                "Ціна має бути числом від 0 до 9999999999.99 "
                "з не більше ніж двома знаками після коми."
            )

        supplier_raw = form.get("supplier_id", "").strip()

        if supplier_raw:
            try:
                supplier_id = int(supplier_raw)
                if supplier_id <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                supplier_id = None
                errors.append("Оберіть коректного постачальника.")
        else:
            supplier_id = None

        if len(description) > 65535:
            errors.append("Опис товару занадто довгий.")

        data = {
            "name": name,
            "sku": sku,
            "description": description,
            "quantity": quantity,
            "min_quantity": min_quantity,
            "price": price,
            "supplier_id": supplier_id,
        }

        return data, errors

    def create_product(self, form):
        """Створює товар із нульовим початковим залишком."""
        data, errors = self.validate_product_data(form)

        if errors:
            return False, errors

        # Початковий залишок не можна встановлювати через форму.
        data["quantity"] = 0

        try:
            product_id = self.product_repository.create(data)

            product = self.product_repository.get_by_id(product_id)
            if product is not None:
                self._notify_stock_status(product)

            return product_id, []

        except Exception as exc:
            if getattr(exc, "errno", None) == 1062:
                return False, ["Такий артикул уже існує."]

            if getattr(exc, "errno", None) == 1452:
                return False, [
                    "Обраного постачальника не знайдено."
                ]

            raise

    def update_product(self, product_id, form):
        """Оновлює дані товару без зміни фактичного залишку."""
        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or product_id <= 0
        ):
            return False, ["Некоректний ID товару."]

        data, errors = self.validate_product_data(form)

        if errors:
            return False, errors

        # Кількість не повинна передаватися в репозиторій при редагуванні.
        data.pop("quantity", None)

        try:
            updated = self.product_repository.update(product_id, data)

            if not updated:
                return False, ["Товар не знайдено."]

            product = self.product_repository.get_by_id(product_id)

            if product is not None:
                self._notify_stock_status(product)

            return True, []

        except Exception as exc:
            if getattr(exc, "errno", None) == 1062:
                return False, ["Такий артикул уже існує."]

            if getattr(exc, "errno", None) == 1452:
                return False, [
                    "Обраного постачальника не знайдено."
                ]

            raise

    def delete_product(self, product_id):
        """Видаляє товар, якщо це дозволяє база даних."""
        if (
            not isinstance(product_id, int)
            or isinstance(product_id, bool)
            or product_id <= 0
        ):
            raise ValueError("Некоректний ID товару.")

        return self.product_repository.delete(product_id)
