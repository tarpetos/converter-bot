import asyncio

from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..config import dp, bot


@dp.message(Command("clear"))
async def command_clear_states_handler(message: types.Message, state: FSMContext):
    bot_message = await message.reply("Clearing states...")
    await asyncio.sleep(0.5)
    await state.clear()
    await bot.edit_message_text(
        "States are cleared.",
        chat_id=message.chat.id,
        message_id=bot_message.message_id,
    )
