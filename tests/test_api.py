import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError
from fastapi.testclient import TestClient

from financial_engineering.app import app
from financial_engineering.application.use_cases.get_data import get_data_controller
from financial_engineering.application.use_cases.get_history import get_history_controller
from financial_engineering.application.datasets import datasets_controller
from financial_engineering.infrastructure import lseg_client


class FakeFrame:
    def __len__(self):
        return 1

    def reset_index(self):
        return self

    def to_dict(self, *, orient):
        self.orient = orient
        return [{'Date': date(2026, 8, 28), 'TRDPRC_1': float('nan')}]


class ApiTest(unittest.TestCase):
    def test_history_request_requires_explicit_dates(self):
        with self.assertRaises(ValidationError):
            get_history_controller.HistoryRequest(ticker='VXc1', end=date(2024, 12, 31))

        with self.assertRaises(ValidationError):
            get_history_controller.HistoryRequest(ticker='VXc1', start=date(2024, 1, 1))

    def test_history_controller_uses_explicit_dates_and_serializes_missing_values(self):
        request = get_history_controller.HistoryRequest(
            instruments=['VXc1', 'VXc2'],
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
        )

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), patch.object(
            lseg_client.LsegClient, 'extract_data', return_value=FakeFrame()
        ) as extract:
            response = get_history_controller.history(request)

        output = Path('data/data_VXc1_VXc2_2024-01-01_to_2024-12-31.csv')
        extract.assert_called_once_with(
            mode='history',
            instruments=['VXc1', 'VXc2'],
            fields=lseg_client.DEFAULT_HISTORY_FIELDS,
            output=output,
            start='2024-01-01',
            end='2024-12-31',
            interval='1D',
        )
        self.assertEqual(response['row_count'], 1)
        self.assertEqual(response['output_file'], str(output))
        self.assertIsNone(response['ticker'])
        self.assertEqual(response['data'], [{'Date': '2026-08-28', 'TRDPRC_1': None}])

    def test_history_controller_supports_one_ticker(self):
        request = get_history_controller.HistoryRequest(
            ticker='VXc1',
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
        )

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), patch.object(
            lseg_client.LsegClient, 'extract_data', return_value=FakeFrame()
        ):
            response = get_history_controller.history(request)

        self.assertEqual(response['ticker'], 'VXc1')
        self.assertEqual(
            response['output_file'],
            str(Path('data/data_VXc1_2024-01-01_to_2024-12-31.csv')),
        )

    def test_data_controller_requests_snapshot_without_history_dates(self):
        request = get_data_controller.DataRequest(ticker='VXc1')

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), patch.object(
            lseg_client.LsegClient, 'extract_data', return_value=FakeFrame()
        ) as extract:
            response = get_data_controller.data(request)

        extract.assert_called_once_with(
            mode='snapshot',
            instruments=['VXc1'],
            fields=lseg_client.DEFAULT_DATA_FIELDS,
            output=lseg_client._output_path(['VXc1']),
            start=None,
            end=None,
            interval='1D',
        )
        self.assertEqual(response['mode'], 'snapshot')
        self.assertEqual(response['ticker'], 'VXc1')

    def test_history_and_data_requests_are_separate(self):
        with self.assertRaises(ValidationError):
            get_data_controller.DataRequest(ticker='VXc1', start=date(2024, 1, 1))

        with self.assertRaises(ValidationError):
            get_data_controller.DataRequest(ticker='VXc1', mode='history')

    def test_instruments_and_ticker_cannot_be_combined(self):
        request = get_data_controller.DataRequest(instruments=['VXc1'], ticker='VXc2')

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), self.assertRaises(
            lseg_client.HTTPException
        ):
            get_data_controller.data(request)

    def test_history_date_range_must_be_valid(self):
        request = get_history_controller.HistoryRequest(
            ticker='VXc1',
            start=date(2024, 12, 31),
            end=date(2024, 1, 1),
        )

        with self.assertRaises(lseg_client.HTTPException):
            get_history_controller.history(request)

    def test_output_path_includes_history_date_range(self):
        self.assertEqual(
            lseg_client._output_path(['VXc1'], '2024-01-01', '2024-12-31'),
            Path('data/data_VXc1_2024-01-01_to_2024-12-31.csv'),
        )

    def test_api_registers_history_and_data_routes(self):
        routes = set(app.openapi()['paths'])

        self.assertIn('/history', routes)
        self.assertIn('/data', routes)
        self.assertIn('/datasets', routes)


class DatasetApiTest(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.previous_directory = datasets_controller.dataset_store.data_directory
        datasets_controller.dataset_store.data_directory = Path(self.temp_directory.name)
        (Path(self.temp_directory.name) / 'curve.csv').write_text(
            ',VXc1,VXc1,VXc2,VXc2\n'
            ',TRDPRC_1,OPINT_1,TRDPRC_1,OPINT_1\n'
            'Date,,,,\n'
            '2026-01-01,20.1,10,21.2,12\n'
            '2026-01-02,20.4,11,21.5,13\n',
            encoding='utf-8',
        )
        self.client = TestClient(app)

    def tearDown(self):
        datasets_controller.dataset_store.data_directory = self.previous_directory
        self.temp_directory.cleanup()

    def test_datasets_can_be_listed_and_read(self):
        response = self.client.get('/datasets')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['datasets'][0]['row_count'], 2)

        response = self.client.get('/datasets/curve.csv')

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['date_range'], {'start': '2026-01-01', 'end': '2026-01-02'})
        self.assertEqual(body['columns'][1]['label'], 'VXc1 / TRDPRC_1')
        self.assertEqual(body['columns'][1]['type'], 'number')
        self.assertEqual(body['rows'][0]['VXc1 / TRDPRC_1'], 20.1)

    def test_dataset_can_be_downloaded_and_unsafe_path_is_rejected(self):
        response = self.client.get('/datasets/curve.csv/download')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response.headers['content-type'])
        self.assertIn('VXc1', response.text)

        response = self.client.get('/datasets/..%2Fpyproject.toml')

        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
