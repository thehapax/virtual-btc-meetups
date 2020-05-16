import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
import datetime as dt
from dateutil.parser import parse
import pytz
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# virtual bitcoin meetups
fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"

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
    return past_events


def fetch_tables(status):
    page = requests.get(fulmo_url).text
    soup = BeautifulSoup(page, "lxml")

    events_table = soup.find_all('table', {'class': 'wikitable'})
    if status == "new":
        all_events = events_table[0] # new events
    elif status == "past":
        all_events = events_table[1] # past events
    return all_events


# All times in Berlin time (GMT+2).
def get_event_content(status, all_events):
    rowcount = len(all_events.find_all("tr"))
    logger.info(f"total number of rows: {rowcount}")
    
    summary = all_events.find_all("tr")
    if status == -1: # use default content
        all_events = summary
    elif rowcount > status:  # parse down content
        end = status+1
        all_events = summary[1:end]
    
#    print(all_events) # skip the th header row
#    print("===============")
        
    event_list = []
    an_event = []
    for row in all_events: #all_events.find_all("tr"):
#        print(str(row) + "\n")
        i = 0
        for elem in row.find_all("td"):
            i += 1
            if i == 2: # skip the time row (for now)
                pass
            else: 
                sitem = str(elem.text).strip()
                an_event.append(sitem)
        if len(an_event) > 0: # append events as lists
            event_list.append(an_event) 
            an_event = []

#    print(event_list)
    return event_list
        

def parse_content(content):
    '''
    pass in data as a dataframe, parse into acceptable markdown for bot
    '''
    text = ""
    for event in content:
        text += "\n"
        for elem in event:
            text += elem + "\n"

    return text

def parse_pastevents(eventlist):
    events = ""
    return events
    


if __name__ == "__main__":
    
    fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"
    
    print("just default all_events")
    all_events = fetch_tables("new")
    past_events = fetch_tables("past")
    print(past_events)
    
    content = parse_pastevents(past_events)
    print(content)

    """
    content = get_event_content(3, all_events)
    formatted_text = parse_content(content)
    print(formatted_text)
    """
        
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
    
