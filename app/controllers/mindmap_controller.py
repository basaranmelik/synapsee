import os
from flask import Flask, flash, redirect, request, jsonify, session, render_template, url_for
from app.models import MindMap, Goal, Step
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

def generate_mindmap_graph(mindmap):
    dot = graphviz.Digraph(comment=mindmap.title, format='png')
    dot.node(mindmap.title, mindmap.title, shape='box')

    for goal in mindmap.goals:
        dot.node(goal.title, goal.title, shape='ellipse')
        dot.edge(mindmap.title, goal.title)

        for step in goal.steps:
            dot.node(step.description, step.description, shape='ellipse')
            dot.edge(goal.title, step.description)

    return dot

def render_mindmap_graphviz(mindmap):
    dot = generate_mindmap_graph(mindmap)

    # Görseli bellekte oluştur
    png_data = dot.pipe(format='png')

    # Base64 formatına çevir
    base64_image = base64.b64encode(png_data).decode('utf-8')
    return f"data:image/png;base64,{base64_image}"

def _view(mindmap_id):
    mindmap = MindMap.query.get(mindmap_id)
    if not mindmap:
        flash("Mindmap bulunamadı!", "danger")
        return redirect(url_for('mindmap.list'))

    mindmap_image_url = render_mindmap_graphviz(mindmap)

    return render_template('mindmap/view.html', mindmap=mindmap, mindmap_image_url=mindmap_image_url)

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
    flash('Mindmap başarıyla silindi!', 'danger')

    return redirect(url_for('mindmap.index'))
