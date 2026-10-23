class Contractor:
    """Модель контрагента."""

    def __init__(
        self,
        id,
        name,
        contractor_type="customer",
        phone=None,
        email=None,
        address=None,
        created_at=None,
    ):
        self.id = id
        self.name = name
        self.contractor_type = contractor_type
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        return cls(**data) if data is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contractor_type": self.contractor_type,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at,
        }
