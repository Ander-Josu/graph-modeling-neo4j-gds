"""Crea bilbao_gds desde la base preparada. No elimina datos ni proyecciones."""
import os
from pathlib import Path
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
with GraphDataScience(
    os.environ['NEO4J_URI'],
    auth=(os.environ['NEO4J_USER'],os.environ['NEO4J_PASSWORD']),
    database='neo4j',
) as gds:
    nodes = int(gds.run_cypher('MATCH (n:BilbaoNode) RETURN count(n) AS n').iloc[0]['n'])
    edges = int(gds.run_cypher('MATCH (:BilbaoNode)-[r:BILBAO_ROAD]->(:BilbaoNode) RETURN count(r) AS n').iloc[0]['n'])
    if (nodes,edges) != (8650,16311):
        raise RuntimeError('Se requieren 8650 nodos y 16311 relaciones. Revisa la carga en una base dedicada; este script no elimina datos.')
    if bool(gds.graph.exists('bilbao_gds')['exists']):
        raise RuntimeError('bilbao_gds ya existe. Revisa su configuración antes de reutilizarlo; no se sobrescribe.')
    graph, result = gds.graph.project(
        'bilbao_gds',
        {'BilbaoNode': {'properties':['x','y']}},
        {'BILBAO_ROAD': {'orientation':'NATURAL','properties':['length']}},
    )
    print(result)
