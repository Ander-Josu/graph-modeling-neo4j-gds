# Fuentes, autoría y atribuciones

Autor del trabajo: **Ander Josu Garigorta Barba** · [GitHub](https://github.com/Ander-Josu).

Contexto confirmado: formación en Data Engineering e Inteligencia Artificial. Pendiente de completar: entidad/curso, autoría de los scripts iniciales y procedencia concreta del snapshot de Bilbao. No se atribuye al autor la creación de los datasets.

| Material | Fuente conocida | Estado |
|---|---|---|
| Karate Club | Loader `gds.graph.load_karate_club()`; exportación local `karate_club.graphml` | 34 nodos y 78 aristas verificados |
| Cora | Loader `gds.graph.load_cora()` | Se documenta su obtención; no se redistribuye una copia aparte |
| LastFM | Loader `gds.graph.load_lastfm()` | Se documenta su obtención; no se redistribuye una copia aparte |
| Bilbao | GraphML con identificadores OSM y metadatos OSMnx | Falta URL/proveedor y fecha de obtención del archivo concreto |
| HTML comparativo | Script Folium del proyecto; fondo Esri y atribución incluida | Conservado; las teselas se cargan al visualizarlo |
| PNG Bilbao | Coordenadas y capas del HTML original; Pillow | Sin teselas de terceros; © OpenStreetMap contributors |
| PNG Karate Club | GraphML local; NetworkX y Pillow | Grados calculados, layout con semilla 42 |

Fuentes técnicas:

- [Datasets del cliente GDS](https://neo4j.com/docs/graph-data-science-client/current/common-datasets/). La documentación identifica también el origen y condiciones de los datos; LastFM remite a HetRec 2011.
- [A* en GDS: requisitos de la heurística](https://neo4j.com/docs/graph-data-science/current/algorithms/astar/).
- [OpenStreetMap: atribución y licencia de datos](https://www.openstreetmap.org/copyright).

Los datos derivados de OpenStreetMap mantienen sus condiciones y atribución. La licencia del código es una decisión separada: no se ha añadido una licencia MIT ni otra licencia general sin confirmar los derechos sobre el material del curso. Completar esa decisión antes de presentar el repositorio como software con licencia abierta. La ausencia de `LICENSE` es deliberada y queda pendiente de la respuesta del autor.
