from typing import Dict, Union

from PIL import Image


class ImageQualityReducer:
    def __init__(self, image_path: str):
        self.image_path = image_path

    def reduce(
        self, quality: int, file_specifier: str = None
    ) -> Union[Dict[str, str], Image.Image]:
        image = Image.open(self.image_path)
        new_path = self.change_path(self.image_path, file_specifier)
        image.save(fp=f"{new_path}", quality=quality)
        return {"reduced_image": image, "new_file_path": new_path}

    @staticmethod
    def change_path(path: str, file_specifier: str) -> str:
        dot_symbol = "."
        sep_ext = path.split(dot_symbol)
        new_path = (
            f"{sep_ext[0]}_reduced_{file_specifier}"
            if file_specifier
            else f"{sep_ext[0]}_reduced"
        )
        full_path = new_path + dot_symbol + sep_ext[1]
        return full_path
