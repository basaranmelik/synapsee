from flask import request, flash, redirect, session, url_for
from app.models.mindmaps import MindMap
from app.models.users import User
from app.models.shared_mindmaps import SharedMindMap
from app import db

def share_mindmap(mindmap_id):
    user_id = session.get('user_id')
    # Formdan gelen kullanıcı adlarını al
    usernames = request.form.get('share_with_users')
    if not usernames:
        flash("Lütfen paylaşılacak kullanıcı adlarını girin.", "danger")
        return redirect(url_for('mindmap.dashboard'))

    # Kullanıcı adlarını ayır ve temizle
    username_list = [username.strip() for username in usernames.split(',')]

    # Mindmap'in paylaşılıp paylaşılmadığını kontrol et
    mindmap = MindMap.query.filter_by(id=mindmap_id, user_id=user_id).first()
    if not mindmap:
        flash("Bu mindmap bulunamadı veya paylaşma izniniz yok.", "danger")
        return redirect(url_for('mindmap.dashboard'))

    # Veritabanına paylaşımı kaydet
    for username in username_list:
        user = User.query.filter_by(username=username).first()
        if user:
            shared_mindmap = SharedMindMap(user_id=user.id, mindmap_id=mindmap.id)
            db.session.add(shared_mindmap)
        else:
            flash(f"Kullanıcı '{username}' bulunamadı.", "warning")

    db.session.commit()
    flash("Mindmap başarıyla paylaşıldı!", "success")
    return redirect(url_for('mindmap.dashboard'))