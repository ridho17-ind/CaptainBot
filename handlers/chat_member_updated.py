from pyrogram import Client
from pyrogram.types import ChatMemberUpdated

from cache import admins


@Client.on_chat_member_updated()
async def chat_member_updated(_, chat_member_updated: ChatMemberUpdated):
    chat, new = chat_member_updated.chat, chat_member_updated.new_chat_member
    if new:
        if chat.id in admins.admins:
            if new.can_manage_voice_chats:
                if new.user.id not in admins.admins[chat.id]:
                    admins.admins[chat.id].append(new.user.id)
            else:
                if new.user.id in admins.admins[chat.id]:
                    admins.admins[chat.id].remove(new.user.id)
