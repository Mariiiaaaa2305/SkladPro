
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.report_service import ReportService


def make_service():
    repository = MagicMock()
    return ReportService(repository=repository), repository


def test_stock_balance_uses_start_of_next_day():
    service, repository = make_service()
    repository.get_stock_balance_rows.return_value = []

    service.get_stock_balance(date(2026, 1, 10))

    next_day = repository.get_stock_balance_rows.call_args.args[0]
    assert next_day == datetime(2026, 1, 11, 0, 0)


def test_stock_balance_calculates_quantity_and_value():
    service, repository = make_service()
    repository.get_stock_balance_rows.return_value = [
        {
            "id": 1,
            "name": "Товар",
            "sku": "SKU-001",
            "current_quantity": 20,
            "min_quantity": 5,
            "price": Decimal("12.50"),
            "movements_after_date": 7,
        }
    ]

    result = service.get_stock_balance(date(2026, 1, 10))

    assert result[0]["quantity_at_date"] == 13
    assert result[0]["value_at_date"] == Decimal("162.50")


def test_stock_movements_filters_by_date_product_and_type():
    service, repository = make_service()
    repository.get_stock_movement_rows.return_value = []

    result = service.get_stock_movements(
        date_from="2026-01-01",
        date_to="2026-01-10",
        product_id="5",
        movement_type="receipt",
    )

    assert result == []

    repository.get_stock_movement_rows.assert_called_once_with(
        date_from=datetime(2026, 1, 1, 0, 0),
        date_to=datetime(2026, 1, 11, 0, 0),
        product_id=5,
        movement_type="receipt",
    )


@pytest.mark.parametrize("product_id", ["abc", "0", "-2"])
def test_stock_movements_rejects_invalid_product_id(product_id):
    service, repository = make_service()

    with pytest.raises(ValueError):
        service.get_stock_movements(product_id=product_id)

    repository.get_stock_movement_rows.assert_not_called()


def test_stock_movements_rejects_invalid_movement_type():
    service, repository = make_service()

    with pytest.raises(ValueError):
        service.get_stock_movements(movement_type="unknown")

    repository.get_stock_movement_rows.assert_not_called()


def test_stock_valuation_calculates_total():
    service, repository = make_service()
    repository.get_stock_valuation_rows.return_value = [
        {"id": 1, "total_value": Decimal("10.50")},
        {"id": 2, "total_value": Decimal("20.25")},
    ]

    report = service.get_stock_valuation()

    assert report["total_value"] == Decimal("30.75")
    assert len(report["items"]) == 2
