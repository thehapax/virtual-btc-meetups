from datafeed import get_new_events, get_event_content, parse_content, fetch_tables
from telethon import TelegramClient, events, sync, utils, functions, Button, custom
import yaml
import sys
import logging
from logging import handlers
from telethon.tl.types import InputWebDocument

log_path = '/Users/octo/virtual-btc-meetups/logs/logfile'

# virtual bitcoin meetups
fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"
bitcoinhk_logo = '/Users/octo/virtual-btc-meetups/site-logo.png'

# logos and byline
fulmo_byline = 'Fulmo: Building the Lightning Network: https://fulmo.org/'
thumb_link = 'https://i.imgur.com/VY44NqO.jpg' # lightning logo
feedback_msg = 'Send your event to @btcfeedbackbot and we\'ll add it to the list\n'

# credits
fulmo_info =  "<b>Content Host:</b>\nFulmo - building Lightning Networks: https://fulmo.org/\n"
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

#### delete sample code
"""
@client.on(events.UserUpdate)
async def handler(event):
    print(event.get_user())
    print(event.last_seen())
"""
@client.on(events.CallbackQuery) #data=b'clickme'))
async def callback(event):
    print(event.data)
    await event.edit('Thank you for clicking {}!'.format(event.data))
    
#from telethon.tl.types import Message
@client.on(events.NewMessage(incoming=True, outgoing=True))    
async def new_handler(event):
 #   print(event.raw_text)
    sender = await event.get_sender()
    name = utils.get_display_name(sender)
    message = event.message
#    print(message)
    logger.info(name + ": " + event.text)
#    print(name, 'said', event.text, '!')
    if 'hello' in event.raw_text:
#        await client.send_message(event.sender_id, 'A single button, with "clickme" as data',
#                        buttons=Button.inline('Get Data', b'clickme'))
        await client.send_message(event.sender_id, 'Send Location data',
                        buttons=Button.request_location('Get location', 
                                                        resize=None, 
                                                        single_use=True,
                                                        selective=True))

######### end sample code


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def start_handler(event):
    await client.send_message(event.sender_id, 'Welcome to Virtual Bitcoin and Lightning Meetups bot\n')
    await client.send_message(event.sender_id, 'Get Events', buttons=[
            [Button.text('Next 3 Events', resize=True, single_use=True),
            Button.text('Next 5 Events', resize=True, single_use=True)],
            [Button.text('All New Events', resize=True, single_use=True),
            Button.text('Add Event', resize=True, single_use=True),],
            [Button.text('Past Events', resize=True, single_use=True), 
            Button.text('About', resize=True, single_use=True)]])

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
   

@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    newevents = fetch_tables('new')
    pastevents = fetch_tables('past')
    if 'Next 3 Events' in event.raw_text:
        content = get_event_content(3, newevents)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text, link_preview=False)
    elif 'Next 5 Events' in event.raw_text:
        content = get_event_content(5, newevents)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text, link_preview=False)
    elif 'All New Events' in event.raw_text:
        content = get_event_content(-1, newevents)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text, link_preview=False)
    elif 'Past Events' in event.raw_text:
        content = get_event_content(-1, pastevents)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text, link_preview=False)
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
        
    
# ==============================   Inline  ==============================
# cache the data
newevents = fetch_tables('new')
pastevents = fetch_tables('past')

NEXT3 = parse_content(get_event_content(3, newevents))
NEXT5 = parse_content(get_event_content(5, newevents))
NEW_EVENTS = parse_content(get_event_content(-1, newevents))
PAST_EVENTS = parse_content(get_event_content(-1, pastevents))

#from telethon.tl.types import InputGeoPoint
#from telethon.tl.types import GeoPoint

@client.on(events.InlineQuery)
async def inline_handler(event):
#    print("event id:")
#    print(event.id)
    
    builder = event.builder
    result = None
    query = event.text.lower()
    if query == '':
        file_in_bytes=51000
        thumb_link = 'https://i.imgur.com/VY44NqO.jpg' # lightning logo
        icon = InputWebDocument(thumb_link, file_in_bytes, 'image/jpeg',[])

        next3 = await builder.article(
            'Next 3 Events',
            text=NEXT3,
            thumb= icon,
            link_preview=False
            )        
        next5 = await builder.article(
            'Next 5 Events',
            text=NEXT5,
            thumb= icon,
            link_preview=False
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
        await event.answer([result, next5, next3])
    else:
        await event.answer("bot offline")
    

# ==============================   Inline  ==============================
 
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()

