# Estudio de volatilidad de futuros del VIX

Este proyecto estudia la volatilidad mediante la estructura temporal histórica de los futuros del VIX. Extrae tres años de datos diarios para los primeros nueve contratos de continuación de futuros del VIX a través de la biblioteca de datos de LSEG para Python.

El conjunto de datos permite investigar:

- Contango y backwardation
- Cambios en la curva de futuros
- Comportamiento de los precios de liquidación
- Interés abierto en distintas posiciones de vencimiento
- Regímenes de volatilidad y períodos de estrés

Los precios actuales son opcionales. El estudio no depende de ellos.

Los materiales de aprendizaje están disponibles en el [índice de documentación](docs/README.md).

Refinitiv Workspace ahora se comercializa como **LSEG Workspace**. Ambos nombres se refieren al mismo producto de escritorio.

## Inicio rápido

Este es el orden general para ejecutar el proyecto:

1. Instalar Git y Python 3.12.
2. Instalar LSEG Workspace Desktop.
3. Iniciar sesión en Workspace Desktop y confirmar que muestra datos.
4. Obtener un App Key con acceso para Eikon Data API y EDP API.
5. Clonar el repositorio.
6. Crear un entorno virtual e instalar el proyecto.
7. Guardar el App Key en `.env`.
8. Ejecutar `fetch_data.py`.

Workspace Desktop debe permanecer abierto y autenticado durante toda la extracción. Una sesión iniciada solamente en el navegador no es suficiente.

### Flujo recomendado con `uv`

`uv` es opcional. Es la alternativa recomendada para proyectos Python porque administra el entorno virtual y las dependencias desde `pyproject.toml` sin instalar paquetes globalmente.

Con Git, Python, Workspace y `uv` instalados:

```bash
cd financial-engineering
uv venv --python 3.12
uv pip install -e .
cp .env.example .env
uv run python -c "import lseg.data, dotenv; print('Dependencias instaladas correctamente')"
uv run python fetch_data.py
```

En Windows PowerShell, reemplaza el comando para copiar `.env` por:

```powershell
Copy-Item .env.example .env
```

Después de crear `.env`, completa `LSEG_APP_KEY` antes de ejecutar el último comando. Para generar un entorno reproducible con lockfile, puedes usar `uv sync`; `uv` creará o actualizará `uv.lock` a partir de `pyproject.toml`. Si generas ese archivo para el proyecto, debes versionarlo junto con el cambio de dependencias.

## Requisitos

- macOS o Windows
- Git
- Python 3.12
- `uv` es opcional, pero recomendado para administrar el entorno y las dependencias
- Una cuenta de LSEG Workspace con acceso a los datos solicitados
- Un App Key de LSEG
- LSEG Workspace Desktop
- Acceso a Internet desde Workspace y Python

Python 3.11 es la versión mínima declarada por el proyecto, pero se recomienda Python 3.12 porque es la versión usada para validar las dependencias de LSEG.

## 1. Instalar Git y Python

No instales paquetes de Python globalmente ni uses `sudo pip`. Todas las dependencias del proyecto se instalarán dentro de `.venv`.

### macOS

#### Instalar Homebrew

Si ya tienes Homebrew, comprueba su instalación:

```bash
brew --version
```

Si no está instalado, ejecuta el comando oficial:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Sigue las instrucciones que muestra el instalador para agregar Homebrew al `PATH`. Luego instala Git y Python 3.12:

```bash
brew install git python@3.12
```

Comprueba las versiones:

```bash
git --version
python3.12 --version
```

El comando debe mostrar Python 3.12.x.

También puedes instalar `uv`, una herramienta moderna para administrar versiones de Python, entornos virtuales y paquetes:

```bash
brew install uv
uv --version
```

### Windows

Abre **PowerShell**. Si tienes `winget`, instala Git y Python 3.12 con:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
```

Cierra y vuelve a abrir PowerShell para que se actualice el `PATH`. Comprueba las versiones:

```powershell
git --version
py -3.12 --version
```

También puedes instalar `uv`, una herramienta moderna para administrar versiones de Python, entornos virtuales y paquetes:

```powershell
winget install --id=astral-sh.uv -e
```

Cierra y vuelve a abrir PowerShell, y comprueba la instalación:

```powershell
uv --version
```

Si `winget` no está disponible, descarga e instala ambos programas desde sus sitios oficiales:

- [Git para Windows](https://git-scm.com/download/win)
- [Python 3.12](https://www.python.org/downloads/)

Durante la instalación de Python, marca **Add python.exe to PATH**. Después, abre una nueva ventana de PowerShell.

## 2. Instalar LSEG Workspace Desktop

Descarga Workspace desde la [página oficial de LSEG](https://www.lseg.com/en/data-analytics/products/workspace/download-workspace). La aplicación de escritorio es necesaria para este proyecto porque la extracción utiliza su API local.

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

Deja Workspace abierto y autenticado. El script no puede consultar datos si la aplicación está cerrada o si la cuenta está desconectada.

## 3. Obtener el App Key

El App Key identifica a esta aplicación. No es la contraseña de Workspace. Para este proyecto, el key debe estar registrado para **Eikon Data API** y **EDP API**.

### Usar un App Key existente de UCEMA

La cuenta de UCEMA ya tiene varios App Keys. Utiliza uno existente en lugar de crear otro:

1. Abre **AppKey Generator**.
2. Revisa los keys registrados para la cuenta de UCEMA.
3. Selecciona un key registrado para **Eikon Data API** y **EDP API**.
4. Copia su valor de **API Key**.
5. Guárdalo en `.env` durante el paso 5.

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

Si todavía no tienes una copia local, abre una terminal y ejecuta:

```bash
git clone https://github.com/AleNavarini/financial-engineering.git
cd financial-engineering
```

Si ya tienes el proyecto, entra en su directorio:

```bash
cd financial-engineering
```

Confirma que estás en la raíz del proyecto. Debes ver `pyproject.toml`, `fetch_data.py` y la carpeta `src`.

## 5. Crear y activar el entorno virtual

El entorno virtual mantiene las dependencias aisladas del resto de Python instalado en el equipo.

### macOS

Desde la raíz del proyecto:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Comprueba que el entorno está activo:

```bash
python --version
which python
```

La ruta de `which python` debe apuntar a `.venv/bin/python`.

### Windows PowerShell

Desde la raíz del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Comprueba que el entorno está activo:

```powershell
python --version
Get-Command python
```

La ruta mostrada debe apuntar a `.venv\Scripts\python.exe`.

Si PowerShell bloquea la activación, permite scripts solamente en la terminal actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El prompt normalmente muestra `(.venv)` mientras el entorno está activo.

### Alternativa con `uv`

Si instalaste `uv`, puedes crear el mismo entorno con:

```bash
uv venv --python 3.12
```

Si Python 3.12 todavía no está instalado, `uv` puede instalarlo por ti:

```bash
uv python install 3.12
uv venv --python 3.12
```

Activa `.venv` usando los comandos de macOS o Windows de este paso.

## 6. Instalar las dependencias

Ejecuta estos comandos con `(.venv)` activo:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Con `uv`, puedes instalar las dependencias sin salir del entorno virtual con:

```bash
uv pip install -e .
```

Ambos métodos leen `pyproject.toml`. Elige un método y úsalo de forma consistente en el mismo entorno.

El parámetro `-e .` instala el proyecto en modo editable y utiliza la configuración de `pyproject.toml`. Se instalan:

- `lseg-data`, la biblioteca de datos de LSEG para Python
- `python-dotenv`, que carga las variables de `.env`
- Este proyecto como paquete local editable

Comprueba que la instalación básica funciona:

```bash
python -c "import lseg.data, dotenv; print('Dependencias instaladas correctamente')"
```

Si el comando imprime el mensaje esperado, Python puede importar las dependencias. Esta comprobación no consulta LSEG y no requiere que Workspace esté abierto.

## 7. Configurar las credenciales

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

También puedes crear el archivo manualmente, siempre que se encuentre en la raíz del proyecto y tenga exactamente la variable `LSEG_APP_KEY`.

No agregues comillas, espacios ni comentarios al valor del key. Nunca subas `.env` al repositorio ni guardes credenciales en el código fuente.

## 8. Ejecutar la extracción histórica

Antes de ejecutar el script, confirma lo siguiente:

1. Workspace Desktop está abierto.
2. La cuenta está autenticada.
3. Workspace muestra datos de mercado.
4. El entorno virtual está activo.
5. `.env` contiene un App Key válido.

### macOS

```bash
source .venv/bin/activate
python fetch_data.py
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python fetch_data.py
```

La configuración predeterminada solicita:

- Los RIC `VXc1` a `VXc9`
- Tres años de historia diaria
- `TRDPRC_1`, `SETTLE` y `OPINT_1`

El resultado se guarda en:

```text
data/vix_futures_3y.csv
```

El script muestra en la terminal la cantidad de filas guardadas. El directorio `data/` y los CSV generados están excluidos de Git.

## 9. Usar el comando CLI

La instalación también registra el comando `refinitiv-extract`. Puedes consultar sus opciones con:

```bash
refinitiv-extract --help
```

El CLI sirve para ejecutar consultas diferentes sin modificar `fetch_data.py`. Por ejemplo, para extraer historia de dos instrumentos:

```bash
refinitiv-extract \
  --mode history \
  --instruments VXc1,VXc2 \
  --fields TRDPRC_1,SETTLE,OPINT_1 \
  --start 2023-01-01 \
  --end 2023-12-31 \
  --output data/vix_futures_2023.csv
```

En Windows PowerShell, puedes escribir el comando en una sola línea:

```powershell
refinitiv-extract --mode history --instruments VXc1,VXc2 --fields TRDPRC_1,SETTLE,OPINT_1 --start 2023-01-01 --end 2023-12-31 --output data/vix_futures_2023.csv
```

El CLI requiere `--start` cuando `--mode history` está activo. Para el modo `snapshot`, usa por ejemplo:

```bash
refinitiv-extract \
  --mode snapshot \
  --instruments VXc1,VXc2 \
  --fields BID,ASK,TRDPRC_1,SETTLE,OPINT_1 \
  --output data/vix_futures_current.csv
```

El modo snapshot no es necesario para el estudio histórico. Cuando el mercado está cerrado, `BID` y `ASK` pueden estar vacíos, mientras que el último precio, la liquidación y el interés abierto pueden conservar los últimos valores disponibles.

## Alcance y limitaciones de los datos

Los RIC de continuación mantienen una posición de vencimiento estable: `VXc1` es el contrato más cercano, `VXc2` es el segundo y así sucesivamente. El contrato detrás de cada columna cambia cuando vencen los contratos.

Por este motivo, los datos son adecuados para analizar la estructura temporal y los regímenes de volatilidad. No representan por sí solos una serie de retornos de una estrategia negociable de futuros.

El script encuentra automáticamente el proxy de Workspace Desktop Data API en los puertos `9000` a `9060`. No es necesario configurar el puerto manualmente.

El flujo histórico utiliza `ld.get_history`. El flujo snapshot utiliza `ld.get_data` mediante la sesión de escritorio disponible. El proyecto no utiliza el endpoint explícito `ld.content.pricing.Definition(...).get_data()` porque esta cuenta no tiene el permiso `trapi.data.pricing.read`.

## Solución de problemas

### `python` o `python3.12` no existe

Comprueba que Python 3.12 está instalado y que el comando está disponible:

```bash
python3.12 --version
```

En Windows usa:

```powershell
py -3.12 --version
```

Si el comando no funciona, instala Python siguiendo el paso 1 y abre una nueva terminal.

### `ModuleNotFoundError`

Activa el entorno virtual y reinstala el proyecto:

```bash
python -m pip install -e .
```

Si la terminal no reconoce `python`, activa `.venv` de nuevo.

### Workspace está cerrado o desconectado

Abre la aplicación instalada de Workspace Desktop, inicia sesión y confirma que muestra datos de mercado. El acceso desde el navegador no reemplaza la sesión de escritorio.

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

Workspace normalmente comienza en el puerto `9000`, pero puede elegir un puerto posterior si otro proceso ya utiliza ese puerto. Un proxy disponible devuelve una respuesta que contiene `ST_PROXY_READY`. El script prueba automáticamente todos los puertos de `9000` a `9060`.

### `403` o `trapi.data.pricing.read`

El endpoint de snapshot explícito de la plataforma requiere `trapi.data.pricing.read`, permiso que esta cuenta no tiene. El extractor evita ese endpoint y utiliza la sesión de escritorio. Los permisos de la cuenta y las suscripciones de mercado siguen determinando qué valores se devuelven.

### Error de permisos al activar PowerShell

Ejecuta lo siguiente en la terminal actual y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Errores de Python o pandas

Usa Python 3.12 y recrea el entorno virtual.

En macOS:

```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

En Windows PowerShell:

```powershell
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Estructura del proyecto

```text
financial-engineering/
├── data/                         # CSV generados, excluidos de Git
├── docs/                         # Guías de conceptos y metodología
├── src/financial_engineering/    # Lógica de extracción y cliente LSEG
├── .env.example                  # Plantilla de configuración
├── fetch_data.py                 # Flujo principal del estudio
└── pyproject.toml                # Dependencias y comando CLI
```

## Seguridad

- Mantén `.env` solamente en tu equipo local.
- No subas App Keys al repositorio.
- No incluyas credenciales en scripts, notebooks, capturas o archivos CSV.
- Revoca un App Key si se expone accidentalmente.

## Documentación adicional

Consulta el [índice de documentación](docs/README.md) para leer sobre volatilidad, VIX, futuros, opciones, decisiones de datos y límites del análisis.
