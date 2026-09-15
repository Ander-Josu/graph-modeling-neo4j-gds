from pathlib import Path
import networkx as nx
import folium


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

ARCHIVO_ENTRADA = Path(__file__).resolve().parent / "bilbao_kruskal_mst.graphml"
ARCHIVO_SALIDA = Path(__file__).resolve().parent / "bilbao_kruskal_mapa.html"

ORIGEN_ID = "1132519581"   # Casco Viejo
DESTINO_ID = "245939768"   # Indautxu


# -------------------------------------------------
# CARGAR GRAFO
# -------------------------------------------------

print("Cargando MST de Kruskal...")

G = nx.read_graphml(ARCHIVO_ENTRADA)

print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())


# -------------------------------------------------
# OBTENER CENTRO DEL MAPA
# -------------------------------------------------

latitudes = []
longitudes = []

for _, datos in G.nodes(data=True):
    if datos.get("y") is not None and datos.get("x") is not None:
        latitudes.append(float(datos["y"]))
        longitudes.append(float(datos["x"]))

centro_lat = sum(latitudes) / len(latitudes)
centro_lon = sum(longitudes) / len(longitudes)


# -------------------------------------------------
# CREAR MAPA
# -------------------------------------------------

print("Creando mapa base...")

m = folium.Map(
    location=[centro_lat, centro_lon],
    zoom_start=13,
    tiles="CartoDB positron"
)


# -------------------------------------------------
# DIBUJAR RELACIONES DEL MST
# -------------------------------------------------

print("Dibujando relaciones del MST sobre el mapa...")

relaciones_dibujadas = 0

for origen, destino, datos in G.edges(data=True):

    if origen not in G.nodes or destino not in G.nodes:
        continue

    nodo_origen = G.nodes[origen]
    nodo_destino = G.nodes[destino]

    if (
        nodo_origen.get("y") is None or nodo_origen.get("x") is None or
        nodo_destino.get("y") is None or nodo_destino.get("x") is None
    ):
        continue

    lat1 = float(nodo_origen["y"])
    lon1 = float(nodo_origen["x"])
    lat2 = float(nodo_destino["y"])
    lon2 = float(nodo_destino["x"])

    nombre = datos.get("name", "Sin nombre")
    longitud = datos.get("length", "?")

    try:
        longitud = round(float(longitud), 2)
    except:
        pass

    popup_texto = f"""
    <b>Calle:</b> {nombre}<br>
    <b>Longitud:</b> {longitud} m
    """

    folium.PolyLine(
        locations=[
            [lat1, lon1],
            [lat2, lon2]
        ],
        color="blue",
        weight=2,
        opacity=0.65,
        popup=popup_texto
    ).add_to(m)

    relaciones_dibujadas += 1


# -------------------------------------------------
# MARCAR CASCO VIEJO E INDAUTXU
# -------------------------------------------------

print("Añadiendo marcadores...")

if ORIGEN_ID in G.nodes:
    nodo = G.nodes[ORIGEN_ID]
    folium.Marker(
        location=[float(nodo["y"]), float(nodo["x"])],
        popup="Casco Viejo",
        tooltip="Casco Viejo",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

if DESTINO_ID in G.nodes:
    nodo = G.nodes[DESTINO_ID]
    folium.Marker(
        location=[float(nodo["y"]), float(nodo["x"])],
        popup="Indautxu",
        tooltip="Indautxu",
        icon=folium.Icon(color="red", icon="stop")
    ).add_to(m)


# -------------------------------------------------
# GUARDAR MAPA
# -------------------------------------------------

m.save(ARCHIVO_SALIDA)

print()
print("MAPA CREADO CORRECTAMENTE")
print("-------------------------")
print("Archivo:", ARCHIVO_SALIDA)
print("Relaciones dibujadas:", relaciones_dibujadas)