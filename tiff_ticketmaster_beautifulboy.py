import argparse
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from emailer import send_deals

target_urls = ['https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/100055171C968D3B?tm_link=promo_generic_feat_recommended_event_findtix4',
               'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/10005518FE538FE1?artistid=1493334&majorcatid=10002&minorcatid=645',
               'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-08-2018/event/1000551713F6878A?artistid=1493334&majorcatid=10002&minorcatid=645']
test_urls = ['https://www1.ticketmaster.ca/anthropocene-toronto-ontario-09-12-2018/event/100055182080A4A2?artistid=1493334&majorcatid=10002&minorcatid=645']

miss_xpath = '//*[@id="edp-wrapper"]/div/div[1]/div[1]/div/div[1]/div/div'
miss_text = 'Oh-no! These tickets went fast and we\'re unable to find more right now.'
def check_TIFF(args):
    hits = []
    browser = webdriver.Chrome('bin/chromedriver.exe')
    for url in test_urls + target_urls:
        print("Getting: {0}".format(url))
        print("Rendering...")
        browser.get(url)
        print("Searching...")
        if not browser.find_element_by_xpath(miss_xpath).text == miss_text:
            print("Success!  Adding to hits...")
            hits.append(url)
    browser.close()

    if hits:
        send_deals(args, hits)
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

    check_TIFF(args)

    if args.seconds or args.minutes:
        scheduler = BackgroundScheduler()
        if args.seconds:
            scheduler.add_job(check_TIFF, 'interval', args=[args] if args is not None else [], minutes=args.seconds)
        elif args.minutes:
            scheduler.add_job(check_TIFF, 'interval', args=[args] if args is not None else [], minutes=args.minutes)
        scheduler.start()
        print('Schedule started...')
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()

