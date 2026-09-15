from pathlib import Path
import os
import networkx as nx
import folium

from dotenv import load_dotenv
from neo4j import GraphDatabase


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

ARCHIVO_MST = Path(__file__).resolve().parent / "bilbao_kruskal_mst.graphml"
ARCHIVO_SALIDA = Path(__file__).resolve().parent / "bilbao_comparacion_final.html"

ORIGEN_ID = "1132519581"   # Casco Viejo
DESTINO_ID = "245939768"   # Indautxu


# -------------------------------------------------
# VARIABLES DE ENTORNO
# -------------------------------------------------

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

URI = os.getenv("NEO4J_URI")
USUARIO = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")


# -------------------------------------------------
# CONECTAR A NEO4J
# -------------------------------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USUARIO, PASSWORD)
)


# -------------------------------------------------
# LEER NODOS
# -------------------------------------------------

print("Leyendo nodos de la red original...")

with driver.session(database="neo4j") as session:

    nodos_neo4j = list(
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


coordenadas = {}

for nodo in nodos_neo4j:

    coordenadas[nodo["id"]] = {
        "x": float(nodo["x"]),
        "y": float(nodo["y"])
    }


print(
    "Nodos originales:",
    len(coordenadas)
)


# -------------------------------------------------
# LEER RELACIONES ORIGINALES
# -------------------------------------------------

print("Leyendo relaciones de la red original...")

with driver.session(database="neo4j") as session:

    relaciones_originales = list(
        session.run("""
            MATCH (a:BilbaoNode)-[r:BILBAO_ROAD]->(b:BilbaoNode)
            RETURN
                a.osmId AS origen,
                b.osmId AS destino
        """)
    )


print(
    "Relaciones originales:",
    len(relaciones_originales)
)


# -------------------------------------------------
# DIJKSTRA
# -------------------------------------------------

print("Calculando camino Casco Viejo -> Indautxu...")

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

        YIELD totalCost, nodeIds

        RETURN
            totalCost,
            [
                nodeId IN nodeIds |
                gds.util.asNode(nodeId).osmId
            ] AS ruta
        """,
        origen=ORIGEN_ID,
        destino=DESTINO_ID
    ).single()


driver.close()


distancia_dijkstra = float(
    resultado["totalCost"]
)

ruta_dijkstra = list(
    resultado["ruta"]
)


print(
    "Distancia Dijkstra:",
    round(distancia_dijkstra, 2),
    "m"
)

print(
    "Nodos del camino:",
    len(ruta_dijkstra)
)


# -------------------------------------------------
# CARGAR MST DE KRUSKAL
# -------------------------------------------------

print("Cargando MST de Kruskal...")

mst = nx.read_graphml(
    ARCHIVO_MST
)

print(
    "Nodos MST:",
    mst.number_of_nodes()
)

print(
    "Relaciones MST:",
    mst.number_of_edges()
)


# -------------------------------------------------
# LÍMITES DEL MAPA
# -------------------------------------------------

latitudes = [
    datos["y"]
    for datos in coordenadas.values()
]

longitudes = [
    datos["x"]
    for datos in coordenadas.values()
]


centro_lat = (
    min(latitudes)
    + max(latitudes)
) / 2

centro_lon = (
    min(longitudes)
    + max(longitudes)
) / 2


# -------------------------------------------------
# CREAR MAPA SIN FONDO PREDETERMINADO
# -------------------------------------------------

print("Creando mapa...")

m = folium.Map(
    location=[
        centro_lat,
        centro_lon
    ],
    zoom_start=12,
    tiles=None,
    control_scale=True,
    prefer_canvas=True
)


# -------------------------------------------------
# MAPA BASE ESRI
# -------------------------------------------------

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/"
        "World_Street_Map/MapServer/"
        "tile/{z}/{y}/{x}"
    ),
    attr=(
        "Tiles © Esri — "
        "Source: Esri, HERE, Garmin, "
        "USGS, Intermap, INCREMENT P, "
        "NRCan, Esri Japan, METI, "
        "Esri China (Hong Kong), "
        "OpenStreetMap contributors, "
        "and the GIS User Community"
    ),
    name="Mapa base Esri",
    overlay=False,
    control=True
).add_to(m)


# -------------------------------------------------
# CAPAS
# -------------------------------------------------

capa_original = folium.FeatureGroup(
    name="Red original de Bilbao",
    show=True
)

capa_mst = folium.FeatureGroup(
    name="MST de Kruskal",
    show=True
)

capa_dijkstra = folium.FeatureGroup(
    name="Ruta Dijkstra / A*",
    show=True
)

capa_puntos = folium.FeatureGroup(
    name="Casco Viejo e Indautxu",
    show=True
)


# =================================================
# RED ORIGINAL
# =================================================

print("Dibujando red original...")

contador_original = 0

for relacion in relaciones_originales:

    origen = relacion["origen"]
    destino = relacion["destino"]

    if (
        origen not in coordenadas
        or destino not in coordenadas
    ):
        continue

    nodo_a = coordenadas[origen]
    nodo_b = coordenadas[destino]

    folium.PolyLine(
        locations=[
            [
                nodo_a["y"],
                nodo_a["x"]
            ],
            [
                nodo_b["y"],
                nodo_b["x"]
            ]
        ],
        color="#808080",
        weight=1,
        opacity=0.20
    ).add_to(capa_original)

    contador_original += 1


# =================================================
# MST DE KRUSKAL
# =================================================

print("Dibujando MST de Kruskal...")

contador_mst = 0

for origen, destino, datos in mst.edges(data=True):

    if (
        origen not in coordenadas
        or destino not in coordenadas
    ):
        continue

    nodo_a = coordenadas[origen]
    nodo_b = coordenadas[destino]

    folium.PolyLine(
        locations=[
            [
                nodo_a["y"],
                nodo_a["x"]
            ],
            [
                nodo_b["y"],
                nodo_b["x"]
            ]
        ],
        color="blue",
        weight=2,
        opacity=0.75
    ).add_to(capa_mst)

    contador_mst += 1


# =================================================
# RUTA DIJKSTRA / A*
# =================================================

print("Dibujando camino mínimo...")

coordenadas_ruta = []

for node_id in ruta_dijkstra:

    if node_id in coordenadas:

        nodo = coordenadas[node_id]

        coordenadas_ruta.append(
            [
                nodo["y"],
                nodo["x"]
            ]
        )


folium.PolyLine(
    locations=coordenadas_ruta,
    color="red",
    weight=6,
    opacity=0.95,
    tooltip=(
        "Camino mínimo: "
        f"{round(distancia_dijkstra, 2)} m"
    )
).add_to(capa_dijkstra)


# =================================================
# CASCO VIEJO
# =================================================

if ORIGEN_ID in coordenadas:

    origen = coordenadas[
        ORIGEN_ID
    ]

    folium.Marker(
        location=[
            origen["y"],
            origen["x"]
        ],
        tooltip="Casco Viejo",
        popup=(
            "<b>Casco Viejo</b><br>"
            "Origen del recorrido"
        ),
        icon=folium.Icon(
            color="green",
            icon="play"
        )
    ).add_to(capa_puntos)


# =================================================
# INDAUTXU
# =================================================

if DESTINO_ID in coordenadas:

    destino = coordenadas[
        DESTINO_ID
    ]

    folium.Marker(
        location=[
            destino["y"],
            destino["x"]
        ],
        tooltip="Indautxu",
        popup=(
            "<b>Indautxu</b><br>"
            "Destino del recorrido"
        ),
        icon=folium.Icon(
            color="red",
            icon="stop"
        )
    ).add_to(capa_puntos)


# -------------------------------------------------
# AÑADIR CAPAS
# -------------------------------------------------

capa_original.add_to(m)
capa_mst.add_to(m)
capa_dijkstra.add_to(m)
capa_puntos.add_to(m)


# -------------------------------------------------
# SELECTOR DE CAPAS
# -------------------------------------------------

folium.LayerControl(
    collapsed=False
).add_to(m)


# -------------------------------------------------
# LEYENDA
# -------------------------------------------------

leyenda = f"""
<div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    width: 330px;
    background-color: white;
    border: 2px solid grey;
    z-index: 9999;
    font-size: 14px;
    padding: 12px;
    border-radius: 6px;
">

<b>Comparación de algoritmos - Bilbao</b>

<br><br>

<span style="
    display:inline-block;
    width:22px;
    height:4px;
    background:#808080;
"></span>
&nbsp; Red original

<br>

<span style="
    display:inline-block;
    width:22px;
    height:4px;
    background:blue;
"></span>
&nbsp; MST de Kruskal

<br>

<span style="
    display:inline-block;
    width:22px;
    height:5px;
    background:red;
"></span>
&nbsp; Dijkstra / A*

<br><br>

<b>Red original:</b>
{len(coordenadas)} nodos /
{len(relaciones_originales)} relaciones

<br>

<b>MST:</b>
{mst.number_of_nodes()} nodos /
{mst.number_of_edges()} relaciones

<br>

<b>Ruta mínima:</b>
{round(distancia_dijkstra, 2)} m

<br>

<b>Nodos de la ruta:</b>
{len(ruta_dijkstra)}

</div>
"""


m.get_root().html.add_child(
    folium.Element(
        leyenda
    )
)


# -------------------------------------------------
# AJUSTAR ZOOM
# -------------------------------------------------

m.fit_bounds(
    [
        [
            min(latitudes),
            min(longitudes)
        ],
        [
            max(latitudes),
            max(longitudes)
        ]
    ]
)


# -------------------------------------------------
# GUARDAR
# -------------------------------------------------

m.save(
    ARCHIVO_SALIDA
)


print()
print("=" * 55)
print("MAPA COMPARATIVO CREADO")
print("=" * 55)

print(
    "Archivo:",
    ARCHIVO_SALIDA
)

print(
    "Red original:",
    contador_original,
    "relaciones"
)

print(
    "MST Kruskal:",
    contador_mst,
    "relaciones"
)

print(
    "Ruta Dijkstra/A*:",
    round(
        distancia_dijkstra,
        2
    ),
    "m"
)