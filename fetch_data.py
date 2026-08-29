import os
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

from financial_engineering.refinitiv_extract import fetch_data


INSTRUMENTS = ['BTC=']
FIELDS = ['BID', 'ASK']
START_DATE = (date.today() - timedelta(days=30)).isoformat()
END_DATE = date.today().isoformat()
OUTPUT = Path('data/refinitiv_data.csv')


def main() -> None:
    load_dotenv()
    app_key = os.getenv('LSEG_APP_KEY')
    if not app_key:
        raise RuntimeError('Set LSEG_APP_KEY in .env')

    row_count = fetch_data(
        app_key=app_key,
        mode='history',
        instruments=INSTRUMENTS,
        fields=FIELDS,
        output=OUTPUT,
        start=START_DATE,
        end=END_DATE,
    )
    print(f'Wrote {row_count} rows to {OUTPUT}')


if __name__ == '__main__':
    main()
