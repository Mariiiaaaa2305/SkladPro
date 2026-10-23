class Notification:
    """Модель сповіщення про стан складських запасів."""

    def __init__(
        self,
        id,
        product_id,
        message,
        is_read=False,
        created_at=None,
    ):
        self.id = id
        self.product_id = product_id
        self.message = message
        self.is_read = bool(is_read)
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        return cls(**data) if data is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }
