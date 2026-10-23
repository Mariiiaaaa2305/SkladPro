from app.services.inventory_service import InventoryService
from app.patterns.commands import (
    ReceiptCommand,
    ShipmentCommand,
    WriteOffCommand,
)


class InventoryFacade:
    """Єдина точка доступу до складських операцій."""

    COMMANDS = {
        "receipt": ReceiptCommand,
        "shipment": ShipmentCommand,
        "write_off": WriteOffCommand,
    }

    def __init__(self, inventory_service=None):
        self.inventory_service = inventory_service or InventoryService()

    def create_movement(
        self,
        movement_type,
        product_id,
        quantity,
        unit_price,
        notes=None,
        created_by=None,
    ):
        """Створює відповідну команду та виконує її."""
        command_class = self.COMMANDS.get(movement_type)

        if command_class is None:
            raise ValueError(
                "Невідомий тип операції. "
                "Дозволено: receipt, shipment, write_off."
            )

        command = command_class(
            inventory_service=self.inventory_service,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            notes=notes,
            created_by=created_by,
        )

        return command.execute()

    def get_products(self):
        return self.inventory_service.get_all_products()

    def get_movements(self, limit=100):
        return self.inventory_service.get_stock_movements(limit=limit)