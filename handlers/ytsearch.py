from typing import Union, Dict

import pyrogram

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


def mrkup(i: Union[int, str], results: Union[Dict[str, int]]):
    for num in i:
        mar = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"{num}", f"https://youtube.com{results[num]['url_suffix']}")
            ]
        ])
        return mar


@Client.on_message(command(["search"]))
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
            text += f"Judul - {results[i]['title']}\n"
            text += f"Durasi - {results[i]['duration']}\n"
            text += f"Penonton - {results[i]['views']}\n"
            text += f"Channel - {results[i]['channel']}\n"
            text += f"https://youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, mrkup(i, results), disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(str(e))
