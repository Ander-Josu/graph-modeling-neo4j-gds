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

G = gds.graph.get("cora")

# Ejecutamos Strongly Connected Components
resultado = gds.scc.stream(G)

print(resultado.head(10))

print("\nNúmero de componentes:")
print(resultado["componentId"].nunique())

print("\nTamaño de los componentes:")
print(
    resultado.groupby("componentId")
    .size()
    .sort_values(ascending=False)
    .head(10)
)

gds.close()