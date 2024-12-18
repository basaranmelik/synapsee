from pyvis.network import Network

# Pyvis network objesi oluştur
mindmap = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)

# Ana Düğüm
mindmap.add_node("MindMap", label="MindMap: Project Roadmap", color="lightblue", size=30)

# Alt Düğümler (Goals)
goals = ["Goal 1: Research", "Goal 2: Development", "Goal 3: Testing"]
for goal in goals:
    mindmap.add_node(goal, label=goal, color="lightgreen", size=20)
    mindmap.add_edge("MindMap", goal)

# Alt Alt Düğümler (Steps)
steps = {
    "Goal 1: Research": ["Step 1.1: Literature Review", "Step 1.2: Feasibility Study"],
    "Goal 2: Development": ["Step 2.1: Write Code", "Step 2.2: Refactor Code"],
    "Goal 3: Testing": ["Step 3.1: Unit Tests", "Step 3.2: Integration Tests"]
}

for goal, step_list in steps.items():
    for step in step_list:
        mindmap.add_node(step, label=step, color="lightyellow", size=15)
        mindmap.add_edge(goal, step)

# HTML olarak kaydet
mindmap.save_graph("templates/mindmap.html")
