# -*- coding: utf-8 -*-
# The main soybean condition scraper script.

import csv
import re
from datetime import datetime
from io import BytesIO, StringIO
from zipfile import ZipFile

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

# File name to be extracted from ZIP archives at USDA website.
EXTRACT_FILE = 'prog_all_tables.csv'

# Outout file name
OUTPUT_FILE = 'soybean_condition'

# Set up script conditions
states = [state.lower() for state in STATES]

################################################################################
# Main script.
################################################################################


def get_zip_files_links(url=URL, year=YEAR):
    """
    Retrieves a list of zip files to download.

    :return: List of links.
    """

    print('Getting list of Zip files')

    page = requests.get(url)
    year = 'n' + str(year)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        soup = soup.findAll('div', attrs={'id': year})
        links = []

        for div in soup:
            links = div.findAll('a', attrs={'href': re.compile("^http://")})
            # Only retain zip files
            links = [link['href'] for link in links if 'zip' in link]

        print('{0} Zip files found'.format(len(links)))

        return links

    else:
        raise Exception('URL could not be found, received {0} error'.format(
            str(page.status_code))
        )


def extract_zip(link, extract_file=EXTRACT_FILE):
    """
    Takes a url links to a zip file, extracts it and returns the main report.

    :param link: Zip file URL link (STR)
    :return: CSV file.
    """

    zipfile = requests.get(link, stream=True)
    zipfile = ZipFile(BytesIO(zipfile.content))

    return zipfile.read(extract_file)


def get_soybean_data(csv_file):
    """
    Extract Soybean Condition data from raw file.

    :param csv_file: The CSV file path (STR)
    :return: A list of dictionary values
    """


    # Open CSV file
    reader = csv.reader(StringIO(csv_file.decode('ISO-8859-1')))

    # Container
    data = list()
    week_ending = None
    soybean_table_found = False

    # Extract data
    for row in reader:

        # See if Soybean table exists and get week ending string
        if row[0] == '35' and row[1] == 't':
            if 'Soybean Condition' in row[2]:
                soybean_table_found = True

            if 'Week Ending' in row[2]:
                week_ending = row[2].split('Week Ending', 1)
                week_ending = week_ending[1].strip()
                week_ending = clean_week_ending(week_ending)

                print('Soybean condition data found for Week ending {0}'
                      .format(week_ending))

        # Get raw data
        if row[0] == '35' and row [1] == 'd':
            conditions = {
                'Very poor': row[3],
                'Poor': row[4],
                'Fair': row[5],
                'Good': row[6],
                'Excellent': row[7],
            }

            for key in conditions:
                if conditions[key] != '-':
                    entry = {
                        'Week ending': week_ending,
                        'State': row[2],
                        'Condition': key,
                        'Percent': conditions[key],
                    }

                    data.append(entry)

    return data, soybean_table_found


def clean_soybean_data(data, states=states):
    """
    Cleans the Soybean Condition data once it had been extracted from the CSV.

    :param data: Soybean data - List of Dictionaries.
    :return: Soybean data - List of Dictionaries.
    """

    return [entry for entry in data if entry['State'].lower() in states]


def create_output_file(output_file=OUTPUT_FILE):
    """
    Creates output file for CSV data.

    :return: Output file name (STR)
    """

    timestamp = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    name = 'output/{0}_{1}.csv'.format(output_file, timestamp)

    with open(name, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, KEYS)
        dict_writer.writeheader()

    print('Output file created: {0}'.format(name))

    return name


def write_to_output_file(file_name, data):
    """
    Takes parsed data (in the form of a list of dictionaries) and writes
    it to the output csv file.

    :param file_name: Path to the output file (STR).
    :param week_ending The week ending for the file (YYY-MM-DD)(STR).
    :param data: The data itself (LIST of DICT).
    """
    try:
        with open(file_name, 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, KEYS)
            dict_writer.writerows(data)

        print('Extracted Soybean condition data')

        return True

    except Exception as e:
        print ('Filed to extract Soybean condition data from {0}')\
            .format(file_name)

        return False


def clean_week_ending(week_ending):
    """
    Cleans a week ending string of type "November 6th 2005" to match the format
    YYYY-MM-DD.

    :param week_ending: Week ending (STR)
    :return: Week ending (STR)
    """

    week_ending = datetime.strptime(week_ending, '%B %d, %Y')
    week_ending = week_ending.strftime('%Y-%m-%d')

    return week_ending


def run():
    """
    Entry point for the script.
    """

    soybean_found = 0
    soybean_extracted = 0

    # 1) Get the list of files to be downloaded based off of YEAR setting value.
    links = get_zip_files_links()

    # 2) Create output file with headers.
    output_file = create_output_file()

    # 3) Download and extract zip files, then clean them and output to csv file.
    soybean_files = len(links)

    for link in links:
        csv_file = extract_zip(link)
        csv_data, soybean_table_exists = get_soybean_data(csv_file)

        if soybean_table_exists:
            soybean_found += 1
            csv_data_clean = clean_soybean_data(csv_data)
            csv_output = write_to_output_file(output_file, csv_data_clean)
            if csv_output:
                soybean_extracted += 1

    print('Found Soybean condition data in {0}/{1} files.'
          .format(soybean_found, soybean_files))
    print('Successfully extracted Soybean condition data from {0}/{1} files.'
          .format(soybean_extracted, soybean_found))


if __name__ == '__main__':
    run()
