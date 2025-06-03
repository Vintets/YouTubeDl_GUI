import re
import sys
from tkinter import BooleanVar, Frame, Label, StringVar, Tk
from tkinter import DISABLED
# from tkinter import GROOVE, OptionMenu
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Button, Checkbutton, Combobox, Entry

from accessory import authorship
from configs import config
from core.commands import Commands
from core.dlp import YoutubeDlExternal
from core.tooltip import Tooltip
from core.validators import Validator
from PIL import Image
import pyperclip
import pystray


class TextRedirector:
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
            pattern = self.pattern.match(line)
            if pattern:
                tag = pattern.group()[2:-1]
                if tag.find(';') != -1:
                    tag = tag.split(';')[1]

                # замена синего на голубой
                tag = '36' if tag == '34' else tag

                line = line[pattern.end():]
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
    def __init__(self, author: str, title: str, version: str, copyright_: str) -> None:
        self.icon = 'YT-DLP.ico'
        self.validator = Validator()
        self.commands = Commands(validator=self.validator, gui=self)
        self.height_console = 48

        Tk.__init__(self)
        self.title(f'YouTubeDl_GUI v{version}')
        self.geometry('+490+150')
        self.iconbitmap(self.icon)

        self.create_buttons_frame()
        self.create_consol_frame()

        self.test = False

        # bg='wheat1', fg='red'
        # 'tomato', 'blue4', 'orange red', 'dodger blue', 'yellow2', 'yellow3', 'dodger bluedeep sky blue'
        # 'snow', 'snow3','ivory2'

        self.bind('<Control-Key>', self.copy_paste)

        self.buffer_insert()
        self.redirect_logging()
        authorship(author, title, version, copyright_, width=130)
        # cprint('9YouTubeDl_GUI запущен!')
        self.after(1500, self.clear_console)
        self.tick()

    def create_buttons_frame(self):
        """Блок основных кнопок"""

        widget_control = Frame(self)
        widget_control.grid(row=1, column=0, padx=3, pady=5, sticky='WE')
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(1, weight=1)
        widget_control.columnconfigure((0, 1), weight=1)
        widget_control.columnconfigure((2, 3, 4, 5), weight=1)
        # widget_control.rowconfigure((0, 1, 2), weight=1)

        self.create_link_frame(frame=widget_control, row=0)
        self.create_widget_all_formats(frame=widget_control, row=2)
        self.create_widget_out_info(frame=widget_control, row=2)
        self.create_widgets_download(frame=widget_control, row=3)
        self.create_widgets_config(frame=widget_control, row=4)
        self.create_widgets_control_console(frame=widget_control, row=4)
        self.redirect_stdout_elements(frame=widget_control, show=False)

    def create_link_frame(self, frame, row):
        """Блок ссылки"""

        self.videohosting(frame=frame, row=row + 1)

        self.inserted_link = StringVar()
        self.label_err_link = Label(frame, text='Введите ссылку на видео или id',
                                    bd=2, fg='black', bg='SystemButtonFace',
                                    font=('Arial', 8, 'bold'))
        self.label_err_link.grid(row=row, column=1, columnspan=4, padx=5, sticky='WE')

        button_trey = Button(frame, text='↓', width=2, command=self.to_tray)
        button_trey.grid(row=row, column=5, padx=16, pady=3, sticky='ES')
        Tooltip(button_trey,
                text='Свернуть в трей',
                wraplength=100)

        self.field_link = Entry(frame, font=('consolas', '10', 'normal'),
                                textvariable=self.inserted_link)
        self.field_link.grid(row=row + 1, column=1, columnspan=4, padx=5, sticky='WE')

        button_enter = Button(frame, text='Вставить', command=self.buffer2entry)
        button_enter.grid(row=row + 1, column=5, padx=5, pady=3, sticky='WS')
        Tooltip(button_enter,
                text='Вставить из буфера обмена',
                wraplength=250)

    def videohosting(self, frame, row):
        self.vhost = self.validator.get_vhost()
        self.label_vhost = Label(frame, textvariable=self.vhost)
        self.label_vhost.grid(row=row, column=0, padx=5, sticky='E')
        Tooltip(self.label_vhost,
                text=f'Видеохостинг',
                wraplength=150)

    def to_tray(self):
        """создать пиктограмму в трее и скрыть основное окно"""
        img = Image.open(self.icon, formats=('ICO',))
        img.size = (16, 16)
        ic = pystray.Icon('test_icon', img, menu=pystray.Menu(
                    pystray.MenuItem('Развернуть', action=self.menu_show_window, default=True),
                    pystray.MenuItem('Выход', action=self.menu_quit_window)
                    ))
        self.withdraw()
        ic.run()

    def menu_show_window(self, icon, item):
        icon.visible = False
        icon.stop()
        self.deiconify()
        self.lift()

    def menu_quit_window(self, icon, item):
        icon.stop()
        self.destroy()

    def create_widget_all_formats(self, frame, row):
        self.button_list_all_formats = Button(frame, text='Вывести список всех доступных форматов',
                                              state=DISABLED,
                                              command=self.commands.list_all_available_formats)
        self.button_list_all_formats.grid(row=row, column=1, columnspan=4, padx=5, pady=3, sticky='WE')

    def create_widget_out_info(self, frame, row):
        self.button_out_info = Button(frame, text='i', state=DISABLED, width=3, command=self.commands.out_info)
        self.button_out_info.grid(row=row, column=5, padx=5, sticky='W')
        Tooltip(self.button_out_info,
                text='Показать информацию по видео',
                wraplength=250)

    def create_widgets_download(self, frame, row):
        label_download = Label(frame, text='Скачать:')
        label_download.grid(row=row, column=0, padx=5, pady=5, sticky='E')

        self.button_format_mp3 = Button(frame, text='mp3', state=DISABLED,
                                        command=self.commands.download_mp3)
        self.button_format_mp3.grid(row=row, column=1, padx=5, sticky='WE')

        self.button_format_1080mp4 = Button(frame, text='Видео mp4 <=1080p', state=DISABLED,
                                            command=self.commands.download_1080mp4)  # font=('Arial', 8, 'bold')
        self.button_format_1080mp4.grid(row=row, column=2, padx=5, sticky='WE')
        Tooltip(self.button_format_1080mp4,
                text='Формат mp4\nЛучшее качество\nРазрешение до 1080p\nСборка: быстро',
                wraplength=250)

        self.button_format_1080 = Button(frame, text='Видео <=1080p', state=DISABLED,
                                         command=self.commands.download_1080)
        self.button_format_1080.grid(row=row, column=3, padx=5, sticky='WE')
        Tooltip(self.button_format_1080,
                text='Формат любой\nЛучшее качество\nРазрешение до 1080p\nСборка: медленно',
                wraplength=250)

        self.button_format_best = Button(frame, text='Видео наилучшее', state=DISABLED,
                                         command=self.commands.download_best)
        self.button_format_best.grid(row=row, column=4, padx=5, sticky='WE')
        Tooltip(self.button_format_best,
                text='Формат любой\nЛучшее качество\nРазрешение максимальное\nСборка: медленно',
                wraplength=250)

        self.button_format_best_progressive = Button(frame, text='Видео без кодирования',
                                                     state=DISABLED,
                                                     command=self.commands.download_best_progressive)
        self.button_format_best_progressive.grid(row=row, column=5, padx=5, sticky='W')
        Tooltip(self.button_format_best_progressive,
                text='Видео в наилучшем качестве (до 720p) без перекодирования! (progressive).\nСразу video+audio формат\nСборка: нет',
                wraplength=250)

    def create_widgets_config(self, frame, row):
        bitrate = ['96 kbps', '128 kbps', '160 kbps', '192 kbps', '224 kbps', '256 kbps', '320 kbps']
        self.bitrate_mp3 = Combobox(frame, values=bitrate, width=12, state='readonly')
        self.bitrate_mp3.grid(row=row, column=1, padx=5, sticky='WE')
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
        c1.grid(row=row, column=2, padx=3, sticky='W')
        self.set_writethumbnail()
        Tooltip(c1,
                text='Сохранять превью изображение',
                wraplength=250)

        self.button_format_custom = Button(frame, text='Указанные:', state=DISABLED,
                                           command=self.commands.download_custom)
        self.button_format_custom.grid(row=row, column=3, padx=5, sticky='WE')
        Tooltip(self.button_format_custom,
                text='Скачать произвольно заданные форматы video+audio',
                wraplength=250)

        self.inserted_format = StringVar()
        self.field_formats = Entry(frame, width=16, font=('consolas', '10', 'normal'),
                                   textvariable=self.inserted_format)
        self.field_formats.grid(row=row, column=4, padx=5, sticky='WE')
        Tooltip(self.field_formats,
                text='Указать id формата или idVideo+idAudio',
                wraplength=250)

    def create_widgets_control_console(self, frame, row):
        button_clear_console = Button(frame, text='Очистить', command=self.clear_console)
        button_clear_console.grid(row=row, column=5, padx=48, pady=3, sticky='ES')
        Tooltip(button_clear_console,
                text='Очистить консоль',
                wraplength=250)

        self.button_toggle_console = Button(frame, text='▲', width=3, command=self.toggle_size_consol)
        self.button_toggle_console.grid(row=row, column=5, padx=16, pady=3, sticky='ES')

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

    def toggle_size_consol(self):
        if self.height_console == 48:
            self.height_console = 24
            self.button_toggle_console.config(text='▼')
            # print('↡', '⇊', '▼', '↓', '⇓', '⇩')
        else:
            self.height_console = 48
            self.button_toggle_console.config(text='▲')
            # print('🠕', '⇈', '▲', '↑', '⇑', '⇧')
        self.log_widget.config(height=self.height_console)

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
        """Illustrate that using 'print' writes to stdout"""
        # print('\r***\033[36mhttp\033[0m---\033[35m0123456789\033[0m---')
        link = self.get_input_link_or_default('This is stdout 0123456789')
        print(f'\033[36m{link}\033[0m' + '---\033[35m0123456789\033[0m---')
        # cprint('9YouTubeDl_GUI запущен!')
        # print('Конец')
        # self.log_widget.tag_add('32', '1.2', '1.5')
        # write_string('\033[36m---0123456789---\033[0m')
        # write_string('---0123456789---')
        pass

    def print_stderr(self):
        """Illustrate that we can write directly to stderr"""
        text = self.get_input_link_or_default('This is stderr 0123456789')
        sys.stderr.write(f'{text}\n')

    def buffer_insert(self):
        if self.validator.validate_link(pyperclip.paste()):
            self.insert_link2field()

    def insert_link2field(self):
        self.inserted_link.set(self.validator.verified_link)

    def tick(self):
        input_link = self.inserted_link.get()
        list_disable = (
                        self.button_out_info,
                        self.button_list_all_formats,
                        self.button_format_1080mp4,
                        self.button_format_1080,
                        self.button_format_best,
                        self.button_format_best_progressive,
                        self.button_format_mp3,
                        self.button_format_custom,
                        )
        if not input_link:
            self.label_err_link.configure(text='Введите ссылку на видео или id', bg='SystemButtonFace', fg='black')
            buttons_state = 'disabled'
            self.validator.set_empty_link()
        else:
            valid_link = self.commands.get_valid_link()
            if valid_link:
                self.label_err_link.config(text=f'Правильный формат ссылки.  id = {self.validator.video_id}',
                                           bg='SystemButtonFace', fg='green')
                buttons_state = 'normal'
                if valid_link != input_link:
                    self.inserted_link.set(valid_link)
            else:
                self.label_err_link.config(text='Неверный формат ссылки', bg='yellow1', fg='red')
                buttons_state = 'disabled'

        self.label_vhost.config(text=self.validator.get_vhost())
        for widget in list_disable:
            widget.config(state=buttons_state)
        # calls every 700 milliseconds to update
        self.field_link.after(700, self.tick)

    def set_bitrate_mp3(self, event, log=True):
        # print(f'{event = }')
        YoutubeDlExternal().set_bitrate_mp3(self.bitrate_mp3.get(), log=log)

    def set_writethumbnail(self):
        YoutubeDlExternal().set_writethumbnail(self.preview.get())

    @staticmethod
    def copy_paste(event):
        if event.keycode == 86 and event.keysym != 'v':
            event.widget.event_generate('<<Paste>>')
        elif event.keycode == 67 and event.keysym != 'c':
            event.widget.event_generate('<<Copy>>')
        elif event.keycode == 88 and event.keysym != 'x':
            event.widget.event_generate('<<Cut>>')
