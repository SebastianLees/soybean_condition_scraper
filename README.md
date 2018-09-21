# Pyfixer

Pyfixer is a small script that queries and stores data from the http://fixer.io/ API. The script will query data for the currencies provided. Scheduling is agnostic and is left at the developers discretion (in the example below we will be using a cron job for scheduling).

### Requirements:
- Python 3.6+

### Installation
1) Clone the repository to a local directory
2) Install the Python dependencies from the requirements.txt file (you may wish you use a virtual environment).
3) The script can be run manually (src/fixer.py) or scheduling can be set up.

### Scheduling
To set up basic scheduling for 9am weekdays, add the following to your crontab file:
0 9 * * 1-5 path/to/fixer.py

### Assumptions
Original specifications require that 'The system holds at least the last month of rates information'. Month is not specified here (30 days / 4 weeks / a calendar month), so the assumption of 30 days has been used.

### Deployment
Deployment could vary. The simplest deployment using crontab and a local machine is described above. For a more robust deployment there are a couple of options:

1) Deploy onto an AWS Lambda endpoint and schedule polling and monitoring via AWS also.
2) Deploy onto a dedicated server / cloud based server and use celery for scheduling. Add logging handlers to email / txt admins in the event of ERROR or CRITICAL failure.

### Future enhancements
Increase testing, improve logging.