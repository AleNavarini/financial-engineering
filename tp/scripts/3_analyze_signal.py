from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INPUT_FILE = DATA_DIR / "features_dataset.csv"


def summarize(df: pd.DataFrame, label: str) -> dict:
    return {
        "grupo": label,
        "n": len(df),
        "freq_stress": df["stress_fwd_20"].mean(),
        "r_medio": df["r_fwd_20"].mean(),
        "r_mediana": df["r_fwd_20"].median(),
        "mdd_medio": df["mdd_fwd_20"].mean(),
    }


def main() -> None:
    df = pd.read_csv(INPUT_FILE, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)

    events = df[(df["entry_backwardation_t"] == 1) & df["stress_fwd_20"].notna()].copy()

    baseline = df[df["stress_fwd_20"].notna()].copy()

    summary = pd.DataFrame([
        summarize(baseline, "Baseline (todos los días, sin espaciar)"),
        summarize(events, "Eventos (entrada en backwardation)"),
    ])
    print("=== Comparación de resultados a 20 días ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
