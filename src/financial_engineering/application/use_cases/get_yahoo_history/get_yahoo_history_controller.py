from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from financial_engineering.application.use_cases.get_yahoo_history.get_yahoo_history_use_case import (
    GetYahooHistoryUseCase,
)


router = APIRouter(tags=['yahoo'])
get_yahoo_history_use_case = GetYahooHistoryUseCase()


class YahooHistoryRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    ticker: str
    fields: list[str] | None = None
    start: date
    end: date
    interval: str = '1d'


@router.post('/yahoo/history')
def yahoo_history(request: YahooHistoryRequest) -> dict[str, Any]:
    return get_yahoo_history_use_case.execute(
        ticker=request.ticker,
        fields=request.fields,
        start=request.start,
        end=request.end,
        interval=request.interval,
    )


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Fetch historical Yahoo Finance data.')
    parser.add_argument('--ticker', required=True, help='Yahoo Finance ticker, for example ^VIX.')
    parser.add_argument('--start', required=True, help='History start date in YYYY-MM-DD format.')
    parser.add_argument('--end', required=True, help='History end date in YYYY-MM-DD format.')
    parser.add_argument('--fields', help='Comma-separated Yahoo Finance fields.')
    parser.add_argument('--interval', default='1d', help='History interval, for example 1d.')
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    try:
        start = date.fromisoformat(args.start)
        end = date.fromisoformat(args.end)
    except ValueError as error:
        parser.error(f'Dates must use YYYY-MM-DD format: {error}')

    result = get_yahoo_history_use_case.execute(
        ticker=args.ticker,
        fields=[item.strip() for item in args.fields.split(',') if item.strip()] if args.fields else None,
        start=start,
        end=end,
        interval=args.interval,
    )
    print(f"Wrote {result['row_count']} rows to {result['output_file']}")


if __name__ == '__main__':
    main()
