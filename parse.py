#!/usr/bin/env python3

import os
import sys
import glob
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse flight prices",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("dir", action="store", type=str, help="Directory to html files")
    args = parser.parse_args()

    min_total_price = None

    html_files = sorted(glob.glob(args.dir + '/*.html'))
    for html_file in html_files:
        print('> Parsing file ' + html_file)
        with open(html_file) as f:
            soup = BeautifulSoup(f, 'html.parser')

        prices = dict(inbound={}, outbound={})

        for flight_type in ('outbound', 'inbound'):
            links_ids = dict(
                outbound='w-nav',
                inbound='w-nav-incoming'
            )

            links = soup.find(id=links_ids[flight_type]).find_all('a')
            for link in links:
                try:
                    _, _, day, month, year, _, currency, amount, *_ = link.text.split()
                except ValueError:
                    continue

                date_str = ' '.join((day, month, year))
                date = datetime.strptime(date_str, '%d %b %Y')
                prices[flight_type][date_str] = float(amount)
                #print('Found {}: {} {} {}'.format(flight_type, date_str, amount, currency))
                del(day, month, year, currency, amount)

        min_outbound_date = min(prices['outbound'], key=lambda x: prices['outbound'][x])
        min_outbound_price = prices['outbound'][min_outbound_date]
        print('Minimal outbound price {}: {}'.format(min_outbound_date, min_outbound_price))

        min_inbound_date = min(prices['inbound'], key=lambda x: prices['inbound'][x])
        min_inbound_price = prices['inbound'][min_inbound_date]
        print('Minimal inbound price  {}: {:.2f}'.format(min_inbound_date, min_inbound_price))

        total_price = min_outbound_price + min_inbound_price
        print('Total price: {:.2f}'.format(total_price))
        print()

        if not min_total_price or total_price < min_total_price:
            min_total_price = total_price
            total_price_date = "{} - {}".format(min_outbound_date, min_inbound_date)

    print('MINIMAL TOTAL PRICE ({}): {:.2f}'.format(total_price_date, min_total_price))
