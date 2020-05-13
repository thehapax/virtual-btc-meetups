from datafeed import get_new_events
from telethon import TelegramClient, events, sync, utils, functions, Button, custom
import yaml
import sys
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# virtual bitcoin meetups
# https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events

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
async def handler(event):
    await client.send_message(event.sender_id, 'Welcome to Virtual Bitcoin and Lightning Meetups bot\n')


@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    if 'start' in event.raw_text:
        await client.send_message(event.sender_id, 'Get Events', buttons=[
            Button.text('Get New Events', resize=True, single_use=True),
            Button.text('Past Events', resize=True, single_use=True)])

    
# ==============================   Inline  ==============================
NEW_EVENTS = (
    "Sample placeholder text here:\n"
    "• [Official Docs](https://docs.python.org/3/tutorial/index.html).\n"
    "• [Dive Into Python 3](https://rawcdn.githack.com/diveintomark/"
    "diveintopython3/master/table-of-contents.html).\n"
    )


@client.on(events.InlineQuery)
async def handler(event):
    builder = event.builder
    result = None
    query = event.text.lower()
    if query == '':
        result = builder.article(
            'New Events',
            text=NEW_EVENTS,
            buttons=custom.Button.url('Join the group!', 't.me/TelethonChat'),
            link_preview=True
        )

    # NOTE: You should always answer, but we want plugins to be able to answer
    #       too (and we can only answer once), so we don't always answer here.
    if result:
        await event.answer([result])


# ==============================   Inline  ==============================
 
client.start(bot_token=TOKEN)
#client.start()

with client:
    client.add_event_handler(handler)
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
#    client.loop.run_until_complete(main())   

