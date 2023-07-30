# Ticketmaster URLs to the shows to find tickets for
from collections import namedtuple

Event = namedtuple('Event', ['title', 'link'])
target_events = [Event('Oppenheimer', 'https://www.amctheatres.com/movies/oppenheimer-66956/showtimes/oppenheimer-66956/2023-08-17/amc-metreon-16/all')]
test_events = [Event('Oppenheimer', 'https://www.amctheatres.com/movies/oppenheimer-66956/showtimes/oppenheimer-66956/2023-08-16/amc-metreon-16/all')]

