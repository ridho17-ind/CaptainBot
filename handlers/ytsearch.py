# the logging things

import logging

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters

from youtube_search import YoutubeSearch

from helpers.filters import command


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(command("search"))
async def ytsearch(_, message: Message):
    if filters.private:
        await message.reply("Gunakan ini hanya dalam grup")
    try:
        if len(message.command) < 2:
            await message.reply(
                "Jika anda ingin mencari via inline, tekan tombol Cari di Youtube atau ketikan /search + nama lagu",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Cari di Youtube", switch_inline_query_current_chat=""
                )]])
            )
            return
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("Mencari....")
        results = YoutubeSearch(query, max_results=4).to_dict()
        i = 0
        text = ""
        while i < 4:
            text += f"{i+1} Judul - {results[i]['title']}\n"
            text += f"      Durasi - {results[i]['duration']} menit\n"
            text += f"      Penonton - {results[i]['views']}\n"
            text += f"      Channel - {results[i]['channel']}\n"
            text += f"      https://youtube.com{results[i]['url_suffix']}\n\n"
            i += 1
        await m.edit(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"{i+1}", url=f"https://youtube.com{results[i]['url_suffix']}") for i in range(4)]
            ]
        ))
    except Exception as e:
        await message.reply_text(str(e))
