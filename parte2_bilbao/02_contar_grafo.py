from pathlib import Path
import networkx as nx

ruta = Path(__file__).resolve().parent / "bilbao-3974.graphml"

print("Cargando grafo de BIlbao...")

G = nx.read_graphml(ruta)

print("\nGrafo cargado correctamente")
print("Número de nodos:", G.number_of_nodes())
print("Número de conexiones:", G.number_of_edges())
print("Es dirigido:", G.is_directed())
print("Es multigrafo:", G.is_multigraph())