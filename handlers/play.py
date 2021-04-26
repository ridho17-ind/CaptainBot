from os import path

from pyrogram import Client
from pyrogram.types import Message

from callsmusic import callsmusic, queues

from converter import converter
from downloaders import youtube

from config import DURATION_LIMIT
from helpers.filters import command, other_filters
from helpers import decorators
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_message(command("music") & other_filters)
@decorators.errors
async def play(_, message: Message):
    lel = await message.reply("🔄 **Memproses** lagu...")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="🔊 Channel",
                    url="https://t.me/InfoOfAllBot")

            ]
        ]
    )

    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ Vidio yang durasinya lebih dari {DURATION_LIMIT} menit tidak diperbolehkan untuk diputar!"
            )

        file_name = get_file_name(audio)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )
    elif url:
        file_path = await converter.convert(youtube.download(url))
    else:
        return await lel.edit_text("❗ Kamu tidak memberikanku apapun untuk diputar!")

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await lel.edit(f"#⃣ **Antri** pada posisi {position}!")
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
            photo="https://telegra.ph/file/a4fa687ed647cfef52402.jpg",
            reply_markup=keyboard,
            caption=f"▶**Memutar** lagu disini, atas permintaan {message.from_user.mention()}!"
            ),
        return await lel.delete()
