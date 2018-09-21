# -*- coding: utf-8 -*-
# The main soybean condition scraper script.

import csv
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


################################################################################
# The settings & setup for the soybean condition scraper script.
################################################################################

# Configure which states are to be extracted (all states by default).
STATES = [

    'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
    'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
    'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
    'maine' 'maryland', 'massachusetts', 'michigan', 'minnesota',
    'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
    'new hampshire', 'new jersey', 'new mexico', 'new york',
    'north carolina', 'north dakota', 'ohio',
    'oklahoma', 'oregon', 'pennsylvania', 'rhode island',
    'south  carolina', 'south dakota', 'tennessee', 'texas', 'utah',
    'vermont', 'virginia', 'washington', 'west virginia',
    'wisconsin', 'wyoming'
]


# Configure the names of the output csv headers. WARNING: Changes to this
# wil cause break in the script.
KEYS = ['Week ending', 'State', 'Condition', 'Percent']

# Year to be extracted
YEAR = 2016

# Url to be interrogated
URL = 'http://usda.mannlib.cornell.edu/MannUsda/viewDocumentInfo.do?documentID=1048'

# Set up script conditions
states = [state.lower() for state in STATES]
csv_file = 'prog_all_tables.csv'


################################################################################
# Main script.
################################################################################


def get_zip_files_links(url=URL, year=YEAR):
    """
    Retrieves a list of zip files to download.

    :return: List of links.
    """

    page = requests.get(url)
    year = 'n' + str(year)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        soup = soup.findAll('div', attrs={'id': year})
        links = []

        for div in soup:
            links = div.findAll('a', attrs={'href': re.compile("^http://")})

            # Only retain zip files
            links = [link for link in links if 'zip' in link]

        return links

    else:
        raise Exception('URL could not be found, received {0} error'.format(
            str(page.status_code))
        )


def get_soybean_data(csv_file):
    """
    Extract Soybean Condition data from raw file.

    :param csv_file: The CSV file path (STR)
    :return: A list of dictionary values
    """

    # Open CSV file
    reader = csv.reader(open(csv_file, 'r', encoding='ISO-8859-1'))

    # Container
    data = list()

    # Extract
    for row in reader:
        if row[0] == '35' and row [1] == 'd':
            conditions = {
                'Very poor': row[3],
                'Poor': row[4],
                'Fair': row[5],
                'Good': row[6],
                'Excellent': row[7],
            }

            for key in conditions:
                entry = {
                    'Week ending': '2016-10-02',
                    'State': row[2],
                    'Condition': key,
                    'Percent': conditions[key],
                }

                data.append(entry)

    return data


def clean_soybean_data(data, states=states):
    """
    Cleans the Soybean Condition data once it had been extracted from the CSV.

    :param data: Soybean data - List of Dictionaries.
    :return: Soybean data - List of Dictionaries.
    """

    return [entry for entry in data if entry['State'].lower() in states]


def create_output_file():
    """
    Creates output file for CSV data.

    :return: Output file name (STR)
    """

    timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    name = 'output/soybean_condition_' + timestamp + '.csv'

    with open(name, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, KEYS)
        dict_writer.writeheader()

    return name


def write_to_output_file(file_name, data):
    """
    Takes parsed data (in the form of a list of dictionaries) and writes
    it to the output csv file.

    :param file_name: Path to the output file (STR)
    :param data: The data itself (LIST of DICT).
    """

    with open(file_name, 'a') as output_file:
        dict_writer = csv.DictWriter(output_file, KEYS)
        dict_writer.writerows(data)


if __name__ == '__main__':
    # 1) Get the list of files to be downloaded based off year.
    links = get_zip_files_links()

    # 2) Create output file with headers.
    file_name = create_output_file()

    # 3) Download and extract zip files, then process to output csv file.
    for link in links:
        a = get_soybean_data('prog_all_tables.csv')
        a = clean_soybean_data(a)
        write_to_output_file(file_name, a)