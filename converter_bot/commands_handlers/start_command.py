from aiogram import types
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

from ..config import dp


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        f"Hello, {hbold(message.from_user.full_name)}! "
        f"You turned to the bot for mutual conversion of PDF and DOCX files.\n\n"
        f'<span class="tg-spoiler">(To see the instructions for use, use the /help command).</span>',
        parse_mode="HTML",
    )
