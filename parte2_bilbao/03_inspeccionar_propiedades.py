from pathlib import Path
import networkx as nx

ruta = Path(__file__).resolve().parent / "bilbao-3974.graphml"

print("Cargando grafo...")
G = nx.read_graphml(ruta)

print("\nTIPO DE GRAFO")
print(type(G))

# ----------------------------
# Primer nodo
# ----------------------------

primer_nodo, datos_nodo = next(iter(G.nodes(data=True)))

print("\nPRIMER NODO")
print("ID:", primer_nodo)
print("Propiedades:")
for clave, valor in datos_nodo.items():
    print(f"  {clave}: {valor}")

# ----------------------------
# Primera relación
# ----------------------------

if G.is_multigraph():
    origen, destino, key, datos_relacion = next(
        iter(G.edges(keys=True, data=True))
    )

    print("\nPRIMERA RELACIÓN")
    print("Origen:", origen)
    print("Destino:", destino)
    print("Key:", key)

else:
    origen, destino, datos_relacion = next(
        iter(G.edges(data=True))
    )

    print("\nPRIMERA RELACIÓN")
    print("Origen:", origen)
    print("Destino:", destino)

print("Propiedades:")
for clave, valor in datos_relacion.items():
    print(f"  {clave}: {valor}")