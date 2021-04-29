from os import getenv

from dotenv import load_dotenv

load_dotenv()

que = {}

# BOT & USERBOT
BOT_TOKEN = getenv("BOT_TOKEN")  # BOT
SESSION_NAME = getenv("SESSION_NAME", "session")  # USERBOT

# NAME
BOT_NAME = getenv("BOT_NAME")  # BOT NAME
DEV_NAME = getenv("DEV_NAME", "Abdul")  # DEV NAME

# USERNAME
BOT_USERNAME = getenv("BOT_USERNAME")  # BOT USERNAME
USERBOT_USERNAME = getenv("USERBOT_USERNAME")  # USERBOT USERNAME

# ID
DEV_ID = int(getenv("DEV_ID", 1398688205))  # DEV ID

# USERBOT ID AND HASH
API_ID = int(getenv("API_ID"))  # API ID
API_HASH = getenv("API_HASH")  # API HASH

# MISC
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "7"))  # DURATION LIMIT

COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ !").split())  # FOR COMMAND

SUDO_USERS = list(map(int, getenv("SUDO_USERS").split()))  # FOR AUTHORIZED USERS

GROUP_URI = getenv("GROUP_URI")  # FOR THE INLINE BUTTON
