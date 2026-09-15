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

# Recuperamos el grafo Karate Club
G = gds.graph.get("karate_club_undirected")

# Ejecutamos PageRank
resultado = gds.pageRank.stream(G)

# Ordenamos de mayor a menor
resultado = resultado.sort_values(
    by="score",
    ascending=False
)

print(resultado.head(10))

gds.close()