import os
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from financial_engineering import api


class FakeFrame:
    def __len__(self):
        return 1

    def reset_index(self):
        return self

    def to_dict(self, *, orient):
        self.orient = orient
        return [{'Date': date(2026, 8, 28), 'TRDPRC_1': float('nan')}]


class ApiTest(unittest.TestCase):
    def test_history_request_defaults_to_three_years_and_serializes_missing_values(self):
        request = api.DataRequest(mode='history')

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), patch.object(
            api, 'extract_data', return_value=FakeFrame()
        ) as extract:
            response = api.fetch(request)

        end = date.today()
        extract.assert_called_once_with(
            app_key='test-key',
            mode='history',
            instruments=api.DEFAULT_INSTRUMENTS,
            fields=api.DEFAULT_HISTORY_FIELDS,
            output=api._output_path(api.DEFAULT_INSTRUMENTS),
            start=api._three_years_ago(end).isoformat(),
            end=end.isoformat(),
            interval='1D',
        )
        self.assertEqual(response['row_count'], 1)
        self.assertEqual(response['output_file'], 'data/data_VXc1_VXc2_VXc3_VXc4_VXc5_VXc6_VXc7_VXc8_VXc9.csv')
        self.assertEqual(response['data'], [{'Date': '2026-08-28', 'TRDPRC_1': None}])

    def test_snapshot_does_not_send_history_dates(self):
        request = api.DataRequest(mode='snapshot', instruments=['VXc1'])

        with patch.dict(os.environ, {'LSEG_APP_KEY': 'test-key'}), patch.object(
            api, 'extract_data', return_value=FakeFrame()
        ) as extract:
            api.fetch(request)

        extract.assert_called_once_with(
            app_key='test-key',
            mode='snapshot',
            instruments=['VXc1'],
            fields=api.DEFAULT_SNAPSHOT_FIELDS,
            output=api._output_path(['VXc1']),
            start=None,
            end=None,
            interval='1D',
        )

    def test_output_path_is_based_on_requested_instruments(self):
        self.assertEqual(api._output_path(['VX']), Path('data/data_VX.csv'))
        self.assertEqual(
            api._output_path(['BIGS', 'VXc1']),
            Path('data/data_BIGS_VXc1.csv'),
        )


if __name__ == '__main__':
    unittest.main()
