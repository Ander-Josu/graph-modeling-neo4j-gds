from pathlib import Path
import os
import networkx as nx

from dotenv import load_dotenv
from neo4j import GraphDatabase


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

URI = os.getenv("NEO4J_URI")
USUARIO = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# -------------------------------------------------
# CONEXIÓN A NEO4J
# -------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USUARIO, PASSWORD)
)


# -------------------------------------------------
# RECUPERAR NODOS
# -------------------------------------------------

print("Leyendo nodos desde Neo4j...")

with driver.session(database="neo4j") as session:

    nodos = list(
        session.run("""
            MATCH (n:BilbaoNode)

            RETURN
                n.osmId AS id,
                n.x AS x,
                n.y AS y
        """)
    )


# -------------------------------------------------
# RECUPERAR RELACIONES
# -------------------------------------------------

print("Leyendo relaciones desde Neo4j...")

with driver.session(database="neo4j") as session:

    relaciones = list(
        session.run("""
            MATCH (a:BilbaoNode)-[r:BILBAO_ROAD]->(b:BilbaoNode)

            RETURN
                a.osmId AS origen,
                b.osmId AS destino,
                r.length AS length,
                r.name AS nombre
        """)
    )


driver.close()


print()
print("GRAFO ORIGINAL")
print("----------------")
print("Nodos:", len(nodos))
print("Relaciones:", len(relaciones))


# -------------------------------------------------
# CREAR GRAFO SIMPLE NO DIRIGIDO
# -------------------------------------------------

G = nx.Graph()


# Añadir nodos
for nodo in nodos:

    G.add_node(
        nodo["id"],
        x=nodo["x"],
        y=nodo["y"]
    )


# Añadir relaciones
#
# Si existen varias calles entre los mismos
# dos nodos, conservamos la de menor longitud.
# -------------------------------------------------

for relacion in relaciones:

    origen = relacion["origen"]
    destino = relacion["destino"]

    length = relacion["length"]

    if length is None:
        continue

    length = float(length)

    nombre = (
        relacion["nombre"]
        if relacion["nombre"]
        else "Sin nombre"
    )

    if G.has_edge(origen, destino):

        longitud_actual = G[
            origen
        ][
            destino
        ]["length"]

        if length < longitud_actual:

            G[
                origen
            ][
                destino
            ]["length"] = length

            G[
                origen
            ][
                destino
            ]["name"] = nombre

    else:

        G.add_edge(
            origen,
            destino,
            length=length,
            name=nombre
        )


print()
print("GRAFO PREPARADO PARA KRUSKAL")
print("----------------------------")
print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())
print("Es dirigido:", G.is_directed())
print("Está conectado:", nx.is_connected(G))


# -------------------------------------------------
# APLICAR KRUSKAL
# -------------------------------------------------

print()
print("Aplicando Kruskal...")

mst = nx.minimum_spanning_tree(
    G,
    algorithm="kruskal",
    weight="length"
)


# -------------------------------------------------
# CALCULAR RESULTADOS
# -------------------------------------------------

peso_total = sum(
    datos["length"]
    for _, _, datos
    in mst.edges(data=True)
)


print()
print("RESULTADO KRUSKAL")
print("------------------")

print(
    "Nodos del árbol:",
    mst.number_of_nodes()
)

print(
    "Relaciones del árbol:",
    mst.number_of_edges()
)

print(
    "Longitud total:",
    round(peso_total, 2),
    "metros"
)


# -------------------------------------------------
# COMPROBACIÓN TEÓRICA
# -------------------------------------------------

esperadas = (
    mst.number_of_nodes()
    - 1
)

print()
print("COMPROBACIÓN")
print("Relaciones esperadas N-1:", esperadas)

print(
    "Cumple estructura de árbol:",
    mst.number_of_edges()
    == esperadas
)


# -------------------------------------------------
# GUARDAR RESULTADO
# -------------------------------------------------

archivo = Path(__file__).resolve().parent / "bilbao_kruskal_mst.graphml"

nx.write_graphml(
    mst,
    archivo
)

print()
print(
    "Archivo creado:",
    archivo
)