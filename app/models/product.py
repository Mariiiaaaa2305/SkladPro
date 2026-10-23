
class Product:
    """Модель товару складського обліку."""

    def __init__(
        self,
        id,
        name,
        sku,
        description=None,
        quantity=0,
        min_quantity=5,
        price=0,
        supplier_id=None,
        created_at=None,
        updated_at=None,
    ):
        self.id = id
        self.name = name
        self.sku = sku
        self.description = description
        self.quantity = quantity
        self.min_quantity = min_quantity
        self.price = price
        self.supplier_id = supplier_id
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, data):
        """Створює модель із рядка БД, отриманого як словник."""
        if data is None:
            return None
        return cls(**data)

    @property
    def is_low_stock(self):
        """Чи досягнуто порогу мінімального запасу."""
        return self.quantity <= self.min_quantity

    def to_dict(self):
        """Повертає дані у форматі, сумісному з поточним кодом."""
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "quantity": self.quantity,
            "min_quantity": self.min_quantity,
            "price": self.price,
            "supplier_id": self.supplier_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
