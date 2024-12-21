from flask import Blueprint, render_template
from app.controllers.mindmap_controller import _save, _list, _view, _edit, _delete
from app.controllers.user_controller import login_required

bp = Blueprint('mindmap', __name__, "../templates", url_prefix="/mindmap")

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    return render_template('mindmap/create.html')

@bp.route("/save", methods=['POST'])
@login_required
def save():
    return _save()

@bp.route("/")
@login_required
def list():
    return _list()

@bp.route("/view/<int:mindmap_id>")
@login_required
def view(mindmap_id):
    return _view(mindmap_id)

@bp.route('/edit/<int:mindmap_id>', methods=['GET', 'POST'])
@login_required
def edit(mindmap_id):
    return _edit(mindmap_id)

@bp.route('/delete/<int:mindmap_id>', methods=['POST'])
@login_required
def delete(mindmap_id):
    return _delete(mindmap_id)

# TODO : resmi getirmeyi ostan değil dbten al