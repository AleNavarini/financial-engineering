# Estudio de volatilidad | Ingeniería Financiera UCEMA

Este proyecto es una herramienta de Ingeniería Financiera de UCEMA para consultar y explorar datos de mercado. Utiliza LSEG Workspace Desktop y la biblioteca de datos de LSEG para Python.

El servicio incluye una API FastAPI y un dashboard web estático. Permite consultar datos históricos y actuales, guardar los resultados en CSV, explorar los archivos generados y visualizar sus columnas numéricas.

Responsables: Alejandro Navarini y Tomas Perez.

Refinitiv Workspace ahora se comercializa como **LSEG Workspace**. Ambos nombres se refieren al mismo producto de escritorio.

## Qué analiza

La configuración inicial consulta los contratos de continuación `VXc1` y `VXc2`, que representan el contrato del VIX más cercano y el segundo más cercano. El proyecto permite investigar:

- Contango y backwardation
- Cambios en la curva de futuros
- Comportamiento de los precios de liquidación
- Interés abierto en distintas posiciones de vencimiento
- Regímenes de volatilidad y períodos de estrés

Los RIC de continuación mantienen una posición de vencimiento estable, pero el contrato detrás de cada RIC cambia en los puntos de rollover. Los resultados sirven para analizar la estructura temporal y los regímenes de volatilidad. Por sí solos, no representan una serie de retornos de una estrategia negociable de futuros.

## Cómo funciona

El flujo utiliza una **sesión de escritorio**:

1. LSEG Workspace Desktop se ejecuta en el mismo equipo que el servicio Python.
2. Workspace está abierto, autenticado y conectado a LSEG.
3. La biblioteca de Python se conecta al proxy local de Workspace.
4. El App Key identifica a esta aplicación.
5. `ld.get_history` solicita los datos históricos.
6. `ld.get_data` solicita una observación actual opcional.
7. La API devuelve los datos y guarda una copia en `data/`.

Iniciar sesión en Workspace desde un navegador no es suficiente. La aplicación instalada de Workspace Desktop debe estar abierta y autenticada.

## Inicio rápido

Después de completar la instalación, el flujo normal es:

### macOS

```bash
cd financial-engineering
cp .env.example .env
# Edita .env y completa LSEG_APP_KEY
make run
```

### Windows PowerShell

```powershell
Set-Location financial-engineering
Copy-Item .env.example .env
# Edita .env y completa LSEG_APP_KEY
.\run.ps1
```

Abre `http://127.0.0.1:8000` en el navegador. La documentación interactiva de la API está en `http://127.0.0.1:8000/docs`.

## Requisitos

- macOS o Windows
- Git
- Python 3.12
- LSEG Workspace Desktop
- Una cuenta de LSEG Workspace con acceso a los datos solicitados
- Un App Key de LSEG
- Acceso a Internet desde Workspace y Python
- GNU Make en macOS; en Windows puedes usar `run.ps1` sin instalar Make

Python 3.11 es la versión mínima declarada por el proyecto, pero se recomienda Python 3.12 porque es la versión utilizada para validar las dependencias de LSEG.

`uv` es opcional. Es una herramienta moderna para administrar Python, entornos virtuales y dependencias desde `pyproject.toml`.

## 1. Instalar Git y Python

No instales paquetes de Python globalmente ni uses `sudo pip`. El proyecto crea y utiliza un entorno virtual local en `.venv`.

### macOS

#### Instalar Homebrew

Si ya tienes Homebrew, comprueba la instalación:

```bash
brew --version
```

Si no está instalado, ejecuta el instalador oficial:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Sigue las instrucciones para agregar Homebrew al `PATH`. Luego instala Git, Python 3.12 y `uv`:

```bash
brew install git python@3.12 uv
```

Comprueba las versiones:

```bash
git --version
python3.12 --version
uv --version
```

### Windows

Abre **PowerShell**. Si tienes `winget`, instala Git, Python 3.12 y `uv`:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id=astral-sh.uv -e
```

Cierra y vuelve a abrir PowerShell para actualizar el `PATH`. Comprueba las versiones:

```powershell
git --version
py -3.12 --version
uv --version
```

Si `winget` no está disponible, descarga e instala los programas desde sus sitios oficiales:

- [Git para Windows](https://git-scm.com/download/win)
- [Python 3.12](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Durante la instalación de Python, marca **Add python.exe to PATH**. Después, abre una nueva ventana de PowerShell.

## 2. Instalar LSEG Workspace Desktop

Descarga Workspace desde la [página oficial de LSEG](https://www.lseg.com/en/data-analytics/products/workspace/download-workspace). La aplicación de escritorio es necesaria porque este proyecto utiliza su API local.

### macOS

1. Descarga el instalador para macOS.
2. Abre el archivo `.dmg`.
3. Sigue las instrucciones del instalador.
4. Abre **Refinitiv Workspace** desde Applications.
5. Inicia sesión con tus credenciales de LSEG.
6. Abre una pantalla que muestre datos de mercado.

### Windows

1. Descarga el instalador para Windows.
2. Ejecuta el instalador.
3. Sigue las instrucciones de instalación.
4. Abre **Refinitiv Workspace** desde el menú Start.
5. Inicia sesión con tus credenciales de LSEG.
6. Abre una pantalla que muestre datos de mercado.

Deja Workspace abierto y autenticado mientras utilizas el dashboard, la API o los comandos CLI.

## 3. Obtener el App Key

El App Key identifica a esta aplicación. No es la contraseña de Workspace. Para este proyecto, registra el key para **Eikon Data API** y **EDP API**. El proxy de escritorio valida el registro de Eikon o Workspace, mientras que los recursos de precios de LSEG requieren permisos de EDP.

### Usar un App Key existente de UCEMA

La cuenta de UCEMA ya tiene varios App Keys. Utiliza uno existente:

1. Abre **AppKey Generator**.
2. Revisa los keys registrados para la cuenta de UCEMA.
3. Selecciona un key registrado para **Eikon Data API** y **EDP API**.
4. Copia su valor de **API Key**.
5. Guárdalo en `.env` durante el paso 6.

El App Key identifica la aplicación, pero no otorga permisos sobre los datos por sí solo. La cuenta de Workspace también debe tener autorización para acceder a los instrumentos y campos solicitados.

### Crear un App Key nuevo

Si ningún key existente es adecuado:

1. Abre la [documentación de API de LSEG](https://apidocs.refinitiv.com/Apps/ApiDocs).
2. Abre **AppKey Generator**.
3. Ingresa un nombre único para la aplicación.
4. Selecciona **Eikon Data API** y **EDP API**.
5. Haz clic en **Register New App**.
6. Copia el **API Key** generado.

Si AppKey Generator no está disponible, solicita al equipo de soporte de LSEG que habilite el acceso a Data Platform API.

## 4. Clonar el repositorio

Si todavía no tienes una copia local:

```bash
git clone https://github.com/AleNavarini/financial-engineering.git
cd financial-engineering
```

Si ya tienes el proyecto, entra en su directorio:

```bash
cd financial-engineering
```

Confirma que estás en la raíz del proyecto. Debes ver `pyproject.toml`, `Makefile`, `run.ps1`, `frontend` y `src`.

## 5. Configurar el entorno Python

El proyecto utiliza `pyproject.toml` como fuente de dependencias y `.venv` como entorno aislado. Los comandos de ejecución crean el entorno automáticamente.

### macOS con Make

Para crear el entorno e instalar las dependencias sin iniciar el servicio:

```bash
make install
```

Comprueba que Python y las dependencias se pueden importar:

```bash
.venv/bin/python -c "import fastapi, lseg.data, dotenv; print('Dependencias instaladas correctamente')"
```

### Windows PowerShell

`run.ps1` crea `.venv` e instala el proyecto automáticamente. Para preparar el entorno sin iniciar la API:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Comprueba la instalación:

```powershell
.\.venv\Scripts\python.exe -c "import fastapi, lseg.data, dotenv; print('Dependencias instaladas correctamente')"
```

### Alternativa moderna con `uv`

Desde la raíz del proyecto:

```bash
uv venv --python 3.12
uv pip install -e .
```

Si Python 3.12 no está instalado, `uv` puede instalarlo:

```bash
uv python install 3.12
uv venv --python 3.12
uv pip install -e .
```

Puedes ejecutar el servicio sin activar manualmente el entorno:

```bash
uv run python -m financial_engineering.app
```

Para usar un lockfile reproducible, ejecuta `uv sync`. Si generas `uv.lock` para el proyecto, debes versionarlo junto con el cambio de dependencias.

## 6. Configurar las credenciales

Desde la raíz del proyecto, crea `.env` a partir de la plantilla.

### macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Edita `.env` y reemplaza el valor de ejemplo:

```env
LSEG_APP_KEY=TU_APP_KEY
```

El archivo debe estar en la raíz del proyecto. No agregues comillas, espacios ni comentarios al valor del key.

Nunca subas `.env` al repositorio ni guardes credenciales en el código fuente.

## 7. Ejecutar la API y el dashboard

Antes de iniciar el servicio, confirma que Workspace Desktop está abierto, autenticado y mostrando datos.

### macOS

```bash
make run
```

`make run` crea `.venv` si hace falta, instala el paquete y ejecuta la API y el dashboard desde un solo proceso. Si cambia `pyproject.toml`, vuelve a instalar las dependencias.

### Windows PowerShell

```powershell
.\run.ps1
```

`run.ps1` crea `.venv`, instala el proyecto cuando es necesario y ejecuta la API. No se necesita Node.js, Bun ni una compilación separada del frontend.

El servicio escucha en `http://127.0.0.1:8000` por defecto. Abre esa dirección para utilizar el dashboard. Para detenerlo, presiona `Ctrl-C` en la terminal.

Puedes cambiar la dirección, el puerto y la carpeta de datos mediante variables de entorno:

```bash
API_HOST=127.0.0.1 API_PORT=8000 DATA_DIR=data make run
```

El dashboard permite:

- Consultar datos históricos para uno o varios tickers
- Consultar una observación actual
- Explorar los CSV disponibles en `DATA_DIR`
- Descargar los archivos originales
- Inspeccionar filas paginadas
- Graficar las columnas numéricas detectadas

## 8. Usar la API

La documentación interactiva está disponible en `http://127.0.0.1:8000/docs`.

Comprueba el servicio sin contactar a LSEG:

```bash
curl http://127.0.0.1:8000/health
```

Solicita datos históricos con fechas explícitas:

```bash
curl -X POST http://127.0.0.1:8000/history \
  -H 'Content-Type: application/json' \
  -d '{"instruments":["VXc1","VXc2"],"start":"2024-01-01","end":"2024-12-31"}'
```

Solicita una observación actual:

```bash
curl -X POST http://127.0.0.1:8000/data \
  -H 'Content-Type: application/json' \
  -d '{"instruments":["VXc1","VXc2"]}'
```

La API expone estas rutas:

- `POST /history` acepta un `ticker` o una lista de `instruments`, además de `start` y `end` obligatorios.
- `POST /data` acepta un `ticker` o una lista de `instruments` para un snapshot actual.
- `GET /datasets` lista los CSV válidos de `DATA_DIR`.
- `GET /datasets/{name}` devuelve columnas normalizadas, tipos detectados, metadatos y filas.
- `GET /datasets/{name}/download` descarga el CSV original.

Cada extracción histórica guarda el rango de fechas en el nombre del archivo. Por ejemplo:

```text
data/data_VXc1_VXc2_2024-01-01_to_2024-12-31.csv
```

La respuesta incluye los instrumentos resueltos, las fechas solicitadas, la cantidad de filas y la ruta `output_file`.

## 9. Usar los comandos CLI

Los mismos casos de uso están disponibles como comandos Python instalados por el proyecto.

Extracción histórica:

```bash
get-history \
  --ticker VXc1 \
  --start 2024-01-01 \
  --end 2024-12-31
```

Snapshot actual:

```bash
get-data --ticker VXc1
```

También puedes ejecutar los módulos directamente:

```bash
python -m financial_engineering.application.use_cases.get_history.get_history_controller \
  --ticker VXc1 \
  --start 2024-01-01 \
  --end 2024-12-31

python -m financial_engineering.application.use_cases.get_data.get_data_controller \
  --ticker VXc1
```

Para usar una lista de instrumentos, reemplaza `--ticker VXc1` por `--instruments VXc1,VXc2`.

## Alcance y limitaciones de los datos

El histórico utiliza `ld.get_history` y el snapshot utiliza `ld.get_data` mediante la sesión de escritorio. El proyecto no utiliza el endpoint explícito `ld.content.pricing.Definition(...).get_data()` porque esta cuenta no tiene el permiso `trapi.data.pricing.read`.

Los valores de `BID` y `ASK` pueden estar vacíos cuando el mercado está cerrado. El último precio, la liquidación y el interés abierto pueden conservar los últimos valores disponibles.

El script encuentra automáticamente el proxy de Workspace Desktop Data API en los puertos `9000` a `9060`. No es necesario configurar el puerto manualmente.

## Solución de problemas

### `python` o `python3.12` no existe

Comprueba la instalación:

```bash
python3.12 --version
```

En Windows usa:

```powershell
py -3.12 --version
```

Si el comando no funciona, instala Python siguiendo el paso 1 y abre una nueva terminal.

### `ModuleNotFoundError`

Reinstala el proyecto dentro de `.venv`.

En macOS:

```bash
make install
```

En Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

### Workspace está cerrado o desconectado

Abre Workspace Desktop, inicia sesión y confirma que muestra datos de mercado. El acceso desde el navegador no reemplaza la sesión de escritorio.

### `500 Network Error` o timeout

Confirma que:

1. Workspace Desktop está abierto.
2. Workspace tiene una sesión activa.
3. Workspace muestra datos de mercado actuales.
4. La VPN, el firewall o el proxy no bloquean los servicios de LSEG.
5. `.env` contiene el App Key correcto.

En macOS, revisa los procesos que escuchan en los puertos de Workspace:

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep -i refinitiv
```

Puedes consultar manualmente el estado de un puerto, por ejemplo:

```bash
curl http://127.0.0.1:9002/api/status
```

Workspace normalmente comienza en el puerto `9000`, pero puede elegir un puerto posterior si otro proceso ya utiliza ese puerto. Un proxy disponible devuelve una respuesta que contiene `ST_PROXY_READY`.

### `403` o `trapi.data.pricing.read`

El endpoint de snapshot explícito de la plataforma requiere `trapi.data.pricing.read`, permiso que esta cuenta no tiene. El extractor evita ese endpoint y utiliza la sesión de escritorio. Los permisos de la cuenta y las suscripciones de mercado siguen determinando qué valores se devuelven.

### Error de permisos al activar PowerShell

Ejecuta lo siguiente en la terminal actual y vuelve a iniciar `run.ps1`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run.ps1
```

### Errores de Python o pandas

Usa Python 3.12 y recrea el entorno virtual.

En macOS:

```bash
rm -rf .venv
make install
```

En Windows PowerShell:

```powershell
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

## Estructura del proyecto

```text
financial-engineering/
├── data/                         # CSV generados, excluidos de Git
├── docs/                         # Guías de conceptos y metodología
├── frontend/                     # HTML, CSS y JavaScript del dashboard
├── src/financial_engineering/    # API, casos de uso e infraestructura LSEG
├── .env.example                  # Plantilla de configuración
├── Makefile                      # Instalación, ejecución y tests
├── run.ps1                       # Lanzador para Windows
└── pyproject.toml                # Dependencias y comandos CLI
```

## Seguridad

- Mantén `.env` solamente en tu equipo local.
- No subas App Keys al repositorio.
- No incluyas credenciales en scripts, notebooks, capturas o archivos CSV.
- Revoca un App Key si se expone accidentalmente.

## Documentación adicional

Consulta el [índice de documentación](docs/README.md) para leer sobre volatilidad, VIX, futuros, opciones, decisiones de datos y límites del análisis.
