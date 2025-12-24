from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from yt_dlp.utils import DownloadError


Param = ParamSpec('Param')
RetType = TypeVar('RetType')


def download_error(func: Callable[Param, RetType]) -> Any:
    """
    mypy type
    _Wrapped[Param, RetType, Param, RetType]
    """
    @wraps(func)
    def wrapper(self: Any, *args: Param.args, **kwargs: Param.kwargs) -> None:
        try:
            func(self, *args, **kwargs)
        except DownloadError as e:
            print(e)
    return wrapper
