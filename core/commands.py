import threading

from core.cprint_linux import cprint
from core.dlp import YoutubeDlExternal
from core.validators import validate_link_format, Validator


class Commands:
    def __init__(self, validator: Validator, gui) -> None:
        self.validator = validator
        self.gui = gui

    def get_valid_link(self):
        if self.validator.validate_link(self.gui.inserted_link.get()):
            return self.validator.verified_link
        return ''

    def get_valid_video_format(self):
        return self.validator.validate_video_format(self.gui.inserted_format.get().strip())

    @validate_link_format
    def list_all_available_formats(self):
        threading.Thread(target=YoutubeDlExternal().listformats,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def out_title(self):
        threading.Thread(target=YoutubeDlExternal().out_title,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def out_info(self):
        threading.Thread(target=YoutubeDlExternal().out_info,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_1080mp4(self):
        threading.Thread(target=YoutubeDlExternal().format1080mp4,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_1080(self):
        threading.Thread(target=YoutubeDlExternal().format1080,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_best(self):
        threading.Thread(target=YoutubeDlExternal().format_best,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_best_progressive(self):
        threading.Thread(target=YoutubeDlExternal().format_best_progressive,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_mp3(self):
        threading.Thread(target=YoutubeDlExternal().format_mp3,
                         kwargs={'link': self.get_valid_link()}).start()

    @validate_link_format
    def download_custom(self):
        valid_format = self.get_valid_video_format()
        if valid_format:
            YoutubeDlExternal().set_formats(valid_format)
            threading.Thread(target=YoutubeDlExternal().format_custom,
                             kwargs={'link': self.get_valid_link()}).start()
        else:
            cprint(f'4Форматы заданы неверно! Введите id формата или idVideo+idAudio, например 137+140')
