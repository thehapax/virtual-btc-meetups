import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup


# fulmo wiki new events, straight table read, fulmo is in Berlin time
def get_new_events(url):
    tables = pd.read_html(url)
    upcoming_events = tables[0]
    print(upcoming_events)
    return upcoming_events.to_string()

#fulmo wiki past events
def get_past_events(url):
    tables = pd.read_html(url)
    past_events = tables[1]
    print(past_events)
    return past_events.to_string()


# All times in Berlin time (GMT+2).

def get_event_content(url):
    # s = requests.Session()
    page = requests.get(url).text
    # soup = BeautifulSoup(page, "lxml")
    soup = BeautifulSoup(page, "html.parser")
#    soup.h1['firstHeading']

    events_table = soup.find_all('table', {'class': 'wikitable'})
    print(len(events_table))
    
    new_events = events_table[0]
    past_events = events_table[1]

#    tr_elements = doc.xpath('//div')
#    print(tr_elements)
#    https://lxml.de/tutorial.html


def parse_content(pd):
    '''
    pass in data as a dataframe, parse into acceptable markdown for bot
    '''
    text = pd.to_string()
    return text


if __name__ == "__main__":
    
    fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"
    #get_event_content(fulmo_url)
    
    results = get_new_events(fulmo_url)
    
    pass