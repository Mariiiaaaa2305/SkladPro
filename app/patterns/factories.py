
from abc import ABC, abstractmethod


class DocumentCreator(ABC):
    """Базовий клас фабричного методу для створення документів."""

    @abstractmethod
    def create_document(self, document_data):
        """Створює документ певного типу."""
        raise NotImplementedError


class InvoiceCreator(DocumentCreator):
    """Фабрика товарної накладної."""

    def create_document(self, document_data):
        document = dict(document_data)
        document["document_type"] = "invoice"
        return document


class ActCreator(DocumentCreator):
    """Фабрика акта."""

    def create_document(self, document_data):
        document = dict(document_data)
        document["document_type"] = "act"
        return document


class DocumentFactory:
    """Вибирає фабрику відповідно до типу документа."""

    _creators = {
        "invoice": InvoiceCreator,
        "act": ActCreator,
    }

    @classmethod
    def get_creator(cls, document_type):
        creator_class = cls._creators.get(document_type)

        if creator_class is None:
            raise ValueError(
                "Невідомий тип документа. Дозволено: invoice, act."
            )

        return creator_class()
