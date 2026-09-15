# Propuesta de publicación

## Texto para copiar

¿Qué cambia cuando miramos una ciudad como un grafo?

En mi formación en Data Engineering e Inteligencia Artificial he trabajado con Neo4j, Graph Data Science y Python para explorar esa pregunta. El recorrido empezó con Karate Club, Cora y LastFM: centralidad, comunidades, conectividad y similitud. Después llevé esos conceptos a la red urbana de Bilbao.

Tras seleccionar su componente principal, trabajé con 8.650 nodos conectados y 16.311 relaciones. A partir de ahí planteé dos problemas diferentes:

• Encontrar el camino mínimo entre Casco Viejo e Indautxu. Dijkstra y A* dieron una distancia de 1.736,81 m, con 24 nodos y 23 tramos.

• Conectar todos los nodos con el menor coste total. Con NetworkX transformé el grafo en simple y no dirigido y apliqué Kruskal: un árbol de 8.650 nodos y 8.649 aristas. Es un análisis matemático de conectividad, no una propuesta real de red viaria.

También comparé fuerza bruta, Greedy, backtracking y A* en un subgrafo pequeño. Greedy no llegó al destino: elegir lo que parece mejor en cada paso no garantiza encontrar una solución. La comparación es didáctica, no un benchmark de rendimiento.

Mi principal aprendizaje: antes de elegir un algoritmo hay que definir el problema, entender la dirección de las relaciones y revisar qué representan sus pesos. Explorar una red, encontrar una ruta y construir un MST responden a preguntas distintas.

Comparto las visualizaciones y el proyecto, con código, resultados, instrucciones y limitaciones:
[URL_DEL_REPOSITORIO]

#DataEngineering #GraphDataScience #Neo4j #Python #GraphAlgorithms #NetworkX

## Antes de publicar

Sustituir `[URL_DEL_REPOSITORIO]` por la URL real una vez creado y revisado el repositorio. Publicar únicamente el texto anterior y adjuntar los dos PNG, en este orden. La sección de instrucciones no forma parte del post.

## Imágenes

1. [bilbao_graph_algorithms.png](docs/images/bilbao_graph_algorithms.png): red de Bilbao en gris, MST en azul y ruta mínima en rojo; vista estática de las capas del HTML original, sin mapa base, con detalle de Casco Viejo–Indautxu.
   Texto alternativo: «Comparación de la red de Bilbao de 8.650 nodos, el árbol de Kruskal de 8.649 aristas y el camino mínimo de 1.736,81 metros entre Casco Viejo e Indautxu».
2. [graph_analysis_results.png](docs/images/graph_analysis_results.png): grafo Karate Club y grado de sus cuatro nodos más conectados, calculado desde el GraphML.
   Texto alternativo: «Karate Club: 34 nodos y 78 aristas. Los nodos 34, 1, 33 y 3 tienen respectivamente 17, 16, 12 y 10 conexiones».
