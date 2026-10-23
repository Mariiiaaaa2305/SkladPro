class Document:
    """Модель накладної або акта."""

    VALID_TYPES = {"invoice", "act"}

    def __init__(
        self,
        id,
        document_number,
        document_type,
        contractor_id=None,
        supplier_id=None,
        created_by=None,
        total_amount=0,
        notes=None,
        created_at=None,
        items=None,
    ):
        if document_type not in self.VALID_TYPES:
            raise ValueError("Невідомий тип документа.")

        self.id = id
        self.document_number = document_number
        self.document_type = document_type
        self.contractor_id = contractor_id
        self.supplier_id = supplier_id
        self.created_by = created_by
        self.total_amount = total_amount
        self.notes = notes
        self.created_at = created_at
        self.items = items or []

    @classmethod
    def from_dict(cls, data):
        return cls(**data) if data is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "document_number": self.document_number,
            "document_type": self.document_type,
            "contractor_id": self.contractor_id,
            "supplier_id": self.supplier_id,
            "created_by": self.created_by,
            "total_amount": self.total_amount,
            "notes": self.notes,
            "created_at": self.created_at,
            "items": self.items,
        }
