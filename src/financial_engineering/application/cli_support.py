from __future__ import annotations

import argparse


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]


def add_instrument_arguments(parser: argparse.ArgumentParser) -> None:
    instruments = parser.add_mutually_exclusive_group(required=True)
    instruments.add_argument('--ticker', help='One LSEG RIC, for example VXc1.')
    instruments.add_argument(
        '--instruments',
        help='Comma-separated LSEG RICs, for example VXc1,VXc2.',
    )
