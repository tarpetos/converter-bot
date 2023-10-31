import asyncio
import os

from typing import List, Tuple, Optional, Union

from pdf2docx import Converter
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from .constants import DOCUMENT_FILE_PREFIX, PDF, DEFAULT_RESULT_FILE_NAME, DOCX
from .filer_loader import FileLoader
from .image_to_file_converter import FileConverter


class DocumentLoader(FileLoader):
    async def save_files(self, file_ids: List[str], **kwargs) -> List[str]:
        file_extension = kwargs["file_extension"]
        document_list = await self._documents_processing(
            file_ids, file_extension=file_extension
        )
        return document_list

    async def _documents_processing(
        self, file_ids: List[str], file_extension: Optional[str] = None
    ) -> List[str]:
        return await self._files_processing(
            file_ids, DOCUMENT_FILE_PREFIX, file_extension
        )


class DocxToPdf(FileConverter):
    LOAD_TIMEOUT = 10

    async def convert(
        self, conversion_file_path: str, paths: List[str], **kwargs
    ) -> None:
        try:
            await self._parse_page(conversion_file_path, paths)
        except TimeoutException:
            await self._parse_page(conversion_file_path, paths)

    async def _parse_page(self, conversion_file_path: str, paths: List[str]) -> None:
        docx_file = os.path.join(conversion_file_path)
        dir_name = paths[0]

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": dir_name,
            },
        )
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://smallpdf.com/word-to-pdf")

        upload_file_button_xpath = "//input[@type='file']"

        file_input = WebDriverWait(driver, self.LOAD_TIMEOUT).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, upload_file_button_xpath)
            )
        )
        file_input.send_keys(docx_file)

        download_file_button_xpath = "//div//span[contains(text(), 'Download')]"
        file_output = WebDriverWait(driver, self.LOAD_TIMEOUT).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, download_file_button_xpath)
            )
        )
        file_output.click()
        await asyncio.sleep(self.LOAD_TIMEOUT)
        self.rename_pdf(docx_file)

    @staticmethod
    def rename_pdf(docx_file_path: str) -> None:
        pdf_file_path = os.path.splitext(docx_file_path)[0] + f".{PDF}"
        if os.path.exists(pdf_file_path):
            new_pdf_file_path = os.path.join(
                os.path.dirname(pdf_file_path), f"{DEFAULT_RESULT_FILE_NAME}.{PDF}"
            )
            os.rename(pdf_file_path, new_pdf_file_path)

    def compress(
        self, image_file: str, compression_allowed: bool
    ) -> Union[Tuple[str, int, int], str]:
        raise NotImplementedError


class PdfToDocx(FileConverter):
    def convert(
        self,
        conversion_file_path: str,
        paths: List[str],
        password: Optional[str] = None,
        **kwargs,
    ) -> None:
        pdf_file = os.path.join(conversion_file_path)
        docx_file = os.path.join(paths[0], f"{DEFAULT_RESULT_FILE_NAME}.{DOCX}")

        conversion_file = Converter(pdf_file, password=password)
        conversion_file.convert(docx_file)
        conversion_file.close()

    def compress(
        self, image_file: str, compression_allowed: bool
    ) -> Union[Tuple[str, int, int], str]:
        raise NotImplementedError
