import hashlib
from flask import flash, render_template, redirect, request, session, url_for
from app.models import User
from app.models.mindmaps import MindMap
from app.models.session import Session
from app import db
from werkzeug.security import generate_password_hash
from app import db
from app.models.users import User
from app.models.admin import Admin
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('user.login_user'))
        return f(*args, **kwargs)
    return decorated_function


def _add_admin(username, email, password, name):
    # Önce User tablosuna admin için yeni bir kullanıcı ekle
    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Yeni eklenen kullanıcıya ait user_id ile Admin tablosuna admin kaydını ekle
    new_admin = Admin(user_id=new_user.user_id, name=name)
    db.session.add(new_admin)
    db.session.commit()

    return new_admin

def _admin_dashboard():    
    return render_template('admin/admin_dashboard.html')

def _users_list():
    # Veritabanından tüm kullanıcıları çekiyoruz
    users = User.query.all()
    
    # Kullanıcıları listeleyen admin sayfasına yönlendiriyoruz
    return render_template('admin/admin_users.html', users=users)

def admin_logout():
    if 'admin_id' in session:  # Eğer admin oturum açmışsa
        # Admin'in session_key'ini al
        raw_session_key = session.get('session_key')

        if raw_session_key:
            # Session key'i hashle ve veritabanında ara
            hashed_session_key = hashlib.sha256(raw_session_key.encode()).hexdigest()
            session_entry = Session.query.filter_by(session_key=hashed_session_key).first()

            if session_entry:
                # Veritabanındaki session kaydını sil
                db.session.delete(session_entry)
                db.session.commit()

        # Tarayıcıdaki session bilgilerini temizle
        session.pop('session_key', None)

        # Admin ID bilgisini temizle
        session.pop('admin_id', None)

        flash('Oturum başarıyla kapatıldı!', 'info')
    else:
        flash('Zaten oturumunuz kapalı!', 'warning')

    return redirect(url_for("user.login_user"))  # Login sayfasına yönlendir

def _user_edit(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("Kullanıcı bulunamadı!", "danger")
        return redirect(url_for("admin.users_list"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Güncellemeleri uygula
        user.username = username
        user.email = email
        if password:  # Eğer şifre girildiyse hashleyip güncelle
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("Kullanıcı başarıyla güncellendi!", "success")
        return redirect(url_for("admin.users_list"))

    return render_template("admin/admin_user_edit.html", user=user)

def _user_delete(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("Kullanıcı bulunamadı!", "danger")
        return redirect(url_for("admin.users_list"))

    # Kullanıcıyı sil
    db.session.delete(user)
    db.session.commit()
    
    flash("Kullanıcı başarıyla silindi!", "success")
    return redirect(url_for("admin.users_list"))


def _user_add():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        # Yeni kullanıcı oluştur
        new_user = User(username=username, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Yeni kullanıcı başarıyla eklendi!', 'success')
            return redirect(url_for('admin.users_list'))  # Admin dashboard sayfasına yönlendir
        except Exception as e:
            db.session.rollback()
            flash(f'Bir hata oluştu: {e}', 'danger')

    return render_template('admin/admin_user_add.html')

def _view_mindmaps():
    # Get all users
    users = User.query.all()

    # Initialize a dictionary to store user mind maps
    user_mindmaps = {}

    # Loop through each user and get their mind maps
    for user in users:
        mindmaps = MindMap.query.filter_by(user_id=user.user_id).all()
        user_mindmaps[user] = mindmaps

    return render_template('admin/admin_mindmaps.html', user_mindmaps=user_mindmaps)

def _view_mindmap(mindmap_id):
    mindmap = MindMap.query.get(mindmap_id)
    if not mindmap:
        flash('Mind map not found!', 'danger')
        return redirect(url_for('admin.view_mindmaps'))

    return render_template('admin/admin_view_mindmap.html', mindmap=mindmap)





 
