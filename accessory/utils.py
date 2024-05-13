import ctypes
import sys
import time
from enum import Enum


MOUSEEVENTF_LEFTDOWN = 2
MOUSEEVENTF_LEFTUP = 4


def check_version() -> None:
    if sys.version_info < (3, 12, 0):
        print(u'Для работы требуется версия Python 3.12.0 и выше')
        time.sleep(4)
        exit()
        raise Exception(u'Для работы требуется версия Python 3.12.0 и выше')


"""
def check_monitor_resolution() -> None:
    size = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    if size not in ((3440, 1440), (2560, 1080)):
        raise err.UnsupportedResolutionError(size)
"""


def create_dirs(path_graphlog) -> None:
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


class ResultType(Enum):
    SUCCESS = 'успешно'
    PARTIAL_SUCCESS = 'успешно случайно'
    WRONG = 'неправильно'
