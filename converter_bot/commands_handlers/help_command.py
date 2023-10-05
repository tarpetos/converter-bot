from aiogram import types
from aiogram.filters import Command
from aiogram.utils.markdown import hcode

from ..config import dp, COMMAND_LIST_DESCRIPTION


@dp.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    await message.reply(
        f"The bot is able to cache up to 20 images that you send to it or send from other users, "
        f"and it also accepts images in the form of files. When the number of images in the cache "
        f"reaches more than 20, the cache is automatically cleared. "
        f"You can also clear it manually (see command below).\n\n"
        f"To convert cached images to PDF and DOCX files, use the {hcode('pdf <optional_arg>')} "
        f"keyword in reply to any message with a cached image. {hcode('<optional_arg>')} must be "
        f"an integer between 1 and 100. If it is 100, the quality will be the same as the original image. "
        f"The lower the number, the worse the image quality.\n\n"
        f"For mutual conversion of PDF and DOCX files, select any message containing the file, "
        f"and use the {hcode('convert')} keyword in reply to it.\n\n"
        f"{COMMAND_LIST_DESCRIPTION}"
    )
