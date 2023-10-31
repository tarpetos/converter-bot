import os
import asyncio
import logging
import sys
from datetime import datetime
from converter_bot import ConverterBot


def configure_logs() -> None:
    logs_dir = "logs"

    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    log_filepath = os.path.join(logs_dir, f"{current_datetime}.log")
    file_handler = logging.FileHandler(log_filepath)
    console_handler = logging.StreamHandler(sys.stdout)

    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(log_formatter)
    console_handler.setFormatter(log_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    # root_logger.addHandler(console_handler)  # console logs are enabled by pdf2docx library


def main() -> None:
    configure_logs()
    bot_starter = ConverterBot()
    asyncio.run(bot_starter.start())


if __name__ == "__main__":
    main()
