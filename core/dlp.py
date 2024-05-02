import json  # noqa: F401
import subprocess

from configs import config

from core.cprint_linux import cprint
from core.errors import download_error
from core.logger_ydl import MyLogger
from core.webp2jpeg import image_convert

from yt_dlp import YoutubeDL
from yt_dlp.downloader import FileDownloader


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
    formats = None
    writethumbnail = False
    nocheckcertificate = True
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
        self.filename_sample = '%(title)s_[%(id)s]_f%(format_id)s.%(ext)s'

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
            # print(json.dumps(info))
        return info

    def append_cookies(self, ydl_opts=''):
        cookies = config.COOKIES_YT
        if config.USE_COOKIES and cookies:
            ydl_opts['cookiefile'] = cookies

    def out_title(self, link=None):
        ydl_opts = {
            'forcetitle': True,
            'skip_download': True,
            'logger': MyLogger(),
        }
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    @download_error
    def out_info(self, link=None):
        info = self.get_listformats_dict(link=link)
        id_ = info['id']
        title = info['title']
        duration = info['duration']
        # duration_string = info['duration_string']
        format_id = info['format_id']
        length = divmod(duration, 60)

        print('Свединия о видео:')
        cprint(f'20    id: ^5_{id_}')
        cprint(f'20    Название:    ^5_{title}')
        cprint(f'20    Длительность ^5_{length[0]}:{length[1]} ({duration}s)')
        cprint(f'20    Наилучшие форматы по умолчанию: ^5_{format_id}')

    @download_error
    def listformats(self, link=None):
        ydl_opts = {
            'forcetitle': True,
            'listformats': True,
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])

    @download_error
    def format1080mp4(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            # 'forcetitle': True,
            # [vcodec~="^((he|a)vc|h26[45])"]   # с кодеком h264 или h265
            # [protocol^=http]                  # по прямой ссылке по протоколу HTTP/HTTPS
            'format': '(bestvideo[ext=mp4][height<=?1080]+bestaudio[ext=m4a])[protocol^=http]/best[ext=mp4][protocol^=http]/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    @download_error
    def format1080(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            # 'forcetitle': True,
            'format': 'bestvideo[height<=?1080]+bestaudio/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        if self.out_format:
            ydl_opts['merge_output_format'] = self.out_format
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    @download_error
    def format_best(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            # 'forcetitle': True,
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        if self.out_format:
            ydl_opts['merge_output_format'] = self.out_format
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    @download_error
    def format_best_progressive(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            # 'forcetitle': True,
            'format': 'best',
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    @download_error
    def format_mp3(self, link=None):
        print(f'Загрузка аудио дорожки и конвертация в mp3 с битрейтом {self.bitrate_mp3} kbps')
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            'forcetitle': True,
            'format': 'bestaudio/best[ext=m4a]/best',  # m4a/bestaudio/best
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.bitrate_mp3,
            }],
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    @download_error
    def format_custom(self, link=None):
        ydl_opts = {
            'writethumbnail': self.writethumbnail,
            'nocheckcertificate': self.nocheckcertificate,
            # 'forcetitle': True,
            'format': self.formats,
            'outtmpl': f'{config.PATH_SAVE}{self.filename_sample}',
            # 'logger': MyLogger(),
        }
        self.append_cookies(ydl_opts)
        if self.out_format:
            ydl_opts['merge_output_format'] = self.out_format
        with self.youtube_dl(ydl_opts) as ydl:
            ydl.download([link])
        self.thumbnail_convert(link)

    def set_bitrate_mp3(self, bitrate_mp3, log=True):
        self.bitrate_mp3 = bitrate_mp3[:-5]
        if log:
            print(f'Выбран битрейт mp3: {self.bitrate_mp3}')

    def set_formats(self, formats):
        self.formats = formats
        cprint(f'20Выбраны форматы: ^14_{self.formats}')

    def set_writethumbnail(self, value):
        self.writethumbnail = value
        message = 'включена' if self.writethumbnail else 'выключена'
        print(f'Загрузка картинки превью - {message}')

    def thumbnail_convert(self, link):
        if self.writethumbnail:
            info = self.get_listformats_dict(link=link)
            id_ = info['id']
            title = info['title']
            expected_filename = f'{title}_[{id_}?_f*.webp'
            for expected_file in config.PATH_SAVE_WIN.glob(expected_filename):
                file_out = expected_file.parent / f'{expected_file.stem}.jpg'
                image_convert(expected_file, file_out)
