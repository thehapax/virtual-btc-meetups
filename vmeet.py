from datafeed import get_event_content, parse_content, fetch_tables, parse_pastevents
from datafeed import output_past, get_numrows, get_next_content, parse_next_content
from telethon import TelegramClient, events, sync, utils, functions, Button, custom
from telethon.tl.types import GeoPoint
from telethon.tl.types import GeoPointEmpty
import yaml
import sys
import logging
from logging import handlers
from telethon.tl.types import InputWebDocument
from tzutils import get_tz_from_coord
import re

log_path = '/Users/octo/virtual-btc-meetups/logs/logfile'
bitcoinhk_logo = '/Users/octo/virtual-btc-meetups/site-logo.png'

# virtual bitcoin meetups
fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"

# logos and byline
fulmo_byline = 'Fulmo: Building the Lightning Network: https://fulmo.org/'
thumb_link = 'https://i.imgur.com/VY44NqO.jpg' # lightning logo
feedback_msg = 'Send your event to @btcfeedbackbot and we\'ll add it to the list\n'

# credits
fulmo_info =  "<b>Content Host:</b>\nFulmo - Building Bitcoin & Lightning Networks: https://fulmo.org/\n"
christina_info  = "<b>Development:</b>\nChristina @ BitcoinHK: https://twitter.com/christinabahk\n"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

########################################
# Log to a rotating file - why isn't this working?
level = logging.INFO
logger.setLevel(level)
# 5*5MB log files max:
h = logging.handlers.RotatingFileHandler(log_path, encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=5)
# example of format: 2019-04-05 20:28:45,944  INFO: blah
h.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s:%(message)s"))
h.setLevel(level)
logger.addHandler(h)
########################################

path  = "./"
config_file = path + 'config.yml'
with open(config_file, 'rb') as f:
    config = yaml.safe_load(f)

TOKEN = config['bot_token']
print(f'Bot Token: {TOKEN}')

client = TelegramClient(config["session_name"], 
                        config["api_id"], 
                        config["api_hash"])

# Default to another parse mode
client.parse_mode = 'html'

@client.on(events.CallbackQuery())
async def callback(event):
    data = str(event.data.decode())
    # print(data)
    logging.info(f'Callback event {data}')
    if re.match(r"^\d-event", data):
        indexes = re.split(r'-', data)
        # print(indexes)
        start = int(indexes[0])
        end = int(start+3)
#        print(f'start:{start} - end: {end}')
        new_events = fetch_tables("new")
        rowcount, summary = get_numrows(new_events)
#        print(f"Row Count - {rowcount}")
        sublist = get_next_content(start, end, summary, rowcount)
        result = parse_next_content(sublist)
        # print(result)
        await client.send_message(event.sender_id, result, link_preview=False)
        next_index = end
#        print(f'Next Index: {next_index}')
        if rowcount > next_index:
            next_index = str(next_index) + "-event"
#            print(f'Next Index: {next_index}')
            await client.send_message(event.sender_id, "Want more events?",
                                      buttons=Button.inline('Get More Events', 
                                                           next_index))
    else:
        await event.edit('No More Events listed')
     
    
@client.on(events.NewMessage(incoming=True, outgoing=True))    
async def new_handler(event):
    try:
#        sender = await event.get_sender()
#        name = utils.get_display_name(sender)
#        message = event.message
#        logger.info(name + ": " + event.text)
        
        if 'timezone' in event.raw_text:
            await client.send_message(event.sender_id, 'Set Your Time Zone:',
                            buttons=Button.request_location('Share location', 
                                                            resize=None, 
                                                            single_use=True,
                                                            selective=True))
        else: 
            geo_point = event.geo
            if geo_point is not GeoPointEmpty and geo_point is not None:
                lat_point = geo_point.lat
                long_point = geo_point.long
                logger.info(f'lat: {lat_point} long: {long_point}')
                from_zone, zone_source = get_tz_from_coord(lat_point, long_point)
                logger.info(from_zone)
                zoneinfo = "Your Time Zone is: " + from_zone
                await client.send_message(event.sender_id, zoneinfo)

    except Exception as e:
        logger.error(e)


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def start_handler(event):
    try:
        await client.send_message(event.sender_id, 'Welcome to Virtual Bitcoin and Lightning Meetups bot!\n', buttons=[
                [Button.text('Next 3 Events', resize=True, single_use=True),
                Button.text('All New Events', resize=True, single_use=True)],
                [Button.text('Add Event', resize=True, single_use=True),
                Button.text('Past Events', resize=False, single_use=True)], 
                [Button.text('About', resize=True, single_use=True)]])
    except Exception as e:
        logger.error(e)


@client.on(events.NewMessage(pattern='(?i)/add', forwards=False, outgoing=False))
async def add_handler(event):
    await client.send_message(event.sender_id, feedback_msg)


@client.on(events.NewMessage(pattern='(?i)/about', forwards=False, outgoing=False))
async def about_handler(event):
    await client.send_message(event.sender_id, 
                                fulmo_info, 
                                link_preview=False)
    await client.send_message(event.sender_id, 
                                christina_info,
                                link_preview=False)
    await client.send_file(event.sender_id, bitcoinhk_logo)

   

@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    try:
    #    print(event.raw_text)
        if 'Next 3 Events' in event.raw_text:
            content = get_event_content(3, newevents)
            formatted_text = parse_content(content)
            await client.send_message(event.sender_id, formatted_text, link_preview=False) 
            if size_newevents > 4:
                # print(f'list size: {size_newevents}')
                await client.send_message(event.sender_id, "Want more?",
                                      buttons=Button.inline('Get more Events', 
                                                            "4-event"))
        elif 'All New Events' in event.raw_text:
            content = get_event_content(-1, newevents)
            formatted_text = parse_content(content)
            await client.send_message(event.sender_id, formatted_text, link_preview=False)
        elif 'Past Events' in event.raw_text:
            events = parse_pastevents(pastevents)
            output = output_past(events, len(events))
            header = "<b>All Events in UTC+2 (Berlin Time)</b>\n\n"
            output = header + output
            await client.send_message(event.sender_id, output, link_preview=False)
        elif 'About' in event.raw_text:
            await client.send_message(event.sender_id, 
                                    fulmo_info, 
                                    link_preview=False)
            await client.send_message(event.sender_id, 
                                    christina_info,
                                    link_preview=False)
            await client.send_file(event.sender_id, bitcoinhk_logo)

        elif 'Add Event' in event.raw_text:
            await client.send_message(event.sender_id, feedback_msg)
    except Exception as e:
        logger.error(e)

    
# ==============================   Inline  ==============================
# cache the data
try:
    pastevents = fetch_tables('past')
    newevents = fetch_tables('new')
    size_newevents = get_numrows(newevents)
    NEXT3 = parse_content(get_event_content(3, newevents))
    NEW_EVENTS = parse_content(get_event_content(-1, newevents))
except Exception as e:
        logger.error(e)


@client.on(events.InlineQuery)
async def inline_handler(event):
    try:   
        sender = await event.get_sender()
        name = utils.get_display_name(sender)
        logging.info("Inline Query: " +  name +  ", Event id:" + str(event.id))
        builder = event.builder
        result = None
        next3 = None
        query = event.text.lower()
        if query == '':
            file_in_bytes=51000
            thumb_link = 'https://i.imgur.com/VY44NqO.jpg' # lightning logo
            icon = InputWebDocument(thumb_link, file_in_bytes, 'image/jpeg',[])
                        
            addevent = await builder.article(
                'Add an Event',
                text=feedback_msg,
                thumb= icon,
                link_preview=False,
                buttons=custom.Button.url("Send a message", 't.me/btcfeedbackbot')
                )
            next3 = await builder.article(
                'Next 3 Events',
                text=NEXT3,
                thumb= icon,
                link_preview=False, 
                buttons=custom.Button.url('Visit the Bot for more', 't.me/bitcoin_events_bot')
                ) 
            result = await builder.article(
                'All New Events',
                text=NEW_EVENTS,
                thumb= icon,
                link_preview=False
                )
        # NOTE: You should always answer, but we want plugins to be able to answer
        #       too (and we can only answer once), so we don't always answer here.
        if result:
            await event.answer([addevent, result, next3])
        else:
            await event.answer("bot offline")
    except Exception as e:
        logger.error(e)


# ==============================   Inline  ==============================
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()

