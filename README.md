# VIX Futures Volatility Study

This project studies volatility through the historical VIX futures term structure. It provides a FastAPI service that extracts data for the first nine VIX futures continuation contracts through the LSEG Data Library for Python.

The primary data set supports research on:

- Contango and backwardation
- Changes in the futures curve
- Settlement-price behavior
- Open interest across maturity positions
- Volatility regimes and stress periods

Current prices are optional. The study does not depend on them.

Project guides and learning material are available in the [documentation index](docs/README.md).

Refinitiv Workspace is now branded as **LSEG Workspace**. The names refer to the same desktop product used by this project.

## Data Scope

The default run requests `VXc1` through `VXc9`, where `VXc1` is the nearest continuation contract and `VXc9` is the ninth. API fetches write daily data to a request-specific CSV file such as `data/data_VXc1_VXc2.csv`.

Continuation RICs make historical curve research simple, but the contract behind each RIC changes at roll points. The output is suitable for term-structure and regime analysis. It is not, by itself, a tradable futures-strategy return series.

## How It Works

The default script uses a **desktop session**:

1. LSEG Workspace Desktop runs on the same computer as the Python script.
2. Workspace is signed in and connected to LSEG.
3. The Python library connects to Workspace's local API service.
4. The App Key identifies this application.
5. `ld.get_history` requests the historical study data.
6. The API returns the result as JSON.

Optional snapshot mode uses `ld.get_data`, which works through the available Desktop data route. The project does not use the explicit `ld.content.pricing.Definition(...).get_data()` endpoint because this account lacks its `trapi.data.pricing.read` scope.

Signing in to Workspace in a browser is not enough for a desktop session. The installed Workspace Desktop application must be open and signed in.

## Requirements

- An LSEG Workspace account with access to the required data
- An LSEG App Key
- LSEG Workspace Desktop for macOS or Windows
- Python 3.12
- Internet access from Workspace and Python

## 1. Install Workspace

Use the official [LSEG Workspace download page](https://www.lseg.com/en/data-analytics/products/workspace/download-workspace).

### macOS

1. Download the macOS installer.
2. Open the downloaded `.dmg` file.
3. Follow the installer instructions.
4. Open **Refinitiv Workspace** from the Applications folder.
5. Sign in with your LSEG credentials.
6. Confirm that market data is visible in Workspace before running Python.

Workspace must remain open and signed in while `fetch_data.py` runs.

### Windows

1. Download the Windows installer.
2. Run the downloaded installer.
3. Follow the installation instructions.
4. Open **Refinitiv Workspace** from the Start menu.
5. Sign in with your LSEG credentials.
6. Confirm that market data is visible in Workspace before running Python.

Workspace must remain open and signed in while `fetch_data.py` runs.

## 2. Select or Create the App Key

The App Key identifies this application. It is not the same as your Workspace password. For this desktop-based project, register the key for both **Eikon Data API** and **EDP API**. The desktop proxy validates the Eikon or Workspace API registration, while LSEG pricing resources require EDP scopes.

### Use an Existing UCEMA App Key

The UCEMA account already has several App Keys. Use one of the existing keys instead of creating another one:

1. Open the AppKey Generator.
2. Review the keys already registered for the UCEMA account.
3. Select a key registered for both **Eikon Data API** and **EDP API**.
4. Copy its **API Key** value.
5. Set that value as `LSEG_APP_KEY` in `.env`.

The App Key identifies the application, but it does not grant data entitlements by itself. The Workspace account must also have permission to access the requested data through the API.

If no existing key is suitable, create a new one:

1. Open the [LSEG API Docs](https://apidocs.refinitiv.com/Apps/ApiDocs).
2. Open **AppKey Generator**.
3. Enter a unique application name.
4. Select both **Eikon Data API** and **EDP API**.
5. Click **Register New App**.
6. Copy the generated **API Key**. This is the App Key used by this project.

If AppKey Generator is not available, ask your LSEG account manager or support team to enable Data Platform API access.

## 3. Configure the Project

Open a terminal or PowerShell in the project directory:

```text
financial-engineering/
```

Create a local environment file.

### macOS

```bash
cp .env.example .env
```

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set the App Key:

```env
LSEG_APP_KEY=YOUR_APP_KEY
```

Never commit `.env` or put credentials directly in source control.

## 4. Create and Activate the Virtual Environment

Python 3.12 is recommended. The LSEG data dependencies may not work correctly with newer Python versions.

### macOS

Check the Python version:

```bash
python3.12 --version
```

Create the virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, the terminal prompt normally shows `(.venv)`.

### Windows PowerShell

Check the Python version:

```powershell
py -3.12 --version
```

Create the virtual environment:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for the current terminal, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

## 5. Install the Python Dependencies

Run these commands while the virtual environment is active.

### macOS and Windows

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

This installs:

- `lseg-data`, the LSEG Data Library for Python
- `fastapi` and `uvicorn`, the HTTP API framework and server
- `python-dotenv`, which loads `.env`
- This project as an editable local package

## 6. Run the API

Start the service while Workspace Desktop is open, signed in, and showing data:

### Unix

```bash
make run
```

The `make run` target creates `.venv` and installs the project automatically when needed. It reinstalls dependencies if `pyproject.toml` changes. You can also run `make install` separately when you want to prepare the environment without starting the service.

### Windows PowerShell

GNU Make is not included with native Windows by default. Run the PowerShell launcher instead:

```powershell
.\run.ps1
```

It creates `.venv` and installs the project automatically when needed. If GNU Make is installed through WSL, MSYS2, or another Unix-like shell, `make run` also works. The Makefile detects the Windows `.venv\Scripts` paths automatically.

The service listens on `http://127.0.0.1:8000` by default. Set `API_HOST` or `API_PORT` in the environment to change the bind address.

The interactive API documentation is available at `http://127.0.0.1:8000/docs`. Check the service without contacting LSEG:

```bash
curl http://127.0.0.1:8000/health
```

Request the default three-year history:

```bash
curl -X POST http://127.0.0.1:8000/data \
  -H 'Content-Type: application/json' \
  -d '{"mode":"history"}'
```

Request a current observation for selected instruments:

```bash
curl -X POST http://127.0.0.1:8000/data \
  -H 'Content-Type: application/json' \
  -d '{"mode":"snapshot","instruments":["VXc1","VXc2"]}'
```

The API writes each fetch to `data/data_<instruments>.csv` and returns the path in `output_file`, along with `mode`, `instruments`, `fields`, `row_count`, and a JSON `data` array. For example, `VX` writes `data/data_VX.csv`, while `BIGS` and `VXc1` write `data/data_BIGS_VXc1.csv`. The original CSV utility remains available in `fetch_data.py` when a custom fixed output path is required.

## 7. Configure the Fetch Script

Open `fetch_data.py`. The settings are constants at the top of the file. The default configuration extracts three years of daily history for the first nine VIX futures continuation contracts, not the VIX spot index:

```python
MODE = 'history'
INSTRUMENTS = [f'VXc{month}' for month in range(1, 10)]
FIELDS = [
    'TRDPRC_1',
    'SETTLE',
    'OPINT_1',
]
END_DATE = date.today()
try:
    START_DATE = END_DATE.replace(year=END_DATE.year - 3).isoformat()
except ValueError:
    START_DATE = END_DATE.replace(year=END_DATE.year - 3, day=28).isoformat()
END_DATE = END_DATE.isoformat()
OUTPUT = Path('data/vix_futures_3y.csv')
```

Change these constants in Python when you need different data:

- `MODE`: `history` for the study data or `snapshot` for an optional current observation
- `INSTRUMENTS`: LSEG RICs such as `VXc1` through `VXc9`
- `FIELDS`: historical fields such as `TRDPRC_1`, `SETTLE`, and `OPINT_1`; snapshot mode can also request `BID` and `ASK`
- `START_DATE`: first date to request
- `END_DATE`: last date to request
- `OUTPUT`: CSV output path

Continuation RICs keep a stable maturity position: `VXc1` is the nearest contract, `VXc2` is the second nearest, and so on. The contract behind each column changes when contracts expire.

The script automatically finds the Workspace Desktop Data API proxy on ports `9000` through `9060`. No proxy port configuration is required.

### Optional Current Observation

Current data is not required for the historical study. To request one current observation through the tested Desktop route, change these constants in `fetch_data.py`:

```python
MODE = 'snapshot'
INSTRUMENTS = [f'VXc{month}' for month in range(1, 10)]
FIELDS = ['BID', 'ASK', 'TRDPRC_1', 'SETTLE', 'OPINT_1']
OUTPUT = Path('data/vix_futures_current.csv')
```

When the market is closed, `BID` and `ASK` can be empty. Last price, settlement, and open interest can still contain the latest available values.

## 8. Run the Script

Before running it, confirm that LSEG Workspace Desktop is open, signed in, and showing data.

### macOS

```bash
source .venv/bin/activate
python3 fetch_data.py
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python fetch_data.py
```

The script fetches data and writes the result to:

```text
data/vix_futures_3y.csv
```

The `data/` directory and generated CSV files are ignored by Git.

## Troubleshooting

### Workspace is signed out

Sign in to the installed Workspace Desktop application and retry. Browser Workspace access does not replace the desktop session.

### `500 Network Error` or timeout

Confirm that:

1. Workspace Desktop is open.
2. Workspace is signed in.
3. Workspace displays current market data.
4. VPN, firewall, or proxy settings are not blocking LSEG services.

On macOS, check the port used by Workspace and then request its status. Workspace starts at port `9000` and can select a later port when another process already uses it:

```bash
lsof -nP -iTCP -sTCP:LISTEN | grep Refinitiv
curl http://127.0.0.1:9002/api/status
```

An available proxy returns a response containing `ST_PROXY_READY`.

### `403` and `trapi.data.pricing.read`

The explicit platform snapshot endpoint requires `trapi.data.pricing.read`, which this account does not have. The extractor avoids that endpoint: history uses `ld.get_history`, and optional current observations use `ld.get_data` through the Desktop session. Exchange entitlements still determine which values are returned.

### `ModuleNotFoundError`

Activate the virtual environment and install the project again:

```bash
python -m pip install -e .
```

### Python or pandas errors

Use Python 3.12 and recreate the environment:

```bash
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, remove the environment with:

```powershell
Remove-Item -Recurse -Force .venv
```

## Security

- Keep `.env` local.
- Do not commit App Keys.
