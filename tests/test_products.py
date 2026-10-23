
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.services.inventory_service import InventoryService


@pytest.fixture
def service():
    with (
        patch("app.services.inventory_service.ProductRepository") as products,
        patch("app.services.inventory_service.StockRepository"),
        patch("app.services.inventory_service.MovementRepository"),
        patch("app.services.inventory_service.NotificationService"),
    ):
        instance = InventoryService()
        instance.product_repository = products.return_value
        yield instance


def valid_product_form(**overrides):
    data = {
        "name": "Тестовий товар",
        "sku": "TEST-001",
        "description": "Опис товару",
        "quantity": "10",
        "min_quantity": "5",
        "price": "12.50",
        "supplier_id": "",
    }
    data.update(overrides)
    return data


def test_validate_product_data_normalizes_valid_values(service):
    data, errors = service.validate_product_data(valid_product_form())

    assert errors == []
    assert data["name"] == "Тестовий товар"
    assert data["sku"] == "TEST-001"
    assert data["quantity"] == 10
    assert data["min_quantity"] == 5
    assert data["price"] == Decimal("12.50")
    assert data["supplier_id"] is None


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"name": "   "}, "Вкажіть назву товару."),
        ({"sku": "   "}, "Вкажіть артикул товару."),
        ({"quantity": "-1"}, "Кількість має бути цілим числом"),
        (
            {"min_quantity": "-1"},
            "Мінімальний залишок має бути цілим числом",
        ),
        (
            {"price": "-1"},
            "Ціна має бути числом",
        ),
        (
            {"price": "12.345"},
            "Ціна має бути числом",
        ),
        (
            {"supplier_id": "abc"},
            "Оберіть коректного постачальника.",
        ),
    ],
)
def test_validate_product_data_rejects_invalid_values(
    service, overrides, expected_error
):
    _, errors = service.validate_product_data(
        valid_product_form(**overrides)
    )

    assert any(expected_error in error for error in errors)


def test_create_product_sets_initial_quantity_to_zero(service):
    service.product_repository.create.return_value = 7
    service.product_repository.get_by_id.return_value = None

    product_id, errors = service.create_product(valid_product_form())

    assert product_id == 7
    assert errors == []

    saved_data = service.product_repository.create.call_args.args[0]
    assert saved_data["quantity"] == 0
    assert saved_data["price"] == Decimal("12.50")


def test_create_product_returns_error_for_duplicate_sku(service):
    duplicate_error = Exception("Duplicate SKU")
    duplicate_error.errno = 1062
    service.product_repository.create.side_effect = duplicate_error

    product_id, errors = service.create_product(valid_product_form())

    assert product_id is False
    assert errors == ["Такий артикул уже існує."]


def test_create_product_does_not_save_invalid_data(service):
    product_id, errors = service.create_product(
        valid_product_form(name="")
    )

    assert product_id is False
    assert errors
    service.product_repository.create.assert_not_called()


def test_update_product_does_not_change_quantity(service):
    service.product_repository.update.return_value = True
    service.product_repository.get_by_id.return_value = None

    result, errors = service.update_product(
        7,
        valid_product_form(quantity="999"),
    )

    assert result is True
    assert errors == []

    updated_data = service.product_repository.update.call_args.args[1]
    assert "quantity" not in updated_data


def test_update_product_rejects_invalid_id(service):
    result, errors = service.update_product(
        0,
        valid_product_form(),
    )

    assert result is False
    assert errors == ["Некоректний ID товару."]
    service.product_repository.update.assert_not_called()


def test_update_product_returns_error_when_product_not_found(service):
    service.product_repository.update.return_value = False

    result, errors = service.update_product(
        7,
        valid_product_form(),
    )

    assert result is False
    assert errors == ["Товар не знайдено."]


def test_delete_product_calls_repository(service):
    service.product_repository.delete.return_value = True

    result = service.delete_product(7)

    assert result is True
    service.product_repository.delete.assert_called_once_with(7)


@pytest.mark.parametrize("product_id", [0, -1, True, "7", None])
def test_delete_product_rejects_invalid_id(service, product_id):
    with pytest.raises(ValueError, match="Некоректний ID товару"):
        service.delete_product(product_id)

    service.product_repository.delete.assert_not_called()


def test_get_product_delegates_to_repository(service):
    expected = {"id": 7, "name": "Тестовий товар"}
    service.product_repository.get_by_id.return_value = expected

    result = service.get_product(7)

    assert result == expected
    service.product_repository.get_by_id.assert_called_once_with(7)
