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

# Recuperamos Cora del catálogo de GDS
G = gds.graph.get("cora")

# Ejecutamos PageRank
resultado = gds.pageRank.stream(G)

# Ordenamos de mayor a menor
resultado = resultado.sort_values(
    by="score",
    ascending=False
)

print(resultado.head(10))

# Guardamos PageRank en los nodos CoraPaper que hemos creado para visualizar
for _, fila in resultado.iterrows():
    gds.run_cypher(
        """
        MATCH (n:CoraPaper {paperId: $id})
        SET n.pageRank = $score
        """,
        params={
            "id": int(fila["nodeId"]),
            "score": float(fila["score"])
        }
    )

print("\nPageRank guardado en los nodos CoraPaper.")

gds.close()