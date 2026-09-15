# Reproducibilidad y orden de ejecución

## Dos recorridos

El recorrido local está validado y usa los GraphML y el HTML conservados. El recorrido Neo4j requiere preparar un servidor y sus proyecciones: no se ha ejecutado durante esta revisión. Todas las instrucciones parten de la raíz del repositorio y usan el entorno de `requirements.txt`.

## Recorrido local

```powershell
python tools/verify_project.py
python tools/render_portfolio.py
python parte2_bilbao/02_contar_grafo.py
python parte2_bilbao/03_inspeccionar_propiedades.py
python parte2_bilbao/09_comparar_estrategias.py
```

`verify_project.py` selecciona la mayor WCC en memoria, calcula Dijkstra, A* y Kruskal y contrasta el MST guardado. No sustituye ningún GraphML. Escribe el informe JSON, incluidos los hashes SHA-256 de los cuatro archivos de entrada. Los segundos medidos varían entre ejecuciones.

`render_portfolio.py` necesita ese JSON y el HTML comparativo original. Extrae sus coordenadas y estilos sin ejecutar JavaScript; comprueba 16.311 segmentos grises, 8.649 azules y una ruta roja de 24 nodos. Genera dos PNG sin servicios cartográficos externos.

Las vistas locales adicionales son `03_visualizar_grafo.py` (abre Matplotlib), `11_visualizar_kruskal.py` (genera PyVis) y `12_visualizar_kruskal_mapa.py` (genera Folium desde el MST guardado). Las vistas PyVis se generan con bibliotecas incorporadas; las de Folium necesitan recursos web para visualizarse completamente.

## Neo4j: preparación

1. Configura una instancia local y el plugin Graph Data Science compatible con el cliente Python. Los scripts usan la base `neo4j`.
2. Copia `.env.example` a `.env` y establece tus credenciales. No publiques `.env`.
3. Anota las versiones reales del servidor con `CALL dbms.components()` y `RETURN gds.version()`. La revisión comprobó el cliente Python 1.22, no la versión del plugin instalado.
4. Utiliza una base dedicada a estos ejercicios. Los loaders crean proyecciones; algunas fases escriben datos persistentes. No sobrescribas una proyección existente sin revisar su contenido.

### Karate Club

```powershell
python karate_cargar.py
python comprobar_gds.py
python karate_undirected.py
python karate_page_rank.py
python karate_louvain.py
```

`karate_cargar.py` crea `karate_club`; `karate_undirected.py` crea `karate_club_undirected`. Repetir un loader con el mismo nombre puede fallar si ya existe. Los scripts no eliminan proyecciones automáticamente.

Louvain calcula resultados y después actualiza nodos persistentes `KaratePerson` por `karateId`. La creación de esos nodos y de `KNOWS_KARATE` fue una fase manual del ejercicio que no está incluida. Sin ella, la consulta `MATCH ... SET` no actualiza nodos aunque el script imprima su mensaje final. El exportador también necesita esa muestra; se ha añadido una comprobación que detiene la exportación si la muestra está incompleta, conservando el GraphML existente. Para la reproducción local ya se incluye la exportación de 34 nodos y 78 aristas.

El loader incluido en el cliente revisado asigna IDs 1–34 a Karate Club. No se debe generalizar que los IDs devueltos por GDS siempre son IDs de negocio.

### Cora

```powershell
python cora_cargar.py
python cora_pagerank.py
python cora_wcc.py
python cora_scc.py
```

Usan la proyección `cora`, dirigida por defecto. La actualización de PageRank espera una muestra persistente `CoraPaper` con `paperId` coherente con los IDs del loader. Su creación no está automatizada; si falta, el análisis puede ejecutarse pero no se guarda esa muestra. La impresión de «guardado» por sí sola no verifica que se haya actualizado ningún nodo.

### LastFM

```powershell
python lastfm_cargar.py
python lastfm_node_similarity.py
python lastfm_fastrp.py
python lastfm_knn.py
```

Usan `lastfm`, no dirigida por defecto. FastRP añade `fastrp_embedding` a la proyección, con dimensión 64 y relaciones `LISTEN_TO`. KNN necesita que esa propiedad siga en memoria; filtra nodos `User` y usa `topK=5`. Persiste una muestra de veinte parejas deduplicadas con `LastFMUser` y `SIMILAR_KNN`. Los scripts originales no fijan semilla, por lo que los pares y puntuaciones pueden variar.

### Bilbao

En una base dedicada vacía, o que ya contenga exactamente el componente principal:

```powershell
python parte2_bilbao/04_cargar_neo4j.py --largest-component
python parte2_bilbao/05_proyectar_gds.py
```

La opción nueva selecciona la WCC en NetworkX **antes de cargar**. Conserva el GraphML y no borra los nodos de otras componentes que puedan existir previamente en Neo4j. Sin esa opción, el cargador conserva su comportamiento de cargar los 8.746 nodos originales. `05_proyectar_gds.py` exige 8.650 nodos y 16.311 relaciones, se detiene si `bilbao_gds` existe y crea una proyección dirigida con `x`, `y` y `length`. No limpia datos ni reemplaza proyecciones.

Con `bilbao_gds` disponible pueden ejecutarse:

```powershell
python parte2_bilbao/06_visualizar_coordenadas.py
python parte2_bilbao/09_preparar_subgrafo.py
python parte2_bilbao/09_comparar_estrategias.py
python parte2_bilbao/10_kruskal.py
python parte2_bilbao/11_visualizar_kruskal.py
python parte2_bilbao/12_visualizar_kruskal_mapa.py
python parte2_bilbao/13_mapa_comparativo_final.py
```

Estas fases regeneran sus archivos de salida. Los scripts 06 y 10 leen datos persistentes; 09 y 13 calculan caminos con la proyección GDS. Deben corresponder al mismo conjunto de nodos. Las consultas originales de BFS, DFS y A* no estaban guardadas como archivos; sus cifras históricas se conservan como resultados aportados, no como una ejecución automatizada validada aquí.

## Fuera del recorrido principal

`crear_bilbao_graphml.py` descarga un grafo distinto por Overpass: radio de 1.000 m, otras etiquetas de coordenadas (`lat/lon`) y modelo `DiGraph`. No genera el dataset `bilbao-3974.graphml` ni debe usarse como sustituto. `inspeccionar_fier.py` y los datos de Albania se conservan localmente y se excluyen de Git.
