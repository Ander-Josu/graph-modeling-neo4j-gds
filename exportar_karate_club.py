from pathlib import Path
import os
import networkx as nx
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

load_dotenv(Path(__file__).resolve().parent / ".env")

gds = GraphDataScience(
    os.getenv("NEO4J_URI"),
    auth=(
        os.getenv("NEO4J_USER"),
        os.getenv("NEO4J_PASSWORD")
    ),
    database="neo4j"
)

# Creamos un grafo no dirigido
G = nx.Graph()

# Recuperamos los nodos
nodos = gds.run_cypher("""
MATCH (n:KaratePerson)
RETURN n.karateId AS id
ORDER BY id
""")

for _, fila in nodos.iterrows():
    G.add_node(int(fila["id"]))

# Recuperamos las relaciones
relaciones = gds.run_cypher("""
MATCH (a:KaratePerson)-[:KNOWS_KARATE]->(b:KaratePerson)
RETURN a.karateId AS origen,
       b.karateId AS destino
""")

for _, fila in relaciones.iterrows():
    G.add_edge(
        int(fila["origen"]),
        int(fila["destino"])
    )

# Exportamos a GraphML
if G.number_of_nodes() != 34 or G.number_of_edges() != 78:
    gds.close()
    raise RuntimeError("La muestra persistente de Karate Club está incompleta. Se conserva el GraphML existente.")
nx.write_graphml(G, Path(__file__).resolve().parent / "karate_club.graphml")

print("Archivo creado correctamente: karate_club.graphml")
print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())

gds.close()
