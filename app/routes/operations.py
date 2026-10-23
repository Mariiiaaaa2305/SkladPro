
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.patterns.facades import InventoryFacade


operations_bp = Blueprint(
    "operations",
    __name__,
    url_prefix="/operations",
)


def is_logged_in():
    return "user_id" in session


@operations_bp.route("/")
def list_operations():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    facade = InventoryFacade()
    movements = facade.get_movements()

    return render_template(
        "operations/list.html",
        movements=movements,
    )


@operations_bp.route("/create", methods=["GET", "POST"])
def create_operation():
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    facade = InventoryFacade()
    products = facade.get_products()

    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", ""))
            quantity = int(request.form.get("quantity", ""))
            unit_price = Decimal(request.form.get("unit_price", ""))
            movement_type = request.form.get(
                "movement_type", ""
            ).strip()
            notes = request.form.get("notes", "").strip() or None

            if product_id <= 0:
                raise ValueError("Оберіть товар.")

            if quantity <= 0:
                raise ValueError("Кількість має бути більшою за нуль.")

            if (
                not unit_price.is_finite()
                or unit_price < 0
                or unit_price > Decimal("9999999999.99")
            ):
                raise ValueError("Некоректна ціна.")

            if movement_type not in facade.COMMANDS:
                raise ValueError("Оберіть коректний тип операції.")

            movement_id = facade.create_movement(
                movement_type=movement_type,
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                notes=notes,
                created_by=session["user_id"],
            )

            flash(
                f"Складську операцію №{movement_id} успішно створено.",
                "success",
            )
            return redirect(url_for("operations.list_operations"))

        except (ValueError, InvalidOperation, TypeError):
            flash(
                "Не вдалося створити операцію. Перевірте введені дані "
                "та доступний залишок товару.",
                "error",
            )

    return render_template(
        "operations/form.html",
        products=products,
    )


@operations_bp.route("/<int:movement_id>")
def operation_detail(movement_id):
    if not is_logged_in():
        return redirect(url_for("auth.login"))

    facade = InventoryFacade()
    movement = facade.inventory_service.get_stock_movement(movement_id)

    if not movement:
        flash("Складську операцію не знайдено.", "error")
        return redirect(url_for("operations.list_operations"))

    return render_template(
        "operations/detail.html",
        movement=movement,
    )
