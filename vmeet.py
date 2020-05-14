from datafeed import get_new_events, get_event_content, parse_content
from telethon import TelegramClient, events, sync, utils, functions, Button, custom
import yaml
import sys
import logging
from logging import handlers

from telethon.tl.types import InputWebDocument

log_path = '/Users/octo/virtual-btc-meetups/logs/logfile'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Log to a rotating file - why isn't this working?
level = logging.INFO
logger.setLevel(level)
# 5*5MB log files max:
h = logging.handlers.RotatingFileHandler(log_path, encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=5)
# example of format: 2019-04-05 20:28:45,944  INFO: blah
h.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s:%(message)s"))
h.setLevel(level)
logger.addHandler(h)

# virtual bitcoin meetups
fulmo_url = "https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events"

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

@client.on(events.CallbackQuery(data=b'clickme'))
async def callback(event):
    print(event.data)
    await event.edit('Thank you for clicking {}!'.format(event.data))
    

@client.on(events.NewMessage(incoming=True, outgoing=True))    
async def new_handler(event):
    print(event.raw_text)
    if 'hello' in event.raw_text:
        await client.send_message(event.sender_id, 'A single button, with "clickme" as data',
                        buttons=Button.inline('Get Data', b'clickme'))


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def start_handler(event):
    await client.send_message(event.sender_id, 'Welcome to Virtual Bitcoin and Lightning Meetups bot\n')
    await client.send_message(event.sender_id, 'Get Events', buttons=[
            Button.text('Get New Events', resize=True, single_use=True),
            Button.text('Past Events', resize=True, single_use=True)])

@client.on(events.NewMessage(pattern='(?i)/add', forwards=False, outgoing=False))
async def ad_handler(event):
    await client.send_message(event.sender_id, 'Send us an event and we\'ll add it to the list\n')

@client.on(events.NewMessage(pattern='(?i)/about', forwards=False, outgoing=False))
async def about_handler(event):
    await client.send_message(event.sender_id, 'About Us\n')



@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    if 'Get New Events' in event.raw_text:
        content = get_event_content('new', fulmo_url)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text)
    elif 'Past Events' in event.raw_text:
        content = get_event_content('past', fulmo_url)
        formatted_text = parse_content(content)
        await client.send_message(event.sender_id, formatted_text)


    
# ==============================   Inline  ==============================
# cache the data
NEW_EVENTS = parse_content(get_event_content('new', fulmo_url))
PAST_EVENTS = parse_content(get_event_content('past', fulmo_url))

@client.on(events.InlineQuery)
async def inline_handler(event):
    builder = event.builder
    result = None
    query = event.text.lower()
    if query == '':
        file_in_bytes=51000
        thumb_link = 'https://i.imgur.com/VY44NqO.jpg'
        url_link= 'https://www.ccn.com/wp-content/uploads/2013/12/bitcoin-image.jpg'
        icon = InputWebDocument(thumb_link, file_in_bytes, 'image/png',[])
        
        result = builder.article(
            'New Events',
            text=NEW_EVENTS,
            thumb= icon,
            buttons=custom.Button.url('Fulmo: Building the Lightning Network', 'https://fulmo.org/'),
            link_preview=True
            )
        result2 = builder.article(
            'Past Events',
            text=PAST_EVENTS,
            thumb= icon,
            buttons=custom.Button.url('Fulmo: Building the Lightning Network', 'https://fulmo.org/'),
            link_preview=True
            )

    # NOTE: You should always answer, but we want plugins to be able to answer
    #       too (and we can only answer once), so we don't always answer here.
    if result:
        await event.answer([result, result2])


# ==============================   Inline  ==============================
 
client.start(bot_token=TOKEN)
#client.start()

with client:
    client.add_event_handler(handler)
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
#    client.loop.run_until_complete(main())   

