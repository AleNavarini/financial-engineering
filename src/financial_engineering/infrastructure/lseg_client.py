from __future__ import annotations

import json
import math
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Sequence
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import HTTPException
import lseg.data as ld


WORKSPACE_PROXY_PORTS = range(9000, 9061)
DEFAULT_HISTORY_FIELDS = ['TRDPRC_1', 'SETTLE', 'OPINT_1']
DEFAULT_DATA_FIELDS = ['BID', 'ASK', 'TRDPRC_1', 'SETTLE', 'OPINT_1']
extraction_lock = Lock()


def find_workspace_proxy_port() -> int:
    for port in WORKSPACE_PROXY_PORTS:
        try:
            with urlopen(f'http://127.0.0.1:{port}/api/status', timeout=0.25) as response:
                status = json.load(response)
                if status.get('statusCode') == 'ST_PROXY_READY':
                    return port
        except (OSError, URLError, TimeoutError, json.JSONDecodeError):
            continue

    raise RuntimeError(
        'Workspace Desktop Data API proxy is not ready on ports 9000 through 9060'
    )


def _output_path(
    instruments: list[str],
    start: str | None = None,
    end: str | None = None,
) -> Path:
    names = [
        re.sub(r'[^A-Za-z0-9]+', '-', instrument.strip()).strip('-')
        for instrument in instruments
    ]
    if any(not name for name in names):
        raise HTTPException(status_code=422, detail='Instrument names must not be empty')
    if (start is None) != (end is None):
        raise HTTPException(status_code=422, detail='Both start and end are required together')

    data_directory = Path(os.getenv('DATA_DIR', 'data'))
    date_range = f'_{start}_to_{end}' if start and end else ''
    return data_directory / f"data_{'_'.join(names)}{date_range}.csv"


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


class LsegClient:
    def __init__(self, app_key: str | None = None) -> None:
        self.app_key = app_key

    def get_data(
        self,
        *,
        instruments: list[str] | None,
        ticker: str | None,
        fields: list[str] | None,
        output: Path | None = None,
    ) -> dict[str, Any]:
        return self._execute_request(
            mode='snapshot',
            instruments=instruments,
            ticker=ticker,
            fields=fields,
            output=output,
        )

    def get_history(
        self,
        *,
        instruments: list[str] | None,
        ticker: str | None,
        fields: list[str] | None,
        start: date,
        end: date,
        interval: str,
        output: Path | None = None,
    ) -> dict[str, Any]:
        if start > end:
            raise HTTPException(status_code=422, detail='start must not be after end')

        return self._execute_request(
            mode='history',
            instruments=instruments,
            ticker=ticker,
            fields=fields,
            start=start,
            end=end,
            interval=interval,
            output=output,
        )

    def extract_data(
        self,
        *,
        mode: str,
        instruments: Sequence[str],
        fields: Sequence[str],
        output: Path | None = None,
        start: str | None = None,
        end: str | None = None,
        interval: str = '1D',
    ) -> Any:
        app_key = self.app_key or os.getenv('LSEG_APP_KEY')
        if not app_key:
            raise RuntimeError('LSEG_APP_KEY is not configured')

        session = ld.session.desktop.Definition(app_key=app_key).get_session()
        session.set_port_number(find_workspace_proxy_port())

        session.open()
        try:
            ld.session.set_default(session)
            instrument_list = list(instruments)
            if len(instrument_list) == 1 and instrument_list[0].startswith('0#'):
                instrument_list = list(ld.discovery.Chain(instrument_list[0]).constituents)

            if mode == 'history':
                data = ld.get_history(
                    universe=instrument_list,
                    fields=list(fields),
                    interval=interval,
                    start=start,
                    end=end or date.today().isoformat(),
                )
            else:
                data = ld.get_data(
                    universe=instrument_list,
                    fields=list(fields),
                )

            if output is not None:
                output.parent.mkdir(parents=True, exist_ok=True)
                data.to_csv(output)
            return data
        finally:
            request_failed = sys.exc_info()[0] is not None
            try:
                session.close()
            except Exception:
                if not request_failed:
                    raise

    def fetch_data(
        self,
        *,
        mode: str,
        instruments: Sequence[str],
        fields: Sequence[str],
        output: Path,
        start: str | None = None,
        end: str | None = None,
        interval: str = '1D',
    ) -> int:
        data = self.extract_data(
            mode=mode,
            instruments=instruments,
            fields=fields,
            output=output,
            start=start,
            end=end,
            interval=interval,
        )
        return len(data)

    def _execute_request(
        self,
        *,
        mode: str,
        instruments: list[str] | None,
        ticker: str | None,
        fields: list[str] | None,
        output: Path | None = None,
        start: date | None = None,
        end: date | None = None,
        interval: str = '1D',
    ) -> dict[str, Any]:
        if not self.app_key and not os.getenv('LSEG_APP_KEY'):
            raise HTTPException(status_code=503, detail='LSEG_APP_KEY is not configured')

        resolved_instruments = self._resolve_instruments(instruments, ticker)
        resolved_fields = fields or (
            DEFAULT_HISTORY_FIELDS if mode == 'history' else DEFAULT_DATA_FIELDS
        )
        start_value = start.isoformat() if start else None
        end_value = end.isoformat() if end else None
        output = output or _output_path(resolved_instruments, start_value, end_value)

        try:
            # The Desktop session is shared by the local LSEG proxy, so serialize calls.
            with extraction_lock:
                data = self.extract_data(
                    mode=mode,
                    instruments=resolved_instruments,
                    fields=resolved_fields,
                    output=output,
                    start=start_value,
                    end=end_value,
                    interval=interval,
                )
        except Exception as error:
            raise HTTPException(status_code=502, detail='LSEG data request failed') from error

        return {
            'mode': mode,
            'instruments': resolved_instruments,
            'ticker': resolved_instruments[0] if ticker else None,
            'fields': resolved_fields,
            'start': start_value,
            'end': end_value,
            'output_file': str(output),
            'row_count': len(data),
            'data': _frame_to_records(data),
        }

    @staticmethod
    def _resolve_instruments(
        instruments: list[str] | None,
        ticker: str | None,
    ) -> list[str]:
        if instruments is not None and ticker is not None:
            raise HTTPException(status_code=422, detail='Use instruments or ticker, not both')

        resolved = instruments if instruments is not None else [ticker] if ticker is not None else []
        if not resolved:
            raise HTTPException(status_code=422, detail='At least one instrument is required')
        return resolved
