# Ticketmaster URLs to the shows to find tickets for
from collections import namedtuple

Event = namedtuple('Event', ['title', 'link'])
target_events = [Event('Beautiful Boy', 'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/100055171C968D3B?tm_link=promo_generic_feat_recommended_event_findtix4'),
                 Event('Beautiful Boy', 'https://www1.ticketmaster.ca/beautiful-boy-toronto-ontario-09-07-2018/event/10005518FE538FE1?artistid=1493334&majorcatid=10002&minorcatid=645')]
test_events = [Event('Skin', 'https://www1.ticketmaster.ca/skin-toronto-ontario-09-08-2018/event/1000551802A29444?artistid=1493334&majorcatid=10002&minorcatid=645&tm_link=venue_msg-0_1000551802A29444')]

# html element and text to search for which indicate a sold-out show.
miss_xpath = '//*[@id="edp-wrapper"]/div/div[1]/div[1]/div/div[1]/div/div'
miss_text = 'Oh-no! These tickets went fast and we\'re unable to find more right now.'

# elements to click through in order to reserve tickets and progress to the next page for payment
hit_xpath = ['//*[@id="modal-dialog"]/div/div[2]/div[2]/div/div[2]/button[2]',
             '//*[@id="quickpicks-listings"]/ul/li/div/div',
             '//*[@id="offer-card-buy-button"]']