from flask import render_template, request, redirect, flash, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.users import User
from app.models.session import Session
from app import db
import uuid
import hashlib
from datetime import datetime, timedelta

# Giriş yapma fonksiyonu
def login_user():
    if 'session_key' in session:  # Eğer kullanıcı zaten giriş yaptıysa, anasayfaya yönlendir
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):

            # Session key oluşturma
            session_key = str(uuid.uuid4())  # Benzersiz bir anahtar oluştur
            expires_at = datetime.utcnow() + timedelta(days=7)  # Oturum süresi (7 gün)

            session_key_hashed = hashlib.sha256(session_key.encode()).hexdigest()

            # Yeni session kaydı
            new_session = Session(session_key=session_key_hashed, user_id=user.user_id, expires_at=expires_at)
            db.session.add(new_session)
            db.session.commit()

            # Tarayıcı session'a oturum anahtarını ekle
            session['session_key'] = session_key

            return redirect(url_for('home.index'))  # Yönlendirme düzenlendi
        else:
            flash('Geçersiz e-posta veya şifre!', 'danger')
            return redirect(url_for('user.login'))
    return render_template("user/login.html")

# Kayıt olma fonksiyonu
def register_user():
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
            return redirect(url_for('user.register'))

        # Şifreyi hash'le
        password_hash = generate_password_hash(password)

        # Eğer kullanıcı daha önceden kayıtlı değilse kaydet ve veritabanına ekle
        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        flash('Başarıyla kayıt oldunuz!', 'success')
        return redirect(url_for('user.login'))

    return render_template('user/register.html')

# Çıkış yapma fonksiyonu
import hashlib

def logout_user():
    if 'session_key' in session:
        # Tarayıcıdaki session_key'i al
        raw_session_key = session['session_key']
        
        # Bu key'i hashle
        hashed_session_key = hashlib.sha256(raw_session_key.encode()).hexdigest()

        # Veritabanından hashlenmiş session_key'i ara
        session_entry = Session.query.filter_by(session_key=hashed_session_key).first()
        if session_entry:
            db.session.delete(session_entry)
            db.session.commit()

        # Tarayıcıdaki session_key'i temizle
        session.pop('session_key', None)
        flash('Oturum kapatıldı!', 'info')

    return redirect(url_for("user.login"))  # Login sayfasına yönlendir

