from pathlib import Path
import math
import time
import heapq
import networkx as nx


# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

ARCHIVO = Path(__file__).resolve().parent / "subgrafo_comparacion.graphml"

ORIGEN = "1132519581"
DESTINO = "245939768"

# Seguridad para fuerza bruta
MAX_RUTAS_BRUTE_FORCE = 200000

# Permitimos rutas de hasta 35 tramos.
# El camino óptimo que encontramos con Dijkstra tenía 23.
MAX_PROFUNDIDAD = 35


# -------------------------------------------------
# DISTANCIA HAVERSINE
# -------------------------------------------------

def distancia_haversine(lat1, lon1, lat2, lon2):

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
# CARGAR GRAFO
# -------------------------------------------------

print("Cargando subgrafo...")

G_multi = nx.read_graphml(ARCHIVO)

print("Nodos:", G_multi.number_of_nodes())
print("Relaciones:", G_multi.number_of_edges())


# -------------------------------------------------
# CONVERTIR MULTIDIGRAFO EN DIGRAFO
#
# Si existen varias relaciones entre A y B,
# conservamos la de menor longitud.
# -------------------------------------------------

G = nx.DiGraph()

for nodo, datos in G_multi.nodes(data=True):

    G.add_node(
        nodo,
        x=float(datos["x"]),
        y=float(datos["y"])
    )


for origen, destino, datos in G_multi.edges(data=True):

    longitud = float(
        datos.get("length", 1.0)
    )

    if G.has_edge(origen, destino):

        longitud_actual = G[origen][destino]["length"]

        if longitud < longitud_actual:
            G[origen][destino]["length"] = longitud

    else:

        G.add_edge(
            origen,
            destino,
            length=longitud
        )


print()
print("Grafo simplificado:")
print("Nodos:", G.number_of_nodes())
print("Relaciones:", G.number_of_edges())


# -------------------------------------------------
# FUNCIÓN PARA CALCULAR EL COSTE DE UNA RUTA
# -------------------------------------------------

def coste_ruta(grafo, ruta):

    coste = 0.0

    for i in range(len(ruta) - 1):

        coste += grafo[
            ruta[i]
        ][
            ruta[i + 1]
        ]["length"]

    return coste


# =================================================
# 1. BRUTE FORCE
# =================================================

def brute_force(grafo, origen, destino):

    mejor_ruta = None
    mejor_coste = float("inf")

    rutas_evaluadas = 0
    limite_alcanzado = False

    inicio = time.perf_counter()

    for ruta in nx.all_simple_paths(
        grafo,
        source=origen,
        target=destino,
        cutoff=MAX_PROFUNDIDAD
    ):

        rutas_evaluadas += 1

        coste = coste_ruta(
            grafo,
            ruta
        )

        if coste < mejor_coste:

            mejor_coste = coste
            mejor_ruta = ruta

        if rutas_evaluadas >= MAX_RUTAS_BRUTE_FORCE:

            limite_alcanzado = True
            break

    tiempo = time.perf_counter() - inicio

    return {
        "ruta": mejor_ruta,
        "coste": mejor_coste,
        "explorados": rutas_evaluadas,
        "tiempo": tiempo,
        "limite": limite_alcanzado
    }


# =================================================
# 2. GREEDY
#
# En cada paso elegimos el vecino que está
# geográficamente más cerca del destino.
# =================================================

def greedy(grafo, origen, destino):

    actual = origen

    ruta = [actual]

    visitados = {
        actual
    }

    nodos_explorados = 1

    destino_x = grafo.nodes[destino]["x"]
    destino_y = grafo.nodes[destino]["y"]

    inicio = time.perf_counter()

    while actual != destino:

        candidatos = []

        for vecino in grafo.successors(actual):

            if vecino in visitados:
                continue

            x = grafo.nodes[vecino]["x"]
            y = grafo.nodes[vecino]["y"]

            heuristica = distancia_haversine(
                y,
                x,
                destino_y,
                destino_x
            )

            candidatos.append(
                (
                    heuristica,
                    vecino
                )
            )

        nodos_explorados += len(candidatos)

        # Si no podemos avanzar, Greedy falla.
        if not candidatos:

            tiempo = (
                time.perf_counter()
                - inicio
            )

            return {
                "ruta": None,
                "coste": float("inf"),
                "explorados": nodos_explorados,
                "tiempo": tiempo,
                "limite": False
            }

        candidatos.sort()

        _, siguiente = candidatos[0]

        ruta.append(siguiente)

        visitados.add(siguiente)

        actual = siguiente

    tiempo = (
        time.perf_counter()
        - inicio
    )

    return {
        "ruta": ruta,
        "coste": coste_ruta(
            grafo,
            ruta
        ),
        "explorados": nodos_explorados,
        "tiempo": tiempo,
        "limite": False
    }


# =================================================
# 3. BACKTRACKING
#
# Explora caminos y retrocede.
#
# Usamos poda: si el coste parcial ya supera
# la mejor solución encontrada, abandonamos
# esa rama.
# =================================================

def backtracking(grafo, origen, destino):

    mejor_ruta = None
    mejor_coste = float("inf")

    llamadas = 0

    inicio = time.perf_counter()

    def explorar(
        actual,
        ruta,
        visitados,
        coste_actual
    ):

        nonlocal mejor_ruta
        nonlocal mejor_coste
        nonlocal llamadas

        llamadas += 1

        # Poda por coste
        if coste_actual >= mejor_coste:
            return

        if actual == destino:

            mejor_coste = coste_actual
            mejor_ruta = ruta.copy()

            return

        # Control de profundidad
        if len(ruta) - 1 >= MAX_PROFUNDIDAD:
            return

        for vecino in grafo.successors(actual):

            if vecino in visitados:
                continue

            coste_arista = grafo[
                actual
            ][
                vecino
            ]["length"]

            visitados.add(vecino)
            ruta.append(vecino)

            explorar(
                vecino,
                ruta,
                visitados,
                coste_actual + coste_arista
            )

            # BACKTRACK
            ruta.pop()
            visitados.remove(vecino)

    explorar(
        origen,
        [origen],
        {origen},
        0.0
    )

    tiempo = (
        time.perf_counter()
        - inicio
    )

    return {
        "ruta": mejor_ruta,
        "coste": mejor_coste,
        "explorados": llamadas,
        "tiempo": tiempo,
        "limite": False
    }


# =================================================
# 4. A* HEURÍSTICO
#
# Implementación propia para poder contar
# cuántos nodos expande.
# =================================================

def astar_heuristico(
    grafo,
    origen,
    destino
):

    destino_x = grafo.nodes[
        destino
    ]["x"]

    destino_y = grafo.nodes[
        destino
    ]["y"]

    def heuristica(nodo):

        x = grafo.nodes[nodo]["x"]
        y = grafo.nodes[nodo]["y"]

        return distancia_haversine(
            y,
            x,
            destino_y,
            destino_x
        )

    inicio = time.perf_counter()

    cola = []

    heapq.heappush(
        cola,
        (
            heuristica(origen),
            0.0,
            origen
        )
    )

    mejor_coste = {
        origen: 0.0
    }

    anterior = {}

    expandidos = 0

    cerrados = set()

    while cola:

        _, coste_actual, actual = (
            heapq.heappop(cola)
        )

        if actual in cerrados:
            continue

        cerrados.add(actual)

        expandidos += 1

        if actual == destino:
            break

        for vecino in grafo.successors(actual):

            coste_nuevo = (
                coste_actual
                + grafo[
                    actual
                ][
                    vecino
                ]["length"]
            )

            if (
                vecino not in mejor_coste
                or coste_nuevo
                < mejor_coste[vecino]
            ):

                mejor_coste[
                    vecino
                ] = coste_nuevo

                anterior[
                    vecino
                ] = actual

                prioridad = (
                    coste_nuevo
                    + heuristica(vecino)
                )

                heapq.heappush(
                    cola,
                    (
                        prioridad,
                        coste_nuevo,
                        vecino
                    )
                )

    tiempo = (
        time.perf_counter()
        - inicio
    )

    if destino not in mejor_coste:

        return {
            "ruta": None,
            "coste": float("inf"),
            "explorados": expandidos,
            "tiempo": tiempo,
            "limite": False
        }

    # Reconstruir ruta
    ruta = [
        destino
    ]

    actual = destino

    while actual != origen:

        actual = anterior[
            actual
        ]

        ruta.append(actual)

    ruta.reverse()

    return {
        "ruta": ruta,
        "coste": mejor_coste[destino],
        "explorados": expandidos,
        "tiempo": tiempo,
        "limite": False
    }


# =================================================
# EJECUTAR COMPARACIÓN
# =================================================

print()
print("=" * 60)
print("COMPARACIÓN DE ESTRATEGIAS")
print("=" * 60)


print()
print("1. BRUTE FORCE...")
resultado_brute = brute_force(
    G,
    ORIGEN,
    DESTINO
)


print("2. GREEDY...")
resultado_greedy = greedy(
    G,
    ORIGEN,
    DESTINO
)


print("3. BACKTRACKING...")
resultado_backtracking = backtracking(
    G,
    ORIGEN,
    DESTINO
)


print("4. HEURÍSTICO A*...")
resultado_astar = astar_heuristico(
    G,
    ORIGEN,
    DESTINO
)


# -------------------------------------------------
# MOSTRAR RESULTADOS
# -------------------------------------------------

resultados = {
    "Brute Force": resultado_brute,
    "Greedy": resultado_greedy,
    "Backtracking": resultado_backtracking,
    "A* Heurístico": resultado_astar
}


print()
print("=" * 60)
print("RESULTADOS")
print("=" * 60)


for nombre, resultado in resultados.items():

    print()
    print(nombre)
    print("-" * len(nombre))

    if resultado["ruta"] is None:

        print("No encontró ruta.")

    else:

        print(
            "Distancia:",
            round(
                resultado["coste"],
                2
            ),
            "m"
        )

        print(
            "Nodos en la ruta:",
            len(
                resultado["ruta"]
            )
        )

        print(
            "Tramos:",
            len(
                resultado["ruta"]
            ) - 1
        )

    print(
        "Explorados:",
        resultado["explorados"]
    )

    print(
        "Tiempo:",
        round(
            resultado["tiempo"],
            6
        ),
        "s"
    )

    if resultado["limite"]:

        print(
            "AVISO: se alcanzó el límite "
            "de fuerza bruta."
        )


print()
print("=" * 60)
print("REFERENCIA")
print("=" * 60)

print(
    "Dijkstra en Neo4j:",
    "1736.81 m"
)