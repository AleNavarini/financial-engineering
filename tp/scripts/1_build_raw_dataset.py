from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FUTURES_FILE = DATA_DIR / "data_VXc1_VXc2_VXc4_2007-09-09_to_2026-09-09.csv"
SPOT_FILE = DATA_DIR / "data_VIX_SP500_2007-09-09_to_2026-09-09.csv"
OUTPUT_FILE = DATA_DIR / "raw_dataset.csv"


def load_futures() -> pd.DataFrame:
    raw = pd.read_csv(FUTURES_FILE, header=[0, 1], index_col=0)
    raw.index = pd.to_datetime(raw.index)
    raw.index.name = "Date"

    settle = raw.xs("SETTLE", axis=1, level=1)
    settle = settle.reset_index()
    return settle


def main() -> None:
    futures = load_futures()
    spot = pd.read_csv(SPOT_FILE, parse_dates=["Date"])

    merged = pd.merge(spot, futures, on="Date", how="outer")
    merged = merged.sort_values("Date").reset_index(drop=True)

    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Guardado: {OUTPUT_FILE} ({len(merged)} filas, {merged['Date'].min().date()} a {merged['Date'].max().date()})")
    print(f"Columnas: {list(merged.columns)}")
    print(f"Filas con algún NaN: {merged.isna().any(axis=1).sum()}")


if __name__ == "__main__":
    main()
