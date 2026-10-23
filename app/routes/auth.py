
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from app.services.auth_service import AuthService


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = AuthService().login(username, password)

        if user is None:
            return render_template(
                "auth/login.html",
                error="Неправильний логін або пароль.",
            ), 401

        # Дозволені лише відомі ролі.
        if user.role not in ("admin", "manager"):
            return render_template(
                "auth/login.html",
                error="Для цього облікового запису не налаштовано доступ.",
            ), 403

        # Очищаємо старі дані сесії.
        session.clear()
        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        # Перенаправляємо відповідно до ролі.
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))

        return redirect(url_for("home"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Самостійна реєстрація вимкнена.
    # Облікові записи створює адміністратор.
    return (
        render_template(
            "auth/login.html",
            error=(
                "Самостійна реєстрація вимкнена. "
                "Зверніться до адміністратора."
            ),
        ),
        403,
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
