import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from financial_engineering.app import app
from financial_engineering.application.use_cases.get_data import get_data_controller
from financial_engineering.application.use_cases.get_history import get_history_controller
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
            'data/data_VXc1_2024-01-01_to_2024-12-31.csv',
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


if __name__ == '__main__':
    unittest.main()
