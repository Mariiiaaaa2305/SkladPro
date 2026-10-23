
from datetime import date

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.report_service import ReportService
from app.services.inventory_service import InventoryService


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports",
)


def login_required():
    if "user_id" not in session:
        return False
    return True


@reports_bp.route("/")
def index():
    if not login_required():
        return redirect(url_for("auth.login"))

    return render_template("reports/index.html")


@reports_bp.route("/stock-balance")
def stock_balance():
    if not login_required():
        return redirect(url_for("auth.login"))

    report_date = request.args.get("date", date.today().isoformat())

    try:
        rows = ReportService().get_stock_balance(report_date)
    except (ValueError, TypeError):
        flash("Вкажіть коректну дату для звіту.", "error")
        return redirect(url_for("reports.index"))

    return render_template(
        "reports/stock_balance.html",
        rows=rows,
        report_date=report_date,
    )


@reports_bp.route("/stock-movements")
def stock_movements():
    if not login_required():
        return redirect(url_for("auth.login"))

    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    product_id = request.args.get("product_id", "")
    movement_type = request.args.get("movement_type", "")

    try:
        rows = ReportService().get_stock_movements(
            date_from=date_from or None,
            date_to=date_to or None,
            product_id=product_id or None,
            movement_type=movement_type or None,
        )
    except (ValueError, TypeError):
        flash("Перевірте параметри фільтрації звіту.", "error")
        return redirect(url_for("reports.index"))

    products = InventoryService().get_all_products()

    return render_template(
        "reports/stock_movement.html",
        rows=rows,
        products=products,
        date_from=date_from,
        date_to=date_to,
        product_id=product_id,
        movement_type=movement_type,
    )


@reports_bp.route("/stock-valuation")
def stock_valuation():
    if not login_required():
        return redirect(url_for("auth.login"))

    report = ReportService().get_stock_valuation()

    return render_template(
        "reports/stock_valuation.html",
        report=report,
    )
