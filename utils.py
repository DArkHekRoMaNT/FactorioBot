import socket
import webbrowser
from typing import AnyStr
from urllib import parse


def first(iterable, *, matcher=None, default=None):
    if matcher:
        for item in iterable:
            if matcher(item):
                return item
    else:
        for item in iterable:
            return item

    return default


def request_oauth_login_by_user(url: str) -> dict[AnyStr, list[AnyStr]]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 8000))
        s.listen()
        webbrowser.open(url)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024).decode()
            qs = data.split()[1][2:]
            conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\nYou may close this window.'.encode())
            return parse.parse_qs(qs)
