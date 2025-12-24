#!/home/admin/venv_flask3/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
PLATFORM = sys.platform
if PLATFORM == 'win32':
    from ctypes import byref, POINTER, Structure, windll, wintypes
    _stdout_handle = windll.kernel32.GetStdHandle(-11)
    _SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
    COORD = wintypes._COORD


class WinStyle(object):
    NORMAL              = 0x00  # dim text, dim background  # noqa E221
    BRIGHT              = 0x08  # bright text, dim background  # noqa E221
    BRIGHT_BACKGROUND   = 0x80  # dim text, bright background  # noqa E221


if PLATFORM == 'win32':
    class ConsoleScreenBufferInfo(Structure):
        """struct in wincon.h."""
        _fields_ = [
            ('dwSize', COORD),
            ('dwCursorPosition', COORD),
            ('wAttributes', wintypes.WORD),
            ('srWindow', wintypes.SMALL_RECT),
            ('dwMaximumWindowSize', COORD),
        ]

        def __str__(self) -> str:
            return '(%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)' % (
                self.dwSize.Y, self.dwSize.X,
                self.dwCursorPosition.Y, self.dwCursorPosition.X,
                self.wAttributes,
                self.srWindow.Top, self.srWindow.Left, self.srWindow.Bottom, self.srWindow.Right,
                self.dwMaximumWindowSize.Y, self.dwMaximumWindowSize.X
            )

    def get_console_screen_buffer_info() -> ConsoleScreenBufferInfo:
        _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo  # noqa N806
        _GetConsoleScreenBufferInfo.argtypes = [
            wintypes.HANDLE,
            POINTER(ConsoleScreenBufferInfo),
        ]
        _GetConsoleScreenBufferInfo.restype = wintypes.BOOL

        csbi = ConsoleScreenBufferInfo()
        _GetConsoleScreenBufferInfo(_stdout_handle, byref(csbi))
        return csbi

    def get_win_default_attributes() -> dict[str, int]:
        _default = get_console_screen_buffer_info().wAttributes
        # print(_default)
        win_default_attributes = {
                'attr': _default,
                'fore': _default & 7,
                'back': (_default >> 4) & 7,
                'style': _default & (WinStyle.BRIGHT | WinStyle.BRIGHT_BACKGROUND)
                }
        return win_default_attributes

    WIN_DEFAULT_ATTRIBUTES = get_win_default_attributes()


def _pr(cstr: str, force_linux: bool = False) -> None:
    clst = cstr.split('^')
    color = 20
    for cstr in clst:
        match = re.search(r'\D', cstr)
        if match is not None:
            dglen = match.start()
            if dglen:
                color = int(cstr[:dglen])
            text = cstr[dglen:]
        else:
            text = cstr
        text = text.replace('\u0456', 'i')
        if text[:1] == '_':
            text = text[1:]
        text = _set_color(color, force_linux) + text
        # sys.stdout.write(text)
        print(text, end='')  # noqa: T201
        sys.stdout.flush()


def _restore_colors(end: str = '') -> None:
    # sys.stdout.write(_set_color(20) + '')
    print(_set_color(20) + '', end=end)  # noqa: T201
    sys.stdout.flush()


def cprint(cstr: str, end: str = '\n', force_linux: bool = False) -> None:
    _pr(cstr, force_linux=force_linux)
    _restore_colors(end=end)


def colors_win() -> dict[int, str]:
    return {
            0 : 'чёрный',  # noqa: E203
            1 : 'синий',  # noqa: E203
            2 : 'зелёный',  # noqa: E203
            3 : 'голубой',  # noqa: E203
            4 : 'красный',  # noqa: E203
            5 : 'фиолетовый',  # noqa: E203
            6 : 'жёлтый',  # noqa: E203
            7 : 'серый',  # noqa: E203

            8 : 'тёмно-серый',  # noqa: E203
            9 : 'светло-синий',  # noqa: E203
            10: 'светло-зелёный',
            11: 'светло-голубой',
            12: 'светло-красный',
            13: 'светло-фиолетовый (пурпурный)',
            14: 'светло-жёлтый',
            15: 'белый',
            }


def colors_win2linux() -> dict[int, int]:
    return {
            0 : 30,  # noqa: E203
            1 : 34,  # noqa: E203
            2 : 32,  # noqa: E203
            3 : 36,  # noqa: E203
            4 : 31,  # noqa: E203
            5 : 35,  # noqa: E203
            6 : 33,  # noqa: E203
            7 : 37,  # noqa: E203

            8 : 90,  # noqa: E203
            9 : 94,  # noqa: E203
            10: 92,
            11: 96,
            12: 91,
            13: 95,
            14: 93,
            15: 97,

            20: 0,
            }


def _dafault_color(force_linux: bool) -> int:
    # цвет по умолчанию: 20
    # для windows это 1?, для linux - сброс
    def_color = 1
    if 'linux' in PLATFORM:
        def_color = 0
    elif force_linux:
        def_color = 20
    elif PLATFORM == 'win32':
        def_color = WIN_DEFAULT_ATTRIBUTES['fore']
    return def_color


def _set_color(color: int, force_linux: bool = False) -> str:
    if color == 20:
        color = _dafault_color(force_linux)
    prefix_color = ''
    if ('linux' in PLATFORM) or force_linux:
        prefix_color = '\033[%(col_linux)sm' % {'col_linux': colors_win2linux()[color]}
    elif PLATFORM == 'win32':
        _SetConsoleTextAttribute(_stdout_handle, color | WIN_DEFAULT_ATTRIBUTES['back'] * 16)  # 0x0070
    return prefix_color


# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    from author_ship import authorship
    from console import init_console
    _width = 120
    _hight = 50
    init_console(width=_width, hight=_hight)

    __author__ = 'master by Vint'
    __title__ = '--- colorprint ---'
    __version__ = '4.1.2'
    __copyright__ = 'Copyright 2024 (c)  bitbucket.org/Vintets'
    authorship(__author__, __title__, __version__, __copyright__, width=_width)

    print(WIN_DEFAULT_ATTRIBUTES)  # noqa: T201
    for col in range(16):
        color_win = {
                'color': col,
                'name': colors_win()[col]
                }
        cprint('%(color)dЦвет %(color)d\t %(name)s' % color_win)

    print('\nПримеры')  # noqa: T201
    cprint('20######### Идем к другу ^14_%s ^8_%d/%d ^20_на ^3_%s ^20_#########' % (12345, 5, 3000, 'main'))
    cprint('13Завершили обход всех ^12_НОВЫХ ^13_друзей')

    cprint('Обрабатываем файл ^5_XXX ^13_YYY')
    cprint('Обрабатываем файл ^5_XXX ^13_YYY ^14_ZZZ', end='')
    cprint('4 конец')

    # input('\n---------------   END   ---------------')

# ==================================================================================================
