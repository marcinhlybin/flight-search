# Flight search / Qatar Airways site crawler

A simple tool to monitor business class fares for Qatar Airways. It fills search forms and then clicks (1) one week forward for outbound flight and (2) one week forward for inbound flight and stores output pages as html files in `html/` directory. Then you can use a sample parser I wrote to get the cheapest price and dates.

The script may return errors when site session expires or if it can't get another site etc. After error a screenshot is taken and stored in file `qatar-error.png`.

To see browser window while running, use `-v` option.


# Intallation

1. Download `geckodriver` binary from https://github.com/mozilla/geckodriver/releases/tag/v0.24.0, uncompress it and save in the project directory.

2. Create virtualenv with `python3 -m venv venv`. Activate it `source venv/bin/activate`

3. Install pip packages `pip install -r requirements.txt`

# Usage

## Options

```
python search.py --help

usage: search.py [-h] [-f FROM_AIRPORT] [-t TO_AIRPORT] [-a {qatar}] [-d DATE]
                 [-w WEEKS] [-m MONTHS] [-c {business,economy}]

Search flight prices

optional arguments:
  -h, --help            show this help message and exit
  -f FROM_AIRPORT, --from FROM_AIRPORT
                        Flight origin (default: WAW)
  -t TO_AIRPORT, --to TO_AIRPORT
                        Flight destination (default: AKL)
  -a {qatar}, --airlines {qatar}
                        Airlines name (default: qatar)
  -d DATE, --date DATE  Departure date (default: 2019-05-19)
  -w WEEKS, --weeks WEEKS
                        Return flight after this number of weeks (default: 3)
  -m MONTHS, --search-months MONTHS
                        Stop search after this number of months (default: 6)
  -c {business,economy}, --class {business,economy}
                        Travel class (default: business)
```

## Flight search example

Search flights by Qatar Airlines (only this one is supported for now) from Warsaw to Aukland, 10 months forward with 3 week difference between departure and arrival date.

```
python search.py -m 10 -f WAW -t AKL -w 3
```

To see browser window while running, add `-v` option. Please take note it will be of size 2560x1440.

Crawled sites are stored in `htmls/`. Simple parser is also available:

```
# Remeber to change directory name
python parse.py htmls/qatar/201905191538-WAW:AKL-business/
```
