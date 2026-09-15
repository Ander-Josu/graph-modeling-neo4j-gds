# Entrega de la preparación del portfolio

## Archivos creados

- Presentación: `README.md`, `LINKEDIN_POST.md`.
- Configuración: `.gitignore`, `.gitattributes`, `.env.example`, `requirements.txt`.
- Documentación: `docs/REPRODUCIBILITY.md`, `docs/SOURCES.md`, `docs/IMAGES.md`, `docs/VALIDATION.md`, `docs/PUBLISHING.md`, `docs/DELIVERY.md`.
- Resultados de comprobación: `docs/validation_results.json`, `docs/release_checks.json`.
- Imágenes: `docs/images/bilbao_graph_algorithms.png`, `docs/images/graph_analysis_results.png`.
- Herramientas: `tools/verify_project.py`, `tools/render_portfolio.py`, `tools/check_release.py`.
- Preparación adicional: `karate_cargar.py`, `parte2_bilbao/05_proyectar_gds.py`.
- Repositorio Git local y entorno auxiliar `.portfolio-venv` (este último excluido de Git).

## Archivos modificados

Rutas relativas a `__file__`, configuración `.env` explícita y ajustes indicados en `VALIDATION.md`:

- `comprobar_gds.py`.
- `cora_cargar.py`, `cora_pagerank.py`, `cora_scc.py`, `cora_wcc.py`.
- `crear_bilbao_graphml.py`, `exportar_karate_club.py`.
- `karate_louvain.py`, `karate_page_rank.py`, `karate_undirected.py`.
- `lastfm_cargar.py`, `lastfm_fastrp.py`, `lastfm_knn.py`, `lastfm_node_similarity.py`.
- `parte2_bilbao/02_contar_grafo.py`, `03_inspeccionar_propiedades.py`, `03_visualizar_grafo.py`, `04_cargar_neo4j.py`, `06_visualizar_coordenadas.py`, `09_comparar_estrategias.py`, `09_preparar_subgrafo.py`, `10_kruskal.py`, `11_visualizar_kruskal.py`, `12_visualizar_kruskal_mapa.py`, `13_mapa_comparativo_final.py`.

No se modificaron el `.env`, los GraphML originales ni el HTML comparativo existente. Las correcciones no se han aplicado a los datos persistentes de Neo4j.

## Archivos movidos

Ninguno. Se conserva la estructura de ejercicios y se añaden `docs/` y `tools/`.

## Archivos excluidos de Git

- `.env` y variantes privadas: credenciales locales.
- `.venv/`, `.portfolio-venv/`, `.uv-cache/`, `cache/`, `__pycache__/`, bytecode y configuración del editor: entorno local o contenido recreable.
- `albania/`, `albania-ALB_graphml.zip`, `inspeccionar_fier.py`: exploración ajena al relato principal. Se conservan localmente.
- `parte2_bilbao/bilbao_coordenadas.html`, `bilbao_kruskal_mapa.html`, `bilbao_kruskal_mst.html` y `lib/`: vistas intermedias y bibliotecas recreables. El HTML comparativo sí se conserva.
- `bilbao_calles.graphml`: salida de una descarga alternativa, distinta del snapshot del caso de estudio.

## README

Terminado para revisión: resultados, evidencia, algoritmos, limitaciones, ejecución y atribuciones. Contiene exactamente dos imágenes. Los resultados comunicados por el autor se distinguen de los recalculados localmente.

## Imágenes

Ambos PNG están generados a 2400 × 1350 px y revisados visualmente. La primera figura representa las capas reales del HTML sin mapa base; incluye ampliación de la ruta. La segunda muestra Karate Club y sus grados. La captura con fondo cartográfico es una alternativa manual opcional, documentada en `IMAGES.md`.

## LinkedIn

`LINKEDIN_POST.md` está preparado: 1.588 caracteres en el cuerpo, seis hashtags, dos imágenes en orden y textos alternativos. Falta sustituir la URL cuando exista el repositorio.

## Seguridad

El `.env` permanece privado y excluido. El escáner no ha encontrado valores sensibles del `.env`, patrones de tokens ni contraseñas literales en los archivos seleccionados para Git. No muestra valores de secretos. El informe documenta el alcance de esta comprobación.

## Requirements

Dependencias directas: NetworkX 3.6.1, Neo4j 6.3.0, GraphDataScience 1.22, python-dotenv 1.2.3, PyVis 0.3.2, Folium 0.20.0, Matplotlib 3.11.2, Pillow 12.3.0 y Requests 2.34.2. No se ha usado un `pip freeze` completo.

## Validación

Sintaxis de 31 scripts, verificación numérica local de Bilbao y grados de Karate Club, comparación de estrategias, comprobación del MST y de los hashes de entrada, enlaces Markdown, dos PNG y longitud del post. También se ha verificado la conversión de booleanos sin ejecutar el cargador. Véanse los informes JSON.

No se probó una integración con Neo4j ni una instalación completa desde cero. Windows bloquea Matplotlib; las imágenes se generan con NetworkX y Pillow en el entorno auxiliar Python 3.12.14. El servidor GDS y las muestras persistentes siguen siendo prerrequisitos externos documentados.

## Pendientes

1. Confirmar la entidad/curso, autoría inicial de los scripts y procedencia concreta del GraphML de Bilbao.
2. Elegir licencia del código cuando se hayan aclarado esos derechos; `LICENSE` no se ha creado.
3. Revisar los documentos y las imágenes.
4. Crear el repositorio remoto y añadir su URL real al post.
5. Si se desea validar la parte GDS de extremo a extremo, preparar un servidor y completar las muestras manuales que faltaban.

## GitHub

Repositorio local inicializado en `main`; no hay publicación remota. Los comandos exactos para commit, remote y push están en [PUBLISHING.md](PUBLISHING.md). No se ha hecho push, creado un repositorio remoto ni publicado en LinkedIn.
