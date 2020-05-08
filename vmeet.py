from telethon import TelegramClient, events, sync, utils, functions, Button
import yaml
import sys
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# virtual bitcoin meetups

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
# https://wiki.fulmo.org/wiki/List_of_Virtual_Bitcoin_and_Lightning_Network_Events


@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    if 'start' in event.raw_text:
        await client.send_message(event.sender_id, 'Get Events', buttons=[[
            Button.text('Next 7 days', resize=True, single_use=True),
            Button.text('This Month', resize=True, single_use=True)],
            [Button.text('Past Events', resize=True, single_use=True)]])    


client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
    
    

