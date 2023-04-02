import io
import logging
from tkinter import *


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_stream = io.BytesIO()
handler = logging.StreamHandler(io.TextIOWrapper(log_stream))
handler.setFormatter(logging.Formatter('{asctime} {levelname:<8} {name}: {message}', style='{', datefmt='%H:%M:%S'))
logger.addHandler(handler)

# Создаем окно Tkinter и текстовое поле
root = Tk()
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

text = Text(root, height=20, width=100)
scrollbar.configure(command=text.yview)
text.pack(side=LEFT, expand=YES, fill=BOTH)


def update_text_widget():
    log_stream.seek(0)
    lines = log_stream.readlines()

    for line in lines:
        last_line = int(text.index(END).split(".")[0]) - 1

        line = line.decode(encoding='utf-8')
        text.insert(END, line)

        splited = line.split()
        tpe = splited[1]
        name = splited[2]

        type_color = 'black'
        type_bg_color = 'white'

        match tpe:
            case 'DEBUG':
                type_color = 'black'
            case 'INFO':
                type_color = 'green'
            case 'CRITICAL':
                type_color = 'red'
                type_bg_color = 'black'
            case 'ERROR':
                type_color = 'red'
            case 'WARNING':
                type_color = 'gold'

        text.tag_add('datetime', f'{last_line}.0', f'{last_line}.8')
        text.tag_add('type'+tpe, f'{last_line}.9', f'{last_line}.17')
        text.tag_add('name', f'{last_line}.18', f'{last_line}.{len(name) + 18}')
        text.tag_config('datetime', foreground='green')
        text.tag_config('type'+tpe, foreground=type_color, background=type_bg_color)
        text.tag_config('name', foreground='purple')

    text.yview_moveto(1)

    log_stream.seek(0)
    log_stream.truncate(0)
    root.after(100, update_text_widget)


def spammer():
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.critical('This is a critical message')
    logger.fatal('This is a fatal message')
    logger.error('This is an error message')

    root.after(3000, spammer)


update_text_widget()
spammer()

root.mainloop()
