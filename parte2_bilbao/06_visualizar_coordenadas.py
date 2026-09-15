from pathlib import Path
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network


# -------------------------------------------------
# CONEXIÓN A NEO4J
# -------------------------------------------------

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

URI = os.getenv("NEO4J_URI")
USUARIO = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

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
            WHERE n.x IS NOT NULL
              AND n.y IS NOT NULL

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
                r.name AS nombre,
                r.length AS longitud
        """)
    )

driver.close()


print("Nodos:", len(nodos))
print("Relaciones:", len(relaciones))


# -------------------------------------------------
# OBTENER LÍMITES DE LAS COORDENADAS
# -------------------------------------------------

xs = [float(n["x"]) for n in nodos]
ys = [float(n["y"]) for n in nodos]

min_x = min(xs)
max_x = max(xs)

min_y = min(ys)
max_y = max(ys)


# -------------------------------------------------
# ESCALAR COORDENADAS
# -------------------------------------------------

def escalar_x(x):

    if max_x == min_x:
        return 0

    return (
        (float(x) - min_x)
        / (max_x - min_x)
        * 1200
    )


def escalar_y(y):

    if max_y == min_y:
        return 0

    # En pantalla el eje Y aumenta hacia abajo,
    # por eso invertimos el valor.
    return -(
        (float(y) - min_y)
        / (max_y - min_y)
        * 900
    )


# -------------------------------------------------
# CREAR VISUALIZACIÓN PYVIS
# -------------------------------------------------

net = Network(
    cdn_resources="in_line",
    height="850px",
    width="100%",
    directed=False,
    bgcolor="white"
)

# Desactivamos la física para respetar
# las coordenadas reales de los nodos.
net.toggle_physics(False)


# -------------------------------------------------
# AÑADIR NODOS
# -------------------------------------------------

print("Añadiendo nodos a la visualización...")

for n in nodos:

    net.add_node(
        n["id"],

        # Usamos un espacio para impedir que PyVis
        # sustituya una etiqueta vacía por el ID.
        label=" ",

        x=escalar_x(n["x"]),
        y=escalar_y(n["y"]),

        size=1.5,
        shape="dot",

        # El ID sigue disponible al pasar el ratón.
        title=f"OSM ID: {n['id']}",

        # Ocultamos el texto de la etiqueta.
        font={"size": 0},

        # Impide que PyVis mueva el nodo.
        fixed=True
    )


# -------------------------------------------------
# AÑADIR RELACIONES
# -------------------------------------------------

print("Añadiendo relaciones a la visualización...")

for r in relaciones:

    nombre = (
        r["nombre"]
        if r["nombre"]
        else "Sin nombre"
    )

    if r["longitud"] is not None:
        longitud = round(
            float(r["longitud"]),
            1
        )
    else:
        longitud = "?"

    net.add_edge(
        r["origen"],
        r["destino"],

        # Información disponible al pasar el ratón.
        title=(
            f"{nombre}"
            f"<br>Longitud: {longitud} m"
        ),

        # Línea fina para evitar saturar el grafo.
        width=0.5
    )


# -------------------------------------------------
# GUARDAR HTML
# -------------------------------------------------

archivo = Path(__file__).resolve().parent / "bilbao_coordenadas.html"

net.write_html(
    str(archivo),
    open_browser=False
)


print()
print("Visualización creada correctamente:")
print(archivo)
print()
print("Nodos visualizados:", len(nodos))
print("Relaciones visualizadas:", len(relaciones))
