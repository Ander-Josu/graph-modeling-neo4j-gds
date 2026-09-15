from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

ruta = Path(__file__).resolve().parent / "bilbao-3974.graphml"

print("Cargando grafo...")
G = nx.read_graphml(ruta)

print("Generando visualización...")

# Layout rápido para una primera visualización topológica
pos = nx.random_layout(G, seed=42)

plt.figure(figsize=(12, 12))

nx.draw(
    G,
    pos,
    node_size=2,
    width=0.15,
    arrows=False,
    with_labels=False
)

plt.title("Grafo de Bilbao - Visualización topológica")
plt.tight_layout()

plt.show()