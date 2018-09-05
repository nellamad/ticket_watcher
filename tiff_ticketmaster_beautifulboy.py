import argparse
import time
from datetime import datetime
import os
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium import common
import threading
from emailer import send_deals

target_urls = ['https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/100055171C968D3B?tm_link=promo_generic_feat_recommended_event_findtix4',
               'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/10005518FE538FE1?artistid=1493334&majorcatid=10002&minorcatid=645',
               'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-08-2018/event/1000551713F6878A?artistid=1493334&majorcatid=10002&minorcatid=645']
test_urls = ['https://www1.ticketmaster.ca/mouthpiece-toronto-ontario-09-07-2018/event/10005518201FA456?artistid=1493334&majorcatid=10002&minorcatid=645']

miss_xpath = '//*[@id="edp-wrapper"]/div/div[1]/div[1]/div/div[1]/div/div'
miss_text = 'Oh-no! These tickets went fast and we\'re unable to find more right now.'
hit_xpath = ['//*[@id="modal-dialog"]/div/div[2]/div[2]/div/div[2]/button[2]',
             '//*[@id="quickpicks-listings"]/ul/li/div/div',
             '//*[@id="offer-card-buy-button"]',
             '//*[@id="submit_btn"]',
             '//*[@id="login-input"]',
             '//*[@id="password-input"]',
             '//*[@id="login-btn"]']


def check_TIFF(args):
    hits = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path='bin/chromedriver.exe', chrome_options=chrome_options)
    browser.set_page_load_timeout(10)

    today = str(datetime.today())
    readable = time.strftime('%Y-%m-%d %I:%M:%S', time.strptime(today[0:today.index('.')], '%Y-%m-%d %H:%M:%S'))
    print("{0}: Searching...".format(readable))
    for url in target_urls:
        try:
            browser.get(url)
        except common.exceptions.TimeoutException:
            print('Timeout.  Moving on...')
            continue

        if not browser.find_element_by_xpath(miss_xpath).text == miss_text:
            print("Success!  Adding to hits...")
            hits.append(url)

    browser.close()

    if hits:
        wait_event = threading.Event()
        browser = webdriver.Chrome('bin/chromedriver.exe')
        browser.implicitly_wait(1)
        browser.get(hits[0])
        try:
            browser.find_element_by_xpath(hit_xpath[0]).click()
            browser.find_element_by_xpath(hit_xpath[1]).click()
            browser.find_element_by_xpath(hit_xpath[2]).click()

            send_deals(args, hits)
        except common.exceptions.NoSuchElementException as e:
            print(e.msg)

        print('Waiting for 30 minutes')
        wait_event.wait(1800.0)
    else:
        print('No tickets found =(')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', help='email user')
    parser.add_argument('-p', '--password', help='email password')
    schedule_group = parser.add_mutually_exclusive_group()
    schedule_group.add_argument('--seconds', type=int, help='schedule a run every number of seconds')
    schedule_group.add_argument('--minutes', type=int, help='schedule a run every number of minutes')
    args = parser.parse_args()

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

