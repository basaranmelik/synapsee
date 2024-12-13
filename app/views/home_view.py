from flask import render_template, Blueprint

# Blueprint oluşturarak daha modüler bir yapı elde ediliyor
bp = Blueprint("home", __name__, template_folder="../templates")

# Yönlendirmeler
@bp.route("/")
def index():
    return render_template("index.html")