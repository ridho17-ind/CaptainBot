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


@Client.on_message(command("search"))
async def ytsearch(_, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("/search membutuhkan argumen!")
            return
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("Mencari....")
        results = YoutubeSearch(query, max_results=4).to_dict()
        i = 1
        text = ""
        while i <= 4:
            text += f"{i}.  Judul - {results[i]['title']}\n"
            text += f"      Durasi - {results[i]['duration']}\n"
            text += f"      Penonton - {results[i]['views']}\n"
            text += f"      Channel - {results[i]['channel']}\n"
            text += f"      https://youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"1", url=f"https://youtube.com{results[0]['url_suffix']}"),
                    InlineKeyboardButton(f"2", url=f"https://youtube.com{results[1]['url_suffix']}"),
                    InlineKeyboardButton(f"3", url=f"https://youtube.com{results[2]['url_suffix']}"),
                    InlineKeyboardButton(f"4", url=f"https://youtube.com{results[3]['url_suffix']}"),
                ]
            ]
        ))
    except Exception as e:
        await message.reply_text(str(e))
