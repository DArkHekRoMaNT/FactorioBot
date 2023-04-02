import logging
import os

import colorlog


def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '{green}{asctime} {log_color}{levelname} {reset}{name}: {white}{message}',
        log_colors={
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        datefmt='%H:%M:%S',
        style='{'
    ))
    return console_handler


def get_file_handler():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = logging.FileHandler('logs/latest.log')
    file_handler.setFormatter(logging.Formatter(
        '{asctime} {levelname} {name}: {message}',
        datefmt='%H:%M:%S',
        style='{'
    ))
    return file_handler


def setup_logger():
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    log.addHandler(get_console_handler())
    log.addHandler(get_file_handler())

    trovo_log = logging.getLogger('trovo')
    trovo_log.setLevel(logging.DEBUG)
