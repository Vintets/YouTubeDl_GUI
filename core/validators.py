import re
import string
from urllib.parse import ParseResult, parse_qsl, quote, unquote, urldefrag, urlencode, urlparse, urlunparse

from core.dlp import VHost

from yt_dlp.utils import DownloadError, ExtractorError


def validate_link_format(func):
    def wrapper(self, *args, **kwargs):
        if not self.get_valid_link():
            print('Формат ссылки неправильный!')
            return
        try:
            func(self, *args, **kwargs)
        except (DownloadError, ExtractorError):
            print('Не удаётся загрузить ресурс по ссылке!')
    return wrapper


class Validator:
    valid_characters_id_rt = string.ascii_lowercase + string.digits
    valid_characters_id_yt = string.ascii_letters + string.digits + '-_'
    valid_characters_id_vk = string.digits + '-_'
    pattern_formats_yt = re.compile(r'\d{1,3}(\+\d{1,3})?')
    pattern_formats_rt = re.compile(r'^\d{1,4}-[01]$')
    pattern_formats_vk = re.compile(r'^\d{3,4}$')

    def __init__(self) -> None:
        self.vhost = ''
        self.reset_vhost()
        self.original_link = ''
        self.video_id = None
        self.verified_link = ''
        self.video_list = ''

    def exclude_substr(self, full_str: str, substr: str) -> str:
        if full_str.startswith(substr):
            full_str = full_str.replace(substr, '')
        return full_str

    def validate_link(self, original_link: str) -> bool:
        if not original_link:
            self.set_empty_link()
            return False
        self.original_link = urldefrag(original_link.strip()).url
        parsed_link = urlparse(unquote(self.normalize_link(self.original_link)))

        if self.detection_rutube(parsed_link):
            correct = self.validate_rutube_link(parsed_link)
        elif self.detection_vkontakte(parsed_link):
            query_params = self.get_filtered_query_params(parsed_link, allowed_parameters=('z', 'oid', 'id'))
            self.set_video_list('')
            correct = self.validate_vkontakte_link(parsed_link, query_params)
        elif self.detection_youtube(parsed_link):
            query_params = self.get_filtered_query_params(parsed_link, allowed_parameters=('v', 'list'))
            self.set_video_list(query_params.get('list', ''))
            correct = self.validate_youtube_link(parsed_link, query_params)
        elif self.detection_youtube_clear_id(original_link):
            correct = True
            self.vhost = VHost.YT.value
            self.video_id = original_link
            self.verified_link = original_link
        else:
            correct = False
            self.set_empty_link()
        return correct

    def normalize_link(self, link: str) -> str:
        link = self.exclude_substr(link, r'https://')
        link = self.exclude_substr(link, r'http://')
        return f'https://{link}'

    def detection_rutube(self, link: ParseResult) -> bool:
        return link.netloc == 'rutube.ru'

    def detection_vkontakte(self, link: ParseResult) -> bool:
        return link.netloc == 'vk.com'

    def detection_youtube(self, link: ParseResult) -> bool:
        return link.netloc in ('youtu.be', 'www.youtube.com',)

    def detection_youtube_clear_id(self, original_link: str) -> bool:
        validate_id = self.validate_video_id(original_link, characters=self.valid_characters_id_yt, length=11)
        result = True if validate_id is not None else False
        return result

    def validate_rutube_link(self, link: ParseResult) -> bool:
        str_link = link.path
        str_link = self.exclude_substr(str_link, '/video/')
        str_link = self.exclude_substr(str_link, '/shorts/')
        video_id = str_link.rstrip('/')
        validate_id = self.validate_video_id(video_id, characters=self.valid_characters_id_rt, length=32)
        # print(f'2  {video_id=}')
        # print(f'3  {validate_id=}')
        if validate_id is not None:
            result = True
            self.vhost = VHost.RT.value
            self.video_id = validate_id
            self.verified_link = urlunparse(link._replace(query=''))
        else:
            result = False
            self.set_empty_link()
        return result

    def validate_vkontakte_link(self, link: ParseResult, query_params: dict) -> bool:  # noqa: C901
        __clip = False
        if link.path == '/video_ext.php':
            oid = query_params.get('oid', '')
            id_ = query_params.get('id', '')
            video_id = f'{oid}_{id_}'
        elif link.path.startswith('/video'):
            video_id = self.exclude_substr(link.path, '/video').strip('/')
        elif link.path.startswith('/clip'):
            video_id = self.exclude_substr(link.path, '/clip').strip('/')
            __clip = True
        elif link.path == '/feed':
            video_id = ''
            query = query_params.get('z', '')
            for par in query.split('/'):
                if par.startswith('video'):
                    video_id = par[5:]
                    break
        else:
            video_id = ''

        validate_id = self.validate_video_id_vk(video_id, characters=self.valid_characters_id_vk)
        # print(f'6  {video_id=}')
        # print(f'7  {validate_id=}')
        if validate_id is not None:
            result = True
            self.vhost = VHost.VK.value
            self.video_id = validate_id
            if __clip:
                self.verified_link = urlunparse(link._replace(query=''))
            else:
                self.verified_link = f'https://vk.com/video{video_id}'
        else:
            result = False
            self.set_empty_link()
        return result

    def validate_youtube_link(self, link: ParseResult, query_params: dict) -> bool:
        if link.netloc == 'youtu.be':
            video_id = link.path.strip('/')
        elif link.path.startswith('/shorts/'):
            video_id = self.exclude_substr(link.path, '/shorts/').strip('/')
        elif link.path.startswith('/watch'):
            video_id = query_params.get('v', '')
        else:
            video_id = ''

        validate_id = self.validate_video_id(video_id, characters=self.valid_characters_id_yt, length=11)
        # print(f'4  {video_id=}')
        # print(f'5  {validate_id=}')
        if validate_id is not None:
            result = True
            self.vhost = VHost.YT.value
            self.video_id = validate_id
            new_query = urlencode(query_params, quote_via=quote)
            self.verified_link = urlunparse(link._replace(query=new_query))
        else:
            result = False
            self.set_empty_link()
        return result

    def validate_video_id(self, video_id: str, characters: str, length: int = 0) -> (str | None):
        if len(video_id) != length:
            return None
        filter_link = ''.join(list(filter(lambda x: x in characters, video_id)))
        if len(filter_link) == length and filter_link == video_id:
            return filter_link
        return None

    def validate_video_id_vk(self, video_id: str, characters: str) -> (str | None):
        # -215588860_456239958
        filter_link = ''.join(list(filter(lambda x: x in characters, video_id)))
        if len(filter_link) < 12 and filter_link != video_id:
            return None
        id_component = video_id.split('_')
        if id_component[0].startswith('-'):
            id_component[0] = id_component[0][1:]
        if (len(id_component) == 2 and
                id_component[0].isdigit() and
                id_component[1].isdigit() and
                len(id_component[1]) == 9):
            return video_id
        return None

    def validate_video_format(self, video_format: str) -> (str | None):
        if not video_format:
            return video_format

        video_format = video_format.replace(' ', '')
        if self.vhost == VHost.RT.value:
            video_format = self.validate_rutube_vkontakte_video_format(
                                                                       video_format,
                                                                       prefixes=('default-', 'm3u8-'),
                                                                       pattern=self.pattern_formats_rt
                                                                       )
        elif self.vhost == VHost.VK.value:
            video_format = self.validate_rutube_vkontakte_video_format(
                                                                       video_format,
                                                                       prefixes=('hls-', 'url'),
                                                                       pattern=self.pattern_formats_vk
                                                                       )
        elif self.vhost == VHost.YT.value:
            video_format = self.validate_youtube_video_format(video_format)
        else:
            video_format = None
        return video_format

    def validate_rutube_vkontakte_video_format(self,
                                               video_format: str,
                                               prefixes: tuple[str],
                                               pattern: re.Pattern
                                               ) -> (str | None):
        analized_format = video_format
        if not analized_format.startswith(prefixes):
            return None
        analized_format = self.exclude_substr(analized_format, prefixes[0])
        analized_format = self.exclude_substr(analized_format, prefixes[1])
        re_format = pattern.match(analized_format)
        if re_format is None or re_format.group() != analized_format:
            return None
        return video_format

    def validate_youtube_video_format(self, video_format: str) -> (str | None):
        re_format = self.pattern_formats_yt.match(video_format)
        if re_format is None or re_format.group() != video_format:
            return None

        # исключаем начало id с 0
        for _f in re_format.group().split('+'):
            if _f.startswith('0'):
                video_format = None
                break
        return video_format

    def get_filtered_query_params(self, parsed_link: ParseResult, allowed_parameters: tuple = tuple()) -> dict:
        query_params = dict(parse_qsl(parsed_link.query))
        filtered_query_params = {key: query_params[key] for key in allowed_parameters if query_params.get(key, False)}
        return filtered_query_params

    def get_vhost(self) -> VHost:
        return self.vhost

    def set_video_list(self, video_list: str) -> None:
        self.video_list = video_list

    def reset_vhost(self) -> None:
        self.vhost = VHost.NONE.value

    def set_empty_link(self) -> None:
        self.reset_vhost()
        self.original_link = ''
        self.video_id = None
        self.verified_link = ''
        self.video_list = ''
