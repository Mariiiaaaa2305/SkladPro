from flask import Blueprint, flash, redirect, render_template, url_for

from app.services.notification_service import NotificationService
from app.utils.decorators import login_required


notifications_bp = Blueprint(
    "notifications",
    __name__,
    url_prefix="/notifications",
)


@notifications_bp.route("/")
@login_required
def index():
    service = NotificationService()
    notifications = service.get_notifications(limit=100)
    unread_count = sum(
        1 for notification in notifications
        if not notification["is_read"]
    )
    return render_template(
        "notifications/list.html",
        notifications=notifications,
        unread_count=unread_count,
    )


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    updated = NotificationService().mark_as_read(notification_id)

    if not updated:
        flash("Сповіщення не знайдено.", "error")
    else:
        flash("Сповіщення позначено як прочитане.", "success")

    return redirect(url_for("notifications.index"))
