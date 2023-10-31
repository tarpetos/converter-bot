import os
import shutil
from abc import ABC, abstractmethod
from typing import List

from aiogram import types

from .constants import MAIN_TEMP_DATA_FOLDER, USER_FOLDER_NAME_PREFIX
from converter_bot.config import bot


class FileLoader(ABC):
    TEMP_DATA_DIR = os.path.abspath(MAIN_TEMP_DATA_FOLDER)

    def __init__(self, message: types.Message, dir_type: str):
        self.message = message
        self.user_id = message.from_user.id
        self.temp_dir = os.path.join(
            self.TEMP_DATA_DIR, f"{USER_FOLDER_NAME_PREFIX}_{dir_type}_{self.user_id}"
        )
        self.create_temp_dir()

    def create_temp_dir(self) -> None:
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def remove_temp_dir(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @abstractmethod
    async def save_files(self, file_ids: List[str], **kwargs) -> List[str]:
        raise NotImplementedError

    async def _files_processing(
        self, file_ids: List[str], filename: str, file_extension: str
    ) -> List[str]:
        file_path_list = []

        for file_index, file_id in enumerate(file_ids):
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            file = await bot.download_file(file_path)

            filename = self._get_filename(filename, file_index, file_extension)
            temp_file_path = os.path.join(self.temp_dir, filename)
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(file.getvalue())

            file_path_list.append(temp_file_path)

        return file_path_list

    @staticmethod
    def _get_filename(document_name: str, file_index: int, file_extension: str) -> str:
        return f"{document_name}_{file_index}.{file_extension}"
