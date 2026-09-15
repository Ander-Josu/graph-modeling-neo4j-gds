import os
from pathlib import Path
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

load_dotenv(Path(__file__).resolve().parent / '.env')
uri = os.environ['NEO4J_URI']
usuario = os.environ['NEO4J_USER']
password = os.environ['NEO4J_PASSWORD']

gds = GraphDataScience(
    uri,
    auth=(usuario, password),
    database="neo4j"
)

# Recuperamos el grafo que ya está cargado en memoria
G = gds.graph.get("karate_club")

# Ejecutamos Degree Centrality
resultado = gds.degree.stream(
    G,
    orientation="UNDIRECTED"
)

# Ordenamos de mayor a menor centralidad
resultado = resultado.sort_values(
    by="score",
    ascending=False
)

print(resultado.head(10))

gds.close()
