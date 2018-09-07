"""
Entry point and core polling logic.
Checks the provided event pages for signs of available tickets and, if available, takes action to reserve them.

"""

import argparse
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
import config
from datetime import datetime
from selenium import webdriver
from selenium import common
import threading
from emailer import send_deals


def check_TIFF(args):
    hits = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    try:
        browser = webdriver.Chrome(executable_path='bin/chromedriver.exe', chrome_options=chrome_options)
        #browser.set_page_load_timeout(10)

        today = str(datetime.today())
        readable = time.strftime('%Y-%m-%d %I:%M:%S', time.strptime(today[0:today.index('.')], '%Y-%m-%d %H:%M:%S'))
        print("{0}: Searching...".format(readable))
        for event in config.test_events:
            try:
                browser.get(event.link)
            except common.exceptions.TimeoutException:
                print('Timeout.  Moving on...')
                continue

            if not browser.find_element_by_xpath(config.miss_xpath).text == config.miss_text:
                print("Success!  Adding {0} to hits...".format(event.title))
                hits.append(event)

        if hits:
            # TODO: open browser for all hits, not just the first one
            send_deals(args, hits)

            browser = webdriver.Chrome('bin/chromedriver.exe')
            browser.implicitly_wait(1)
            browser.get(hits[0].link)

            try:
                browser.find_element_by_xpath(config.hit_xpath[0]).click()
                browser.find_element_by_xpath(config.hit_xpath[1]).click()
                browser.find_element_by_xpath(config.hit_xpath[2]).click()

                print('Waiting for 30 minutes')
                # TODO: capture browser close event, to end this thread early
                wait_event = threading.Event()
                wait_event.wait(1800.0)

            except common.exceptions.NoSuchElementException as e:
                print(e.msg)
        else:
            print('No tickets found =(')
    finally:
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='email user')
    parser.add_argument('-p', '--password', help='email password')
    schedule_group = parser.add_mutually_exclusive_group()
    schedule_group.add_argument('--seconds', type=int, help='schedule a run every number of seconds')
    schedule_group.add_argument('--minutes', type=int, help='schedule a run every number of minutes')
    args = parser.parse_args()

    # TODO: block execution of multiple workers with a lock
    if args.seconds or args.minutes:
        scheduler = BackgroundScheduler()
        if args.seconds:
            scheduler.add_job(check_TIFF, 'interval', args=[args] if args is not None else [], seconds=args.seconds)
        elif args.minutes:
            scheduler.add_job(check_TIFF, 'interval', args=[args] if args is not None else [], minutes=args.minutes)
        scheduler.start()
        print('Schedule started...')
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        check_TIFF(args)
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()

