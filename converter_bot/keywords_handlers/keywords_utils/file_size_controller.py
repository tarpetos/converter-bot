from typing import Optional

from aiogram import types
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types import FSInputFile

from converter_bot.config import bot


async def is_document_sent(
    message: types.Message, file_to_send: str, new_filename: Optional[str] = None
) -> bool:
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile(file_to_send, filename=new_filename),
        )
        return True
    except TelegramEntityTooLarge:
        return False
