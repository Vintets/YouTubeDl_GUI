#!/usr/bin/env python

"""
Проект YouTubeDl_GUI
Враппер для консольной утилиты youtube-dl обновлён для yt-dlp

Скачивание файлов с youtube c практичными настройками

/*******************************************************
 * Copyright 2022 Vintets <programmer@vintets.ru> - All Rights Reserved
 *
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Vintets <programmer@vintets.ru>, Octember 2022
 *
 * This file is part of YouTubeDl_GUI project.
 * YouTubeDl_GUI can not be copied and/or distributed without the express
 * permission of Vintets
*******************************************************/

# for python 3.9.7 and over
"""

import os
from pathlib import Path
import sys
import time

PATH_SCRIPT = Path(__file__).parent
os.chdir(PATH_SCRIPT)

from accessory import authorship, check_version, init_console, logger  # noqa: E402
from configs import config  # noqa: E402
from core.gui import MainGUI  # noqa: E402


__version_info__ = ('2', '8', '2')
__version__ = '.'.join(__version_info__)
__author__ = 'master by Vint'
__title__ = '--- YouTubeDl_GUI ---'
__copyright__ = 'Copyright 2022-2024 (c)  bitbucket.org/Vintets'


def exit_from_program(code: int = 0) -> None:
    time.sleep(1)
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)


def main() -> None:
    app = MainGUI(
                  author=__author__,
                  title=__title__,
                  version=__version__,
                  copyright_=__copyright__
                  )
    app.mainloop()


if __name__ == '__main__':
    init_console(width=130, hight=54)
    check_version(version=(3, 12, 0))

    authorship(__author__, __title__, __version__, __copyright__)  # width=_width

    try:
        main()
    except KeyboardInterrupt:
        logger.info('Отмена. Скрипт остановлен.')
        exit_from_program(code=0)
    except Exception as e:
        logger.critical(e)  # __str__()
        if config.EXCEPTION_TRACE:
            raise e
        exit_from_program(code=1)
