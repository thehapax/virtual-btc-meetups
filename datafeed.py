import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
import datetime as dt
from dateutil.parser import parse
import pytz

# fulmo wiki new events, straight table read, fulmo is in Berlin time
def get_new_events(url):
    tables = pd.read_html(url)
    upcoming_events = tables[0]
    print(upcoming_events.columns)
    return upcoming_events

#fulmo wiki past events
def get_past_events(url):
    tables = pd.read_html(url)
    past_events = tables[1]
#    print(past_events)
#    return past_events.to_string()
    return past_events


# All times in Berlin time (GMT+2).
def get_event_content(url):
    # s = requests.Session()
    page = requests.get(url).text
    # soup = BeautifulSoup(page, "lxml")
    soup = BeautifulSoup(page, "html.parser")

    events_table = soup.find_all('table', {'class': 'wikitable'})
#    print(len(events_table))
    new_events = events_table[0]
#    past_events = events_table[1]

    #print(new_events)
    header = new_events.find_all("th")
    rows = new_events.find_all("td")
    
        
    #print(str(header) + "########")
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
    
    results = get_new_events(fulmo_url)
    r = results[['Date', 'Name', 'Link']]
    print(r)
    
    
    #content = get_event_content(fulmo_url)
    
    """
    # time zone formatting examples
    timezone = pytz.timezone('America/New_York')
    date_time_str = '2018-06-29 17:08:00'
    date_time = 'Mon, 21 March, 2015'
    dtj = dt.datetime.strptime(date_time,  '%a, %d %B, %Y')
    print(dtj)
    
    date_time_str = str(dt.datetime.now())
    print(date_time_str)
    print(parse(date_time_str))
    
    date_time_obj = dt.datetime.strptime(date_time_str,  '%Y-%m-%d %H:%M:%S.%f')
    print(date_time_obj)
    
    date_time_obj = dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
    timezone_date_time_obj = timezone.localize(date_time_obj)
    
    print(timezone_date_time_obj)
    print(timezone_date_time_obj.tzinfo)
    """
    
    #Index(['Date', 'Time', 'Name', 'Link'], dtype='object')
