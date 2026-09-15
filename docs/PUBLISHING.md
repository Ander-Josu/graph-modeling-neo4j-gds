# Publicación en GitHub y LinkedIn

Autor: Ander Josu Garigorta Barba. Perfil confirmado: [Ander-Josu](https://github.com/Ander-Josu).

Nombre propuesto: `graph-modeling-neo4j-gds`. No se ha comprobado su disponibilidad ni se ha creado un repositorio remoto.

Descripción propuesta: «Modelado y análisis de grafos con Neo4j GDS y Python: centralidad, comunidades y similitud, con Bilbao como caso de rutas mínimas y MST».

Temas propuestos: `neo4j`, `graph-data-science`, `networkx`, `python`, `graph-algorithms`, `geospatial`, `data-engineering`.

## Revisión previa

Revisa el README, los dos PNG y el texto de LinkedIn. Completa en `SOURCES.md` la entidad del curso, el origen del snapshot de Bilbao y la autoría del código inicial. Decide la licencia del código una vez aclarados esos derechos. No se ha añadido un `LICENSE` genérico a los datasets.

## Comandos locales

El repositorio local está inicializado en `main`. No se ha creado un commit ni configurado un remote. Desde PowerShell:

```powershell
Set-Location 'C:\Users\ajgar\Desktop\CURSO DATA ENGINEERING\Modelado_Grafos_2'
git add .
git status
git diff --cached --stat
git commit -m "Add graph modeling and Neo4j GDS project"
```

Si Git pide identidad, configura tu nombre y el correo que quieras asociar al commit; no se ha inventado ni configurado un correo en esta preparación.

Después crea tú el repositorio en GitHub, vacío, sin generar allí README, licencia ni `.gitignore`. Copia su URL exacta. Sustituye el marcador entre comillas en los siguientes comandos; no es una URL existente:

```powershell
git remote add origin '<URL_DEL_REPOSITORIO>'
git remote -v
git branch -M main
git push -u origin main
```

Si ya has añadido un remote entretanto, consulta `git remote -v` y revisa su destino antes de añadir otro; no sobrescribas uno existente por seguir estas instrucciones.

No se ha ejecutado `git push`. Estos comandos son para utilizarlos cuando hayas revisado el resultado y quieras publicarlo.

## LinkedIn

Una vez publicado GitHub, sustituye `[URL_DEL_REPOSITORIO]` en `LINKEDIN_POST.md`. Copia únicamente «Texto para copiar» y adjunta, en orden, `bilbao_graph_algorithms.png` y `graph_analysis_results.png`. Incluye los textos alternativos propuestos. El cuerpo tiene 1.588 caracteres antes de sustituir la URL.

## Revalidar antes de publicar

Con el entorno local preparado durante esta revisión:

```powershell
.\.portfolio-venv\Scripts\python.exe tools/verify_project.py
.\.portfolio-venv\Scripts\python.exe tools/render_portfolio.py
.\.portfolio-venv\Scripts\python.exe tools/check_release.py
git add .
git status
```

El entorno `.portfolio-venv` es local y no se publica. En otro equipo, instala las dependencias según el README. Los scripts de validación y figuras requieren NetworkX y Pillow; Matplotlib solo se utiliza en la visualización topológica original.
