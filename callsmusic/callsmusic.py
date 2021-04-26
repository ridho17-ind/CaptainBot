from pyrogram import Client
from pytgcalls import PyTgCalls

from config import SESSION_NAME, API_ID, API_HASH
from queues import get, task_done, is_empty

client = Client(SESSION_NAME, API_ID, API_HASH)
pytgcalls = PyTgCalls(client)


@pytgcalls.on_stream_end()
def on_stream_end(chat_id: int) -> None:
    task_done(chat_id)

    if is_empty(chat_id):
        pytgcalls.leave_group_call(chat_id)
        client.leave_chat(chat_id)
    else:
        pytgcalls.change_stream(
            chat_id, get(chat_id)["file"]
        )


run = pytgcalls.run
