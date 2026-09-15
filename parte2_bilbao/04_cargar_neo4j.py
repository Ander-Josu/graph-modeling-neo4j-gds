from pathlib import Path
import os
import argparse
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

RUTA = Path(__file__).resolve().parent / "bilbao-3974.graphml"

BATCH_NODOS = 1000
BATCH_RELACIONES = 1000


def graphml_bool(value):
    """GraphML de OSMnx puede almacenar 'False' como texto."""
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {'true', '1', 'yes'}:
        return True
    if normalized in {'false', '0', 'no', '', 'none'}:
        return False
    raise ValueError(f'Booleano GraphML no reconocido: {value!r}')


# -------------------------------------------------
# CARGAR GRAPHML
# -------------------------------------------------

print("Cargando GraphML...")

G = nx.read_graphml(RUTA)

parser = argparse.ArgumentParser(description='Carga Bilbao en Neo4j; modifica nodos y relaciones.')
parser.add_argument('--largest-component', action='store_true', help='Selecciona la mayor WCC en memoria antes de cargar; no borra datos de Neo4j.')
args = parser.parse_args()
if args.largest_component:
    G = G.subgraph(max(nx.weakly_connected_components(G), key=len)).copy()

print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())


# -------------------------------------------------
# CONEXIÓN A NEO4J
# -------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USUARIO, PASSWORD)
)


# -------------------------------------------------
# CREAR RESTRICCIÓN DE UNICIDAD
# -------------------------------------------------

with driver.session(database="neo4j") as session:

    session.run("""
        CREATE CONSTRAINT bilbao_node_id IF NOT EXISTS
        FOR (n:BilbaoNode)
        REQUIRE n.osmId IS UNIQUE
    """)


# -------------------------------------------------
# PREPARAR NODOS
# -------------------------------------------------

nodos = []

for node_id, datos in G.nodes(data=True):

    nodos.append({
        "osmId": str(node_id),
        "x": float(datos["x"]) if "x" in datos else None,
        "y": float(datos["y"]) if "y" in datos else None,
        "highway": str(datos.get("highway", "")),
        "street_count": int(datos.get("street_count", 0))
    })


# -------------------------------------------------
# INSERTAR NODOS POR LOTES
# -------------------------------------------------

print("\nInsertando nodos...")

with driver.session(database="neo4j") as session:

    for inicio in range(0, len(nodos), BATCH_NODOS):

        lote = nodos[inicio:inicio + BATCH_NODOS]

        session.run("""
            UNWIND $lote AS fila

            MERGE (n:BilbaoNode {osmId: fila.osmId})

            SET n.x = fila.x,
                n.y = fila.y,
                n.highway = fila.highway,
                n.street_count = fila.street_count
        """, lote=lote)

        print(
            f"Nodos procesados: "
            f"{min(inicio + BATCH_NODOS, len(nodos))}"
            f"/{len(nodos)}"
        )


# -------------------------------------------------
# PREPARAR RELACIONES
# -------------------------------------------------

relaciones = []

for origen, destino, key, datos in G.edges(
    keys=True,
    data=True
):

    relaciones.append({
        "origen": str(origen),
        "destino": str(destino),

        # Identificador único para conservar el multigrafo
        "relId": f"{origen}|{destino}|{key}",

        "key": str(key),

        "name": str(datos.get("name", "")),
        "highway": str(datos.get("highway", "")),

        "length": float(
            datos.get("length", 0.0)
        ),

        "oneway": graphml_bool(
            datos.get("oneway", False)
        ),

        "reversed": graphml_bool(
            datos.get("reversed", False)
        )
    })


# -------------------------------------------------
# INSERTAR RELACIONES POR LOTES
# -------------------------------------------------

print("\nInsertando relaciones...")

with driver.session(database="neo4j") as session:

    for inicio in range(
        0,
        len(relaciones),
        BATCH_RELACIONES
    ):

        lote = relaciones[
            inicio:inicio + BATCH_RELACIONES
        ]

        session.run("""
            UNWIND $lote AS fila

            MATCH (a:BilbaoNode {
                osmId: fila.origen
            })

            MATCH (b:BilbaoNode {
                osmId: fila.destino
            })

            MERGE (a)-[r:BILBAO_ROAD {
                relId: fila.relId
            }]->(b)

            SET r.key = fila.key,
                r.name = fila.name,
                r.highway = fila.highway,
                r.length = fila.length,
                r.oneway = fila.oneway,
                r.reversed = fila.reversed
        """, lote=lote)

        print(
            f"Relaciones procesadas: "
            f"{min(inicio + BATCH_RELACIONES, len(relaciones))}"
            f"/{len(relaciones)}"
        )


driver.close()

print("\nCarga finalizada correctamente.")
