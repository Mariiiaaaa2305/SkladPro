
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from mysql.connector import Error

from app.repositories.supplier_repository import SupplierRepository
from app.services.inventory_service import InventoryService
from app.utils.decorators import login_required


products_bp = Blueprint("products", __name__, url_prefix="/products")


def get_suppliers():
    """Повертає постачальників для форми товару."""
    suppliers = SupplierRepository().get_all()

    return [
        {"id": supplier["id"], "name": supplier["name"]}
        for supplier in suppliers
    ]


def render_product_form(product=None, errors=None):
    return render_template(
        "products/form.html",
        product=product or {},
        suppliers=get_suppliers(),
        errors=errors or [],
    )


@products_bp.route("/")
@login_required
def list_products():
    service = InventoryService()
    products = service.get_all_products()
    low_stock_only = request.args.get("low_stock") == "1"

    if low_stock_only:
        products = [
            product for product in products
            if product["quantity"] <= product["min_quantity"]
        ]

    return render_template(
        "products/list.html",
        products=products,
        low_stock_only=low_stock_only,
    )


@products_bp.route("/low-stock")
@login_required
def low_stock():
    return redirect(url_for("products.list_products", low_stock=1))


@products_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        service = InventoryService()
        product_id, errors = service.create_product(request.form)

        if errors:
            return render_product_form(request.form, errors), 400

        flash("Товар успішно додано.", "success")
        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    return render_product_form()


@products_bp.route("/<int:product_id>")
@login_required
def product_detail(product_id):
    product = InventoryService().get_product(product_id)

    if product is None:
        abort(404)

    return render_template("products/detail.html", product=product)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    service = InventoryService()
    product = service.get_product(product_id)

    if product is None:
        abort(404)

    if request.method == "POST":
        updated, errors = service.update_product(product_id, request.form)

        if errors:
            return render_product_form(request.form, errors), 400

        if not updated:
            abort(404)

        flash("Дані товару успішно оновлено.", "success")
        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    return render_product_form(product)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    service = InventoryService()

    if service.get_product(product_id) is None:
        abort(404)

    try:
        service.delete_product(product_id)
        flash("Товар видалено.", "success")
    except Error as exc:
        if exc.errno in (1451, 1452):
            flash(
                "Не можна видалити товар, який використовується "
                "в документах або складських операціях.",
                "error",
            )
        else:
            raise

    return redirect(url_for("products.list_products"))
