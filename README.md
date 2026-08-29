# Financial Engineering

Python CLI for extracting data from the Refinitiv Data Platform, now called the LSEG Data Platform.

## Setup

```bash
cd financial-engineering
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Desktop access needs LSEG Workspace running on the same computer, an App Key, and entitlements for the requested instruments and fields.

Create a local `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Set `LSEG_APP_KEY` in `.env`. `LSEG_USERNAME` and `LSEG_PASSWORD` are only required for a platform session.

## Snapshot Data

The default desktop session uses the signed-in Workspace application:

```bash
refinitiv-extract \
  --instruments 'AAPL.O,MSFT.O' \
  --fields 'BID,ASK' \
  --output data/prices.csv
```

Snapshot access requires the `trapi.data.pricing.read` API scope on the LSEG account.

## Historical Data

```bash
refinitiv-extract \
  --mode history \
  --instruments 'AAPL.O,MSFT.O' \
  --fields 'TRDPRC_1' \
  --start 2025-01-01 \
  --end 2025-01-31 \
  --output data/history.csv
```

For unattended use without Workspace Desktop, select a platform session and supply machine credentials:

```bash
export LSEG_USERNAME='YOUR_MACHINE_ID'
export LSEG_APP_KEY='YOUR_APP_KEY'
export LSEG_PASSWORD='YOUR_PASSWORD'

refinitiv-extract \
  --session platform \
  --mode history \
  --instruments 'AAPL.O' \
  --start 2025-01-01
```

Do not commit credentials. The project ignores `.env` files and generated CSV files under `data/`.
