# Imágenes de GitHub y LinkedIn

Se utilizan exactamente estos dos PNG de 2400 × 1350 px (16:9):

1. `docs/images/bilbao_graph_algorithms.png`: capas reales del HTML comparativo, con vista general y detalle de la ruta.
2. `docs/images/graph_analysis_results.png`: Karate Club, grado y nodos principales calculados desde el GraphML.

Regeneración: `python tools/verify_project.py` y después `python tools/render_portfolio.py`.

## Procedencia visual

El navegador de la sesión bloqueó la apertura del HTML local. La primera imagen es una representación estática de las coordenadas extraídas de ese HTML; no es una captura del navegador ni una imagen generativa. No incluye teselas Esri. Conserva los colores, datos, puntos representativos y atribución OSM. La segunda no simula una captura de Neo4j ni asigna comunidades inexistentes en el archivo.

## Captura opcional del mapa original

Si prefieres sustituir la primera imagen por una captura con mapa base:

1. Abre localmente `parte2_bilbao/bilbao_comparacion_final.html` en tu navegador con conexión a Internet.
2. Usa un área de página de 2400 × 1350 px, o 1920 × 1080 px como mínimo, con zoom del navegador al 100 %.
3. Activa «Mapa base Esri», «Red original de Bilbao», «MST de Kruskal», «Ruta Dijkstra / A*» y «Casco Viejo e Indautxu».
4. Comienza con zoom cartográfico 13. Centra Bilbao y comprueba que se ven los dos marcadores, toda la ruta roja y suficiente red azul. Baja a 12 si se recortan los extremos; sube a 14 si la ruta es demasiado pequeña y prefieres destacar el centro.
5. Mantén la leyenda completa abajo a la izquierda y las atribuciones del mapa visibles. Espera a que las teselas carguen; cierra popups y aparta el cursor.
6. Captura solo el contenido de la página: sin barra de direcciones, escritorio, terminal ni rutas personales.
7. Guarda sustituyendo `docs/images/bilbao_graph_algorithms.png`, manteniendo dos imágenes principales. Si lo sustituyes, actualiza el pie de imagen del README y del post para describirlo como captura y no como vista sin mapa base.

La captura es opcional: los dos PNG estáticos sirven para la propuesta actual.
