#!/usr/bin/env python3

import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.firefox.options import Options

SUPPORTED_AIRLINES = ("qatar",)


def qatar_search(from_airport, to_airport, departure_date, return_date, travel_class):
    time.sleep(5)
    from_element = driver.find_element_by_id("T7-from")
    from_element.clear()
    from_element.send_keys(from_airport)
    from_element.send_keys(Keys.DOWN)
    from_element.send_keys(Keys.RETURN)

    to_element = driver.find_element_by_id("T7-to")
    to_element.clear()
    to_element.send_keys(to_airport)
    to_element.send_keys(Keys.DOWN)
    to_element.send_keys(Keys.RETURN)

    departure_element = driver.find_element_by_id("T7-departure_1")
    departure_element.clear()
    departure_element.send_keys(departure_date.strftime('%d %b %Y'))

    arrival_element = driver.find_element_by_id("T7-arrival_1")
    arrival_element.clear()
    arrival_element.send_keys(return_date.strftime('%d %b %Y'))

    passengers_element = driver.find_element_by_id("T7-passengers")
    passengers_element.clear()
    passengers_element.send_keys("1 Passenger")

    try:
        premium_element = driver.find_element_by_xpath("//span[text()='Economy']")
        premium_element.click()
        travel_class_keys = dict(business="b", economy="e")
        actions = ActionChains(driver)
        actions.send_keys(travel_class_keys[travel_class])
        actions.send_keys(Keys.RETURN)
        actions.perform()
    except ElementNotInteractableException:
        if travel_class != "economy":
            premium_element = driver.find_element_by_xpath("//span[text()='Premium only']")
            premium_element.click()

    search_element = driver.find_element_by_id("T7-search")
    search_element.click()


def qatar_get_page_date(page_type, max_retries=12, sleep=5):
    WebDriverWait(driver, 300).until(
        EC.visibility_of_element_located((By.ID, "w-nav-incoming"))
    )

    WebDriverWait(driver, 300).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "slick-center"))
    )

    date_element_ids = dict(
        outbound='w-nav',
        inbound='w-nav-incoming'
    )

    date_element = driver.find_element_by_id(date_element_ids[page_type])
    date_element = date_element.find_element_by_class_name("slick-center")
    date = date_element.text.replace('\n', ' ').split()
    date = ' '.join(date[2:5])
    date = datetime.strptime(date, '%d %b %Y')

    return date


def qatar_go_next_page(page_type, last_page_date, max_retries=36, sleep=5):
    print("   > waiting for the next {:>8s} page...".format(page_type), end="", flush=True)

    scroll_view_element_ids = dict(
        outbound='outbound',
        inbound='return'
    )
    scroll_view_element = driver.find_element_by_id(scroll_view_element_ids[page_type])
    driver.execute_script("arguments[0].scrollIntoView(true);", scroll_view_element)
    time.sleep(2)

    next_page_element_ids = dict(
        outbound='flightDetailForm_outbound:next_OB',
        inbound='flightDetailForm_inbound:next_RT'
    )
    next_page_element = driver.find_element_by_id(next_page_element_ids[page_type])
    actions = ActionChains(driver)
    actions.move_to_element(next_page_element).click().perform()

    for _ in range(0, max_retries):
        next_page_date = qatar_get_page_date(page_type)
        if next_page_date != last_page_date:
            print(" got " + next_page_date.strftime("%d %b %Y"), flush=True)
            return

        time.sleep(sleep)

    raise Exception("Could not get page")


def qatar_main(args):
    # Parse dates
    departure_date = datetime.strptime(args.date, "%Y-%m-%d")
    departure_date_str = departure_date.strftime('%d %b %Y')
    return_date = departure_date + timedelta(weeks=3)
    return_date_str = return_date.strftime('%d %b %Y')
    search_end_date = departure_date + relativedelta(months=args.months)
    search_end_date_str = search_end_date.strftime('%d %b %Y')

    print("=> QATAR SEARCH (until {})".format(search_end_date_str))
    print("   flight:      {}-{} {}".format(args.from_airport, args.to_airport, args.travel_class.title()))
    print("   departure:   " + departure_date_str)
    print("   return:      " + return_date_str)

    driver.get("https://www.qatarairways.com/en/homepage.html")

    qatar_search(
        from_airport=args.from_airport,
        to_airport=args.to_airport,
        departure_date=departure_date,
        return_date=return_date,
        travel_class=args.travel_class
    )

    today_date_str = datetime.now().strftime('%Y%m%d%H%M')
    dir_name = 'htmls/qatar/{}-{}:{}-{}'.format(today_date_str, args.from_airport, args.to_airport, args.travel_class)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    page_dates = dict(
        inbound=qatar_get_page_date('inbound'),
        outbound=qatar_get_page_date('outbound')
    )

    while page_dates['outbound'] <= search_end_date:
        for page_type in ('inbound', 'outbound'):
            site_filename = "qatar-{}-{}:{}-{}:{}-{}:{}.html".format(
                args.travel_class,
                args.from_airport,
                args.to_airport,
                departure_date.strftime('%Y%m%d'),
                return_date.strftime('%Y%m%d'),
                page_dates['outbound'].strftime('%Y%m%d'),
                page_dates['inbound'].strftime('%Y%m%d')
            )
            with open(dir_name + '/' + site_filename, 'w') as f:
                f.write(driver.page_source)

            qatar_go_next_page(page_type=page_type, last_page_date=page_dates[page_type])
            page_dates[page_type] = qatar_get_page_date(page_type=page_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Search flight prices',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-f", "--from", dest="from_airport", default="WAW", help="Flight origin")
    parser.add_argument("-t", "--to", dest="to_airport", default="AKL", help="Flight destination")
    parser.add_argument("-a", "--airlines", default=SUPPORTED_AIRLINES[0], choices=SUPPORTED_AIRLINES, help="Airlines name")
    parser.add_argument("-d", "--date", default=datetime.now().strftime('%Y-%m-%d'), help="Departure date")
    parser.add_argument("-w", "--weeks", default=3, help="Return flight after this number of weeks")
    parser.add_argument("-m", "--search-months", dest="months", type=int, default=6, help="Stop search after this number of months")
    parser.add_argument("-c", "--class", dest="travel_class", default="business", choices=("business", "economy"), help="Travel class")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Show browser window while executing")
    args = parser.parse_args()

    # Headless execution
    options = Options()

    if not args.verbose:
        options.headless = True
        os.environ['MOZ_HEADLESS_WIDTH'] = '2560' # workaround to set size correctly
        os.environ['MOZ_HEADLESS_HEIGHT'] = '1440'

    # Global driver variable
    driver = webdriver.Firefox(executable_path=os.path.abspath("geckodriver"), options=options)
    driver.set_window_size(2560, 1440)

    try:
        if args.airlines == 'qatar':
            qatar_main(args)
    except:
        driver.save_screenshot(args.airlines + '-error.png')
        raise
    finally:
        driver.quit()
