from pathlib import Path
import os
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

# Cargar dataset Cora
G = gds.graph.load_cora()

print("Grafo cargado correctamente")
print("Nombre:", G.name())
print("Número de nodos:", G.node_count())
print("Número de relaciones:", G.relationship_count())
print("Etiquetas de nodos:", G.node_labels())
print("Tipos de relaciones:", G.relationship_types())

gds.close()