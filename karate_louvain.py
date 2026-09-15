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

# Recuperamos el grafo no dirigido
G = gds.graph.get("karate_club_undirected")

# Ejecutamos Louvain
resultado = gds.louvain.stream(G)

# Ordenamos por comunidad
resultado = resultado.sort_values(
    by=["communityId", "nodeId"]
)

print(resultado)

print("\nTamaño de cada comunidad:")
print(resultado.groupby("communityId").size())

for _, fila in resultado.iterrows():
    gds.run_cypher(
        """
        MATCH (n:KaratePerson {karateId: $id})
        SET n.communityId = $community
        """,
        params={
            "id": int(fila["nodeId"]),
            "community": int(fila["communityId"])
        }
    )

print("\nComunidades guardadas en Neo4j.")

gds.close()