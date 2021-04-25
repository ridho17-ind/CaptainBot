import os

# Other From Stuff
from asyncio import QueueEmpty
from PIL import Image, ImageFont, ImageDraw

# Network Stuff
import aiofiles
import requests
import aiohttp

# Youtube Stuff
from youtube_search import YoutubeSearch

# PYROGRAM STUFF
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant

# GroupMusic Module
from ..callsmusic import callsmusic, queues
from ..callsmusic.callsmusic import client as user
from ..converter import convert
from ..downloaders import youtube
from ..helpers.admins import get_administrators
from ..helpers.filters import command, other_filters
from ..helpers.decorators import errors, authorized_users_only, cb_admin_check
from ..helpers.functions import changeImageSize


async def generate_cover(requested_by, title, duration, thumbnail, message: Message):
    """
    Function to create new edited cover from original youtube video cover
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("../etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("../etc/font.otf", 32)
    draw.text((190, 550), f"Judul: {title}", (255, 255, 255), font=font)
    draw.text(
        (190, 590), f"Durasi: {duration}", (255, 255, 255), font=font
    )
    draw.text((190, 630), f"Diputar Di: {message.chat.title[:20]}...", (255, 255, 255), font=font)
    draw.text((190, 670),
              f"Atas Permintaan: {requested_by}",
              (255, 255, 255),
              font=font,
              )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


def updated_stats(chat, queue, vol=100):
    """
    Function to update stats in active voice chats
    """
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = 'Pengaturan dari **{}**'.format(chat.title)
        if len(que) > 0:
            stats += '\n\n'
            stats += f'Volume : {vol}%\n'
            stats += f'Lagu dalam antrian : `{len(que)}`\n'
            stats += f'Sedang diputar : **{queue[0][0]}**\n'
            stats += f'Atas permintaan : {queue[0][1].mention}'
    else:
        stats = None
    return stats


def ply_typ(type_):
    if type_ == "play":
        ico = "▶"
    else:
        ico = "⏸"
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('⏹', 'leave'),
                InlineKeyboardButton('⏸', 'pause'),
                InlineKeyboardButton('▶', 'resume'),
                InlineKeyboardButton('⏭', 'skip')
            ],
            [
                InlineKeyboardButton(f"Playlist 📖", "playlist")
            ],
            [
                InlineKeyboardButton(f"❌ Tutup", "cls")
            ]
        ]
    )
    return mar


@Client.on_callback_query(filters.regex(pattern=r'^(playlist)$'))
async def plylist_callback(_, cb):
    global que
    type_ = cb.matches[0].group(1)
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Bot bisa digunakan")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = f"**Sedang Diputar** di {cb.message.chat.title}"
        msg += f"\n- {now_playing}"
        msg += f"\n- Atas Permintaan {by}"
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Dalam Antrian**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Atas Permintaan{usr}"
        await cb.message.edit(msg)


@Client.on_callback_query(filters.regex(pattern=r'^(play|pause|skip|leave|pus|resume|menu|cls)$'))
@cb_admin_check
async def othr_callback(_, cb):
    global que
    queue = que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    chat_id = cb.message.chat.id
    msg_chat = cb.message.chat
    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data

    if type_ == "play":
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Tidak ada obrolan suara yang aktif")
        if callsmusic.pytgcalls.active_calls[chat_id] == "playing":
            await cb.answer("Sudah Memutar!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chat_id)
            await cb.answer("Lagu Dilanjutkan!")
            await cb.message.edit(updated_stats(msg_chat, queue), reply_markup=ply_typ("pause"))

    elif type_ == "pause":
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Tidak ada obrolan suara yang aktif")
        if callsmusic.pytgcalls.active_calls[chat_id] == "playing":
            await cb.answer("Sudah Memutar!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chat_id)
            await cb.answer("Lagu Dijeda")
            await cb.message.edit(updated_stats(msg_chat, queue), reply_markup=ply_typ("play"))

    elif type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Bot bisa digunakan")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = f"**Sedang Diputar** di {cb.message.chat.title}"
        msg += f"\n- {now_playing}"
        msg += f"\n- Atas Permintaan {by}"
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Dalam Antrian**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n- {name}"
                msg += f"\n- Atas Permintaan{usr}"
        await cb.message.edit(msg)

    elif type_ == "resume":
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Tidak ada obrolan suara yang aktif")
        if callsmusic.pytgcalls.active_calls[chat_id] == "playing":
            await cb.answer("Sudah Memutar!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chat_id)
            await cb.answer("Lagu Dilanjutkan!")

    elif type_ == "puse":
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Tidak ada obrolan suara yang aktif")
        if callsmusic.pytgcalls.active_calls[chat_id] == "playing":
            await cb.answer("Sudah Memutar!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chat_id)
            await cb.answer("Lagu Dijeda")

    elif type_ == "cls":
        await cb.answer("Menu Ditutup")
        await cb.message.delete()

    elif type_ == "menu":
        stats = updated_stats(msg_chat, queue)
        await cb.answer("Menu Dibuka")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⏹', 'leave'),
                    InlineKeyboardButton('⏸', 'pause'),
                    InlineKeyboardButton('▶️', 'resume'),
                    InlineKeyboardButton('⏭', 'skip')
                ],
                [
                    InlineKeyboardButton(f"Playlist 📖", "playlist")
                ],
                [
                    InlineKeyboardButton("❌ Tutup", 'cls')
                ]
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)

    elif type_ == "skip":
        if queue:
            skip = queue.pop(0)
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Bot Tidak Memutar Musik", show_alert=True)
        else:
            callsmusic.queues.task_done(chat_id)
            if callsmusic.queues.is_empty(chat_id):
                callsmusic.pytgcalls.leave_group_call(chat_id)
                await cb.message.edit("- Tidak Ada Playlist...\n- Keluar dari Obrolan Suara")

            else:
                callsmusic.pytgcalls.change_stream(chat_id, callsmusic.queues.get(chat_id)["file"])
                await cb.answer("Lagu Di-Skip!")
                await cb.message.edit((msg_chat, queue), reply_markup=ply_typ(the_data))
                await cb.message.reply(f"- Lagu Di-Skip!\n- Sekarang Memutar **{queue[0][0]}**")

    else:
        if chat_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chat_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.leave_group_call(chat_id)
            await cb.message.edit("Sukses Keluar dari Obrolan Suara!")
        else:
            await cb.answer("Tidak Terhubung ke Obrolan Suara", show_alert=True)


@Client.on_message(command("play") & other_filters)
@errors
async def play(_, message: Message):
    global file_path
    global que
    lel = await message.reply("🔄 **Memprosses** ...")
    admins = await get_administrators(message.chat)
    chat_id = message.chat.id

    for admin in admins:
        if admin == message.from_user.id:
            try:
                invite_link = await _.create_chat_invite_link(chat_id, member_limit=1)
            except:
                await lel.edit("**Tambahkan saya sebagai admin terlebih dahulu.**")
                return
            try:
                await user.join_chat(invite_link)
                await lel.edit("**Userbot masuk kedalam grup**")
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                pass
    try:
        chatdetails = await user.get_chat(chat_id)
    except:
        await lel.edit("__Bot helper tidak ada didalam grup, minta admin untuk mengirim perintah /play pada pertama "
                       "kali atau tambahkan bot secara manual__")
        return

    user_name = message.from_user.first_name
    requested_by = user_name
    chat_title = message.chat.title
    await lel.edit("🔎 **Mencari**...")

    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    await lel.edit("🎵 **Memproses Lagu**...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)

        duration = results[0]["duration"]

    except Exception as e:
        await lel.edit(
            "❌ Tidak menemukan apapun.\n\nPeriksa ejaan atau cari lagu lain."
        )
        print(str(e))
        return
    await lel.edit("__**Memproses Thumbnail...**__")
    await generate_cover(requested_by, title, duration, thumbnail, chat_title)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📖 Playlist", callback_data="playlist"),
                InlineKeyboardButton("⏯ Menu", callback_data="menu")
            ],
            [
                InlineKeyboardButton(
                    text="Tonton Di YouTube 🎬",
                    url=url
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Tutup",
                    callback_data="cls"
                )
            ]
        ]
    )

    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None

    if audio:
        await lel.edit_text("Gunakan perintah /music jika anda ingin memutar lagu dari sebuah file")

    elif url:
        file_path = await convert(youtube.download(url))
    else:
        return await lel.edit_text("❗ Kamu tidak memberikan apapun kepada saya untuk diputar!")

    if message.chat.id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
            photo="final.png",
            caption=f"#⃣ Lagu yang kamu berikan antri pada posisi {position}!",
            reply_markup=keyboard
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        callsmusic.pytgcalls.join_group_call(message.chat.id, file_path)
        await message.reply_photo(
            photo="final.png",
            reply_markup=keyboard,
            caption=f"▶**Memutar Lagu disini**, {message.from_user.mention()} me-request {query} melalui YouTube "
                    f"Music 😜 "
        )
        os.remove("final.png")
        return await lel.delete()


@Client.on_message(command("current") & other_filters)
async def currents(_, message: Message):
    global que
    queuess = que.get(message.chat.id)
    stats = updated_stats(message.chat, queuess)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("Tidak ada obrolan suara yang berjalan di grup ini")


@Client.on_message(command("playlist") & other_filters)
async def playlists(_, message: Message):
    global que
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply("Bot musik tersedia")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = f"**Sedang Diputar** di {message.chat.title}"
    msg += f"\n- {now_playing}"
    msg += f"\n- Atas permintaan {by}"
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**Antrian**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n- {name}"
            msg += f"\n- Atas Permintaan {usr}"
    await message.reply(msg)


@Client.on_message(command("player") & other_filters)
@authorized_users_only
async def player(_, message: Message):
    playing = None
    if message.chat.id in callsmusic.pytgcalls.active_calls:
        playing = True
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=ply_typ("pause"))
        else:
            await message.reply(stats, reply_markup=ply_typ("play"))
    else:
        await message.reply("Tidak ada Obrolan suara yang berjalan disini")

