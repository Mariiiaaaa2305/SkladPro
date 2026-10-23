
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    """Керує сповіщеннями про низькі складські залишки."""

    def __init__(self, repository=None):
        self.repository = repository or NotificationRepository()

    def create_low_stock_notification(
        self,
        product_id,
        product_name,
        quantity,
        min_quantity,
    ):
        """Створює сповіщення, якщо запас досяг мінімуму."""

        if quantity > min_quantity:
            return None

        message = (
            f"Низький залишок товару «{product_name}»: "
            f"{quantity} од. (мінімум: {min_quantity} од.)."
        )
        message = message[:255]

        return self.repository.create(product_id, message)

    def get_notifications(self, unread_only=False, limit=100):
        """Повертає останні сповіщення."""
        return self.repository.get_all(
            unread_only=unread_only,
            limit=limit,
        )

    def mark_as_read(self, notification_id):
        """Позначає сповіщення як прочитане."""
        return self.repository.mark_as_read(notification_id)
