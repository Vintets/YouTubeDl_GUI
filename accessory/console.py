import os
import sys


def clear_console() -> None:  # очищаем консоль
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


def init_console(width: int = 120, hight: int = 50) -> None:
    if sys.platform == 'win32':
        # os.system('color 71')
        os.system('mode con cols=%d lines=%d' % (width, hight))
        os.system('powershell -command "&{$H=get-host;$W=$H.ui.rawui;$B=$W.buffersize;$B.width=%d;$B.height=%d;$W.buffersize=$B;}"' % (width, 4000))
    else:
        os.system('setterm -background white -foreground white -store')
        # ubuntu terminal
        os.system('setterm -term linux -back $blue -fore white -clear')
    clear_console()
