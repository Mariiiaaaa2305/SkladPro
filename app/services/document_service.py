
from decimal import Decimal, InvalidOperation

from app.models.document import Document
from app.patterns.factories import DocumentFactory
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    """Бізнес-логіка створення та отримання документів."""

    def __init__(self, repository=None):
        self.repository = repository or DocumentRepository()

    def create_document(
        self,
        document_number,
        document_type,
        items,
        created_by=None,
        contractor_id=None,
        supplier_id=None,
        notes=None,
    ):
        if not isinstance(document_number, str) or not document_number.strip():
            raise ValueError("Номер документа обов'язковий.")

        document_number = document_number.strip()

        if len(document_number) > 50:
            raise ValueError("Номер документа не може перевищувати 50 символів.")

        if not isinstance(items, list) or not items:
            raise ValueError("Документ повинен містити хоча б один товар.")

        creator = DocumentFactory.get_creator(document_type)

        prepared_items = []
        total_amount = Decimal("0.00")

        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Позиція документа має бути словником.")

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if (
                not isinstance(product_id, int)
                or isinstance(product_id, bool)
                or product_id <= 0
            ):
                raise ValueError("ID товару має бути додатним цілим числом.")

            if (
                not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or quantity <= 0
            ):
                raise ValueError("Кількість товару має бути додатним цілим числом.")

            try:
                unit_price = Decimal(str(item.get("unit_price")))
            except (InvalidOperation, TypeError, ValueError):
                raise ValueError("Некоректна ціна товару.") from None

            if (
                not unit_price.is_finite()
                or unit_price < 0
                or unit_price > Decimal("9999999999.99")
                or unit_price.as_tuple().exponent < -2
            ):
                raise ValueError(
                    "Ціна має бути невід'ємною та містити не більше 2 знаків після коми."
                )

            total_amount += unit_price * quantity

            prepared_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
            })

        if total_amount > Decimal("9999999999.99"):
            raise ValueError("Загальна сума документа завелика.")

        document_data = creator.create_document({
            "document_number": document_number,
            "total_amount": total_amount,
            "created_by": created_by,
            "contractor_id": contractor_id,
            "supplier_id": supplier_id,
            "notes": notes,
        })

        document = Document.from_dict(document_data)
        document_data = document.to_dict()

        return self.repository.create(document_data, prepared_items)

    def get_documents(self, limit=100):
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 1000
        ):
            raise ValueError("Ліміт має бути від 1 до 1000.")

        rows = self.repository.get_all(limit=limit)

        return [
            Document.from_dict(row).to_dict()
            for row in rows
        ]

    def get_document(self, document_id):
        if (
            not isinstance(document_id, int)
            or isinstance(document_id, bool)
            or document_id <= 0
        ):
            raise ValueError("Некоректний ID документа.")

        row = self.repository.get_by_id(document_id)

        if row is None:
            return None

        items = row.pop("items", [])
        document = Document.from_dict(row).to_dict()
        document["items"] = items

        return document
