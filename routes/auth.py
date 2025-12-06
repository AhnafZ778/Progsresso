"""
Authentication routes for Progresso
"""

from flask import Blueprint, render_template, request, redirect, url_for
from functools import wraps
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    """Decorator to require login for routes"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page and handler"""
    if AuthService.is_authenticated():
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember_me = request.form.get("remember_me") == "on"

        if not email or not password:
            return render_template(
                "login.html", error="Please fill in all fields", mode="login"
            )

        result = AuthService.sign_in(email, password, remember_me)

        if result["success"]:
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error=result["error"], mode="login")

    return render_template("login.html", mode="login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page and handler"""
    if AuthService.is_authenticated():
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password:
            return render_template(
                "login.html", error="Please fill in all fields", mode="register"
            )

        if password != confirm_password:
            return render_template(
                "login.html", error="Passwords do not match", mode="register"
            )

        if len(password) < 6:
            return render_template(
                "login.html",
                error="Password must be at least 6 characters",
                mode="register",
            )

        result = AuthService.sign_up(email, password)

        if result["success"]:
            # If auto_login is True, session is already set - go to app
            if result.get("auto_login"):
                return redirect(url_for("index"))
            else:
                # Fallback message if email confirmation is required
                return render_template(
                    "login.html",
                    success=result.get(
                        "message", "Account created! You can now log in."
                    ),
                    mode="login",
                )
        else:
            return render_template("login.html", error=result["error"], mode="register")

    return render_template("login.html", mode="register")


@auth_bp.route("/logout")
def logout():
    """Logout handler"""
    AuthService.sign_out()
    return redirect(url_for("auth.login"))
