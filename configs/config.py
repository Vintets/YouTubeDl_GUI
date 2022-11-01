from pathlib import Path


PATH_SAVE = '%HOMEDRIVE%\\%HOMEPATH%\\Desktop\\'
PATH_LOGS = Path('logs')
COLOR_TK_CONSOLE = True

# Контейнеры, которые можно использовать при слиянии, например 'mp4/mkv' (avi, flv, mkv, mov, mp4, webm)
MERGE_OUTPUT_FORMAT = 'mp4/mkv'

CLOSECONSOLE = True
LOGGER_NAME_MODULE = True
EXCEPTION_TRACE = True

EN_RU = {
        'Video unavailable': 'Видео недоступно',
        }

PROXIES = [
        '91.217.42.4:8080',
        '91.217.42.3:8080',
        '91.217.42.64:8080',
        '149.248.58.57:8080',
        '64.154.38.86:8080',
        '199.195.248.24:8080',
        ]
