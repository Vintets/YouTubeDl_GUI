
# Проект YouTubeDl_GUI

GUI-враппер для консольной утилиты youtube-dl обновлён для yt-dlp v.2022.11.11

---------------------------------------------------------


Скачивание файлов с youtube c практичными настройками

Сам форк форк yt-dlp
https://github.com/yt-dlp/yt-dlp


## Зависимости

> Требуется Python 3.9.7+

Установка зависимостей:
```sh
pip3 install -r requirements.txt
```
включает:
> pip3 install yt-dlp==2022.11.11
> pip3 install pyperclip
> pip3 install loguru

+ ffmpeg-master-latest-win64-gpl_fix



Добавить в Path путь:
D:\YandexDisk\_Python\_Python_Projects\YouTubeDl_GUI
D:\YandexDisk\_Python\_Python_Projects\YouTubeDl_GUI\yt-dlp


> Warning : nsig extraction failed: You may experience throttling for some formats
> Install PhantomJS to workaround the issue. Please download it from
> https://phantomjs.org/download.html

## Конфигурирование

`configs/config.py`

- PATH_SAVE - путь до папки сохранения
- PATH_LOGS - путь до папки логов
- COLOR_TK_CONSOLE - поддержка цветного вывода в консольном виджете tkinter

- EN_RU - словать переведённых фраз для замены
- EXCEPTION_TRACE - трассировать неотловленные ошибки

## Запуск

```cmd
python3 YouTubeDl_GUI.py
```

## Скриншоты

ver 1.0
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2022-10-20_13-52-15_screenshot_1.png)

clear open
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2022-10-21_14-10-10_screenshot_2.png)


## Структура скрипта

____

:copyright: 2022 by Vint

:license:
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

____


> Примичание: ...

