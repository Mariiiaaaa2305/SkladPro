from decimal import Decimal
from functools import wraps

from flask import Blueprint, jsonify, request, session

from app.services.inventory_service import InventoryService

api_bp = Blueprint("api", __name__, url_prefix="/api")


def api_login_required(view):
    """Перевіряє, чи користувач увійшов у систему."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Необхідно увійти в систему."}), 401
        return view(*args, **kwargs)
    return wrapped_view


def api_admin_required(view):
    """Дозволяє операцію лише адміністратору."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Необхідно увійти в систему."}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Недостатньо прав."}), 403
        return view(*args, **kwargs)
    return wrapped_view


def serialize_product(product):
    """Перетворює товар на JSON-сумісний словник."""
    result = dict(product)
    for key, value in result.items():
        if isinstance(value, Decimal):
            result[key] = str(value)
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
    return result


def get_service():
    return InventoryService()


@api_bp.route("/products", methods=["GET"])
@api_login_required
def list_products():
    products = get_service().get_all_products()
    return jsonify([serialize_product(product) for product in products])


@api_bp.route("/products/<int:product_id>", methods=["GET"])
@api_login_required
def get_product(product_id):
    product = get_service().get_product(product_id)
    if product is None:
        return jsonify({"error": "Товар не знайдено."}), 404
    return jsonify(serialize_product(product))


@api_bp.route("/products", methods=["POST"])
@api_admin_required
def create_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Очікується JSON-об'єкт."}), 400

    product_id, errors = get_service().create_product(data)
    if errors:
        return jsonify({"errors": errors}), 400

    product = get_service().get_product(product_id)
    return jsonify(serialize_product(product)), 201


@api_bp.route("/products/<int:product_id>", methods=["PATCH"])
@api_admin_required
def update_product(product_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Очікується JSON-об'єкт."}), 400

    # PATCH зберігає поточні значення полів, які не передані.
    service = get_service()
    current = service.get_product(product_id)
    if current is None:
        return jsonify({"error": "Товар не знайдено."}), 404

    merged = dict(current)
    merged.update(data)

    # Перетворюємо значення у формат, який очікує валідатор форми.
    for key in ("quantity", "min_quantity", "supplier_id"):
        if merged.get(key) is not None:
            merged[key] = str(merged[key])
    merged["price"] = str(merged.get("price", "0"))

    updated, errors = service.update_product(product_id, merged)
    if errors:
        return jsonify({"errors": errors}), 400
    if not updated:
        return jsonify({"error": "Товар не знайдено."}), 404

    return jsonify(serialize_product(service.get_product(product_id)))


@api_bp.route("/products/<int:product_id>", methods=["DELETE"])
@api_admin_required
def delete_product(product_id):
    service = get_service()
    if service.get_product(product_id) is None:
        return jsonify({"error": "Товар не знайдено."}), 404

    try:
        deleted = service.delete_product(product_id)
    except Exception:
        # Наприклад, товар може бути пов'язаний з історією руху.
        return jsonify({
            "error": "Не вдалося видалити товар. Можливо, він має пов'язані записи."
        }), 409

    if not deleted:
        return jsonify({"error": "Товар не знайдено."}), 404

    return "", 204
