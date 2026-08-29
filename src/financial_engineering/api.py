from __future__ import annotations

import math
import os
import re
from datetime import date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from financial_engineering.refinitiv_extract import extract_data


DEFAULT_INSTRUMENTS = [f'VXc{month}' for month in range(1, 10)]
DEFAULT_HISTORY_FIELDS = ['TRDPRC_1', 'SETTLE', 'OPINT_1']
DEFAULT_SNAPSHOT_FIELDS = ['BID', 'ASK', 'TRDPRC_1', 'SETTLE', 'OPINT_1']
extraction_lock = Lock()


class DataRequest(BaseModel):
    mode: Literal['history', 'snapshot'] = 'history'
    instruments: list[str] = Field(default_factory=lambda: DEFAULT_INSTRUMENTS.copy())
    fields: list[str] | None = None
    start: date | None = None
    end: date | None = None
    interval: str = '1D'


app = FastAPI(
    title='Financial Engineering Data API',
    description='HTTP access to the VIX futures data extraction workflow.',
    version='0.1.0',
)


def _three_years_ago(value: date) -> date:
    try:
        return value.replace(year=value.year - 3)
    except ValueError:
        return value.replace(year=value.year - 3, day=28)


def _request_values(
    request: DataRequest,
) -> tuple[list[str], list[str], str | None, str | None]:
    if not request.instruments:
        raise HTTPException(status_code=422, detail='At least one instrument is required')

    fields = request.fields
    if not fields:
        fields = DEFAULT_HISTORY_FIELDS if request.mode == 'history' else DEFAULT_SNAPSHOT_FIELDS

    if request.mode == 'history':
        end = request.end or date.today()
        start = request.start or _three_years_ago(end)
        if start > end:
            raise HTTPException(status_code=422, detail='start must not be after end')
        return request.instruments, fields, start.isoformat(), end.isoformat()

    return request.instruments, fields, None, None


def _output_path(instruments: list[str]) -> Path:
    names = [
        re.sub(r'[^A-Za-z0-9]+', '-', instrument.strip()).strip('-')
        for instrument in instruments
    ]
    if any(not name for name in names):
        raise HTTPException(status_code=422, detail='Instrument names must not be empty')

    data_directory = Path(os.getenv('DATA_DIR', 'data'))
    return data_directory / f"data_{'_'.join(names)}.csv"


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


@app.get('/')
def root() -> dict[str, str]:
    return {
        'name': 'Financial Engineering Data API',
        'docs': '/docs',
        'health': '/health',
    }


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/data')
def fetch(request: DataRequest) -> dict[str, Any]:
    app_key = os.getenv('LSEG_APP_KEY')
    if not app_key:
        raise HTTPException(status_code=503, detail='LSEG_APP_KEY is not configured')

    instruments, fields, start, end = _request_values(request)
    output = _output_path(instruments)
    try:
        # The Desktop session is shared by the local LSEG proxy, so serialize calls.
        with extraction_lock:
            data = extract_data(
                app_key=app_key,
                mode=request.mode,
                instruments=instruments,
                fields=fields,
                output=output,
                start=start,
                end=end,
                interval=request.interval,
            )
    except Exception as error:
        raise HTTPException(status_code=502, detail='LSEG data request failed') from error

    return {
        'mode': request.mode,
        'instruments': instruments,
        'fields': fields,
        'output_file': str(output),
        'row_count': len(data),
        'data': _frame_to_records(data),
    }


def main() -> None:
    import uvicorn

    uvicorn.run(
        'financial_engineering.api:app',
        host=os.getenv('API_HOST', '127.0.0.1'),
        port=int(os.getenv('API_PORT', '8000')),
    )


if __name__ == '__main__':
    main()
