from yt_dlp.utils import DownloadError


def download_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except DownloadError as e:
            print(e)
    return wrapper
