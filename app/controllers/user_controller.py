# Giriş yapma fonksiyonu
from functools import wraps
from flask import render_template, request, redirect, flash, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Admin, Session, MindMap
from app import db
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timedelta

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user.login_user'))  # Kullanıcı giriş yapmamışsa login sayfasına yönlendir
        return f(*args, **kwargs)
    return wrapper

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
        if user and check_password_hash(user.password, password):
            # Kullanıcı doğrulandı

            # Session key oluşturma
            session_key = str(uuid.uuid4())
            session['username'] = user.username
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

        # Yeni kullanıcıyı veritabanına eklemeye çalış
        try:
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Başarıyla kayıt oldunuz!', 'success')
            return redirect(url_for('user.login_user'))
        
        except IntegrityError as e:
            db.session.rollback()  # Veritabanı hatası durumunda işlemi geri al
            if "email_check" in str(e):
                flash("Geçersiz e-posta adresi formatı. Lütfen '@' işareti ve geçerli bir alan adı kullandığınızdan emin olun.", "danger")
            elif "duplicate key" in str(e):
                flash("Bu e-posta adresi veya kullanıcı adı zaten kullanılıyor. Lütfen başka bir değer deneyin.", "danger")
            else:
                flash("Kayıt işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.", "danger")
            return redirect(url_for('user.register_user'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Bilinmeyen bir hata oluştu: {str(e)}", "danger")
            return redirect(url_for('user.register_user'))

    return render_template('user/register.html')

# Çıkış yapma fonksiyonu
def _logout_user():
    if 'session_key' in session:
        # Tarayıcıdaki session_key'i al
        raw_session_key = session.get('session_key')

        # Veritabanından bu session_key ile kaydı ara
        session_entry = Session.query.filter_by(session_key=raw_session_key).first()
        if session_entry:
            # Veritabanından session kaydını sil
            db.session.delete(session_entry)
            db.session.commit()

    # Tüm oturum anahtarlarını temizle
    session.clear()  # Tüm oturum bilgilerini temizler
    flash('Oturum kapatıldı!', 'info')

    return redirect(url_for("user.login_user"))  # Login sayfasına yönlendir

def _profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Giriş yapmanız gerekiyor!', 'danger')
        return redirect(url_for('user.login_user'))

    user = User.query.get(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Güncellemeleri uygula
        user.username = username
        user.email = email
        if password:  # Eğer şifre girildiyse hashleyip güncelle
            user.password = generate_password_hash(password)

        db.session.commit()
        flash('Profiliniz başarıyla güncellendi!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', user=user)

def _delete():
    user_id = session.get('user_id')
    if not user_id:
        flash('Giriş yapmanız gerekiyor!', 'danger')
        return redirect(url_for('user.login_user'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        password = request.form.get('password')

        # Şifre doğrulama
        if not check_password_hash(user.password, password):
            flash('Şifreniz yanlış!', 'danger')
            return redirect(url_for('user.profile'))

        # Oturumdan kullanıcıyı çıkar
        session.pop('user_id', None)
        session.clear()

        # Veritabanından kullanıcının session bilgilerini sil
        sessions = Session.query.filter_by(user_id=user_id).all()
        for s in sessions:
            db.session.delete(s)

        # Kullanıcıya ait mindmap'leri sil
        mindmaps = MindMap.query.filter_by(user_id=user_id).all()
        for mindmap in mindmaps:
            db.session.delete(mindmap)

        db.session.commit()  # Session ve mindmap'lerin silinmesini kaydet

        # Kullanıcıyı sil
        db.session.delete(user)
        db.session.commit()

        flash('Hesabınız ve oturum bilgileriniz başarıyla silindi!', 'success')
        return redirect(url_for('user.login_user'))

    return render_template('user/delete_account.html', user=user)
