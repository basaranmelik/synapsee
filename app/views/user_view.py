from flask import render_template, Blueprint
from app.controllers.user_controller import _login_user, _register_user, _logout_user, _profile, _delete

# Blueprint oluşturarak daha modüler bir yapı elde ediliyor
bp = Blueprint("user", __name__, template_folder="../templates")

# Yönlendirmeler
@bp.route("/login", methods=["GET", "POST"])
def login_user():
    return _login_user()

@bp.route("/register", methods=["GET", "POST"])
def register_user():
    return _register_user()

@bp.route("/logout")
def logout_user():
    return _logout_user()

@bp.route("/profile", methods=['GET', 'POST'])
def profile():
    return _profile()

@bp.route("/profile/delete", methods=['GET', 'POST'])
def delete():
    return _delete()


