from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from financial_engineering.application.cli_support import (
    add_instrument_arguments,
    split_values,
)
from financial_engineering.application.use_cases.get_history.get_history_use_case import (
    GetHistoryUseCase,
)


router = APIRouter(tags=['history'])
get_history_use_case = GetHistoryUseCase()


class HistoryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    instruments: list[str] | None = None
    ticker: str | None = None
    fields: list[str] | None = None
    start: date
    end: date
    interval: str = '1D'


@router.post('/history')
def history(request: HistoryRequest) -> dict[str, Any]:
    return get_history_use_case.execute(
        instruments=request.instruments,
        ticker=request.ticker,
        fields=request.fields,
        start=request.start,
        end=request.end,
        interval=request.interval,
    )


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Fetch historical LSEG data.')
    add_instrument_arguments(parser)
    parser.add_argument('--start', required=True, help='History start date in YYYY-MM-DD format.')
    parser.add_argument('--end', required=True, help='History end date in YYYY-MM-DD format.')
    parser.add_argument('--fields', help='Comma-separated LSEG fields.')
    parser.add_argument('--interval', default='1D', help='History interval, for example 1D.')
    parser.add_argument('--output', type=Path, help='CSV output path.')
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    load_dotenv()
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    if not os.getenv('LSEG_APP_KEY'):
        parser.error('Set LSEG_APP_KEY or pass it through the environment')

    try:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
    except ValueError as error:
        parser.error(f'Dates must use YYYY-MM-DD format: {error}')

    result = get_history_use_case.execute(
        instruments=split_values(args.instruments) if args.instruments else None,
        ticker=args.ticker,
        fields=split_values(args.fields) if args.fields else None,
        start=start,
        end=end,
        interval=args.interval,
        output=args.output,
    )
    print(f"Wrote {result['row_count']} rows to {result['output_file']}")


if __name__ == '__main__':
    main()
