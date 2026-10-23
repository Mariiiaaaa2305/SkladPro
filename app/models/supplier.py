
class Supplier:
    """Модель постачальника."""

    def __init__(
        self,
        id,
        name,
        contact_person=None,
        phone=None,
        email=None,
        address=None,
        created_at=None,
    ):
        self.id = id
        self.name = name
        self.contact_person = contact_person
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data):
        """Створює модель із рядка БД."""
        if data is None:
            return None
        return cls(**data)

    def to_dict(self):
        """Повертає дані у форматі словника."""
        return {
            "id": self.id,
            "name": self.name,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at,
        }
