
from decimal import Decimal
from unittest.mock import patch

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    with app.test_client() as test_client:
        yield test_client

# Перевірка авторизації
def test_products_api_requires_login(client):
    response = client.get("/api/products")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Необхідно увійти в систему."
    }


def test_single_product_api_requires_login(client):
    response = client.get("/api/products/999999")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "Необхідно увійти в систему."
    }


def test_create_product_requires_admin(client):
    response = client.post(
        "/api/products",
        json={
            "name": "Тестовий товар",
            "sku": "TEST-API-001",
            "quantity": 1,
            "min_quantity": 0,
            "price": "10.00",
            "supplier_id": "",
        },
    )

    assert response.status_code == 401


def test_update_product_requires_admin(client):
    response = client.patch(
        "/api/products/999999",
        json={"name": "Оновлена назва"},
    )

    assert response.status_code == 401


def test_delete_product_requires_admin(client):
    response = client.delete("/api/products/999999")

    assert response.status_code == 401


# Перевірка доступу звичайного користувача
def test_products_api_denies_regular_user_create(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "user"

    response = client.post(
        "/api/products",
        json={
            "name": "Тестовий товар",
            "sku": "TEST-API-002",
            "quantity": 1,
            "min_quantity": 0,
            "price": "10.00",
            "supplier_id": "",
        },
    )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Недостатньо прав."
    }


def test_products_api_denies_regular_user_update(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "user"

    response = client.patch(
        "/api/products/999999",
        json={"name": "Нова назва"},
    )

    assert response.status_code == 403


def test_products_api_denies_regular_user_delete(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "user"

    response = client.delete("/api/products/999999")

    assert response.status_code == 403



# Перевірка формату запитів
def test_create_product_rejects_non_object_json(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json=["не", "JSON-об'єкт"],
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Очікується JSON-об'єкт."
    }


def test_update_product_rejects_non_object_json(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.patch(
        "/api/products/1",
        json=["не", "JSON-об'єкт"],
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Очікується JSON-об'єкт."
    }


# Перевірка читання товарів
def test_products_api_returns_list_for_logged_in_user(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "user"

    products = [
        {
            "id": 1,
            "name": "Тестовий товар",
            "sku": "TEST-001",
            "quantity": 5,
            "price": Decimal("12.50"),
        }
    ]

    with patch("app.routes.api.get_service") as mock_get_service:
        mock_get_service.return_value.get_all_products.return_value = products

        response = client.get("/api/products")

    assert response.status_code == 200

    result = response.get_json()
    assert len(result) == 1
    assert result[0]["name"] == "Тестовий товар"
    assert result[0]["price"] == "12.50"


def test_get_product_returns_404_when_missing(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "user"

    with patch("app.routes.api.get_service") as mock_get_service:
        mock_get_service.return_value.get_product.return_value = None

        response = client.get("/api/products/999999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Товар не знайдено."
    }
