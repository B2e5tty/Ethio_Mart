from telethon import TelegramClient
import csv
import os
import sys
from dotenv import load_dotenv
from telethon.errors import FloodWaitError, SessionExpiredError
import asyncio
import nest_asyncio
nest_asyncio.apply()


# load enivronment
load_dotenv()
api_id = os.getenv('TG_API_ID')
api_hash = os.getenv('TG_API_HASH')
phone = os.getenv('phone')

print(api_id)
print(api_hash)
print(phone)

# scrape data 
async def scrape_channel(client, channel_username, writer, media_dir):
    print('k')
    entity =  await client. get_entity(channel_username)
    channel_title = entity.title      # channel tittle
    print('m')

    async for message in client.iter_messages(entity, limit = 500):
        print('v')
        media_path = None
        if message.media and hasattr(message.media, 'photo'):
            filename = f"{channel_username}_{message.id}.jpg"
            media_path = os.path.join(media_dir, filename)
            
            # download
            await client.download_media(message.media, media_path)
            print('pp')
        print('j')
        # Write the channel title along with other data
        writer.writerow([channel_title, channel_username, message.id, message.message, message.date, media_path])
        print('lk')
# Intialize the client
print('j')
# client = TelegramClient('scraping_session', api_id, api_hash)
print('i')

async def main_def():
    try: 
        print('p')
        async with TelegramClient('scraping_session', api_id, api_hash) as client:
            await client.start(phone=phone)
            print('Client started successfully')

            # directory for image files
            media_dir = 'photos'
            os.makedirs(media_dir, exist_ok=True)
            print('o')

             # prepare the CSV file
            with open('telegram_data.csv', 'w', newline='', encoding='utf-8') as file:
                print('c')
                writer = csv.writer(file)
                writer.writerow(['Channel Title', 'Channel Username', 'ID', 'Message', 'Date', 'Media Path'])  # header

                channel = '@sinayelj'
                print('d')

                await scrape_channel(client, channel, writer, media_dir)
                print(f"Scraped data from {channel}")

    except FloodWaitError as e:
            print(f"FloodWaitError: Please wait for {e.seconds} seconds before retrying.")
    except SessionExpiredError as e:
        print("SessionExpiredError: Session has expired. You may need to reauthenticate.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")    # Log the error or take any necessary recovery steps

