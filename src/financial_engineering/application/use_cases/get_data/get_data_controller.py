from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from financial_engineering.application.cli_support import (
    add_instrument_arguments,
    split_values,
)
from financial_engineering.application.use_cases.get_data.get_data_use_case import (
    GetDataUseCase,
)
from financial_engineering.infrastructure.logging_config import setup_logging


router = APIRouter(tags=['data'])
get_data_use_case = GetDataUseCase()


class DataRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    instruments: list[str] | None = None
    ticker: str | None = None
    fields: list[str] | None = None


@router.post('/data')
def data(request: DataRequest) -> dict[str, Any]:
    return get_data_use_case.execute(
        instruments=request.instruments,
        ticker=request.ticker,
        fields=request.fields,
    )


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Fetch current LSEG data.')
    add_instrument_arguments(parser)
    parser.add_argument('--fields', help='Comma-separated LSEG fields.')
    parser.add_argument('--output', type=Path, help='CSV output path.')
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    setup_logging()
    load_dotenv()
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    if not os.getenv('LSEG_APP_KEY'):
        parser.error('Set LSEG_APP_KEY or pass it through the environment')

    result = get_data_use_case.execute(
        instruments=split_values(args.instruments) if args.instruments else None,
        ticker=args.ticker,
        fields=split_values(args.fields) if args.fields else None,
        output=args.output,
    )
    print(f"Wrote {result['row_count']} rows to {result['output_file']}")


if __name__ == '__main__':
    main()
