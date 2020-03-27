from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiogram
from bs4 import BeautifulSoup
import aiohttp
from loggers import events
from datetime import datetime, timedelta
from pytz import timezone
import logging
from io import BytesIO
from typing import Union
from aiogram.types import InputFile
from config_checker import check_config

try:
    import ujson as json
except ImportError:
    import json

logging.getLogger("apscheduler").setLevel(logging.WARNING)  # Disable apscheduler logs
temp_posts = []
scheduler = AsyncIOScheduler()


async def download_image(url: str) -> Union[BytesIO, bool]:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = BytesIO()
                f.seek(0)
                f.write(await resp.read())
                if f.getbuffer().nbytes <= 1000000:
                    f.seek(0)
                    return f
                else:
                    return False
            else:
                return False


async def load_config() -> dict:
    with open('data.json', 'rb') as f:
        return json.load(f)  # Load configuration


def load_config_sync() -> dict:
    with open('data.json', 'rb') as f:
        return json.load(f)  # Load configuration


class BotInstance:
    def __init__(self):
        temp_data = load_config_sync()
        self.bot = aiogram.Bot(temp_data['token'], parse_mode=temp_data.get('parse_mode', None))
        self.dp = aiogram.Dispatcher(self.bot)
        self.chat = temp_data['chat']
        self.caption = temp_data.get('caption', None)
        self.tz = timezone(temp_data['timezone'])
        self.send_doc = temp_data.get('send_document', False)
        self.log_fills = temp_data.get('log_fills', True)
        if self.send_doc:
            self.doc_caption = temp_data.get('document_caption', None)
            self.doc_name = temp_data.get('document_name', 'Document')


async def log_msg(message: str):
    global botdata
    if botdata.log_fills:
        events.info(message)


async def send_post(link: BytesIO, mime: str):
    global botdata
    tempf = link.read()
    link.seek(0)

    await botdata.bot.send_photo(chat_id=botdata.chat, photo=link, caption=botdata.caption)
    if botdata.send_doc:
        link = BytesIO()
        link.write(tempf)
        link.seek(0)
        await botdata.bot.send_document(chat_id=botdata.chat, caption=botdata.doc_caption,
                                        document=InputFile(path_or_bytesio=link, filename=botdata.doc_name + mime))


async def fetch_posts():
    global temp_posts

    data = await load_config()
    page = data['page']

    while len(temp_posts) == 0:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(f'https://yande.re/post?page={page}') as resp:
                text = await resp.read()
        soup = BeautifulSoup(text, features='lxml')

        for post in soup.find_all('img', {'class': 'preview'}):

            rating = post['title'].lower().split('rating:')[1].split('score')[0].strip()  # Get post rating
            link = 'https://files.yande.re/image/' + post['src'].rsplit('/', maxsplit=1)[1]  # Get image in best quality

            if rating in data['ratings'].lower() or data['ratings'] == '*' or data['ratings'] is None:
                temp_posts.append(link)

        data['page'] -= 1
        if data['page'] == 1:
            events.critical('Out of posts! Current page: 1')
            exit()  # Selfkill if no posts left
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=1)


async def fill_posts(sched: AsyncIOScheduler, reschedule: bool = False):
    global botdata
    await log_msg('Filling posts..')

    data = await load_config()  # Load configuration
    now = datetime.now(tz=botdata.tz)

    for post_time in data['post_time']:
        # Replace hours and minutes
        run_date = now.replace(hour=int(post_time.split(':')[0]), minute=int(post_time.split(':')[1]), second=0)
        if run_date > now:

            link = False
            while not link:  # Check if photo isn't too large (<10MB)

                while len(temp_posts) == 0:
                    await fetch_posts()  # Out of posts, fetch new

                link = await download_image(temp_posts[0])  # Get first post from the list
                if not link:
                    temp_posts.pop(0)  # Photo is too large, omit it
            mime = '.' + temp_posts[0].rsplit('.', maxsplit=1)[1]  # Get file mime type
            sched.add_job(func=send_post, trigger='date', args=(link, mime), id=temp_posts[0], coalesce=True,
                          max_instances=1, replace_existing=True, run_date=run_date)
            run_date = run_date.strftime('%d-%m-%Y %H:%M')
            await log_msg(f'{run_date} filled with {temp_posts[0]}')
            temp_posts.pop(0)  # Remove the post we use from the list
    await log_msg('Finished filling posts')
    if reschedule:
        day = (now + timedelta(days=1)).day
        run_date = now.replace(hour=int(data['post_time'][0].split(':')[0]),
                               minute=int(data['post_time'][0].split(':')[1]), day=day)
        sched.modify_job(job_id='fetcher', next_run_time=run_date - timedelta(minutes=5), args=(sched,))


if __name__ == '__main__':
    check_config()  # Validate config
    botdata = BotInstance()  # Load data
    scheduler.remove_all_jobs()  # Remove previous jobs
    # Schedule posts every 24 hours
    scheduler.add_job(fill_posts, args=(scheduler, True), id='fetcher', trigger='interval', hours=24, coalesce=True,
                      max_instances=2, replace_existing=True, next_run_time=datetime.now() + timedelta(seconds=2))
    scheduler.start()
    aiogram.executor.start_polling(botdata.dp)  # Initialize bot polling
