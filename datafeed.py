import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
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
    logger.info("Fetching Tables")
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
    events = []
    for row in eventlist.find_all("tr"):
        single = ""
        for elem in row.find_all("td"):
            single += (str(elem.text).strip()) + "\n"
       # print(single)
        events.append(single)     
    return events
    
def output_past(events, len):
    output = ""
    i = 0
    for item in events[::-1]:
        if i <= len:
            output += item +"\n"
            i = i + 1
        else:
            break
    return output


if __name__ == "__main__":
    
    fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"

    header = "All Events in UTC+2 (Berlin Time)"
    past_events = fetch_tables("past")    
    events = parse_pastevents(past_events)
    output = output_past(events, len(events))
    #    output = output_past(events, 5)
    output = header + output
    print(output)

        
