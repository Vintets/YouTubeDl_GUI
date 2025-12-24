from __future__ import annotations

import ctypes
from enum import Enum
import os
from pathlib import Path
import sys
import time


MOUSEEVENTF_LEFTDOWN = 2
MOUSEEVENTF_LEFTUP = 4


def check_version(version: tuple[int, int, int] = (3, 12, 0)) -> None:
    if sys.version_info < version:
        print(u'Для работы требуется версия Python %d.%d.%d и выше' % (version[0], version[1], version[2]))
        exit_from_program(code=1)
        raise Exception(u'Для работы требуется версия Python %d.%d.%d и выше' % (version[0], version[1], version[2]))


"""
def check_monitor_resolution() -> None:
    size = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    if size not in ((3440, 1440), (2560, 1080)):
        raise err.UnsupportedResolutionError(size)
"""


def create_dirs(path_graphlog: Path) -> None:
    if not (path_graphlog.exists() and path_graphlog.is_dir()):
        path_graphlog.mkdir()


def limit(value: int, low: int = 0, high: int = 255) -> int:
    """Лимиты для переданного значения"""
    return min(max(value, low), high)


def lclick(x_coord: int, y_coord: int) -> None:
    win32api = ctypes.windll.user32
    win32api.SetCursorPos(x_coord, y_coord)
    win32api.mouse_event(MOUSEEVENTF_LEFTDOWN, x_coord, y_coord, 0, 0)
    time.sleep(0.3)
    win32api.mouse_event(MOUSEEVENTF_LEFTUP, x_coord, y_coord, 0, 0)


def exit_from_program(code: int = 0, close: bool = False) -> None:
    if not close:
        input('\n{dash}   END   {dash}'.format(dash='-' * 20))
    else:
        time.sleep(1)
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)


class ResultType(Enum):
    SUCCESS = 'успешно'
    PARTIAL_SUCCESS = 'успешно случайно'
    WRONG = 'неправильно'
