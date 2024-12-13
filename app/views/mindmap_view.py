from flask import Blueprint, render_template

bp = Blueprint('mindmap', __name__, "../templates")

@bp.route('/mindmap/create', methods=['GET', 'POST'])
def create():
    return render_template('mindmap/create_mindmap.html')
