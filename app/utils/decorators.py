from functools import wraps

from flask import redirect, session, url_for


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        if session.get("role") != "admin":
            return redirect(url_for("index"))

        return view(*args, **kwargs)

    return wrapped_view
