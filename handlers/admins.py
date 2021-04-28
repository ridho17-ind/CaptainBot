from asyncio.queues import QueueEmpty

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import Message
from callsmusic import callsmusic
from callsmusic.callsmusic import client as user

from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only, admin_only

import cache.admins


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply("❗ Tidak ada lagu yang diputar")
    if callsmusic.pytgcalls.active_calls[message.chat.id] == 'paused':
        await message.reply("❗ Lagu sudah dijeda sebelumnya!")
    else:
        callsmusic.pytgcalls.pause_stream(message.chat.id)
        await message.reply_text("▶️ Dijeda!")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply("❗ Tidak ada lagu yang diputar")
    if callsmusic.pytgcalls.active_calls[message.chat.id] == 'playing':
        await message.reply("❗ Lagu sudah berputar!")
    else:
        callsmusic.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("⏸ Melanjutkan!")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ Tidak ada pemutaran lagu!")
    else:
        try:
            callsmusic.queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("❌ Berhenti memutar!\n")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("Tidak ada lagu yang sedang diputar!")
    else:
        callsmusic.queues.task_done(message.chat.id)

        if callsmusic.queues.is_empty(message.chat.id):
            callsmusic.pytgcalls.leave_group_call(message.chat.id)
        else:
            callsmusic.pytgcalls.change_stream(
                message.chat.id,
                callsmusic.queues.get(message.chat.id)["file"]
            )

        await message.reply_text("➡Melewati Lagu saat ini!")


@Client.on_message(command("reload"))
@errors
@admin_only
async def reload(_, message: Message):
    cache.admins.set(message.chat.id, [member.user for member in await message.chat.get_members(filter="administrators")])
    await message.reply("✅ **Bot berhasil dimulai ulang!\n\n• Daftar admin telah diperbarui.**")


@Client.on_message(~filters.group & command("joinbot"))
@admin_only
@errors
async def invtochnl(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chat_id)
    except:
        await message.reply("**Tambahkan saya sebagai admin didalam grup anda.**")
        return

    try:
        userr = await user.get_me()
    except:
        userr.first_name = "Captain Music"

    try:
        await user.join_chat(invitelink)
        await message.reply("`Asisten masuk kedalam grup.`")
    except UserAlreadyParticipant:
        await message.reply("`Asisten sudah berada didalam grup.`")
    except Exception as e:
        print(e)
        await message.reply(
            f"**User {userr.first_name} tidak dapat masuk kedalam grup! Pastikan dia tidak di ban dari grup"
            f"\n\nAtau tambahkan @CaptMusic secara manual kedalam grup anda.**"
        )
        return


@Client.on_message(~filters.group & command("leavebot"))
@errors
@admin_only
async def lvfromchnl(_, message: Message):
    chat_id = message.chat.id
    try:
        await user.leave_chat(chat_id)
        await message.reply("`Asisten berhasil keluar dari grup.`")
    except UserNotParticipant:
        await message.reply("`Asisten sudah keluar dari grup sebelumnya`.")
        return
    except Exception as e:
        await message.reply("`Ada sebuah error yang ditemukan, coba kick asisten secara manual.`")
        print(e)
        return
