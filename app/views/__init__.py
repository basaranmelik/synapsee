from app.views import home_view, user_view, mindmap_view, admin_view

# Oluşturulan blueprintler import edilerek bir listede saklanıyor, 
# daha sonra init dosyamızda bu listeyi kullanarak daha kolay bir şekilde blueprintleri kaydedebileceğiz.
blueprints = [home_view.bp, user_view.bp, mindmap_view.bp, admin_view.bp]