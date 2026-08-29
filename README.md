# Financial Engineering

This project extracts financial data from Refinitiv Workspace through the LSEG Data Library for Python.
It supports the Workspace Desktop environment on macOS and Windows only.

Refinitiv Workspace is now branded as **LSEG Workspace**. The names refer to the same desktop product used by this project.

## How It Works

The default script uses a **desktop session**:

1. LSEG Workspace Desktop runs on the same computer as the Python script.
2. Workspace is signed in and connected to LSEG.
3. The Python library connects to Workspace's local API service.
4. The App Key identifies this application.
5. The script requests data and writes it to a CSV file.

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

The App Key identifies this application. It is not the same as your Workspace password. The key must be registered for the **EDP API** (Enterprise Data Platform API), because this project uses the LSEG Data Library API.

### Use an Existing UCEMA App Key

The UCEMA account already has several App Keys. Use one of the existing keys instead of creating another one:

1. Open the AppKey Generator.
2. Review the keys already registered for the UCEMA account.
3. Select a key registered for **EDP API**.
4. Copy its **API Key** value.
5. Set that value as `LSEG_APP_KEY` in `.env`.

The App Key identifies the application, but it does not grant data entitlements by itself. The Workspace account must also have permission to access the requested data through the API.

If no existing key is suitable, create a new one:

1. Open the [LSEG API Docs](https://apidocs.refinitiv.com/Apps/ApiDocs).
2. Open **AppKey Generator**.
3. Enter a unique application name.
4. Select **EDP API**.
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
- `python-dotenv`, which loads `.env`
- This project as an editable local package

## 6. Configure the Fetch Script

Open `fetch_data.py`. The settings are constants at the top of the file:

```python
INSTRUMENTS = ['BTC=']
FIELDS = ['BID', 'ASK']
START_DATE = (date.today() - timedelta(days=30)).isoformat()
END_DATE = date.today().isoformat()
OUTPUT = Path('data/refinitiv_data.csv')
```

Change these constants when you need different data:

- `INSTRUMENTS`: LSEG RICs such as `AAPL.O`, `MSFT.O`, or `BTC=`
- `FIELDS`: fields such as `BID`, `ASK`, or `TRDPRC_1`
- `START_DATE`: first date to request
- `END_DATE`: last date to request
- `OUTPUT`: CSV output path

## 7. Run the Script

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
data/refinitiv_data.csv
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

On macOS, Workspace's local API status can be checked with:

```bash
curl http://127.0.0.1:9000/api/status
```

An available proxy returns a response containing `ST_PROXY_READY`.

### `403` and `trapi.data.pricing.read`

The LSEG account can display data in Workspace but may not have API pricing access. Ask LSEG to enable the `trapi.data.pricing.read` scope. Workspace display entitlements and API entitlements are separate.

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
