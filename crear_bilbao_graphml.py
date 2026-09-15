from pathlib import Path
import math
import requests
import networkx as nx


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

# Centro aproximado de Bilbao
LAT = 43.2630
LON = -2.9350

# Radio en metros
RADIO = 1000

# Endpoint alternativo de Overpass
OVERPASS_URL = "https://overpass.private.coffee/api/interpreter"


# -------------------------------------------------
# FUNCIÓN PARA CALCULAR DISTANCIAS
# -------------------------------------------------

def distancia_metros(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia aproximada en metros
    entre dos coordenadas geográficas.
    """

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


# -------------------------------------------------
# CONSULTA A OPENSTREETMAP / OVERPASS
# -------------------------------------------------

print("Descargando red de calles de OpenStreetMap...")

consulta = f"""
[out:json][timeout:60];

way
  (around:{RADIO},{LAT},{LON})
  ["highway"~"^(primary|secondary|tertiary|residential|living_street|unclassified|service)$"];

out body;
>;
out skel qt;
"""

headers = {
    "User-Agent": "ModeladoGrafosCurso/1.0",
    "Accept": "application/json"
}

respuesta = requests.post(
    OVERPASS_URL,
    data={"data": consulta},
    headers=headers,
    timeout=90
)

respuesta.raise_for_status()

datos = respuesta.json()

print("Datos descargados correctamente")


# -------------------------------------------------
# RECUPERAR COORDENADAS DE LOS NODOS OSM
# -------------------------------------------------

coordenadas = {}

for elemento in datos["elements"]:

    if elemento["type"] == "node":

        coordenadas[elemento["id"]] = (
            elemento["lat"],
            elemento["lon"]
        )


# -------------------------------------------------
# CREAR GRAFO
# -------------------------------------------------

G = nx.DiGraph()


for elemento in datos["elements"]:

    if elemento["type"] != "way":
        continue

    tags = elemento.get("tags", {})

    nodos = elemento.get("nodes", [])

    nombre = str(
        tags.get(
            "name",
            "sin_nombre"
        )
    )

    tipo_via = str(
        tags.get(
            "highway",
            "desconocido"
        )
    )

    oneway = str(
        tags.get(
            "oneway",
            "no"
        )
    ).lower() in {
        "yes",
        "true",
        "1"
    }


    # Recorremos pares consecutivos de nodos de la calle
    for origen, destino in zip(
        nodos[:-1],
        nodos[1:]
    ):

        if (
            origen not in coordenadas
            or destino not in coordenadas
        ):
            continue

        lat1, lon1 = coordenadas[origen]
        lat2, lon2 = coordenadas[destino]

        distancia = distancia_metros(
            lat1,
            lon1,
            lat2,
            lon2
        )


        # -----------------------------
        # Nodo origen
        # -----------------------------

        G.add_node(
            origen,
            lat=float(lat1),
            lon=float(lon1)
        )


        # -----------------------------
        # Nodo destino
        # -----------------------------

        G.add_node(
            destino,
            lat=float(lat2),
            lon=float(lon2)
        )


        # -----------------------------
        # Relación origen -> destino
        # -----------------------------

        G.add_edge(
            origen,
            destino,
            length=float(distancia),
            name=nombre,
            highway=tipo_via,
            osmid=str(elemento["id"])
        )


        # -----------------------------
        # Si no es sentido único,
        # añadimos también destino -> origen
        # -----------------------------

        if not oneway:

            G.add_edge(
                destino,
                origen,
                length=float(distancia),
                name=nombre,
                highway=tipo_via,
                osmid=str(elemento["id"])
            )


# -------------------------------------------------
# MOSTRAR INFORMACIÓN DEL GRAFO
# -------------------------------------------------

print()
print("Red construida correctamente")
print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())


# -------------------------------------------------
# GUARDAR COMO GRAPHML
# -------------------------------------------------

archivo_salida = Path(__file__).resolve().parent / "bilbao_calles.graphml"

nx.write_graphml(
    G,
    archivo_salida
)

print()
print(
    f"Archivo creado correctamente: {archivo_salida}"
)