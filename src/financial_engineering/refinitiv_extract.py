from __future__ import annotations

import argparse
import os
from datetime import date
from getpass import getpass
from pathlib import Path
from typing import Sequence

import lseg.data as ld
from dotenv import load_dotenv


load_dotenv()


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]


def fetch_data(
    *,
    app_key: str,
    session_type: str,
    mode: str,
    instruments: Sequence[str],
    fields: Sequence[str],
    output: Path,
    username: str | None = None,
    password: str | None = None,
    start: str | None = None,
    end: str | None = None,
    interval: str = '1D',
) -> int:
    if session_type == 'desktop':
        session = ld.session.desktop.Definition(app_key=app_key).get_session()
    else:
        session = ld.session.platform.Definition(
            app_key=app_key,
            grant=ld.session.platform.GrantPassword(
                username=username,
                password=password,
            ),
        ).get_session()

    session.open()
    try:
        ld.session.set_default(session)

        if mode == 'history':
            data = ld.get_history(
                universe=list(instruments),
                fields=list(fields),
                interval=interval,
                start=start,
                end=end or date.today().isoformat(),
            )
        else:
            response = ld.content.pricing.Definition(
                universe=list(instruments),
                fields=list(fields),
            ).get_data(session=session)
            data = response.data.df

        output.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output)
        return len(data)
    finally:
        session.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Extract data from the LSEG Data Platform into a CSV file.'
    )
    parser.add_argument(
        '--username',
        default=os.getenv('LSEG_USERNAME'),
        help='Platform username or machine ID. Defaults to LSEG_USERNAME.',
    )
    parser.add_argument(
        '--app-key',
        default=os.getenv('LSEG_APP_KEY'),
        help='LSEG application key. Defaults to LSEG_APP_KEY.',
    )
    parser.add_argument(
        '--session',
        choices=('desktop', 'platform'),
        default='desktop',
        help='Connection type. Desktop requires Workspace to be running.',
    )
    parser.add_argument(
        '--mode',
        choices=('snapshot', 'history'),
        default='snapshot',
    )
    parser.add_argument(
        '--instruments',
        required=True,
        help='Comma-separated RICs, for example AAPL.O,MSFT.O.',
    )
    parser.add_argument(
        '--fields',
        help='Comma-separated fields. Defaults to BID,ASK or TRDPRC_1 for history.',
    )
    parser.add_argument('--start', help='History start date in YYYY-MM-DD format.')
    parser.add_argument('--end', help='History end date in YYYY-MM-DD format.')
    parser.add_argument('--interval', default='1D', help='History interval, for example 1D.')
    parser.add_argument('--output', type=Path, default=Path('data/refinitiv_data.csv'))
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.app_key:
        parser.error('--app-key or LSEG_APP_KEY is required')
    if args.mode == 'history' and not args.start:
        parser.error('--start is required when --mode=history')

    password = None
    if args.session == 'platform':
        if not args.username:
            parser.error('--username or LSEG_USERNAME is required for platform sessions')
        password = os.getenv('LSEG_PASSWORD') or getpass('LSEG password: ')

    default_fields = 'TRDPRC_1' if args.mode == 'history' else 'BID,ASK'
    fields = split_values(args.fields or default_fields)
    instruments = split_values(args.instruments)

    row_count = fetch_data(
        app_key=args.app_key,
        session_type=args.session,
        mode=args.mode,
        instruments=instruments,
        fields=fields,
        output=args.output,
        username=args.username,
        password=password,
        start=args.start,
        end=args.end,
        interval=args.interval,
    )
    print(f'Wrote {row_count} rows to {args.output}')


if __name__ == '__main__':
    main()
