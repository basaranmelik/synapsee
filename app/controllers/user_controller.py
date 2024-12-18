
# Giriş yapma fonksiyonu
from flask import render_template, request, redirect, flash, session, url_for
from werkzeug.security import check_password_hash
from app.models.users import User
from app.models.admin import Admin
from app.models.session import Session
from app import db
import uuid
from datetime import datetime, timedelta

def _login_user():
    if 'session_key' in session:  # Eğer kullanıcı zaten giriş yaptıysa, yönlendir
        if 'admin_id' in session:
            return redirect(url_for('admin.admin_dashboard'))  # Admin için admin paneline yönlendir
        else:
            return redirect(url_for('home.index'))  # Normal kullanıcı için ana sayfaya yönlendir

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        # Kullanıcıyı kontrol et
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Kullanıcı doğrulandı

            # Session key oluşturma
            session_key = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(days=7)  # 7 gün geçerli

            # Session kaydını veritabanına ekle
            new_session = Session(session_key=session_key, user_id=user.user_id, expires_at=expires_at)
            db.session.add(new_session)
            db.session.commit()

            # Session key'i tarayıcıya kaydet
            session['session_key'] = session_key

            # Admin olup olmadığını kontrol et
            admin = Admin.query.filter_by(user_id=user.user_id).first()
            if admin:
                session['admin_id'] = admin.user_id  # Admin oturumu başlat
                return redirect(url_for('admin.admin_dashboard'))  # Admin paneline yönlendir
            else:
                session['user_id'] = user.user_id  # Normal kullanıcı oturumu başlat
                return redirect(url_for('home.index'))  # Ana sayfaya yönlendir

        else:
            flash('Geçersiz e-posta veya şifre!', 'danger')
            return redirect(url_for('user.login_user'))

    return render_template("user/login.html")



# Kayıt olma fonksiyonu
def _register_user():
    if 'session_key' in session:  # Eğer kullanıcı zaten giriş yaptıysa, anasayfaya yönlendir
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Kullanıcının veritabanında var olup olmadığını kontrol et
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kullanılıyor!', 'danger')
            return redirect(url_for('user.register_user'))

        # Yeni kullanıcı oluştur ve veritabanına ekle
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Başarıyla kayıt oldunuz!', 'success')
        return redirect(url_for('user.login_user'))

    return render_template('user/register.html')


# Çıkış yapma fonksiyonu
import hashlib

def _logout_user():
    if 'session_key' in session:
        # Tarayıcıdaki session_key'i al
        raw_session_key = session['session_key']

        # Veritabanından bu session_key ile kaydı ara
        session_entry = Session.query.filter_by(session_key=raw_session_key).first()
        if session_entry:
            db.session.delete(session_entry)
            db.session.commit()

        # Tarayıcıdaki session_key'i temizle
        session.pop('session_key', None)
        flash('Oturum kapatıldı!', 'info')

        if 'admin_id' in session:
            session.pop('admin_id', None)

    return redirect(url_for("user.login_user"))  # Login sayfasına yönlendir

