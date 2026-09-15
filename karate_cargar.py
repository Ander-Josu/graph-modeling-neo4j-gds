"""Carga la proyección inicial usada por comprobar_gds.py."""
import os
from pathlib import Path
from dotenv import load_dotenv
from graphdatascience import GraphDataScience

load_dotenv(Path(__file__).resolve().parent / '.env')
with GraphDataScience(
    os.environ['NEO4J_URI'],
    auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD']),
    database='neo4j',
) as gds:
    graph = gds.graph.load_karate_club()
    print(graph.name(), graph.node_count(), graph.relationship_count())
