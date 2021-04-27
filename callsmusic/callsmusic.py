from pyrogram import Client
from pytgcalls import PyTgCalls

from config import SESSION_NAME, API_ID, API_HASH
from .queues import queues

client = Client(SESSION_NAME, API_ID, API_HASH)
pytgcalls = PyTgCalls(client)


@pytgcalls.on_stream_end()
async def on_stream_end(chat_id: int) -> None:
    queues.task_done(chat_id)
    if queues.is_empty(chat_id):
        pytgcalls.leave_group_call(chat_id)
        await client.leave_chat(chat_id)
    else:
        pytgcalls.change_stream(
            chat_id, queues.get(chat_id)["file"]
        )


run = pytgcalls.run
