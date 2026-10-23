
from abc import ABC, abstractmethod


class StockObserver(ABC):
    """Інтерфейс спостерігача за змінами складських залишків."""

    @abstractmethod
    def update(self, product_id, product_name, quantity, min_quantity):
        """Реагує на зміну залишку товару."""
        raise NotImplementedError


class StockSubject:
    """Повідомляє підписаних спостерігачів про зміну залишків."""

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, product_id, product_name, quantity, min_quantity):
        for observer in tuple(self._observers):
            observer.update(
                product_id,
                product_name,
                quantity,
                min_quantity,
            )


class LowStockObserver(StockObserver):
    """Створює сповіщення, коли запас досягає мінімального рівня."""

    def __init__(self, notification_service):
        self.notification_service = notification_service

    def update(self, product_id, product_name, quantity, min_quantity):
        if quantity <= min_quantity:
            self.notification_service.create_low_stock_notification(
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                min_quantity=min_quantity,
            )
