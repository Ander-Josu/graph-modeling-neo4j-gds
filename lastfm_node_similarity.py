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

G = gds.graph.get("lastfm")

# Calculamos similitud utilizando los artistas escuchados
resultado = gds.nodeSimilarity.stream(
    G,
    relationshipTypes=["LISTEN_TO"],
    topK=10,
    similarityCutoff=0.1
)

# Ordenamos de mayor a menor similitud
resultado = resultado.sort_values(
    by="similarity",
    ascending=False
)

print(resultado.head(20))

gds.close()