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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import common
from selenium.webdriver.common.by import By
import threading
from emailer import send_deals


def check_AMC(args):
    hits = []
    options = Options()
    options.add_argument("--headless")
    try:
        browser = webdriver.Chrome(options=options)

        today = str(datetime.today())
        readable = time.strftime('%Y-%m-%d %I:%M:%S', time.strptime(today[0:today.index('.')], '%Y-%m-%d %H:%M:%S'))
        print("{0}: Searching...".format(readable))

        target_events = config.test_events if args.debug else config.target_events
        for event in target_events:
            try:
                browser.get(event.link)
            except common.exceptions.TimeoutException:
                print('Timeout.  Moving on...')
                continue

            showtimes = browser.find_element(By.CLASS_NAME, "Theatre-Wrapper-First").find_elements(By.LINK_TEXT, "AMC Metreon 16")
            if showtimes:
                print("Success!  Adding {0} to hits...".format(event.title))
                hits.append(event)

        if hits:
            # TODO: open browser for all hits, not just the first one
            send_deals(args, hits)

            options = Options()
            browser = webdriver.Chrome(options=options)
            browser.implicitly_wait(1)
            browser.get(hits[0].link)

            try:
                showtimes = browser.find_element(By.CLASS_NAME, "Theatre-Wrapper-First").find_elements(By.CLASS_NAME, "Showtime")
                showtimes[0].find_element(By.CLASS_NAME, "Btn").click()

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
    parser.add_argument('--debug', default=False, action='store_true', help='debug mode')
    schedule_group = parser.add_mutually_exclusive_group()
    schedule_group.add_argument('--seconds', type=int, help='schedule a run every number of seconds')
    schedule_group.add_argument('--minutes', type=int, help='schedule a run every number of minutes')
    args = parser.parse_args()

    # TODO: block execution of multiple workers with a lock
    if args.seconds or args.minutes:
        scheduler = BackgroundScheduler()
        if args.seconds:
            scheduler.add_job(check_AMC, 'interval', args=[args] if args is not None else [], seconds=args.seconds, max_instances=1)
        elif args.minutes:
            scheduler.add_job(check_AMC, 'interval', args=[args] if args is not None else [], minutes=args.minutes, max_instances=1)
        scheduler.start()
        print('Schedule started...')
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        check_AMC(args)
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()

