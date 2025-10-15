# Accidentes Viales en Hermosillo

## Descripción del Proyecto
Este proyecto busca contestar la siguiente pregunta:

> ¿Cuales son las principales causas de accidentes de trafico en Hermosillo y que factores atribuyen a ello?

## Fuentes de Datos primarias
Los datasets descargados son:
- Accidentes de trafico por [Accidentes de Tránsito Terrestre en Zonas Urbanas y Suburbanas (ATUS)](https://www.google.com/url?q=https%3A%2F%2Fwww.inegi.org.mx%2Fprogramas%2Faccidentes%2F%23datos_abiertos) <br>
(Series de tiempo, Datos georeferenciados, Datos cualitativos y cuantitativos, Datos en forma de texto)
      
- Accidentes de trafico por [Datos AXA de percances viales](https://i2ds.org/datos-abiertos/) <br>
(Series de tiempo, Datos georeferenciados, Datos cualitativos y cuantitativos, Datos en forma de texto)
- Datos del clima de [Open-Meteo](https://open-meteo.com/en/docs) <br>
  (Series de tiempo, Datos georeferenciados, Datos cuantitativos)

## Publico Objetivo
Este proyecto esta destinado a:
- El *Sector Publico*
- A *tomadores de decisiones* en el área vial

---

# Proyecto Ciencia de Datos

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Analisis con datos sobre una problematica real

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         proyecto_ciencia_de_datos and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── proyecto_ciencia_de_datos   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes proyecto_ciencia_de_datos a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------
## Inicio Rápido del Proyecto

<font color='#4169E1'><strong>1. Requisitos del Sistema</strong></font>

Antes de utilizar el proyecto, aseguráte de tener instalado:

- Python 3.13, ya que el entorno virtual se crea usando la versión de Python activa. Puedes verificar la versión usa el comando en terminal con:

```powershell
python3 --version
```

- La herramienta `make`, el cual puedes verificar en terminal:

```powershell
make --version
```

Dado que `make` tiene distintas formas de obtenerse en Windows, recomendamos leer la guía [Acciones de GitHub y MakeFile: Una introducción práctica](#https://www.datacamp.com/es/tutorial/makefile-github-actions-tutorial) para su instalación. Asimismo, la publicación aborda sistemas macOS/Linux.

<font color='#4169E1'><strong>2. Creación y ejecución del entorno virtual</strong></font>

En terminal ejecuta:

```powershell
make create_environment
```

El comando crea el ambiente virtual dentro de la carpeta raíz del proyecto bajo el nomvre `.venv` y con la versión actual de Python del sistema operativo.

Activa el entorno virtual en terminal manualmente, para Windows (CMD o PowerShell):

```powershell
./.venv/Scripts/activate
```

Para sistemas macOS o Linux:

```
source ./.venv/Scripts/activate
```

El nombre del entorno cambiará y `.venv` aparecerá en la línea de comandos, indicando que se encuentra activo. Puedes confirmar el entorno virtual con el comando `pip list`, el cual te mostrará las librerías cargadas en el entorno. Únicamente debería aparecer `pip` en la lista.

<font color='#4169E1'><strong>3. Pipeline de Datos</strong></font>


Con el entorno virtual activado, ejecuta el comando de pipeline para descarga la información y convertir en formato raw y tidy (automáticamente carga las librerías requeridas al entorno virtual).

```powershell
make pipeline
```
El comando guardara los archivos originales en `/data/raw/` y su forma tidy en `/data/processed/`.