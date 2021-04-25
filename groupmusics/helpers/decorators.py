from typing import Callable

from pyrogram import Client
from pyrogram.types import Message

from ..helpers.admins import get_administrators
from ..config import SUDO_USERS
from ..cache.admins import admins as a


def errors(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        try:
            return await func(client, message)
        except Exception as e:
            await message.reply(f"{type(e).__name__}: {e}")

    return decorator


def authorized_users_only(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        if message.from_user.id in SUDO_USERS:
            return await func(client, message)

        administrators = await get_administrators(message.chat)

        for administrator in administrators:
            if administrator == message.from_user.id:
                return await func(client, message)

    return decorator


def admin_only(func: Callable) -> Callable:
    async def decorator(client: Client, message: Message):
        admins = await get_administrators(message.chat)
        for admin in admins:
            if admin == message.from_user.id:
                return await func(client, message)
    return decorator


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admin = a.get(cb.message.chat.id)
        if cb.from_user.id in admin:
            return await func(client, cb)
        else:
            await cb.answer("Kamu tidak diizinkan untuk melakukan ini!", show_alert=True)
            return
    return decorator


