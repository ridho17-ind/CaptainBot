from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_NAME as BN
from config import DEV_NAME as DNAME

from config import BOT_USERNAME as BUN
from config import USERBOT_USERNAME as USUN

from config import GROUP_URI as GURI

from config import DEV_ID as DID
from config import STICKER_ID as SID

from helpers.filters import other_filters2, other_filters


@Client.on_message(filters.command("start") & other_filters2)
async def start(_, message: Message):
    await message.reply_sticker(SID)
    await message.reply_text(
        f"""Haiii {message.from_user.first_name} Saya **{BN}** 🎵\n\n
        Saya bisa memutar musik di obrolan suara grup anda. Saya dikembangkan oleh [{DNAME}](tg://user?id={str(DID)}).\n
        Tambahkan [Assistant](https://t.me/{USUN}) dan [Bot](https://t.me/{BUN}) 
        kedalam grup Anda, dan nikmati mendengar musik dengan bebas!
        """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎛 Perintah", url="https://telegra.ph/Perintah---Captain-Music-Bot-04-25"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💬 Grup", url=f"{GURI}"
                    ),
                    InlineKeyboardButton(
                        "🔊 Bot Info Channel", url="https://t.me/InfoOfAllBot"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ Tambahkan Bot Kedalam Grup ➕", url=f"https://t.me/{BUN}?startgroup=true"
                    )
                ]
            ]
        ),
        disable_web_page_preview=True
    )


@Client.on_message(filters.command("online") & other_filters2)
async def gstart(_, message: Message):
    await message.reply_text("""**Bot Musik Online ✅**""")


@Client.on_message(filters.command("help") & other_filters2 & ~filters.group)
async def ghelp(_, message: Message):
    await message.reply(
        f"Untuk perintah silahkan klik tombol dibawah ini",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎛 Perintah", url="https://telegra.ph/Perintah---Captain-Music-Bot-04-25"
                    )
                ]
            ]
        )
    )
