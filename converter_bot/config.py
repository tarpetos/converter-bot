from os import getenv
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = getenv("BOT_TOKEN")

COMMAND_LIST_DESCRIPTION = """
/start - Initial command
/clear - Clear all active states
/help - Use instruction
"""

dp = Dispatcher()
bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
