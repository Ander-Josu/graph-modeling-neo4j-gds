# Revisión técnica

## Alcance

Se inspeccionaron los scripts Python, los GraphML de entrada/salida, los HTML y sus dependencias locales. No había README, imágenes PNG ni repositorio Git iniciales. El proyecto incluía un `.env`, entorno virtual, caché, un ZIP y grafos exploratorios de Albania. No se eliminó ningún dataset, no se ejecutaron cargas ni operaciones en Neo4j y no se publicó contenido.

## Resultados corroborados

`tools/verify_project.py` analiza la sintaxis de todos los scripts propios y recalcula los resultados usando los archivos locales:

- Bilbao original: 8.746 nodos / 16.429 aristas, `MultiDiGraph`.
- WCC: 38 componentes; mayor de 8.650 nodos / 16.311 aristas; 96 nodos descartados en memoria.
- Dijkstra y A* de NetworkX: mismo camino de 24 nodos y 1.736,81 m.
- Grafo simple no dirigido: 8.650 nodos / 12.172 aristas.
- Kruskal: 8.649 aristas, 647.491,25 m; `nx.is_tree=True`. El MST guardado tiene el mismo conjunto de nodos y coste total, y también es un árbol.
- Estrategias: Brute Force 2 rutas; Greedy sin solución, contador 38; Backtracking 826 llamadas; A* 42 expansiones.
- Karate Club: 34 nodos / 78 aristas y grados 17, 16, 12 y 10 para los nodos 34, 1, 33 y 3.

Los recuentos y distancias coinciden con el resumen del autor. Los tiempos medidos son distintos entre ejecuciones, como es esperable; se guardan en el JSON y no se presentan como benchmark. [Informe completo](validation_results.json).

## Correcciones y matices

1. **Rutas:** la configuración `.env` y los archivos de entrada/salida se resuelven desde `__file__`. Se conserva la estructura original.
2. **Booleanos:** `bool('False')` devuelve `True`. El cargador de Bilbao ahora interpreta explícitamente los textos booleanos y rechaza valores ambiguos. Se comprueba la función aislada sin importar el cargador ni acceder a Neo4j.
3. **Dependencia inicial ausente:** se añadió `karate_cargar.py` para crear la proyección `karate_club` utilizada por Degree Centrality.
4. **Preparación de Bilbao:** se añadió `--largest-component` al cargador y un script para proyectar GDS. La selección sucede en memoria; no elimina los datos existentes de la base.
5. **Exportación vacía:** el exportador de Karate Club se detiene si la muestra no tiene 34 nodos y 78 aristas; conserva la exportación existente.
6. **PyVis:** convierte los destinos `Path` a texto y genera HTML con bibliotecas incorporadas para evitar dependencias relativas en `lib/`.
7. **A* GDS:** la documentación actual describe Haversine en millas náuticas, mientras `length` está en metros. No se afirma una ventaja de exploración de esa ejecución. El A* Python del subgrafo usa metros; las implementaciones y sus mediciones se distinguen.
8. **Kruskal:** tener N−1 aristas no basta por sí solo para demostrar que un grafo es un árbol. El verificador comprueba también la estructura.
9. **Subgrafo:** el radio de 80 m se mide respecto a nodos de la ruta, no respecto a un buffer continuo de calles.
10. **Persistencia:** `MATCH ... SET` en Louvain y Cora necesita muestras previamente creadas. Sus mensajes de «guardado» originales no verifican el número de nodos actualizados. La creación de esas muestras no estaba incluida.

## Imágenes

El generador extrae del HTML 16.311 segmentos de red, 8.649 del MST y una ruta de 24 puntos. Verifica que las coordenadas de esa ruta coinciden con los IDs obtenidos por Dijkstra sobre el GraphML. El segundo gráfico usa los grados reales de Karate Club. Se han revisado los PNG visualmente; no contienen credenciales, escritorio ni rutas personales.

## Entornos y comprobaciones pendientes

El entorno original contiene Python 3.14.6 y las versiones directas de `requirements.txt`. NetworkX permitió ejecutar la validación, pero Windows bloqueó una DLL de Matplotlib. Un entorno aislado con Python 3.12.14, NetworkX 3.6.1 y Pillow 12.3.0 permite generar las imágenes sin Matplotlib. El script original `03_visualizar_grafo.py` sí usa Matplotlib y puede requerir un entorno donde esa biblioteca esté admitida.

No se realizó una instalación limpia completa de todas las dependencias ni una prueba de integración con el servidor. La disponibilidad de paquetes se revisó en el entorno original; eso no equivale a garantizar que todas sus DLL se puedan cargar. Los scripts de Neo4j/GDS se revisaron estáticamente, sin ejecutar escrituras.

No se reejecutaron los resultados históricos de PageRank, Louvain, Cora, LastFM, BFS y DFS en GDS. El GraphML de Karate Club no contiene comunidades ni PageRank; por eso la segunda imagen muestra grado. Faltan la versión exacta del servidor y la procedencia específica del snapshot de Bilbao.

## Seguridad y selección de archivos

`tools/check_release.py` revisa los archivos que Git incluiría, comprueba que `.env` y los entornos están excluidos y busca coincidencias con sus valores sensibles sin imprimirlos. Añade detección de patrones de tokens y asignaciones literales a variables sensibles. Es una revisión acotada, no una garantía absoluta frente a cualquier secreto posible.

El informe [release_checks.json](release_checks.json) recoge los hallazgos, enlaces locales, dimensiones de las dos imágenes, tamaño de archivos y longitud del texto de LinkedIn. No se usa Git LFS. Se conserva el HTML comparativo (aproximadamente 13,4 MB) y el GraphML de Bilbao (12,7 MB); los HTML intermedios quedan excluidos.
