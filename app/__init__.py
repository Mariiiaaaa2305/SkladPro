
from flask import Flask, redirect, url_for, session, render_template

from app.config import Config
from app.routes.api import api_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.products import products_bp
from app.routes.suppliers import suppliers_bp
from app.routes.documents import documents_bp
from app.routes.operations import operations_bp
from app.routes.reports import reports_bp
from app.routes.notifications import notifications_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(operations_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)

    # Початкова адреса сайту завжди відкриває сторінку входу.
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # Головна сторінка доступна після авторизації.
    @app.route("/home")
    def home():
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        from app.services.inventory_service import InventoryService

        service = InventoryService()
        statistics = service.get_dashboard_statistics()

        return render_template(
            "dashboard.html",
            statistics=statistics,
        )

    return app
