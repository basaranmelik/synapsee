from flask import Blueprint, render_template
from app.controllers.admin_controller import _users_list, _admin_dashboard, _user_edit, _user_delete, _user_add, admin_required

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/")
@admin_required
def admin_dashboard():
    return _admin_dashboard()

@bp.route("/users")
@admin_required
def users_list():
    return _users_list()

@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def user_edit(user_id):
    return _user_edit(user_id)

@bp.route("/users/<int:user_id>/delete")
@admin_required
def user_delete(user_id):
    return _user_delete(user_id)

@bp.route("/users/add", methods=['POST', 'GET'])
@admin_required
def user_add():
    return _user_add()
