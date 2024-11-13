import asyncio
import os
import logging
import mimetypes
import json

from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.types import ContentType, FSInputFile
from aiogram.methods import SendPhoto, SendVideo, SendMessage
from aiogram.filters import Command


data = json.load(open("data.json"))
MEDIA_DIR = os.path.dirname(os.path.abspath(__file__)) + '/media'
TOKEN = data["token"]
TARGET_USER_ID = data["target_user_id"]
ALLOWED_USERS = data["other_users"]
ALLOWED_USERS.append(TARGET_USER_ID)
TARGET_CHANNEL = data["target_chanel"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

def is_not_hidden_(file_):
    return not file_.startswith('.')

def list_non_hidden_(path_):
    return list(filter(is_not_hidden_, os.listdir(path_)))


async def save_media(message: types.Message) -> None:
    if message.from_user.id == TARGET_USER_ID and message.content_type in [ContentType.PHOTO, ContentType.VIDEO]:
        file_id = message.photo[-1].file_id if message.content_type == ContentType.PHOTO else message.video.file_id
        file_info = await bot.get_file(file_id)
        save_path = os.path.join(MEDIA_DIR, os.path.basename(file_info.file_path.replace('\\', '/')))
        try:
            await bot.download_file(file_info.file_path, save_path)
        except:
            await message.reply('Cant download this file')
            if os.path.exists(save_path) and os.path.isfile(save_path):
                os.remove(save_path)
            return
        try:
            if message.content_type == ContentType.PHOTO:
                check_file_to_send = await bot(SendPhoto(chat_id=TARGET_USER_ID, photo=FSInputFile(save_path)))
            else:
                check_file_to_send = await bot(SendVideo(chat_id=TARGET_USER_ID, video=FSInputFile(save_path)))
            await bot.delete_message(chat_id=TARGET_USER_ID, message_id=check_file_to_send.message_id)
        except:
            await message.reply('Cant handle this file')
            if os.path.exists(save_path) and os.path.isfile(save_path):
                os.remove(save_path)


async def send_count(message: types.Message) -> None:
    if message.from_user.id in ALLOWED_USERS and message.content_type == ContentType.TEXT:
        files = list_non_hidden_(MEDIA_DIR)
        await message.answer(f"Files left: {len(files)}")


async def send_media():
    logger.info("Trying to send")
    files = sorted(list_non_hidden_(MEDIA_DIR))
    if not files:
        await bot(SendMessage(chat_id=TARGET_USER_ID, text='NOTHING TO SEND! UPLOAD MORE MEDIA!'))
        logger.info("Nothing to send!")
        return
    file_path = os.path.join(MEDIA_DIR, files[0])
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type.startswith('video'):
            await bot(SendVideo(chat_id=TARGET_CHANNEL, video=FSInputFile(file_path)))
            logger.info("Video sent!")
        elif mime_type.startswith('image'):
            await bot(SendPhoto(chat_id=TARGET_CHANNEL, photo=FSInputFile(file_path)))
            logger.info("Image sent!")
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Error sending media: {e}")
        return
    if len(files) == 1:
        await bot(SendMessage(chat_id=TARGET_USER_ID, text='No content left!'))
    elif len(files) <= 6:
        await bot(SendMessage(chat_id=TARGET_USER_ID, text=f"There are few media files left, only {len(files) - 1}!"))


async def process_files_schedule():
    logger.info("Sender started")

    while True:
        current_date = datetime.now()
        current_time = current_date.time()

        if 7 <= current_time.hour or current_time.hour < 1:
            if current_time.minute == 0 or current_time.minute == 30:
                logger.info("Time to post")
                try:
                    await send_media()
                    await asyncio.sleep((30 * 60) - datetime.now().time().second)
                except Exception as e:
                    logger.error(f"Error processing files: {e}")
            else:
                if current_time.minute > 30:
                    minute_to_wait = 60 - current_time.minute
                elif current_time.minute <= 30:
                    minute_to_wait = 30 - current_time.minute
                logger.info("Sleeping until right minute")
                await asyncio.sleep((minute_to_wait * 60) - datetime.now().second)
        else:
            next_execution_time = datetime(current_date.year, current_date.month, current_date.day, 7, 0)
            time_difference = next_execution_time - datetime.now()
            logger.info("Its to late, im sleeping")
            await asyncio.sleep(time_difference.total_seconds())


@dp.message(Command("content_count"))
async def content_count(message: types.Message):
    await send_count(message)


@dp.message()
async def handle_media(message: types.Message):
    await save_media(message)


async def main() -> None:
    logger.info("App started")

    asyncio.create_task(process_files_schedule())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

