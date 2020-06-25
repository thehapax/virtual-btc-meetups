import pandas as pd
import requests
from lxml import html
from bs4 import BeautifulSoup
from dateutil.parser import parse
import pytz
import logging
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# virtual bitcoin meetups
fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"

def fetch_lastupdated():
    logger.info("fetching last updated")
    page = requests.get(fulmo_url).text
    soup = BeautifulSoup(page, "lxml")
    update_tag = soup.find_all('li', {'id': 'footer-info-lastmod'})
    updatetxt = update_tag[0].text.split('was')
    updated = updatetxt[1].strip()
    logger.info(updated)
    return updated


def fetch_tables(status):
    try:
        logger.info("Fetching Tables")
        page = requests.get(fulmo_url).text
        soup = BeautifulSoup(page, "lxml")

        events_table = soup.find_all('table', {'class': 'wikitable'})
        if status == "new":
            all_events = events_table[0] # new events
        elif status == 'ongoing':
            all_events = events_table[1] # new events
        elif status == "past":
            all_events = events_table[2] # past events
  
        return all_events
    except Exception as e: 
        logger.error(e)
        return None


def get_numrows(eventlist):
    summary = eventlist.find_all("tr")
    rowcount = len(summary)
    total = rowcount
    logger.info(f"total number of rows: {total}")
    return total, summary


def get_next_content(begin, end, summary, rowcount):
    # row 0 is the th header,  row 1 .... X is content
#    summary = all_events.find_all("tr")
#    rowcount = len(summary)
    if begin >= rowcount:
        logger.info("get_next_content: begin >= rowcount")
        return None
    if  end <= rowcount:  # 4-6 where total is 6
        logger.info("get_next_content: end <= rowcount")
        return summary[begin:end]
    elif end > rowcount:
        logger.info("get_next_content:end > rowcount")
        return summary[begin:rowcount]
    
    
def parse_next_content(all_events):
    event_list = []
    an_event = []
    for row in all_events: 
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
            
    text = ""
    for event in event_list:
        text += "\n"
        for elem in event:
            text += elem + "\n"
    return text

    
###################################################
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
    elif rowcount < status: # list length shorter than status, return entire list
        all_events = summary

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
    last_updated = fetch_lastupdated()
    
    
    """    
    header = "All Events in UTC+2 (Berlin Time)"
    past_events = fetch_tables("past")    
    events = parse_pastevents(past_events)
    output = output_past(events, len(events))
    #    output = output_past(events, 5)
    output = header + output
    #print(output)
    """

    """    
    new_events = fetch_tables("new")
    data = "4-event"
    
    if re.match(r"^\d-event", data):
        print("matches event")
        indexes = re.split(r'-', data)
        print(indexes)
        start = int(indexes[0])
        #end = int(start+3)
        end = int(start+10)
        print(f'start:{start} - end: {end}')
        rowcount, summary = get_numrows(new_events)
 #       print(summary)
        print(f'rowcount new events: {rowcount}')
        print(type(rowcount))
        sublist = get_next_content(start, end, summary, int(rowcount))
#        print(sublist)
        result = parse_next_content(sublist)
        print(result)
    """