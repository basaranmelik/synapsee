from flask import Blueprint, render_template
from app.controllers.admin_controller import _users_list, _admin_dashboard, _user_edit, _user_delete, _user_add, admin_required, _view_mindmaps, _view_mindmap, _delete_mindmap
from app.models.activity_logs import ActivityLog

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

@bp.route("/mindmaps")
@admin_required
def view_mindmaps():
    return _view_mindmaps()

@bp.route('/mindmap/<int:map_id>')
@admin_required
def view_mindmap(map_id):
    return _view_mindmap(map_id)

@bp.route('/logs')
def admin_logs():
    # ActivityLog tablosundan son 50 işlemi çekiyoruz
    logs = ActivityLog.query.order_by(ActivityLog.action_datetime.desc()).limit(50).all()
    return render_template('admin/admin_logs.html', logs=logs)

@bp.route('/delete_mindmap/<int:map_id>', methods=['POST'])
def delete_mindmap(map_id):
    return _delete_mindmap(map_id)
