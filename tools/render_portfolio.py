"""Dos figuras deterministas desde resultados reales, sin red ni Neo4j."""
from pathlib import Path
import json
import math
import re
import os
import networkx as nx
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'images'
BG, INK, BLUE, RED = '#f5f7fa', '#142a40', '#2379bd', '#cf343b'
SIZE = (2400, 1350)


def font(size, bold=False):
    custom = os.environ.get('PORTFOLIO_FONT_BOLD' if bold else 'PORTFOLIO_FONT')
    filename = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    candidates = [custom, filename,
                  str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/('arialbd.ttf' if bold else 'arial.ttf')),
                  '/usr/share/fonts/truetype/dejavu/'+filename,
                  '/System/Library/Fonts/Supplemental/'+('Arial Bold.ttf' if bold else 'Arial.ttf')]
    for candidate in candidates:
        if candidate:
            try:
                return ImageFont.truetype(candidate,size)
            except OSError:
                pass
    raise RuntimeError('Configura PORTFOLIO_FONT y PORTFOLIO_FONT_BOLD con rutas a fuentes TrueType.')


def text(draw, point, value, size=28, bold=False, fill=INK):
    draw.text(point,value,font=font(size,bold),fill=fill)


def project(points, box, bounds=None):
    x0,y0,x1,y1 = box
    if bounds is None:
        xs,ys=zip(*points)
        bounds = min(xs),min(ys),max(xs),max(ys)
    xmin,ymin,xmax,ymax=bounds
    scale = min((x1-x0)/(xmax-xmin),(y1-y0)/(ymax-ymin))
    midx,midy=(xmin+xmax)/2,(ymin+ymax)/2
    return [((x0+x1)/2+(x-midx)*scale,(y0+y1)/2-(y-midy)*scale) for x,y in points]


def generate_map():
    html = (ROOT/'parte2_bilbao'/'bilbao_comparacion_final.html').read_text(encoding='utf-8')
    pattern = r'L\.polyline\(\s*(\[\[.*?\]\]),\s*(\{.*?\})\s*\)'
    layers = {'#808080':[], 'blue':[], 'red':[]}
    for coords, style in re.findall(pattern,html,re.S):
        options=json.loads(style)
        if options.get('color') in layers:
            layers[options['color']].append(json.loads(coords))
    assert [len(layers[x]) for x in layers] == [16311,8649,1], 'Capas distintas: revisar el HTML.'
    report=json.loads((ROOT/'docs'/'validation_results.json').read_text(encoding='utf-8'))
    assert len(layers['red'][0]) == report['route']['nodes'] == 24
    graph=nx.read_graphml(ROOT/'parte2_bilbao'/'bilbao-3974.graphml')
    expected=[[float(graph.nodes[n]['y']),float(graph.nodes[n]['x'])] for n in report['route']['osm_ids']]
    assert expected == layers['red'][0], 'La ruta del HTML no coincide con la validación.'
    def xy(poly):
        return [((lon+2.935)*111320*math.cos(math.radians(43.263)),(lat-43.263)*111320) for lat,lon in poly]
    lines={key:[xy(poly) for poly in polys] for key,polys in layers.items()}
    route=lines['red'][0]
    image=Image.new('RGB',SIZE,BG)
    draw=ImageDraw.Draw(image)
    text(draw,(85,62),'BILBAO · UNA RED, DOS PROBLEMAS',52,True)
    text(draw,(85,136),'Conectar todos los nodos y encontrar el camino mínimo entre dos puntos',30)
    full_box=(70,240,1370,1100)
    detail_box=(1450,280,2320,780)
    draw.rounded_rectangle(full_box,radius=20,fill='white')
    draw.rounded_rectangle((1420,235,2340,820),radius=20,fill='white')
    allpoints=[p for line in lines['#808080'] for p in line]
    xs,ys=zip(*allpoints)
    full_bounds=(min(xs),min(ys),max(xs),max(ys))
    rx,ry=zip(*route)
    detail_bounds=(min(rx)-350,min(ry)-300,max(rx)+350,max(ry)+300)
    for box,bounds in [(full_box,full_bounds),(detail_box,detail_bounds)]:
        layer=Image.new('RGB',(box[2]-box[0],box[3]-box[1]),'white')
        pen=ImageDraw.Draw(layer)
        local_box=(25,25,layer.width-25,layer.height-25)
        for key,color,width in [('#808080','#c0c7ce',2),('blue',BLUE,2),('red','white',12),('red',RED,7)]:
            for line in lines[key]:
                pen.line(project(line,local_box,bounds),fill=color,width=width)
        image.paste(layer,(box[0],box[1]))
        if box == detail_box:
            points=project(route,local_box,bounds)
            for point,label,offset in [(points[0],'Casco Viejo',(-160,22)),(points[-1],'Indautxu',(-35,-53))]:
                x,y=point
                pen.ellipse((x-9,y-9,x+9,y+9),fill=RED,outline='white',width=3)
                tx,ty=x+offset[0],y+offset[1]
                label_box=pen.textbbox((tx,ty),label,font=font(26,True))
                pen.rectangle((label_box[0]-6,label_box[1]-5,label_box[2]+6,label_box[3]+5),fill='white')
                text(pen,(tx,ty),label,26,True)
            image.paste(layer,(box[0],box[1]))
    draw=ImageDraw.Draw(image)
    text(draw,(96,255),'RED COMPLETA',23,True)
    text(draw,(1450,243),'CASCO VIEJO → INDAUTXU',24,True)
    text(draw,(1460,850),'1.736,81 m',64,True,RED)
    text(draw,(1460,931),'Camino mínimo · 24 nodos · 23 tramos',27)
    text(draw,(1460,998),'8.650 nodos conectados',39,True)
    text(draw,(1460,1058),'Red: 16.311 aristas  |  MST: 8.649 aristas',27)
    text(draw,(1460,1104),'Kruskal: 647.491,25 m de longitud total',27)
    for x,color,label in [(95,'#808080','Red tras WCC'),(505,BLUE,'MST de Kruskal'),(930,RED,'Dijkstra / A*')]:
        draw.line((x,1174,x+55,1174),fill=color,width=8)
        text(draw,(x+75,1157),label,28)
    text(draw,(85,1220),'Datos y capas del HTML original · Vista estática sin mapa base · Segmentos entre nodos',25)
    text(draw,(85,1273),'© OpenStreetMap contributors · openstreetmap.org/copyright  |  MST: análisis matemático, sin propuesta viaria',22)
    image.save(OUT/'bilbao_graph_algorithms.png')


def generate_karate():
    graph=nx.read_graphml(ROOT/'karate_club.graphml')
    top=sorted(graph.degree,key=lambda item:(-item[1],int(item[0])))[:4]
    assert top == [('34',17),('1',16),('33',12),('3',10)]
    image=Image.new('RGB',SIZE,BG)
    draw=ImageDraw.Draw(image)
    text(draw,(85,62),'KARATE CLUB · ¿QUÉ NODOS CONCENTRAN CONEXIONES?',45,True)
    text(draw,(85,140),'Degree Centrality sobre el GraphML exportado del proyecto',31)
    layout=nx.spring_layout(graph,seed=42,iterations=150)
    points=project([(-float(p[1]),float(p[0])) for p in layout.values()],(115,280,1310,1080))
    positions=dict(zip(layout,points))
    for a,b in graph.edges:
        draw.line([positions[a],positions[b]],fill='#aabac7',width=3)
    highlighted={n for n,_ in top}
    for node,(x,y) in positions.items():
        radius=12+math.sqrt(graph.degree[node])*4
        color=BLUE if node in highlighted else '#dbe6ed'
        draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=color,outline='white',width=3)
        draw.text((x,y),node,font=font(22,node in highlighted),anchor='mm',fill='white' if node in highlighted else INK)
    text(draw,(1460,320),'MAYOR NÚMERO DE CONEXIONES',28,True)
    for i,(node,degree) in enumerate(top):
        y=425+i*130
        text(draw,(1460,y+8),f'Nodo {node}',31)
        draw.rounded_rectangle((1655,y,1655+degree*30,y+60),radius=5,fill=BLUE)
        text(draw,(1680+degree*30,y+5),str(degree),38,True)
    text(draw,(1460,995),'34 nodos · 78 aristas',45,True)
    text(draw,(1460,1070),'Grafo simple no dirigido',29)
    text(draw,(1460,1114),'Tamaño de nodo según su grado',27)
    text(draw,(85,1207),'El grado mide conexiones directas. No equivale a PageRank ni identifica comunidades.',29)
    text(draw,(85,1271),'Fuente: karate_club.graphml · IDs conservados · Layout NetworkX con semilla 42 · Resultado verificado localmente',22)
    image.save(OUT/'graph_analysis_results.png')


if __name__ == '__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    generate_map()
    generate_karate()
    print('Generadas exactamente dos imágenes PNG de 2400 × 1350 px.')
