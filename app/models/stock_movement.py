class StockMovement:
    """Модель руху товару на складі."""

    VALID_TYPES = {"receipt", "shipment", "write_off"}

    def __init__(
        self,
        id,
        product_id,
        movement_type,
        quantity,
        unit_price=0,
        notes=None,
        created_by=None,
        created_at=None,
        product_name=None,
        sku=None,
    ):
        if movement_type not in self.VALID_TYPES:
            raise ValueError("Невідомий тип складської операції.")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Кількість має бути додатним цілим числом.")

        self.id = id
        self.product_id = product_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.unit_price = unit_price
        self.notes = notes
        self.created_by = created_by
        self.created_at = created_at
        self.product_name = product_name
        self.sku = sku

    @classmethod
    def from_dict(cls, data):
        return cls(**data) if data is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "movement_type": self.movement_type,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "product_name": self.product_name,
            "sku": self.sku,
        }
