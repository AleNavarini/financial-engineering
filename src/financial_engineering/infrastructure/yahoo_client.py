from __future__ import annotations

import math
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf
from fastapi import HTTPException


DEFAULT_HISTORY_FIELDS = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']


def _output_path(ticker: str, start: str, end: str) -> Path:
    name = re.sub(r'[^A-Za-z0-9]+', '-', ticker.strip()).strip('-')
    if not name:
        raise HTTPException(status_code=422, detail='Ticker must not be empty')

    data_directory = Path(os.getenv('DATA_DIR', 'data'))
    return data_directory / f'data_yahoo_{name}_{start}_to_{end}.csv'


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if hasattr(value, 'item'):
        return _json_value(value.item())
    return value


def _frame_to_records(data: Any) -> list[dict[str, Any]]:
    rows = data.reset_index().to_dict(orient='records')
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in rows
    ]


class YahooClient:
    def get_history(
        self,
        *,
        ticker: str,
        fields: list[str] | None,
        start: date,
        end: date,
        interval: str,
        output: Path | None = None,
    ) -> dict[str, Any]:
        if start > end:
            raise HTTPException(status_code=422, detail='start must not be after end')

        start_value = start.isoformat()
        end_value = end.isoformat()
        resolved_fields = fields or DEFAULT_HISTORY_FIELDS
        output = output or _output_path(ticker, start_value, end_value)

        try:
            data = yf.download(
                ticker,
                start=start_value,
                end=end_value,
                interval=interval,
                auto_adjust=False,
                progress=False,
            )
        except Exception as error:
            raise HTTPException(status_code=502, detail='Yahoo Finance data request failed') from error

        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f'No Yahoo Finance data found for {ticker}')

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        available_fields = [field for field in resolved_fields if field in data.columns]
        if not available_fields:
            raise HTTPException(status_code=422, detail='None of the requested fields are available')
        data = data[available_fields]

        data.index.name = 'Date'
        output.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output)

        return {
            'mode': 'yahoo_history',
            'ticker': ticker,
            'fields': available_fields,
            'start': start_value,
            'end': end_value,
            'output_file': str(output),
            'row_count': len(data),
            'data': _frame_to_records(data),
        }
