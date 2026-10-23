
import pytest

from app.patterns.strategies import (
    ReceiptStrategy,
    ShipmentStrategy,
    WriteOffStrategy,
    StockMovementStrategyFactory,
)


def test_receipt_increases_stock():
    strategy = ReceiptStrategy()

    assert strategy.calculate_new_quantity(10, 5) == 15


def test_shipment_decreases_stock():
    strategy = ShipmentStrategy()

    assert strategy.calculate_new_quantity(10, 4) == 6


def test_write_off_decreases_stock():
    strategy = WriteOffStrategy()

    assert strategy.calculate_new_quantity(10, 3) == 7


@pytest.mark.parametrize(
    "strategy",
    [
        ReceiptStrategy(),
        ShipmentStrategy(),
        WriteOffStrategy(),
    ],
)
@pytest.mark.parametrize("quantity", [0, -1])
def test_strategies_reject_non_positive_quantity(strategy, quantity):
    with pytest.raises(ValueError):
        strategy.calculate_new_quantity(10, quantity)


def test_shipment_rejects_insufficient_stock():
    strategy = ShipmentStrategy()

    with pytest.raises(ValueError, match="Недостатньо товару"):
        strategy.calculate_new_quantity(3, 5)


def test_write_off_rejects_insufficient_stock():
    strategy = WriteOffStrategy()

    with pytest.raises(ValueError, match="Недостатньо товару"):
        strategy.calculate_new_quantity(3, 5)


@pytest.mark.parametrize(
    ("movement_type", "expected_class"),
    [
        ("receipt", ReceiptStrategy),
        ("shipment", ShipmentStrategy),
        ("write_off", WriteOffStrategy),
    ],
)
def test_factory_returns_correct_strategy(movement_type, expected_class):
    strategy = StockMovementStrategyFactory.get_strategy(movement_type)

    assert isinstance(strategy, expected_class)


def test_factory_rejects_unknown_movement_type():
    with pytest.raises(ValueError, match="Невідомий тип"):
        StockMovementStrategyFactory.get_strategy("unknown")
