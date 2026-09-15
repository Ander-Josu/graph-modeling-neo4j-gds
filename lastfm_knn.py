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

# KNN usando los embeddings creados por FastRP
resultado = gds.knn.stream(
    G,
    nodeProperties=["fastrp_embedding"],
    nodeLabels=["User"],
    topK=5
)

resultado = resultado.sort_values(
    by="similarity",
    ascending=False
)

print(resultado.head(20))

# Eliminamos parejas duplicadas A-B / B-A
resultado["usuario1"] = resultado[["node1", "node2"]].min(axis=1)
resultado["usuario2"] = resultado[["node1", "node2"]].max(axis=1)

top_parejas = (
    resultado
    .sort_values(by="similarity", ascending=False)
    .drop_duplicates(subset=["usuario1", "usuario2"])
    .head(20)
)

# Guardamos una pequeña muestra en Neo4j para visualizar
for _, fila in top_parejas.iterrows():

    gds.run_cypher(
        """
        MERGE (a:LastFMUser {userId: $usuario1})
        MERGE (b:LastFMUser {userId: $usuario2})

        MERGE (a)-[r:SIMILAR_KNN]->(b)
        SET r.similarity = $similarity
        """,
        params={
            "usuario1": int(fila["usuario1"]),
            "usuario2": int(fila["usuario2"]),
            "similarity": float(fila["similarity"])
        }
    )

print("\nTop 20 parejas KNN guardadas en Neo4j.")

gds.close()