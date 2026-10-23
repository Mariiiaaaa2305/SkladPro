from abc import ABC, abstractmethod


class StockMovementCommand(ABC):
    """Базовий клас команди складської операції."""

    def __init__(
        self,
        inventory_service,
        product_id,
        quantity,
        unit_price,
        notes=None,
        created_by=None,
    ):
        self.inventory_service = inventory_service
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.notes = notes
        self.created_by = created_by

    @property
    @abstractmethod
    def movement_type(self):
        """Тип складської операції."""
        raise NotImplementedError

    def execute(self):
        """Виконує операцію через наявний сервіс."""
        return self.inventory_service.create_stock_movement(
            product_id=self.product_id,
            movement_type=self.movement_type,
            quantity=self.quantity,
            unit_price=self.unit_price,
            notes=self.notes,
            created_by=self.created_by,
        )


class ReceiptCommand(StockMovementCommand):
    """Команда оприбуткування товару."""

    @property
    def movement_type(self):
        return "receipt"


class ShipmentCommand(StockMovementCommand):
    """Команда відвантаження товару."""

    @property
    def movement_type(self):
        return "shipment"


class WriteOffCommand(StockMovementCommand):
    """Команда списання товару."""

    @property
    def movement_type(self):
        return "write_off"