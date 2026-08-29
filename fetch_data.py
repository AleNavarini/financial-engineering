import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from financial_engineering.infrastructure.lseg_client import LsegClient


MODE = 'history'
INSTRUMENTS = [f'VXc{month}' for month in range(1, 10)]
FIELDS = [
    'TRDPRC_1',
    'SETTLE',
    'OPINT_1',
]
END_DATE = date.today()
try:
    START_DATE = END_DATE.replace(year=END_DATE.year - 3).isoformat()
except ValueError:
    START_DATE = END_DATE.replace(year=END_DATE.year - 3, day=28).isoformat()
END_DATE = END_DATE.isoformat()
OUTPUT = Path('data/vix_futures_3y.csv')


def main() -> None:
    load_dotenv()
    app_key = os.getenv('LSEG_APP_KEY')
    if not app_key:
        raise RuntimeError('Set LSEG_APP_KEY in .env')

    row_count = LsegClient(app_key).fetch_data(
        mode=MODE,
        instruments=INSTRUMENTS,
        fields=FIELDS,
        output=OUTPUT,
        start=START_DATE,
        end=END_DATE,
    )
    print(f'Wrote {row_count} rows to {OUTPUT}')


if __name__ == '__main__':
    main()
