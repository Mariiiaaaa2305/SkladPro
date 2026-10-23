from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)

from app.repositories.product_repository import ProductRepository
from app.repositories.contractor_repository import ContractorRepository
from app.repositories.supplier_repository import SupplierRepository
from app.services.document_service import DocumentService


documents_bp = Blueprint("documents", __name__, url_prefix="/documents")


def _get_products():
    products = ProductRepository().get_all()

    return [
        {
            "id": product["id"],
            "name": product["name"],
            "sku": product["sku"],
            "quantity": product["quantity"],
            "price": product["price"],
        }
        for product in products
    ]


def _get_suppliers():
    return [
        {"id": supplier["id"], "name": supplier["name"]}
        for supplier in SupplierRepository().get_all()
    ]


def _get_contractors():
    return [
        {"id": contractor["id"], "name": contractor["name"]}
        for contractor in ContractorRepository().get_all()
    ]


@documents_bp.route("/")
def list_documents():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    documents = DocumentService().get_documents()
    return render_template("documents/list.html", documents=documents)


@documents_bp.route("/create", methods=["GET", "POST"])
def create_document():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        try:
            product_ids = request.form.getlist("product_id")
            quantities = request.form.getlist("quantity")
            prices = request.form.getlist("unit_price")

            if not (len(product_ids) == len(quantities) == len(prices)):
                raise ValueError("Перевірте позиції документа.")

            items = []

            for product_id, quantity, unit_price in zip(
                product_ids, quantities, prices
            ):
                items.append({
                    "product_id": int(product_id),
                    "quantity": int(quantity),
                    "unit_price": unit_price,
                })

            contractor_id = request.form.get("contractor_id") or None
            supplier_id = request.form.get("supplier_id") or None

            document_id = DocumentService().create_document(
                document_number=request.form.get("document_number", ""),
                document_type=request.form.get("document_type", ""),
                items=items,
                created_by=session.get("user_id"),
                contractor_id=int(contractor_id) if contractor_id else None,
                supplier_id=int(supplier_id) if supplier_id else None,
                notes=request.form.get("notes", "").strip() or None,
            )

            flash("Документ успішно створено.", "success")
            return redirect(
                url_for(
                    "documents.document_detail",
                    document_id=document_id,
                )
            )

        except (ValueError, TypeError) as error:
            flash(str(error), "error")

        except Exception:
            flash(
                "Не вдалося створити документ. "
                "Перевірте номер документа та введені дані.",
                "error",
            )

    return render_template(
        "documents/form.html",
        products=_get_products(),
        suppliers=_get_suppliers(),
        contractors=_get_contractors(),
    )


@documents_bp.route("/<int:document_id>")
def document_detail(document_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    document = DocumentService().get_document(document_id)

    if document is None:
        flash("Документ не знайдено.", "error")
        return redirect(url_for("documents.list_documents"))

    return render_template("documents/detail.html", document=document)
