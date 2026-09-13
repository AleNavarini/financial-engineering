from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INPUT_FILE = DATA_DIR / "raw_dataset.csv"
OUTPUT_FILE = DATA_DIR / "features_dataset.csv"

WINDOW = 20
DD_THRESHOLD = -0.05
RV_PERCENTILE = 0.90
RV_MIN_PERIODS = 60
TRADING_DAYS_PER_YEAR = 252


def compute_beta(df: pd.DataFrame) -> pd.DataFrame:
    df["beta_t"] = (df["VXc4"] - df["VXc1"]) / df["VIX"]
    df["backwardation_t"] = np.where(df["beta_t"].isna(), np.nan, (df["beta_t"] < 0).astype(float))

    prev_beta = df["beta_t"].shift(1)
    entry = (df["beta_t"] < 0) & (prev_beta >= 0)
    entry = entry.where(df["beta_t"].notna() & prev_beta.notna())
    df["entry_backwardation_t"] = entry.astype(float)

    df["intensity_t"] = np.where(df["entry_backwardation_t"] == 1, -df["beta_t"], np.nan)
    return df


def compute_trailing_realized_vol(returns: pd.Series, window: int) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)


def compute_forward_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    prices = df["SP500"].values
    n = len(prices)

    r_fwd = np.full(n, np.nan)
    mdd_fwd = np.full(n, np.nan)
    rv_fwd = np.full(n, np.nan)

    log_returns = np.log(prices[1:] / prices[:-1])

    for t in range(n - WINDOW):
        p_t = prices[t]
        window_prices = prices[t : t + WINDOW + 1]

        if np.isnan(p_t) or np.isnan(window_prices).any():
            continue

        r_fwd[t] = window_prices[-1] / p_t - 1

        running_max = np.maximum.accumulate(window_prices)
        drawdowns = window_prices / running_max - 1
        mdd_fwd[t] = drawdowns.min()

        window_returns = log_returns[t : t + WINDOW]
        if len(window_returns) == WINDOW and not np.isnan(window_returns).any():
            rv_fwd[t] = window_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    df["r_fwd_20"] = r_fwd
    df["mdd_fwd_20"] = mdd_fwd
    df["rv_fwd_20"] = rv_fwd
    return df


def compute_backward_controls(df: pd.DataFrame) -> pd.DataFrame:
    prices = df["SP500"]
    df["r_pre_20"] = prices / prices.shift(WINDOW) - 1

    daily_log_returns = np.log(prices / prices.shift(1))
    df["rv_pre_20"] = compute_trailing_realized_vol(daily_log_returns, WINDOW)
    return df


def compute_stress_labels(df: pd.DataFrame) -> pd.DataFrame:
    daily_log_returns = np.log(df["SP500"] / df["SP500"].shift(1))
    rv_trailing = compute_trailing_realized_vol(daily_log_returns, WINDOW)
    df["p90_rv_trailing_t"] = rv_trailing.expanding(min_periods=RV_MIN_PERIODS).quantile(RV_PERCENTILE)

    df["dd_stress_fwd_20"] = (df["mdd_fwd_20"] <= DD_THRESHOLD).astype(float)
    df.loc[df["mdd_fwd_20"].isna(), "dd_stress_fwd_20"] = np.nan

    rv_condition = (df["rv_fwd_20"] > df["p90_rv_trailing_t"]) & (df["r_fwd_20"] < 0)
    df["rv_stress_fwd_20"] = rv_condition.astype(float)
    df.loc[df["rv_fwd_20"].isna() | df["p90_rv_trailing_t"].isna() | df["r_fwd_20"].isna(), "rv_stress_fwd_20"] = np.nan

    df["stress_fwd_20"] = df[["dd_stress_fwd_20", "rv_stress_fwd_20"]].max(axis=1, skipna=True)
    return df


def main() -> None:
    df = pd.read_csv(INPUT_FILE, parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)

    df = compute_beta(df)
    df = compute_backward_controls(df)
    df = compute_forward_outcomes(df)
    df = compute_stress_labels(df)

    df.to_csv(OUTPUT_FILE, index=False)

    n_entries = int(df["entry_backwardation_t"].sum(skipna=True))
    n_with_outcome = df["stress_fwd_20"].notna().sum()
    print(f"Guardado: {OUTPUT_FILE} ({len(df)} filas)")
    print(f"Eventos de entrada en backwardation: {n_entries}")
    print(f"Filas con resultado a 20 días calculable: {n_with_outcome}")


if __name__ == "__main__":
    main()
