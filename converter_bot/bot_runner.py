from .config import dp, bot


class ConverterBot:
    @staticmethod
    async def start() -> None:
        await dp.start_polling(bot)
