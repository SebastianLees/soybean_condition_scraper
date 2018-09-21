# -*- coding: utf-8 -*-
# The soybean condition scraper tests.

from unittest.mock import patch, mock_open

import pytest

from scraper.scraper import get_zip_files_links, get_soybean_data, YEAR,\
    clean_soybean_data, create_output_file, write_to_output_file, clean_week_ending


def mock_response(*args, **kwargs):
    class MockResponse():
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content

    return MockResponse(
        200,
        '<div id="n{0}"><a href="http://google.com/file.zip">zip</a></div>'
            .format(str(YEAR))
    )


@patch('scraper.scraper.requests.get', side_effect=mock_response)
def test_get_zip_files_links(mock_reponse):
    links = get_zip_files_links()
    assert links == ['http://google.com/file.zip']
    assert len(links) == 1


@pytest.mark.parametrize('table_found,csv_file_data,output_data', [
    (True,
     ['35', 't', '"Soybean Condition Week Ending November 30, 2001"', '\n'
      '35', 'd', 'Texas', '35', '34', '12', '8', '10'],
     [{'Week ending': '2001-11-30', 'State': 'Texas', 'Condition': 'Very poor', 'Percent': '35'},
      {'Week ending': '2001-11-30', 'State': 'Texas', 'Condition': 'Poor', 'Percent': '34'},
      {'Week ending': '2001-11-30', 'State': 'Texas', 'Condition': 'Fair', 'Percent': '12'},
      {'Week ending': '2001-11-30', 'State': 'Texas', 'Condition': 'Good', 'Percent': '8'},
      {'Week ending': '2001-11-30', 'State': 'Texas', 'Condition': 'Excellent', 'Percent': '10'}])
])
def test_get_soybean_data(table_found, csv_file_data, output_data):

    csv_file_data = ','.join(csv_file_data)
    test_data, test_table_found = get_soybean_data(csv_file_data,
                                                   decode_file=False)

    assert test_table_found == table_found
    assert test_data == output_data


@pytest.mark.parametrize('dirty_data, clean_data', [
    ([{
        'Week ending': '',
        'State': '',
        'Condition': 'poor',
        'Percent': 47,
    },
    {
        'Week ending': '2018-10-10',
        'State': 'Texas',
        'Condition': 'Very poor',
        'Percent': 15,
    }],
    [{
        'Week ending': '2018-10-10',
        'State': 'Texas',
        'Condition': 'Very poor',
        'Percent': 15,
    }])
])
def test_clean_soybean_data(dirty_data, clean_data):
    assert clean_soybean_data(dirty_data) == clean_data


def test_create_output_file():
    with patch('builtins.open', new_callable=mock_open()) as m:
        filename = create_output_file(output_file='test_file')

    assert 'output/test_file' in filename


@pytest.mark.parametrize('dirty_date,clean_date', [
    ('November 6, 2012', '2012-11-06'),
    ('October 8, 1999', '1999-10-08'),
    ('May 1, 2018', '2018-05-01'),
])
def test_clean_week_ending(dirty_date, clean_date):
    assert clean_week_ending(dirty_date) == clean_date
