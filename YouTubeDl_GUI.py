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
import sys
import json  # noqa: F401
import string
import time
import threading
import re
import functools
import subprocess
from tkinter import Tk, Frame, Label, StringVar, Toplevel, BooleanVar
from tkinter import OptionMenu, GROOVE  # noqa: F401
from tkinter import DISABLED, LEFT, SOLID
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Entry, Button, Combobox, Checkbutton
# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL, FileDownloader
from yt_dlp.utils import DownloadError, ExtractorError
import pyperclip
from configs import config
from accessory import authorship, clear_consol, cprint, check_version, logger

cprint = functools.partial(cprint, force_linux=config.COLOR_TK_CONSOLE)


__version_info__ = ('0', '3', '5')
__version__ = '.'.join(__version_info__)
__author__ = 'master by Vint'
__title__ = '--- YouTubeDl_GUI ---'
__copyright__ = 'Copyright 2022 (c)  bitbucket.org/Vintets'


def validate_link_format(func):
    def wrapper(self, *args, **kwargs):
        if not self.get_valid_id_link():
            print('Формат ссылки неправильный!')
            return
        try:
            func(self, *args, **kwargs)
        except (DownloadError, ExtractorError):
            print('Не удаётся загрузить ресурс по ссылке!')
    return wrapper


class MyLogger():
    def trace(self, msg):
        print(f'tr**{msg}')

    def debug(self, msg):
        print(f'++{msg}')

    def info(self, msg):
        print(f'inf**{msg}')

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def listformats(video_link):
    ydl_opts = {
        'writethumbnail': True,
        'listformats': True,
        # 'forcetitle': True,
        # 'force-ipv4': True,
        'extractaudio': True,
        'noplaylist': True,
        'http_chunk_size': 2097152,
        # 'max_downloads': 1,
        # 'progress_hooks': [youtubeDlHook],
        'format': 'bestaudio/best',  # webm
        # 'ignoreerrors': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        # 'outtmpl': yt_song_structure['playlist_path'] + '/' + yt_song_structure['title'] + '.%(ext)s',
        'outtmpl': f'{config.PATH_SAVE}%(title)s-%(id)s.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_link])


def _prepare_multiline_status_color_tk(self, lines=1):
    """Path FileDownloader._prepare_multiline_status for all color output"""
    from yt_dlp.minicurses import (
        BreaklineStatusPrinter,
        MultilineLogger,
        MultilinePrinter,
        QuietMultilinePrinter,
    )
    if self.params.get('noprogress'):
        self._multiline = QuietMultilinePrinter()
    elif self.ydl.params.get('logger'):
        self._multiline = MultilineLogger(self.ydl.params['logger'], lines)
    elif self.params.get('progress_with_newline'):
        self._multiline = BreaklineStatusPrinter(self.ydl._out_files.out, lines)
    else:
        self._multiline = MultilinePrinter(self.ydl._out_files.out, lines, not self.params.get('quiet'))
    self._multiline.allow_colors = True and not self.params.get('no_color')


class YoutubeDLColorTk(YoutubeDL):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._allow_colors.out = True

        # патч вывода цветной статистики во время загрузки
        FileDownloader._prepare_multiline_status = _prepare_multiline_status_color_tk

    # def _format_out(self, *args, **kwargs):
        # return self._format_text(self._out_files.out, True, *args, **kwargs)

    pass


class YoutubeDlExternal:
    instance = None
    youtube_dl = None
    bitrate_mp3 = None
    writethumbnail = False
    out_format = config.MERGE_OUTPUT_FORMAT

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if config.COLOR_TK_CONSOLE:
            self.youtube_dl = YoutubeDLColorTk
        else:
            self.youtube_dl = YoutubeDL
        self.filename_sample = '%(title)s-%(id)s.%(ext)s'

    def external_list_all_available_formats_(self, link=None):
        if link:
            ytdl = f'yt-dlp.exe -F {link}'
            # subprocess.call(ytdl, shell=True)
            subprocess.check_call(ytdl, shell=False)

    def get_listformats_dict(self, link=None):
        ydl_opts = {}
        with self.youtube_dl(ydl_opts) as ydl:
            info_obj = ydl.extract_info(link, download=False)

            # ℹ️ ydl.sanitize_info makes the info json-serializable
            info = ydl.sanitize_info(info_obj)
            # print(json.dumps(info_json))
        return info

    def out_title(self, link=None):
        ydl_opts = {
            'forcetitle': True,
            'skip_download': True,
            'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def out_info(self, link=None):
        info = self.get_listformats_dict(link=link)
        id_ = info['id']
        title = info['title']
        duration = info['duration']
        # duration_string = info['duration_string']
        format_id = info['format_id']
        length = divmod(duration, 60)

        print('Свединия о видео:')
        cprint(f'20    id: ^5_{id_}', force_linux=config.COLOR_TK_CONSOLE)
        cprint(f'20    Название:    ^5_{title}', force_linux=config.COLOR_TK_CONSOLE)
        cprint(f'20    Длительность ^5_{length[0]}:{length[1]} ({duration}s)', force_linux=config.COLOR_TK_CONSOLE)
        cprint(f'20    Наилучшие форматы по умолчанию: ^5_{format_id}', force_linux=config.COLOR_TK_CONSOLE)

    def listformats(self, link=None):
        ydl_opts = {
            'forcetitle': True,
            'listformats': True,
            # 'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def format1080mp4(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            # 'forcetitle': True,
            'format': 'bestvideo[ext=mp4][height<=?1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def format1080(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            # 'forcetitle': True,
            'format': 'bestvideo[height<=?1080]+bestaudio/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        if self.out_format:
            ydl_opts['merge_output_format'] = self.out_format
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def format_best(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            # 'forcetitle': True,
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        if self.out_format:
            ydl_opts['merge_output_format'] = self.out_format
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def format_best_progressive(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            # 'forcetitle': True,
            'format': 'best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def format_mp3(self, link=None):
        print(f'Загрузка аудио дорожки и конвертация в mp3 с битрейтом {self.bitrate_mp3} kbps')
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'forcetitle': True,
            'format': 'm4a/bestaudio/best',  # bestaudio/best
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.bitrate_mp3,
            }],
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    def set_bitrate_mp3(self, bitrate_mp3, log=True):
        self.bitrate_mp3 = bitrate_mp3[:-5]
        if log:
            print(f'Выбран битрейт mp3: {self.bitrate_mp3}')

    def set_writethumbnail(self, value):
        self.writethumbnail = value
        message = 'включена' if self.writethumbnail else 'выключена'
        print(f'Загрузка картинки превью - {message}')


class TextRedirector():
    def __init__(self, widget, tag='stdout'):
        self.widget = widget
        self.tag = tag
        self.pattern = re.compile(r'\033\[(\d;)*\d+m')

    def write(self, text):
        if text == '':
            return
        self.widget.configure(state='normal')  # сделать поле редактируемым
        if text.startswith('\r'):
            self.delete_last_line()

        if text.startswith('ERROR:'):
            text = f'\033[31mERROR:\033[0m{text[6:]}'

        text = self.translate_ru(text)

        color_lines = self.split_text_by_color(text)
        for line in color_lines:
            tag = self.tag
            m = self.pattern.match(line)
            if m:
                tag = m.group()[2:-1]
                if tag.find(';') != -1:
                    tag = tag.split(';')[1]

                # замена синего на голубой
                tag = '36' if tag == '34' else tag

                line = line[m.end():]
            self.widget.insert('end', line, (tag,))
        # self.widget.insert('end', text, (tag,))
        self.widget.see('end')  # scroll to end
        self.widget.configure(state='disabled')  # сделать поле доступным только для чтения

    def split_text_by_color(self, text):
        delim = '\033'
        lines = [f'{delim}{line}' for line in text.split(delim) if line]
        if not text.startswith(delim):
            lines[0] = lines[0][1:]
        # sys.__stdout__.write(f'{lines}')
        return lines

    def delete_last_line(self):
        # self.widget.delete('end-1c linestart', 'end-1c')
        self.widget.delete('end-1 lines', 'end-1c')

    def flush(self):  # needed for file like object
        # sys.__stdout__.flush()
        pass

    def translate_ru(self, text):
        for en, ru in config.EN_RU.items():
            if text.find(en) != -1:
                text = text.replace(en, ru)
        return text


class MainGUI(Tk):
    def __init__(self):
        self.valid_characters_id = string.ascii_letters + string.digits + '-_'

        Tk.__init__(self)
        self.title(f'YouTubeDl_GUI v{__version__}')
        self.geometry('+490+150')

        self.create_link_frame()
        self.create_buttons_frame()
        self.create_consol_frame()

        self.test = False

        # bg='wheat1', fg='red'
        # 'tomato', 'blue4', 'orange red', 'dodger blue', 'yellow2', 'yellow3', 'dodger bluedeep sky blue'
        # 'snow', 'snow3','ivory2'

        self.buffer_insert()
        self.redirect_logging()
        # cprint('9YouTubeDl_GUI запущен!', force_linux=config.COLOR_TK_CONSOLE)
        self.tick()

    def create_link_frame(self):
        """Блок ссылки"""

        link_block = Frame(self)  # bd=5, bg='ivory2'
        # link_block.pack(side='top', fill='x')
        link_block.grid(row=0, column=0, padx=5, pady=5)

        self.inserted_link = StringVar()
        self.label_err_link = Label(link_block, text='Введите ссылку на видео или id',
                                    bd=2, padx=12, pady=3, fg='black', bg='SystemButtonFace',
                                    font=('Arial', 8, 'bold'))
        self.label_err_link.pack()
        self.field_link = Entry(link_block, width=75, font=('consolas', '10', 'normal'), textvariable=self.inserted_link)
        self.field_link.pack(side='left', padx=3)

        button_enter = Button(link_block, text='Вставить', command=self.buffer2entry)
        button_enter.pack(side='left', padx=3)
        Tooltip(button_enter,
                text='Вставить из буфера обмена',
                wraplength=250)

        self.button_out_info = Button(link_block, text='i', state=DISABLED, width=3, command=self.out_info)
        self.button_out_info.pack(side='right', padx=3)
        Tooltip(self.button_out_info,
                text='Показать информацию по видео',
                wraplength=250)

    def create_buttons_frame(self):
        """Блок основных кнопок"""

        widget_control = Frame(self)
        widget_control.grid(row=1, column=0, padx=3, pady=5, sticky='WE')
        self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        widget_control.columnconfigure((0, 1), weight=1)
        widget_control.columnconfigure((2, 3, 4, 5), weight=1)
        # widget_control.rowconfigure((0, 1, 2), weight=1)

        self.create_widget_all_formats(frame=widget_control)
        self.create_widgets_download(frame=widget_control)
        self.create_widgets_config(frame=widget_control)
        self.create_widgets_control_console(frame=widget_control)
        self.redirect_stdout_elements(frame=widget_control, show=False)

    def create_widget_all_formats(self, frame):
        self.button_list_all_formats = Button(frame, text='Вывести список всех доступных форматов',
                                               state=DISABLED,
                                               command=self.list_all_available_formats)
        self.button_list_all_formats.grid(row=0, column=1, columnspan=4, padx=5, pady=3, sticky='WE')

    def create_widgets_download(self, frame):
        label_download = Label(frame, text='Скачать:')
        label_download.grid(row=1, column=0, padx=5, pady=5, sticky='E')

        self.button_format_mp3 = Button(frame, text='mp3', state=DISABLED,
                                        command=self.download_mp3)
        self.button_format_mp3.grid(row=1, column=1, padx=5, sticky='WE')

        self.button_format_1080mp4 = Button(frame, text='Видео mp4 <=1080p', state=DISABLED,
                                            command=self.download_1080mp4)  # font=('Arial', 8, 'bold')
        self.button_format_1080mp4.grid(row=1, column=2, padx=5, sticky='WE')
        Tooltip(self.button_format_1080mp4,
                text='Формат mp4\nЛучшее качество\nРазрешение до 1080p\nСборка: быстро',
                wraplength=250)

        self.button_format_1080 = Button(frame, text='Видео <=1080p', state=DISABLED,
                                         command=self.download_1080)
        self.button_format_1080.grid(row=1, column=3, padx=5, sticky='WE')
        Tooltip(self.button_format_1080,
                text='Формат любой\nЛучшее качество\nРазрешение до 1080p\nСборка: медленно',
                wraplength=250)

        self.button_format_best = Button(frame, text='Видео наилучшее', state=DISABLED,
                                         command=self.download_best)
        self.button_format_best.grid(row=1, column=4, padx=5, sticky='WE')
        Tooltip(self.button_format_best,
                text='Формат любой\nЛучшее качество\nРазрешение максимальное\nСборка: медленно',
                wraplength=250)

        self.button_format_best_progressive = Button(frame, text='Видео без кодирования',
                                                     state=DISABLED,
                                                     command=self.download_best_progressive)
        self.button_format_best_progressive.grid(row=1, column=5, padx=5, sticky='W')
        Tooltip(self.button_format_best_progressive,
                text='Видео в наилучшем качестве без перекодирования! (progressive).\nСразу video+audio формат\nСборка: нет',
                wraplength=250)

    def create_widgets_config(self, frame):
        bitrate = ['96 kbps', '128 kbps', '160 kbps', '192 kbps', '224 kbps', '256 kbps', '320 kbps']
        self.bitrate_mp3 = Combobox(frame, values=bitrate, width=12, state='readonly')
        self.bitrate_mp3.grid(row=2, column=1, padx=5, sticky='WE')
        self.bitrate_mp3.current(3)  # 192 kbps
        self.bitrate_mp3.bind('<<ComboboxSelected>>', self.set_bitrate_mp3)
        self.set_bitrate_mp3(None, log=False)
        Tooltip(self.bitrate_mp3,
                text='Выбрать битрейт mp3',
                wraplength=250)

        self.preview = BooleanVar()
        self.preview.set(1)
        c1 = Checkbutton(frame, text='Картинка превью',
                         variable=self.preview,
                         onvalue=1, offvalue=0,
                         command=self.set_writethumbnail
                         )
        c1.grid(row=2, column=2, padx=3, sticky='W')
        self.set_writethumbnail()
        Tooltip(c1,
                text='Сохранять превью изображение',
                wraplength=250)

    def create_widgets_control_console(self, frame):
        button_clear_console = Button(frame, text='Очистить', command=self.clear_console)
        button_clear_console.grid(row=2, column=5, padx=48, pady=3, sticky='ES')
        Tooltip(button_clear_console,
                text='Очистить консоль',
                wraplength=250)

        # print('↡', '⇊', '▼', '↓', '⇓', '⇩')
        button_clear_console = Button(frame, text='▼', width=3, command=self.clear_console)
        button_clear_console.grid(row=2, column=5, padx=16, pady=3, sticky='ES')

    def redirect_stdout_elements(self, frame, show=True):
        label_redirect = Label(frame, text='Redirect console:')  # relief=GROOVE
        self.button_redirect = Button(frame, text='to widget', command=self.redirect_logging)
        self.button_redirect_reset = Button(frame, text='reset', command=self.reset_logging)

        print_stdout_button = Button(frame, text='Print to stdout', command=self.print_stdout)
        print_stderr_button = Button(frame, text='Print to stderr', command=self.print_stderr)

        if show:
            label_redirect.grid(row=3, column=0, padx=5, pady=5, sticky='W')
            self.button_redirect.grid(row=3, column=1, padx=5, sticky='WE')
            self.button_redirect_reset.grid(row=3, column=2, padx=5, sticky='WE')
            print_stdout_button.grid(row=3, column=3, padx=5, pady=3, sticky='ES')
            print_stderr_button.grid(row=3, column=4, padx=5, pady=3, sticky='WS')

    def create_consol_frame(self):
        """Блок виджета консоли"""

        widget_consol = Frame(self)
        widget_consol.grid(row=2, column=0, padx=3, pady=3)
        self.columnconfigure(0, weight=1)
        # self.rowconfigure(2, weight=1)
        widget_consol.columnconfigure(0, weight=1)
        widget_consol.rowconfigure(0, weight=1)

        self.log_widget = ScrolledText(widget_consol, state='disabled', wrap='word',
                                       height=48, width=130, bg='#cccccc', fg='#000080',
                                       font=('consolas', '8', 'normal'))
        # self.log_widget.pack(side='top', fill='both', expand=True)
        self.log_widget.grid(row=0, column=0, columnspan=6, sticky='ES')
        self.create_tags()

    def buffer2entry(self):
        text = pyperclip.paste()
        self.field_link.delete(0, 'end')
        self.field_link.insert(0, text)

    def create_tags(self):
        self.log_widget.tag_configure('stderr', foreground='#b22222')
        self.log_widget.tag_configure('0', foreground='#000080')  # restore

        self.log_widget.tag_configure('30', foreground='#000000')  # black
        self.log_widget.tag_configure('31', foreground='#C50F1F')  # red
        self.log_widget.tag_configure('32', foreground='#13A10E')  # green
        self.log_widget.tag_configure('33', foreground='#C19C00')  # yellow
        self.log_widget.tag_configure('34', foreground='#000080')  # blue
        self.log_widget.tag_configure('35', foreground='#881798')  # purple
        self.log_widget.tag_configure('36', foreground='#3A96DD')  # cyan
        self.log_widget.tag_configure('37', foreground='#CCCCCC')  # grey

        # Замена под серую консоль. Меняем серый, на тёмно-серый
        self.log_widget.tag_configure('37', foreground='#767676')  # dark_grey

        self.log_widget.tag_configure('90', foreground='#767676')  # dark_grey
        self.log_widget.tag_configure('91', foreground='#E74856')  # light_red
        self.log_widget.tag_configure('92', foreground='#16C60C')  # light_green
        self.log_widget.tag_configure('93', foreground='#F9F1A5')  # light_yellow
        self.log_widget.tag_configure('94', foreground='#3B78FF')  # light_blue
        self.log_widget.tag_configure('95', foreground='#B4009E')  # light_purple
        self.log_widget.tag_configure('96', foreground='#61D6D6')  # light_cyan
        self.log_widget.tag_configure('97', foreground='#FFFFFF')  # white

    def reset_logging(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.button_redirect.config(state='normal')
        self.button_redirect_reset.config(state='disabled')

    def redirect_logging(self):
        sys.stdout = TextRedirector(self.log_widget, 'stdout')
        # sys.stderr = TextRedirector(self.log_widget, 'stderr')
        self.button_redirect.config(state='disabled')
        self.button_redirect_reset.config(state='normal')

    def clear_console(self):
        self.log_widget.configure(state='normal')
        self.log_widget.delete('1.0', 'end')
        self.log_widget.configure(state='disabled')

    def get_input_link_or_default(self, default_link=''):
        input_link = self.inserted_link.get()
        link = f'Введённая ссылка: {input_link}' if input_link else default_link
        return link

    def print_stdout(self):
        '''Illustrate that using 'print' writes to stdout'''
        # print('\r***\033[36mhttp\033[0m---\033[35m0123456789\033[0m---')
        link = self.get_input_link_or_default('This is stdout 0123456789')
        print(f'\033[36m{link}\033[0m' + '---\033[35m0123456789\033[0m---')
        # cprint('9YouTubeDl_GUI запущен!', force_linux=config.COLOR_TK_CONSOLE)
        # print('Конец')
        # self.log_widget.tag_add('32', '1.2', '1.5')
        # write_string('\033[36m---0123456789---\033[0m')
        # write_string('---0123456789---')
        pass

    def print_stderr(self):
        '''Illustrate that we can write directly to stderr'''
        text = self.get_input_link_or_default('This is stderr 0123456789')
        sys.stderr.write(f'{text}\n')

    def validate_link(self, link):
        if not link:
            return(link)
        link = link.split('&')[0]
        if link.startswith(r'https://'):
            link = link.replace(r'https://', '')
        if link.startswith(r'www.youtube.com/watch?v='):
            link = link.replace(r'www.youtube.com/watch?v=', '')
        if link.startswith(r'youtu.be/'):
            link = link.replace(r'youtu.be/', '')
        filter_link = ''.join(list(filter(lambda x: x in self.valid_characters_id, link)))
        if len(filter_link) == 11 and filter_link == link:
            return filter_link
        return False

    def buffer_insert(self):
        self.insert_link2field(self.validate_link(pyperclip.paste()))

    def insert_link2field(self, link):
        if link:
            self.inserted_link.set(f'https://youtu.be/{link}')

    def get_valid_id_link(self):
        return self.validate_link(self.inserted_link.get())

    def tick(self):
        input_link = self.inserted_link.get()
        list_disable = (
                        self.button_out_info,
                        self.button_list_all_formats,
                        self.button_format_1080mp4,
                        self.button_format_1080,
                        self.button_format_best,
                        self.button_format_best_progressive,
                        self.button_format_mp3
                        )
        if not input_link:
            self.label_err_link.configure(text='Введите ссылку на видео или id', bg='SystemButtonFace', fg='black')
            for widget in list_disable:
                widget.config(state='disabled')
        else:
            valid_id_link = self.get_valid_id_link()
            if valid_id_link:
                self.label_err_link.config(text=f'Правильный формат ссылки.  id = {valid_id_link}',
                                           bg='SystemButtonFace', fg='green')
                for widget in list_disable:
                    widget.config(state='normal')
                self.remove_excess_parameters(input_link)
            else:
                self.label_err_link.config(text='Неверный формат ссылки', bg='yellow1', fg='red')
                for widget in list_disable:
                    widget.config(state='disabled')

        # calls every 500 milliseconds to update
        self.field_link.after(700, self.tick)

    def remove_excess_parameters(self, original_link):
        link = original_link.split('&')[0]
        if link != original_link:
            self.inserted_link.set(link)

    @validate_link_format
    def list_all_available_formats(self):
        # YoutubeDlExternal().listformats(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().listformats,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def out_title(self):
        # YoutubeDlExternal().out_title(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().out_title,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def out_info(self):
        # YoutubeDlExternal().out_info(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().out_info,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def download_1080mp4(self):
        # YoutubeDlExternal().format1080mp4(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().format1080mp4,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def download_1080(self):
        # YoutubeDlExternal().format1080(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().format1080,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def download_best(self):
        # YoutubeDlExternal().format_best(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().format_best,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def download_best_progressive(self):
        # YoutubeDlExternal().format_best_progressive(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().format_best_progressive,
                         kwargs={'link': self.get_valid_id_link()}).start()

    @validate_link_format
    def download_mp3(self):
        # YoutubeDlExternal().format_mp3(link=self.get_valid_id_link())
        threading.Thread(target=YoutubeDlExternal().format_mp3,
                         kwargs={'link': self.get_valid_id_link()}).start()

    def set_bitrate_mp3(self, event, log=True):
        # print(f'{event = }')
        YoutubeDlExternal().set_bitrate_mp3(self.bitrate_mp3.get(), log=log)

    def set_writethumbnail(self):
        YoutubeDlExternal().set_writethumbnail(self.preview.get())


class Tooltip:
    '''
    It creates a tooltip for a given widget as the mouse goes on it.

    see:

    http://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216

    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.

    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.

      Tested on Ubuntu 16.04/16.10, running Python 3.5.2

    TODO: themes styles support
    '''

    def __init__(self, widget,  # noqa: CFQ002
                 *,
                 bg='#FFFFEA',
                 pad=(5, 3, 5, 3),
                 text='widget info',
                 waittime=400,
                 wraplength=250):

        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def on_enter(self, event=None):
        self.schedule()

    def on_leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    @staticmethod
    def tip_pos_calculator(widget, label,
                           *,
                           tip_delta=(10, 5), pad=(5, 3, 5, 3)):

        w = widget

        s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

        width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                         pad[1] + label.winfo_reqheight() + pad[3])

        mouse_x, mouse_y = w.winfo_pointerxy()

        x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
        x2, y2 = x1 + width, y1 + height

        x_delta = x2 - s_width
        if x_delta < 0:
            x_delta = 0
        y_delta = y2 - s_height
        if y_delta < 0:
            y_delta = 0

        offscreen = (x_delta, y_delta) != (0, 0)

        if offscreen:

            if x_delta:
                x1 = mouse_x - tip_delta[0] - width

            if y_delta:
                y1 = mouse_y - tip_delta[1] - height

        offscreen_again = y1 < 0  # out on the top

        if offscreen_again:
            # No further checks will be done.

            # TIP:
            # A further mod might automagically augment the
            # wraplength when the tooltip is too high to be
            # kept inside the screen.
            y1 = 0

        return x1, y1

    def show(self):
        bg = self.bg
        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = Frame(self.tw,
                    background=bg,
                    borderwidth=0)
        label = Label(win,
                      text=self.text,
                      justify=LEFT,
                      background=bg,
                      relief=SOLID,
                      borderwidth=0,
                      wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]),
                   pady=(pad[1], pad[3]),
                   sticky='NSEW')
        win.grid()

        x, y = self.tip_pos_calculator(widget, label)
        self.tw.wm_geometry('+%d+%d' % (x, y))

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None


def exit_from_program(code: int = 0) -> None:
    time.sleep(1)
    try:
        sys.exit(code)
    except SystemExit:
        os._exit(code)


def main(video_link):
    app = MainGUI()

    # authorship(__author__, __title__, __version__, __copyright__)
    app.mainloop()


if __name__ == '__main__':
    _width = 130
    _hight = 54
    if sys.platform == 'win32':
        os.system('color 71')
        # os.system('mode con cols=%d lines=%d' % (_width, _hight))
    else:
        os.system('setterm -background white -foreground white -store')
        # ubuntu terminal
        os.system('setterm -term linux -back $blue -fore white -clear')
    cur_script = __file__
    PATH_SCRIPT = os.path.abspath(os.path.dirname(cur_script))
    os.chdir(PATH_SCRIPT)
    clear_consol()
    check_version()

    authorship(__author__, __title__, __version__, __copyright__)  # width=_width

    video_link = 'https://www.youtube.com/watch?v=XifjHd4ySWA'
    video_link = 'https://youtu.be/XifjHd4ySWA'
    video_link = 'https://youtu.be/b_tdqGM4_sE'

    try:
        main(video_link)
    except Exception as e:
        logger.critical(e)  # __str__()
        if config.EXCEPTION_TRACE:
            raise e
        exit_from_program(code=1)
    except KeyboardInterrupt:
        logger.info('Отмена. Скрипт остановлен.')
        exit_from_program(code=0)
