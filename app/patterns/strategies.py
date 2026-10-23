
from abc import ABC, abstractmethod


class StockMovementStrategy(ABC):
    """Спільний інтерфейс стратегій складських операцій."""

    @abstractmethod
    def calculate_new_quantity(self, current_quantity, quantity):
        """Обчислює залишок після операції."""
        raise NotImplementedError


class ReceiptStrategy(StockMovementStrategy):
    """Стратегія надходження товару."""

    def calculate_new_quantity(self, current_quantity, quantity):
        if quantity <= 0:
            raise ValueError("Кількість має бути більшою за нуль.")
        return current_quantity + quantity


class ShipmentStrategy(StockMovementStrategy):
    """Стратегія відвантаження товару."""

    def calculate_new_quantity(self, current_quantity, quantity):
        if quantity <= 0:
            raise ValueError("Кількість має бути більшою за нуль.")
        if current_quantity < quantity:
            raise ValueError("Недостатньо товару на складі.")
        return current_quantity - quantity


class WriteOffStrategy(StockMovementStrategy):
    """Стратегія списання товару."""

    def calculate_new_quantity(self, current_quantity, quantity):
        if quantity <= 0:
            raise ValueError("Кількість має бути більшою за нуль.")
        if current_quantity < quantity:
            raise ValueError("Недостатньо товару для списання.")
        return current_quantity - quantity


class StockMovementStrategyFactory:
    """Вибирає стратегію за типом складської операції."""

    _strategies = {
        "receipt": ReceiptStrategy,
        "shipment": ShipmentStrategy,
        "write_off": WriteOffStrategy,
    }

    @classmethod
    def get_strategy(cls, movement_type):
        strategy_class = cls._strategies.get(movement_type)
        if strategy_class is None:
            raise ValueError("Невідомий тип складської операції.")
        return strategy_class()
