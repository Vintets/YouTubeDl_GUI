import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def image_convert(file_in: Path, file_out: Path) -> None:
    try:
        image = Image.open(file_in)
        image.save(file_out, format='JPEG', quality=97, optimize=True,
                   dpi=(100, 100))
    except UnidentifiedImageError:
        print('Ошибка открытия файла превью!')
    except OSError:
        print('Ошибка сохранения перекодированного файла превью!')
    else:
        os.remove(file_in)
