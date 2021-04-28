# the logging things

import logging

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client

from youtube_search import YoutubeSearch

from helpers.filters import command


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


logging.getLogger("pyrogram").setLevel(logging.WARNING)


def mrkup(result):
    for num in range(0, 4):
        (InlineKeyboardButton(f"{num}", url=f"https://youtube.com{result[num]['url_suffix']}"),)


@Client.on_message(command("search"))
async def ytsearch(_, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("/search membutuhkan argumen!")
            return
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("Mencari....")
        results = YoutubeSearch(query, max_results=4).to_dict()
        i = 0
        text = ""
        while i < 4:
            text += f"{i}.  Judul - {results[i]['title']}\n"
            text += f"      Durasi - {results[i]['duration']}\n"
            text += f"      Penonton - {results[i]['views']}\n"
            text += f"      Channel - {results[i]['channel']}\n"
            text += f"      https://youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[mrkup(result=results)]]))
    except Exception as e:
        await message.reply_text(str(e))
