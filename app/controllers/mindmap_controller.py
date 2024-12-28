import os
from flask import Flask, flash, redirect, request, jsonify, session, render_template, url_for
from app.models import MindMap, Goal, Step, SharedMindmap, User, Style
from app import db
import graphviz
import base64

def _save():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Kullanıcı oturumu bulunamadı! Lütfen giriş yapın.'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Geçersiz veri!'}), 400

    title = data.get('title')
    description = data.get('description')
    goals_data = data.get('goals')

    if not title or not goals_data:
        return jsonify({'error': 'Başlık ve hedefler zorunludur!'}), 400

    mindmap = MindMap(user_id=user_id, title=title, description=description)
    db.session.add(mindmap)
    db.session.commit()

    for goal_data in goals_data:
        goal = Goal(map_id=mindmap.map_id, title=goal_data['title'])
        db.session.add(goal)
        db.session.commit()

        for step_data in goal_data['steps']:
            step = Step(goal_id=goal.goal_id, description=step_data['description'])
            db.session.add(step)

    db.session.commit()
    return jsonify({'message': 'Mind Map başarıyla kaydedildi!'}), 200

def _list():
    user_id = session.get('user_id')
    if not user_id:
        flash("Giriş yapmanız gerekiyor!", "danger")
        return redirect(url_for('user.login_user'))

    mindmaps = MindMap.query.filter_by(user_id=user_id).all()
    return render_template('/mindmap/list.html', mindmaps=mindmaps)

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

def _view(mindmap_id):
    # Mindmap'i veritabanından al
    mindmap = MindMap.query.get(mindmap_id)
    if not mindmap:
        flash("Mindmap bulunamadı!", "danger")
        return redirect(url_for('admin.view_mindmaps'))

    # Formdan gelen style_id parametresini al, eğer yoksa None döner
    style_id = request.form.get('style_id')

    # Görselleştirme işlemini yap, stil ID'sini gönder
    mindmap_image_url = render_mindmap_graphviz(mindmap, style_id)

    # Stiller için gerekli verileri al (stil seçme formu için)
    styles = Style.query.all()

    return render_template('mindmap/view.html', mindmap=mindmap, mindmap_image_url=mindmap_image_url, styles=styles)

def _edit(mindmap_id):
    mindmap = MindMap.query.get_or_404(mindmap_id)

    if request.method == 'POST':
        mindmap.title = request.form['title']
        mindmap.content = request.form['content']

        db.session.commit()
        flash('Mindmap başarıyla güncellendi!', 'success')
        return redirect(url_for('mindmap.view', mindmap_id=mindmap.id))

    return render_template('mindmap/edit.html', mindmap=mindmap)

def _delete(mindmap_id):
    mindmap = MindMap.query.get_or_404(mindmap_id)

    db.session.delete(mindmap)
    db.session.commit()
    flash('Mindmap başarıyla silindi!', 'success')

    return redirect(url_for('mindmap.list'))

def _share(mindmap_id):
     # Mindmap'i bul
    mindmap = MindMap.query.get_or_404(mindmap_id)
    
    # Kullanıcı adı al
    username = request.form['username']
    
    # Kullanıcıyı veritabanında ara
    user = User.query.filter_by(username=username).first()
    if not user:
        # Kullanıcı bulunamazsa hata mesajı döndür
        return redirect(url_for('mindmap.view', mindmap_id=mindmap_id, error='Kullanıcı bulunamadı!'))
    
    # Paylaşımı veritabanına kaydet (permission_level ile birlikte)
    shared_mindmap = SharedMindmap(
        map_id=mindmap_id, 
        shared_with_user_id=user.user_id,
        permission_level=1  # Varsayılan olarak 'okuma' izni (1) veriyoruz
    )
    db.session.add(shared_mindmap)
    db.session.commit()

    # Başarıyla paylaşım yapılmışsa mindmap detay sayfasına yönlendir
    return redirect(url_for('mindmap.view', mindmap_id=mindmap_id))

def _shared_mindmaps():
    # Kullanıcının kimliği alınacak (oturum açmış kullanıcıdan alabilirsiniz)
    user_id = session.get('user_id') # Eğer Flask-Login kullanıyorsanız, current_user'dan alabilirsiniz

    # Kullanıcıya ait paylaşılan mindmap'leri alıyoruz
    shared_mindmaps = SharedMindmap.query.filter_by(shared_with_user_id=user_id).all()

    # Paylaşılan mindmap'leri almak
    mindmaps = []
    for shared in shared_mindmaps:
        mindmap = MindMap.query.get(shared.map_id)
        if mindmap:
            mindmaps.append(mindmap)

    return render_template('mindmap/shared_mindmaps.html', mindmaps=mindmaps)
