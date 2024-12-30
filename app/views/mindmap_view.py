from flask import Blueprint, render_template
from app.controllers.mindmap_controller import _save, _list, _view, _delete, _share, _shared_mindmaps
from app.controllers.user_controller import login_required
from app.models.styles import Style

bp = Blueprint('mindmap', __name__, "../templates", url_prefix="/mindmap")

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    styles = Style.query.all()  # Veritabanından tüm stilleri getir
    return render_template('mindmap/create.html', styles=styles)

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


@bp.route('/delete/<int:mindmap_id>', methods=['POST'])
@login_required
def delete(mindmap_id):
    return _delete(mindmap_id)

@bp.route('/share/<int:mindmap_id>', methods=['POST'])
@login_required
def share(mindmap_id):
    return _share(mindmap_id)

@bp.route('/shared_mindmaps', methods=['GET'])
@login_required
def shared_mindmaps():
    return _shared_mindmaps()




# TODO : resmi getirmeyi ostan değil dbten al