from flask import render_template, Blueprint
from app.controllers.user_controller import login_user, register_user, logout_user

# Blueprint oluşturarak daha modüler bir yapı elde ediliyor
bp = Blueprint("user", __name__, template_folder="../templates")

# Yönlendirmeler
@bp.route("/login", methods=["GET", "POST"])
def login():
    return login_user()

@bp.route("/register", methods=["GET", "POST"])
def register():
    return register_user()

@bp.route("/logout")
def logout():
    return logout_user()
