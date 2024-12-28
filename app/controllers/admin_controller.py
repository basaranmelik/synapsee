import base64
import hashlib
from flask import flash, render_template, redirect, request, session, url_for
import graphviz
from app.models import User
from app.models.mindmaps import MindMap
from app.models.sessions import Session
from app import db
from werkzeug.security import generate_password_hash
from app import db
from app.models.styles import Style
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
    # Arama sorgusunu alıyoruz (GET parametresi)
    search_query = request.args.get('search', '').strip()
    
    if search_query:
        # Kullanıcı adı arama sorgusuna göre filtreleme
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    else:
        # Arama yapılmadıysa tüm kullanıcıları getir
        users = User.query.all()
    
    # Kullanıcıları listeleyen admin sayfasına yönlendiriyoruz
    return render_template('admin/admin_users.html', users=users, search_query=search_query)


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

from flask import request

def _view_mindmaps():
    # Get all users
    users = User.query.all()

    # Initialize a dictionary to store user mind maps
    user_mindmaps = {}

    # Get the search term from the request, if any
    search_term = request.args.get('search', '').lower()

    # Loop through each user and get their mind maps
    for user in users:
        # Get all mindmaps for this user
        mindmaps = MindMap.query.filter_by(user_id=user.user_id).all()

        # If there's a search term, filter mindmaps based on the title
        if search_term:
            mindmaps = [m for m in mindmaps if search_term in m.title.lower()]

        # Only add the user to the dictionary if they have at least one mindmap
        if mindmaps:
            user_mindmaps[user] = mindmaps

    return render_template('admin/admin_mindmaps.html', user_mindmaps=user_mindmaps, search_term=search_term)

def generate_mindmap_graph(mindmap, style_id=None):
    # Stil seçimi: Gönderilen style_id veya varsayılan ilk stil
    style = Style.query.get(style_id) if style_id else Style.query.first()

    # Eğer stil bulunamazsa varsayılan değerler belirleyelim
    default_color = "gray"
    default_shape = "ellipse"

    # Graphviz grafiğini oluştur
    dot = graphviz.Digraph(comment=mindmap.title, format='png')

    # Mindmap düğümü
    dot.node(
        mindmap.title, 
        mindmap.title, 
        color=style.color if style else default_color, 
        shape=style.shape if style else default_shape
    )

    for goal in mindmap.goals:
        dot.node(
            goal.title, 
            goal.title, 
            color=style.color if style else default_color, 
            shape=style.shape if style else default_shape
        )
        dot.edge(mindmap.title, goal.title)

        for step in goal.steps:
            dot.node(
                step.description, 
                step.description, 
                color=style.color if style else default_color, 
                shape=style.shape if style else default_shape
            )
            dot.edge(goal.title, step.description)

    return dot

def render_mindmap_graphviz(mindmap, style_id=None):
    dot = generate_mindmap_graph(mindmap, style_id)

    # Graphviz grafiğini bellek içinde PNG olarak üret
    png_data = dot.pipe(format='png')

    # Base64 formatına dönüştür
    base64_image = base64.b64encode(png_data).decode('utf-8')
    return f"data:image/png;base64,{base64_image}"

def _view_mindmap(mindmap_id):
    mindmap = MindMap.query.get(mindmap_id)
    if not mindmap:
        flash('Mind map not found!', 'danger')
        return redirect(url_for('admin.view_mindmaps'))

    # Generate the Base64 image URL
    mindmap_image_url = render_mindmap_graphviz(mindmap)

    return render_template('mindmap/view.html', mindmap=mindmap, mindmap_image_url=mindmap_image_url)


def _delete_mindmap(map_id):
    mindmap = MindMap.query.get_or_404(map_id)
    db.session.delete(mindmap)
    db.session.commit()
    flash('Mindmap başarıyla silindi.', 'success')
    return redirect(url_for('admin.admin_dashboard'))





 
