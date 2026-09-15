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

resultado = gds.fastRP.mutate(
    G,
    embeddingDimension=64,
    mutateProperty="fastrp_embedding",
    relationshipTypes=["LISTEN_TO"]
)

print(resultado)

gds.close()