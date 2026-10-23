
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from mysql.connector import IntegrityError

from app.utils.decorators import admin_required
from app.repositories.user_repository import UserRepository


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    repository = UserRepository()

    if request.method == "POST":
        action = request.form.get("action", "update_role")

        if action == "create_user":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(username) < 3 or len(username) > 50:
                flash("Логін має містити від 3 до 50 символів.", "error")
                return redirect(url_for("admin.users"))

            if len(password) < 8:
                flash("Пароль має містити щонайменше 8 символів.", "error")
                return redirect(url_for("admin.users"))

            if password != confirm_password:
                flash("Паролі не збігаються.", "error")
                return redirect(url_for("admin.users"))

            if repository.get_by_username(username) is not None:
                flash("Такий логін уже існує.", "error")
                return redirect(url_for("admin.users"))

            try:
                repository.create(username, password, role="manager")
                flash("Обліковий запис менеджера створено.", "success")
            except IntegrityError:
                # Захист від дублювання логіна при одночасних запитах.
                flash("Такий логін уже існує.", "error")
            except ValueError as exc:
                flash(str(exc), "error")
            except Exception:
                flash("Не вдалося створити користувача.", "error")

            return redirect(url_for("admin.users"))

        if action != "update_role":
            flash("Невідома дія.", "error")
            return redirect(url_for("admin.users"))

        user_id = request.form.get("user_id", type=int)
        role = request.form.get("role", "")
        current_user_id = session.get("user_id")

        if user_id is None:
            flash("Не вдалося визначити користувача.", "error")
            return redirect(url_for("admin.users"))

        if role not in UserRepository.ALLOWED_ROLES:
            flash("Обрана роль некоректна.", "error")
            return redirect(url_for("admin.users"))

        if current_user_id == user_id:
            flash("Не можна змінювати власну роль через цю сторінку.", "error")
            return redirect(url_for("admin.users"))

        try:
            all_users = repository.get_all()
            target_user = next(
                (user for user in all_users if user["id"] == user_id),
                None,
            )

            if target_user is None:
                flash("Користувача не знайдено.", "error")
                return redirect(url_for("admin.users"))

            if target_user["role"] == "admin" and role != "admin":
                if repository.count_admins() <= 1:
                    flash(
                        "Не можна позбавити ролі останнього адміністратора.",
                        "error",
                    )
                    return redirect(url_for("admin.users"))

            updated = repository.update_role(user_id, role)
            flash(
                "Роль користувача успішно оновлено."
                if updated else "Роль не змінено.",
                "success" if updated else "error",
            )
        except Exception:
            flash("Не вдалося оновити роль користувача.", "error")

        return redirect(url_for("admin.users"))

    return render_template(
        "admin/users.html",
        users=repository.get_all(),
    )


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    repository = UserRepository()
    current_user_id = session.get("user_id")

    if user_id == current_user_id:
        flash("Не можна змінювати статус власного акаунта.", "error")
        return redirect(url_for("admin.users"))

    try:
        users = repository.get_all()
        target = next(
            (user for user in users if user["id"] == user_id),
            None,
        )

        if target is None:
            flash("Користувача не знайдено.", "error")
            return redirect(url_for("admin.users"))

        new_status = not bool(target["is_active"])

        if (
            target["role"] == "admin"
            and target["is_active"]
            and not new_status
            and repository.count_admins() <= 1
        ):
            flash(
                "Не можна деактивувати останнього активного адміністратора.",
                "error",
            )
            return redirect(url_for("admin.users"))

        repository.set_active(user_id, new_status)

        flash(
            "Обліковий запис активовано."
            if new_status
            else "Обліковий запис деактивовано.",
            "success",
        )
    except Exception:
        flash("Не вдалося змінити статус облікового запису.", "error")

    return redirect(url_for("admin.users"))
