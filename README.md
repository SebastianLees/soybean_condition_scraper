# Soybean condition scraper

Soybean condition scraper is a small script that queries and stores soybean condition data from the US National Agricultural Statistics Service (http://usda.mannlib.cornell.edu/MannUsda/viewDocumentInfo.do?documentID=1048). The script will scrape zipped csv data from the USNAS website for a specified year, and look to see if any information on soybean condition is contained within. It was output all collected data as a csv file of schema:

- Week ending (YYYY-MM-DD)
- State
- Condition
- Percent

### Requirements:
- Python 3.6+

### Installation
1) Clone the repository to a local directory
2) Install the Python dependencies from the requirements.txt file (you may wish you use a virtual environment).
3) The script can be run manually (scraper.py) or scheduling can be set up.

### Assumptions
This is designed to be a simple script - features like logging, advanced dugging and custom functionality are not included.

### Deployment
Deployment could vary. The simplest deployment is just running the script manually. You could also crontab and a local machine (e.g. to check weekly). For a more robust deployment there are a couple of options:

1) Deploy onto an AWS Lambda endpoint and schedule polling and monitoring via AWS also.
2) Deploy onto a dedicated server / cloud based server and use celery for scheduling. Add logging handlers to email / txt admins in the event of ERROR or CRITICAL failure.

### Future enhancements
Increase testing, improve logging, make universal for all USNAS tabled data (and have user select which tables they would like). 
