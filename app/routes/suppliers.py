
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
from app.utils.decorators import login_required


suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


def validate_supplier_form(form):
    """Перевіряє дані форми постачальника."""
    data = {
        "name": form.get("name", "").strip(),
        "contact_person": form.get("contact_person", "").strip(),
        "phone": form.get("phone", "").strip(),
        "email": form.get("email", "").strip(),
        "address": form.get("address", "").strip(),
    }
    errors = []

    if not data["name"]:
        errors.append("Вкажіть назву постачальника.")
    elif len(data["name"]) > 150:
        errors.append("Назва не може перевищувати 150 символів.")

    if len(data["contact_person"]) > 120:
        errors.append("Ім'я контактної особи задовге.")

    if len(data["phone"]) > 30:
        errors.append("Номер телефону не може перевищувати 30 символів.")

    if len(data["email"]) > 120:
        errors.append("Електронна адреса не може перевищувати 120 символів.")

    if len(data["address"]) > 255:
        errors.append("Адреса не може перевищувати 255 символів.")

    return data, errors


def render_supplier_form(supplier=None, errors=None):
    return render_template(
        "suppliers/form.html",
        supplier=supplier or {},
        errors=errors or [],
    )


@suppliers_bp.route("/")
@login_required
def list_suppliers():
    suppliers = SupplierRepository().get_all()
    return render_template(
        "suppliers/list.html",
        suppliers=suppliers,
    )


@suppliers_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_supplier():
    if request.method == "POST":
        data, errors = validate_supplier_form(request.form)

        if errors:
            return render_supplier_form(data, errors), 400

        supplier_id = SupplierRepository().create(data)
        flash("Постачальника успішно додано.", "success")
        return redirect(
            url_for("suppliers.supplier_detail", supplier_id=supplier_id)
        )

    return render_supplier_form()


@suppliers_bp.route("/<int:supplier_id>")
@login_required
def supplier_detail(supplier_id):
    supplier = SupplierRepository().get_by_id(supplier_id)

    if supplier is None:
        abort(404)

    return render_template(
        "suppliers/detail.html",
        supplier=supplier,
    )


@suppliers_bp.route("/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
def edit_supplier(supplier_id):
    repository = SupplierRepository()
    supplier = repository.get_by_id(supplier_id)

    if supplier is None:
        abort(404)

    if request.method == "POST":
        data, errors = validate_supplier_form(request.form)

        if errors:
            data["id"] = supplier_id
            return render_supplier_form(data, errors), 400

        repository.update(supplier_id, data)
        flash("Дані постачальника оновлено.", "success")
        return redirect(
            url_for("suppliers.supplier_detail", supplier_id=supplier_id)
        )

    return render_supplier_form(supplier)


@suppliers_bp.route("/<int:supplier_id>/delete", methods=["POST"])
@login_required
def delete_supplier(supplier_id):
    repository = SupplierRepository()

    if repository.get_by_id(supplier_id) is None:
        abort(404)

    try:
        repository.delete(supplier_id)
        flash("Постачальника видалено.", "success")
    except Error as exc:
        if exc.errno == 1451:
            flash(
                "Не можна видалити постачальника, оскільки з ним пов'язані товари.",
                "error",
            )
        else:
            raise

    return redirect(url_for("suppliers.list_suppliers"))
