"""
__author__ = 'master by Vint'
__title__ = '--- Name ---'
__version__ = '0.0.1'
__build__ = 0x000000
__copyright__ = 'Copyright 2025 ©  bitbucket.org/Vintets'
__license__ = ''
author_ship.authorship(__author__, __title__, __version__, __copyright__)
"""


import shutil


def authorship(author: str, title: str, version: str, copyright_: str, width: int = 0) -> None:
    if not width:
        width = shutil.get_terminal_size().columns
    copyright_ = copyright_.center(width, ' ')
    version = f'version {version} {author}'.center(width, ' ')
    name_product = title.center(width, ' ')
    print('{0}{1}{2}{0}'.format('*' * width, copyright_, version))  # noqa: T201
    print('{0}\n'.format(name_product))  # noqa: T201
