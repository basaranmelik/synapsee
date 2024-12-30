import base64
import hashlib
from flask import flash, render_template, redirect, request, session, url_for
import graphviz
from sqlalchemy.exc import IntegrityError
from app.models import User, MindMap, Style, Session, Admin, SharedMindmap
from app import db
from werkzeug.security import generate_password_hash
from app import db
from functools import wraps

# Admin gerektiren işlemler için dekoratör
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('user.login_user'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard sayfasını render etme fonksiyonu
def _admin_dashboard():    
    return render_template('admin/admin_dashboard.html')

# Kullanıcı listesini görüntüleme fonksiyonu
def _users_list():
    # Arama sorgusunu alıyoruz (GET parametresi)
    search_query = request.args.get('search', '').strip()
    
    if (search_query):
        # Kullanıcı adı arama sorgusuna göre filtreleme
        users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
    else:
        # Arama yapılmadıysa tüm kullanıcıları getir
        users = User.query.all()
    
    # Kullanıcıları listeleyen admin sayfasına yönlendiriyoruz
    return render_template('admin/admin_users.html', users=users, search_query=search_query)

# Admin oturumunu kapatma fonksiyonu
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

# Kullanıcı düzenleme fonksiyonu
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

# Kullanıcı silme fonksiyonu
def _user_delete(user_id):
    user = User.query.get_or_404(user_id)

    # Kullanıcıya ait mindmapleri sil
    mindmaps = MindMap.query.filter(MindMap.user_id == user_id).all()
    for mindmap in mindmaps:
        db.session.delete(mindmap)
    db.session.commit()

    # Kullanıcıyı sil
    db.session.delete(user)
    db.session.commit()

    flash("Kullanıcı başarıyla silindi!", "success")
    return redirect(url_for("admin.users_list"))

# Yeni kullanıcı ekleme fonksiyonu
def _user_add():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Kullanıcının veritabanında var olup olmadığını kontrol et
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kullanılıyor!', 'danger')
            return redirect(url_for('admin.user_add'))

        # Yeni kullanıcıyı veritabanına eklemeye çalış
        try:
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Yeni kullanıcı başarıyla eklendi!', 'success')
            return redirect(url_for('admin.users_list'))
        
        except IntegrityError as e:
            db.session.rollback()
            if "email_check" in str(e):
                flash("Geçersiz e-posta adresi formatı. Lütfen '@' işareti ve geçerli bir alan adı kullandığınızdan emin olun.", "danger")
            elif "duplicate key" in str(e):
                flash("Bu e-posta adresi veya kullanıcı adı zaten kullanılıyor. Lütfen başka bir değer deneyin.", "danger")
            else:
                flash("Kullanıcı ekleme işlemi sırasında bir hata oluştu. Lütfen tekrar deneyin.", "danger")
            return redirect(url_for('admin.user_add'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Bilinmeyen bir hata oluştu: {str(e)}", "danger")
            return redirect(url_for('admin.user_add'))

    return render_template('admin/admin_user_add.html')

from flask import request

# Mindmap'leri görüntüleme fonksiyonu
def _view_mindmaps():
    # Tüm kullanıcıları al
    users = User.query.all()

    # Kullanıcı mindmap'lerini saklamak için bir sözlük başlat
    user_mindmaps = {}

    # İstekten arama terimini al, varsa
    search_term = request.args.get('search', '').lower()

    # Her kullanıcı için mindmap'leri al
    for user in users:
        # Bu kullanıcı için tüm mindmap'leri al
        mindmaps = MindMap.query.filter_by(user_id=user.user_id).all()

        # Eğer bir arama terimi varsa, mindmap'leri başlığa göre filtrele
        if search_term:
            mindmaps = [m for m in mindmaps if search_term in m.title.lower()]

        # Kullanıcıyı sadece en az bir mindmap'i varsa sözlüğe ekle
        if mindmaps:
            user_mindmaps[user] = mindmaps

    return render_template('admin/admin_mindmaps.html', user_mindmaps=user_mindmaps, search_term=search_term)

# Mindmap grafiği oluşturma fonksiyonu
def generate_mindmap_graph(mindmap, style_id=None):
    style = Style.query.get(style_id) if style_id else Style.query.first()

    # Eğer stil bulunamazsa varsayılan değerler belirleyelim
    default_color = "gray"
    default_shape = "ellipse"

    # Stil bulunamadığında varsayılan değerleri kullan
    color = style.color if style else default_color
    shape = style.shape if style else default_shape

    dot = graphviz.Digraph(comment=mindmap.title, format='png')

    dot.node(
        mindmap.title, 
        mindmap.title, 
        color=color, 
        shape=shape
    )

    for goal in mindmap.goals:
        dot.node(
            goal.title, 
            goal.title, 
            color=color, 
            shape=shape
        )
        dot.edge(mindmap.title, goal.title)

        for step in goal.steps:
            dot.node(
                step.description, 
                step.description, 
                color=color, 
                shape=shape
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

# Mindmap görüntüleme fonksiyonu
def _view_mindmap(mindmap_id):
    mindmap = MindMap.query.get(mindmap_id)
    if not mindmap:
        flash('Mind map not found!', 'danger')
        return redirect(url_for('admin.view_mindmaps'))

    # Base64 resim URL'si oluştur
    mindmap_image_url = render_mindmap_graphviz(mindmap)

    return render_template('mindmap/view.html', mindmap=mindmap, mindmap_image_url=mindmap_image_url)

# Mindmap silme fonksiyonu
def _delete_mindmap(mindmap_id):
    # Önce shared_mindmaps tablosundaki ilişkili kayıtları sil
    SharedMindmap.query.filter_by(map_id=mindmap_id).delete()

    # Ardından mindmaps tablosundaki mindmap kaydını sil
    mindmap = MindMap.query.get_or_404(mindmap_id)
    db.session.delete(mindmap)

    # Değişiklikleri veritabanına kaydet
    db.session.commit()

    flash('Mindmap başarıyla silindi!', 'success')
    return redirect(url_for('admin.admin_dashboard'))
