import os

import asyncio
import time

import requests
import wget
import youtube_dl

from pyrogram import filters, Client
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos

from helpers.filters import command
from helpers.functions import get_text, progress

is_downloading = False


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


@Client.on_message(command('song') & ~filters.private & ~filters.channel)
def song(_, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 Menemukan lagu...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb{title}.jpg'
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)

        duration = results[0]["duration"]

    except Exception as e:
        m.edit(
            "❌ Tidak menemukan apapun.\n\nPeriksa ejaan atau coba cari lagu lain."
        )
        print(str(e))
        return
    m.edit("Mengunduh lagu...")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = '**🎵 Lagu Terkirim**'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, thumb=thumb_name, parse_mode='md', title=title, duration=dur)
        m.delete()
    except Exception as e:
        m.edit('❌ Error')
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)


@Client.on_message(command("video"))
async def ytvid(client: Client, message: Message):
    global is_downloading
    if is_downloading:
        await message.reply("Ada download lain yang sedang dalam proses, coba dalam beberapa menit.")
        return

    url = get_text(message)

    adminun = await client.send_message(message.chat.id, f"`Mendapatkan {url} dari Server Youtube. Harap Tunggu.`")
    if not url:
        await adminun.edit("Perintah tidak benar, cek menu help untuk mengetahui lebih lanjut")
        return

    search = SearchVideos(f"{url}", offset=1, mode="dict", max_results=1)
    res = search.result()
    src_res = res["search_result"]
    link = src_res[0]["link"]
    title = src_res[0]["title"]
    vid_id = src_res[0]["id"]
    ch_name = src_res[0]["channel"]
    thumbs = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
    await asyncio.sleep(1)
    urls = src_res
    wget_dl = wget.download(thumbs)
    ops = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
        ],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        is_downloading = True
        with youtube_dl.YoutubeDL(ops) as ytdl:
            infoo = ytdl.extract_info(urls, False)
            duration = round(infoo["duration"] / 60)

            if duration > 8:
                await adminun.edit(
                    f"❌ Video yang lebih dari 8 menit tidak diperbolehkan, maximal hanya sampai {duration} menit"
                )
                is_downloading = False
                return
            ytdl_data = ytdl.extract_info(urls, download=True)

    except Exception as e:
        await adminun.edit(f"Gagal mendownload!\nError: {str(e)}")
        is_downloading = False
        return

    c_time = time.time()
    vid_file = f"{ytdl_data['id']}.mp4"
    capt = f"**Judul Video** `{title}` \n**Ditujukan untuk :** `{url}` \n **Channel :** `{ch_name}` \n**Link :** `{link}`"
    await client.send_video(message.chat.id, video=open(vid_file, "rb"), duration=int(ytdl_data["duration"]), file_name=str(ytdl_data["title"]), thumb=thumbs, caption=capt, supports_streaming=True, progress=progress, progress_args=(adminun, c_time, f"Mengunggah {url} dari Youtube!", vid_file))
    await adminun.delete()
    is_downloading = False
    for files in (wget_dl, vid_file):
        if files and os.path.exists(files):
            os.remove(files)