import functools

from accessory import cprint

from configs import config


cprint = functools.partial(cprint, force_linux=config.COLOR_TK_CONSOLE)
