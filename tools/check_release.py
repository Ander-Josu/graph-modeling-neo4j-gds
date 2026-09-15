"""Comprueba los archivos publicables sin imprimir secretos ni conectar a servicios."""
from pathlib import Path
import ast
import json
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    command = ['git','-c',f'safe.directory={ROOT.as_posix()}','-C',str(ROOT)]
    output = subprocess.check_output(command+['ls-files','--cached','--others','--exclude-standard','-z'])
    names = sorted(set(output.decode('utf-8').strip('\0').split('\0')))
    paths = [ROOT/name for name in names if name]
    assert all(not any(part in {'.env','.venv','.portfolio-venv','.uv-cache','cache','__pycache__'} for part in p.relative_to(ROOT).parts) for p in paths)
    # Lee solo en memoria los valores sensibles locales para comprobar que no se copiaron.
    secrets=[]
    env=ROOT/'.env'
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key,value=line.split('=',1)
                if re.search(r'password|secret|token|api.?key',key,re.I):
                    value=value.strip().strip('\"\'')
                    if len(value)>=4:
                        secrets.append(value)
    findings=[]
    tokens=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}')
    for p in paths:
        if p.suffix.lower() in {'.png','.jpg','.zip'}:
            continue
        content=p.read_text(encoding='utf-8-sig',errors='replace')
        if any(value in content for value in secrets):
            findings.append({'file':p.relative_to(ROOT).as_posix(),'reason':'Coincidencia con un valor sensible de .env'})
        if tokens.search(content):
            findings.append({'file':p.relative_to(ROOT).as_posix(),'reason':'Patrón de clave privada o token'})
        if p.suffix=='.py':
            tree=ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node,(ast.Assign,ast.AnnAssign)):
                    value=node.value
                    targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                    sensitive=any(isinstance(t,ast.Name) and re.search(r'password|passwd|secret|token|api_?key',t.id,re.I) for t in targets)
                    if sensitive and isinstance(value,ast.Constant) and isinstance(value.value,str) and value.value:
                        findings.append({'file':p.relative_to(ROOT).as_posix(),'line':node.lineno,'reason':'Asignación literal a variable sensible'})
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    assert len(re.findall(r'!\[.*?\]\(',readme))==2
    pngs=sorted((ROOT/'docs'/'images').glob('*.png'))
    assert len(pngs)==2
    images={}
    for p in pngs:
        with Image.open(p) as im:
            assert im.size==(2400,1350)
            images[p.name]={'size':list(im.size),'bytes':p.stat().st_size}
    broken=[]
    for p in [x for x in paths if x.suffix=='.md']:
        content=p.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',content):
            if '://' in target or target.startswith('#'):
                continue
            if not (p.parent/target.split('#')[0]).exists():
                broken.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
    post=(ROOT/'LINKEDIN_POST.md').read_text(encoding='utf-8').split('## Texto para copiar\n\n')[1].split('\n## Antes de publicar')[0].strip()
    assert 1300 <= len(post) <= 1800, f'Post: {len(post)} caracteres'
    assert 5 <= len(re.findall(r'(?<!\w)#\w+',post)) <=8
    # Verifica el arreglo de booleanos sin importar/ejecutar el cargador de Neo4j.
    loader=ast.parse((ROOT/'parte2_bilbao'/'04_cargar_neo4j.py').read_text(encoding='utf-8-sig'))
    definition=next(n for n in loader.body if isinstance(n,ast.FunctionDef) and n.name=='graphml_bool')
    namespace={}
    exec(compile(ast.Module(body=[definition],type_ignores=[]),'<boolean conversion>','exec'),namespace)
    parse=namespace['graphml_bool']
    assert parse('False') is False and parse(False) is False and parse('True') is True and parse('0') is False
    try:
        parse('unexpected')
    except ValueError:
        pass
    else:
        raise AssertionError('Debe rechazar valores ambiguos')
    report={'files_reviewed':len(paths),'total_bytes':sum(p.stat().st_size for p in paths),
            'largest_file':max(paths,key=lambda p:p.stat().st_size).relative_to(ROOT).as_posix(),
            'files_over_50_mib':[p.relative_to(ROOT).as_posix() for p in paths if p.stat().st_size>50*1024**2],
            'env_present_and_excluded':env.exists() and env not in paths,'secret_findings':findings,
            'broken_markdown_links':broken,'images':images,'linkedin_characters':len(post),
            'boolean_conversion_checks':'passed','neo4j_executed':False}
    (ROOT/'docs'/'release_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert not findings and not broken


if __name__=='__main__':
    main()
