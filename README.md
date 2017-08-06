**Please note: this application is NOT in any way associated or
affiliated with the government owned company
[Systembolaget](https://en.wikipedia.org/wiki/Systembolaget).**

# Systembolaget

This application uses
[Systembolaget's open API](https://www.systembolaget.se/api/) to create
an SQLite database that can be viewed via the local Flask webserver as
seen in the screenshot below.

![alt text](https://github.com/iiMaXii/Systembolaget/blob/master/screenshots/web-table.png "")

## How to run
This application requires Python 3.

1. Install dependencies: `pip3 install -r requirements.txt`
2. Generate database: `python3 systembolaget_parser.py`
3. Run the webserver: `python3 web.py`
