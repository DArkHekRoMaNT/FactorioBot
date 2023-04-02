import json
import logging
import os
import zipfile
from datetime import datetime
from json import JSONDecodeError

_log = logging.getLogger(__name__)


def save(filename: str, data: dict):
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(f'data/{filename}.json', 'w+', encoding='utf-8') as f:
            f.write(json.dumps(data, default=dict, indent=True))
    except Exception as e:
        _log.critical(e)


def load(filename: str) -> dict:
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(f'data/{filename}.json', 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except FileNotFoundError as e:
        _log.warning(f'File not found {e.filename}')
    except JSONDecodeError as e:
        _log.error(e)
    except Exception as e:
        _log.critical(e)
    return {}


def backup():
    backup_path = f'backups/backup_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.zip'
    if not os.path.exists('backups'):
        os.makedirs('backups')
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('data/'):
            for file in files:
                filepath = os.path.join(root, file)
                zf.write(filepath)
    _log.info(f'Backup file {backup_path} created')
