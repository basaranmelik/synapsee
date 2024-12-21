from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# SQLAlchemy  
# (global olarak tanımlanıyor ama başlatılmıyor bu sayede diğer dosyalarda db işlemleri gerçekleştirilebiliyor)
db = SQLAlchemy()

def create_app():
    # Flask uygulamasını oluştur
    app = Flask(__name__, static_folder='app/static')
    app.config.from_object(Config)


    # Veritabanını başlat
    db.init_app(app)

    # Blueprint'leri kaydet
    from app.views import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()

    return app
