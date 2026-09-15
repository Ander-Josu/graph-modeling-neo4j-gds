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

G = gds.graph.load_karate_club(
    graph_name="karate_club_undirected",
    undirected=True
)

print("Nombre:", G.name())
print("Nodos:", G.node_count())
print("Relaciones:", G.relationship_count())

gds.close()