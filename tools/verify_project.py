"""Validación local: no conecta a Neo4j ni modifica los datasets."""
from pathlib import Path
import ast
import hashlib
import json
import math
import runpy
import contextlib
import io
import os
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
BILBAO = ROOT / 'parte2_bilbao'


def haversine(a, b):
    lat1, lat2 = map(math.radians, (float(a['y']), float(b['y'])))
    dlat = lat2 - lat1
    dlon = math.radians(float(b['x']) - float(a['x']))
    v = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(v)))


def main():
    scripts = [p for p in ROOT.rglob('*.py') if not any(x in p.parts for x in ('.venv', '.portfolio-venv', '.uv-cache', 'cache', '__pycache__'))]
    imports = set()
    for p in scripts:
        tree = ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p.relative_to(ROOT)))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(x.name.split('.')[0] for x in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split('.')[0])
    raw = nx.read_graphml(BILBAO / 'bilbao-3974.graphml')
    components = sorted(nx.weakly_connected_components(raw), key=len, reverse=True)
    graph = raw.subgraph(components[0]).copy()
    for _, _, data in graph.edges(data=True):
        data['length'] = float(data['length'])
        assert math.isfinite(data['length']) and data['length'] >= 0
    source, target = '1132519581', '245939768'
    route = nx.dijkstra_path(graph, source, target, weight='length')
    distance = nx.dijkstra_path_length(graph, source, target, weight='length')
    astar = nx.astar_path(graph, source, target, heuristic=lambda a,b: haversine(graph.nodes[a],graph.nodes[b]), weight='length')
    simple = nx.Graph()
    simple.add_nodes_from(graph.nodes(data=True))
    for a, b, data in graph.edges(data=True):
        if not simple.has_edge(a,b) or data['length'] < simple[a][b]['length']:
            simple.add_edge(a,b,length=data['length'])
    mst = nx.minimum_spanning_tree(simple, algorithm='kruskal', weight='length')
    saved = nx.read_graphml(BILBAO / 'bilbao_kruskal_mst.graphml')
    karate = nx.read_graphml(ROOT / 'karate_club.graphml')
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        comparison = runpy.run_path(str(BILBAO / '09_comparar_estrategias.py'))
    results = {k:{'distance_m':v['coste'] if v['ruta'] else None,'explored':v['explorados'], 'route_nodes':len(v['ruta']) if v['ruta'] else 0, 'seconds':v['tiempo'], 'limit_reached':v['limite']} for k,v in comparison['resultados'].items()}
    assert (len(raw),raw.number_of_edges(),len(components)) == (8746,16429,38)
    assert (len(graph),graph.number_of_edges()) == (8650,16311)
    assert (len(route),round(distance,2)) == (24,1736.81)
    assert nx.is_tree(mst) and nx.is_tree(saved) and set(saved)==set(mst)
    assert math.isclose(mst.size(weight='length'),saved.size(weight='length'),abs_tol=1e-6)
    assert round(mst.size(weight='length'),2)==647491.25
    assert [r['explored'] for r in results.values()] == [2,38,826,42]
    report = {
        'syntax_checked':len(scripts), 'imports':sorted(imports),
        'original':{'nodes':len(raw),'edges':raw.number_of_edges(),'type':type(raw).__name__},
        'wcc':{'components':len(components),'nodes':len(graph),'edges':graph.number_of_edges(),'removed_nodes':len(raw)-len(graph)},
        'route':{'distance_m':distance,'nodes':len(route),'edges':len(route)-1,'osm_ids':route,'astar_same_path':route == astar},
        'simple_undirected':{'nodes':len(simple),'edges':simple.number_of_edges()},
        'mst':{'nodes':len(mst),'edges':mst.number_of_edges(),'length_m':mst.size(weight='length'),'is_tree':nx.is_tree(mst)},
        'saved_mst':{'nodes':len(saved),'edges':saved.number_of_edges(),'length_m':saved.size(weight='length'),'is_tree':nx.is_tree(saved),'same_nodes':set(saved)==set(mst)},
        'karate':{'nodes':len(karate),'edges':karate.number_of_edges(),'top_degree':sorted(karate.degree,key=lambda x:(-x[1],int(x[0])))[:4]},
        'subgraph':{'nodes':len(comparison['G_multi']),'edges':comparison['G_multi'].number_of_edges()},
        'strategies':results,
        'sha256':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BILBAO/'bilbao-3974.graphml',BILBAO/'bilbao_kruskal_mst.graphml',BILBAO/'subgrafo_comparacion.graphml',ROOT/'karate_club.graphml']}
    }
    output = ROOT / 'docs' / 'validation_results.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
