from pathlib import Path
import os
import math
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

ORIGEN = "1132519581"      # Casco Viejo
DESTINO = "245939768"      # Indautxu

# Distancia máxima respecto al camino de Dijkstra
# para incluir nodos alternativos.
RADIO_CORREDOR_METROS = 80


# -------------------------------------------------
# FUNCIÓN DE DISTANCIA GEOGRÁFICA
# -------------------------------------------------

def distancia_metros(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia aproximada entre dos
    coordenadas mediante la fórmula Haversine.
    """

    radio_tierra = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    return 2 * radio_tierra * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


# -------------------------------------------------
# CONEXIÓN A NEO4J
# -------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USUARIO, PASSWORD)
)


# -------------------------------------------------
# RECUPERAR EL CAMINO DE DIJKSTRA
# -------------------------------------------------

print("Recuperando camino de Dijkstra...")

with driver.session(database="neo4j") as session:

    resultado = session.run(
        """
        MATCH (origen:BilbaoNode {osmId: $origen})
        MATCH (destino:BilbaoNode {osmId: $destino})

        CALL gds.shortestPath.dijkstra.stream(
            'bilbao_gds',
            {
                sourceNode: origen,
                targetNodes: [destino],
                relationshipWeightProperty: 'length'
            }
        )

        YIELD nodeIds

        UNWIND nodeIds AS nodeId

        WITH gds.util.asNode(nodeId) AS n

        RETURN
            n.osmId AS id,
            n.x AS x,
            n.y AS y
        """,
        origen=ORIGEN,
        destino=DESTINO
    )

    nodos_dijkstra = list(resultado)


print(
    "Nodos del camino de Dijkstra:",
    len(nodos_dijkstra)
)


# -------------------------------------------------
# COORDENADAS DEL CAMINO
# -------------------------------------------------

coordenadas_camino = []

ids_camino = set()

for nodo in nodos_dijkstra:

    node_id = nodo["id"]

    ids_camino.add(node_id)

    coordenadas_camino.append(
        (
            float(nodo["y"]),
            float(nodo["x"])
        )
    )


# -------------------------------------------------
# RECUPERAR TODOS LOS NODOS DE BILBAO
# -------------------------------------------------

print("Leyendo nodos de Bilbao...")

with driver.session(database="neo4j") as session:

    todos_nodos = list(
        session.run(
            """
            MATCH (n:BilbaoNode)

            WHERE n.x IS NOT NULL
              AND n.y IS NOT NULL

            RETURN
                n.osmId AS id,
                n.x AS x,
                n.y AS y
            """
        )
    )


# -------------------------------------------------
# SELECCIONAR NODOS CERCANOS AL CAMINO
# -------------------------------------------------

print(
    f"Seleccionando nodos a menos de "
    f"{RADIO_CORREDOR_METROS} metros del camino..."
)

ids_seleccionados = set()

datos_nodos = {}


for nodo in todos_nodos:

    node_id = nodo["id"]

    lat = float(nodo["y"])
    lon = float(nodo["x"])

    distancia_minima = min(
        distancia_metros(
            lat,
            lon,
            lat_camino,
            lon_camino
        )
        for lat_camino, lon_camino
        in coordenadas_camino
    )

    if (
        distancia_minima
        <= RADIO_CORREDOR_METROS
        or node_id in ids_camino
    ):

        ids_seleccionados.add(node_id)

        datos_nodos[node_id] = {
            "x": lon,
            "y": lat
        }


print(
    "Nodos seleccionados:",
    len(ids_seleccionados)
)


# -------------------------------------------------
# RECUPERAR RELACIONES ENTRE ESOS NODOS
# -------------------------------------------------

print("Leyendo relaciones del corredor...")

with driver.session(database="neo4j") as session:

    relaciones = list(
        session.run(
            """
            MATCH (a:BilbaoNode)-[r:BILBAO_ROAD]->(b:BilbaoNode)

            WHERE a.osmId IN $ids
              AND b.osmId IN $ids

            RETURN
                a.osmId AS origen,
                b.osmId AS destino,
                r.relId AS relId,
                r.length AS length
            """,
            ids=list(ids_seleccionados)
        )
    )


driver.close()


# -------------------------------------------------
# CREAR SUBGRAFO NETWORKX
# -------------------------------------------------

G = nx.MultiDiGraph()


for node_id, propiedades in datos_nodos.items():

    G.add_node(
        node_id,
        x=propiedades["x"],
        y=propiedades["y"]
    )


for relacion in relaciones:

    longitud = relacion["length"]

    if longitud is None:
        longitud = 1.0

    G.add_edge(
        relacion["origen"],
        relacion["destino"],
        key=str(relacion["relId"]),
        length=float(longitud)
    )


# -------------------------------------------------
# COMPROBACIONES
# -------------------------------------------------

print()
print("SUBGRAFO DE COMPARACIÓN")
print("-----------------------")

print(
    "Nodos:",
    G.number_of_nodes()
)

print(
    "Relaciones:",
    G.number_of_edges()
)

print(
    "Origen incluido:",
    ORIGEN in G
)

print(
    "Destino incluido:",
    DESTINO in G
)


if (
    ORIGEN in G
    and DESTINO in G
):

    existe_camino = nx.has_path(
        G,
        ORIGEN,
        DESTINO
    )

    print(
        "Existe camino Casco Viejo -> Indautxu:",
        existe_camino
    )


# -------------------------------------------------
# GUARDAR SUBGRAFO
# -------------------------------------------------

archivo = Path(__file__).resolve().parent / "subgrafo_comparacion.graphml"

nx.write_graphml(
    G,
    archivo
)

print()
print(
    "Archivo creado:",
    archivo
)