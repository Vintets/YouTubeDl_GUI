
# Проект YouTubeDl_GUI

GUI-враппер для консольной утилиты youtube-dl обновлён для yt-dlp v.2023.2.17

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

> Требуется Python 3.9.7+

Установка зависимостей:
```sh
pip3 install -r requirements.txt
```
включает:
> pip3 install yt-dlp==2023.2.17

> pip3 install pyperclip

> pip3 install loguru

+ ffmpeg-master-latest-win64-gpl_fix



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

```cmd
\venv\Scripts\activate.bat
python3 YouTubeDl_GUI.py
```

через виртуальное окружение
```cmd
venv\Scripts\pythonw.exe YouTubeDl_GUI.py
```

## Скриншоты

ver 1.5.3
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2023-02-28_17-24-24_v1.5.3_screenshot_3.png)

clear open
![Скриншот работы скрипта](https://github.com/Vintets/YouTubeDl_GUI/raw/master/screenshots/2023-02-28_17-13-39_v1.5.3_screenshot_4.png)


<!--
## Структура скрипта
-->

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


<!-- 
> Примичание: ...
-->
