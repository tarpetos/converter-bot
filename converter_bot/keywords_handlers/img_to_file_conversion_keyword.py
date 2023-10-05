import re
from typing import Any, Dict

from aiogram import F, types
from aiogram.enums import ContentType
from aiogram.filters import and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from .keywords_utils.constants import IMAGES_FOLDER, DEFAULT_RESULT_FILE_NAME, PDF, DOCX
from .keywords_utils.document_checks import (
    file_option_selector,
    parse_args,
    get_conversion_path_name,
)
from .keywords_utils.file_size_controller import is_document_sent
from .keywords_utils.image_to_file_converter import (
    ImageLoader,
    PDFConverter,
    DOCXConverter,
)
from ..config import dp


class ImageForm(StatesGroup):
    image_data = State()


@dp.message(and_f(ImageForm.image_data, (F.photo | F.document)))
async def image_pdf_converter_helper(message: types.Message, state: FSMContext):
    photo = file_option_selector(message)
    if not photo:
        await state.clear()
        return

    data = await state.get_data()
    data["photo_counter"] += 1
    photo_counter = data["photo_counter"]
    data[f"photo_{photo_counter}"] = dict(photo)
    data[f"allowed_message_id_list"].append(message.message_id)

    await state.update_data(data)

    if data["photo_counter"] > 20:
        await state.clear()


@dp.message(F.photo | F.document)
async def keyword_file_to_file_handler(
    message: types.Message, state: FSMContext
) -> None:
    state_is_set = await state.get_state()
    if state_is_set:
        await image_pdf_converter_helper(message, state)
        return

    first_photo = file_option_selector(message)
    if not first_photo:
        return
    await state.set_state(ImageForm.image_data)

    await state.set_data(
        {
            "photo_0": dict(first_photo),
            "photo_counter": 0,
            "allowed_message_id_list": [message.message_id],
        }
    )


@dp.message(
    and_f(
        ImageForm.image_data,
        F.reply_to_message,
        F.text.regexp(
            re.compile(
                "^pdf\s*([1-9][0-9]?|100)?$|^пдф\s*([1-9][0-9]?|100)?$", re.IGNORECASE
            )
        ),
    )
)
async def image_pdf_converter_end_state_handler(
    message: types.Message, state: FSMContext
) -> None:
    state_data = await state.get_data()
    user_message_ids = state_data["allowed_message_id_list"]
    check_message_id = message.reply_to_message.message_id
    replied_message = message.reply_to_message.content_type
    allowed_content = (ContentType.PHOTO, ContentType.DOCUMENT)

    if replied_message in allowed_content and check_message_id in user_message_ids:
        await process_conversion(message, state, state_data)


async def process_conversion(
    message: types.Message, state: FSMContext, state_data: Dict[str, Any]
) -> None:
    images_server_ids = [
        state_data[key]["file_id"]
        for key in state_data
        if key.startswith("photo") and not isinstance(state_data[key], int)
    ]
    file_loader = ImageLoader(message, IMAGES_FOLDER)
    image_path_list = await file_loader.save_files(images_server_ids)

    bot_message = await message.reply("PDF and DOCX conversion started...")

    compression_level = parse_args(message)
    user_id = message.from_user.id
    conversion_pdf_path = get_conversion_path_name(
        IMAGES_FOLDER, user_id, PDF, filename=DEFAULT_RESULT_FILE_NAME
    )
    pdf_converter = PDFConverter()
    pdf_converter.convert(
        conversion_pdf_path, image_path_list, compression_level=compression_level
    )

    conversion_docx_path = get_conversion_path_name(
        IMAGES_FOLDER, user_id, DOCX, filename=DEFAULT_RESULT_FILE_NAME
    )
    docx_converter = DOCXConverter()
    docx_converter.convert(
        conversion_docx_path, image_path_list, compression_level=compression_level
    )

    bot_message_data = await send_documents(
        message, conversion_pdf_path, conversion_docx_path
    )

    await bot_message.edit_text(text=bot_message_data)

    file_loader.remove_temp_dir()
    await state.clear()


async def send_documents(message: types.Message, pdf_path: str, docx_path: str) -> str:
    pdf_sent = await is_document_sent(message, pdf_path)
    docx_sent = await is_document_sent(message, docx_path)

    if pdf_sent and docx_sent:
        return "Conversion was successfully ended!"
    elif pdf_sent and not docx_sent:
        return "Conversion error: converted DOCX is to large (must be less than 50 MB)!"
    elif not pdf_sent and docx_sent:
        return "Conversion error: converted PDF is to large (must be less than 50 MB)!"
    return "Conversion failed because converted files are larger than 50MB!"
