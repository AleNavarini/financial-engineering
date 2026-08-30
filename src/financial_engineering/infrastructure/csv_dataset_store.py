from __future__ import annotations

import csv
import math
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any


class CsvDatasetStore:
    def __init__(self, data_directory: Path | None = None) -> None:
        self.data_directory = data_directory or Path(os.getenv('DATA_DIR', 'data'))

    def list_datasets(self) -> list[dict[str, Any]]:
        datasets = []
        for path in self.data_directory.glob('*.csv'):
            try:
                datasets.append(self._summary(path))
            except ValueError:
                continue
        return sorted(datasets, key=lambda dataset: dataset['modified_at'], reverse=True)

    def get_dataset(self, name: str) -> dict[str, Any]:
        path = self._resolve_path(name)
        columns, rows = self._parse(path)
        return {
            **self._summary(path, columns=columns, rows=rows),
            'rows': rows,
        }

    def get_download_path(self, name: str) -> Path:
        path = self._resolve_path(name)
        if not path.is_file():
            raise FileNotFoundError(name)
        return path

    def _summary(
        self,
        path: Path,
        *,
        columns: list[dict[str, str]] | None = None,
        rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if columns is None or rows is None:
            columns, rows = self._parse(path)

        date_columns = [column['key'] for column in columns if column['type'] == 'date']
        dates = [row[date_columns[0]] for row in rows if date_columns and row[date_columns[0]]]
        return {
            'name': path.name,
            'size_bytes': path.stat().st_size,
            'modified_at': datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(),
            'row_count': len(rows),
            'columns': columns,
            'date_range': {
                'start': min(dates),
                'end': max(dates),
            } if dates else None,
        }

    def _parse(self, path: Path) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        with path.open('r', encoding='utf-8-sig', newline='') as csv_file:
            raw_rows = list(csv.reader(csv_file))

        if not raw_rows:
            raise ValueError(f'Dataset is empty: {path.name}')

        header_rows = 3 if self._has_multi_level_header(raw_rows) else 1
        if len(raw_rows) <= header_rows:
            raise ValueError(f'Dataset has no data rows: {path.name}')

        headers = self._build_headers(raw_rows[:header_rows])
        data_rows = [row for row in raw_rows[header_rows:] if any(value.strip() for value in row)]
        rows = [
            {
                column['key']: self._parse_value(row[index] if index < len(row) else '')
                for index, column in enumerate(headers)
            }
            for row in data_rows
        ]
        columns = [
            {
                **column,
                'type': self._column_type(column['key'], [row[column['key']] for row in rows]),
            }
            for column in headers
        ]
        return columns, rows

    @staticmethod
    def _has_multi_level_header(rows: list[list[str]]) -> bool:
        return (
            len(rows) >= 3
            and not rows[0][0].strip()
            and not rows[1][0].strip()
            and rows[2][0].strip().lower() in {'date', 'datetime', 'timestamp'}
        )

    @staticmethod
    def _build_headers(header_rows: list[list[str]]) -> list[dict[str, str]]:
        width = max(len(row) for row in header_rows)
        headers = []
        used_keys: set[str] = set()
        for index in range(width):
            parts = [row[index].strip() for row in header_rows if index < len(row) and row[index].strip()]
            label = ' / '.join(dict.fromkeys(parts)) or f'Column {index + 1}'
            key = label
            suffix = 2
            while key in used_keys:
                key = f'{label} ({suffix})'
                suffix += 1
            used_keys.add(key)
            headers.append({'key': key, 'label': label})
        return headers

    @staticmethod
    def _parse_value(value: str) -> Any:
        value = value.strip()
        if not value or value.lower() in {'nan', 'nat', 'none', 'null'}:
            return None
        try:
            number = float(value)
        except ValueError:
            return value
        if math.isfinite(number):
            return int(number) if number.is_integer() else number
        return None

    @staticmethod
    def _column_type(key: str, values: list[Any]) -> str:
        non_empty = [value for value in values if value is not None]
        if not non_empty:
            return 'string'
        if any(isinstance(value, (int, float)) and not isinstance(value, bool) for value in non_empty):
            return 'number' if all(isinstance(value, (int, float)) for value in non_empty) else 'string'
        if 'date' in key.lower() or 'time' in key.lower():
            if all(CsvDatasetStore._is_date(value) for value in non_empty):
                return 'date'
        return 'string'

    @staticmethod
    def _is_date(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        try:
            date.fromisoformat(value[:10])
        except ValueError:
            return False
        return True

    def _resolve_path(self, name: str) -> Path:
        path = (self.data_directory / name).resolve()
        data_directory = self.data_directory.resolve()
        if path.parent != data_directory or path.suffix.lower() != '.csv':
            raise ValueError('Only CSV files in the data directory can be accessed')
        return path
