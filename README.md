
# Проект YouTubeDl_GUI

GUI-враппер для консольной утилиты youtube-dl обновлён для yt-dlp v.2026.2.4

<div align="center">
<!-- ![YouTubeDl_GUI](https://github.com/Vintets/YouTubeDl_GUI/raw/master/zYouTubeDl_GUI_development/YT-DLP_128.png)  -->
<a href="#readme" target="_blank">
<img src="https://github.com/Vintets/YouTubeDl_GUI/raw/master/zYouTubeDl_GUI_development/YT-DLP_128.png" height="128"/>
</a>
</div>

---------------------------------------------------------


Скачивание файлов с youtube c практичными настройками

Сам форк yt-dlp
https://github.com/yt-dlp/yt-dlp


## Зависимости

![Python version](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=ffdd54)

> Требуется Python 3.12.0+

Установка зависимостей:
```sh
pip install -r requirements_venv_YTDL312.txt
```
включает:
> pip install loguru

> pip install pillow

> pip install pyperclip

> pip install pystray

> pip install yt-dlp==2026.2.4  [![yt-dlp](https://img.shields.io/badge/>__dlp-yt--dlp-red)](https://github.com/yt-dlp/yt-dlp)

- \+ ffmpeg-master-latest-win64-gpl_fix



Добавить в Path пути:

```
D:\YandexDisk\_Python\_Python_Projects\YouTubeDl_GUI
D:\YandexDisk\_Python\_Python_Projects\YouTubeDl_GUI\yt-dlp
```


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

Обычный через ярлык. Ярлык должен вести на launcher_YTDL.cmd
```cmd
YouTubeDl_GUI
```

```cmd
venv\Scripts\activate.bat
python YouTubeDl_GUI.py
```

через виртуальное окружение
```cmd
venv\Scripts\pythonw.exe YouTubeDl_GUI.py
```

## Скриншоты

ver 2.1.0
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2024-05-08_14-56-08_v2.1.0_screenshot_5.png)

ver 1.5.3
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2023-02-28_17-24-24_v1.5.3_screenshot_3.png)

clear open
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2024-05-08_15-15-51_v2.1.0_screenshot_6.png)


____

:copyright: 2022-2025 by Vint

## License

:license:
/*******************************************************
 * Copyright 2022-2025 Vintets <programmer@vintets.ru> - All Rights Reserved
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
