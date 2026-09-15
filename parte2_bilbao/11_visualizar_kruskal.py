from pathlib import Path
import networkx as nx
from pyvis.network import Network


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

ARCHIVO_ENTRADA = Path(__file__).resolve().parent / "bilbao_kruskal_mst.graphml"
ARCHIVO_SALIDA = Path(__file__).resolve().parent / "bilbao_kruskal_mst.html"

ORIGEN_ID = "1132519581"      # Casco Viejo
DESTINO_ID = "245939768"      # Indautxu


# -------------------------------------------------
# CARGAR MST
# -------------------------------------------------

print("Cargando MST de Kruskal...")

G = nx.read_graphml(ARCHIVO_ENTRADA)

print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())


# -------------------------------------------------
# OBTENER RANGO DE COORDENADAS
# -------------------------------------------------

xs = []
ys = []

for _, datos in G.nodes(data=True):

    if (
        datos.get("x") is not None
        and datos.get("y") is not None
    ):

        xs.append(float(datos["x"]))
        ys.append(float(datos["y"]))


min_x = min(xs)
max_x = max(xs)

min_y = min(ys)
max_y = max(ys)


# -------------------------------------------------
# ESCALAR COORDENADAS PARA PYVIS
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

    # Negativo para que norte quede arriba
    return -(
        (float(y) - min_y)
        / (max_y - min_y)
        * 900
    )


# -------------------------------------------------
# CREAR VISUALIZACIÓN
# -------------------------------------------------

net = Network(
    cdn_resources="in_line",
    height="850px",
    width="100%",
    directed=False,
    bgcolor="white"
)

net.toggle_physics(False)


# -------------------------------------------------
# AÑADIR NODOS
# -------------------------------------------------

print("Añadiendo nodos...")

for nodo_id, datos in G.nodes(data=True):

    x = float(datos["x"])
    y = float(datos["y"])

    # Valores normales
    label = " "
    size = 1.5
    color = "#4A90E2"
    font = {
        "size": 0
    }

    titulo = f"OSM ID: {nodo_id}"

    # Casco Viejo
    if nodo_id == ORIGEN_ID:

        label = "Casco Viejo"
        size = 12
        color = "#2E8B57"

        font = {
            "size": 16,
            "color": "#1B5E20"
        }

        titulo = (
            "Casco Viejo"
            f"<br>OSM ID: {nodo_id}"
        )

    # Indautxu
    elif nodo_id == DESTINO_ID:

        label = "Indautxu"
        size = 12
        color = "#D9534F"

        font = {
            "size": 16,
            "color": "#8B0000"
        }

        titulo = (
            "Indautxu"
            f"<br>OSM ID: {nodo_id}"
        )

    net.add_node(
        nodo_id,
        label=label,
        x=escalar_x(x),
        y=escalar_y(y),
        size=size,
        shape="dot",
        color=color,
        title=titulo,
        font=font,
        fixed=True
    )


# -------------------------------------------------
# AÑADIR RELACIONES DEL MST
# -------------------------------------------------

print("Añadiendo relaciones del MST...")

for origen, destino, datos in G.edges(data=True):

    longitud = datos.get("length")

    if longitud is not None:

        longitud = round(
            float(longitud),
            1
        )

    else:

        longitud = "?"

    nombre = datos.get(
        "name",
        "Sin nombre"
    )

    net.add_edge(
        origen,
        destino,
        title=(
            f"{nombre}"
            f"<br>Longitud: {longitud} m"
        ),
        width=0.6
    )


# -------------------------------------------------
# GUARDAR HTML
# -------------------------------------------------

net.write_html(
    str(ARCHIVO_SALIDA),
    open_browser=False
)


print()
print("VISUALIZACIÓN CREADA")
print("---------------------")
print("Archivo:", ARCHIVO_SALIDA)
print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())
print()

print(
    "Casco Viejo:",
    ORIGEN_ID
)

print(
    "Indautxu:",
    DESTINO_ID
)
