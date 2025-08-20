import logging
import configparser
import sys
from packages import CONFIG


@staticmethod
def read_ini(key, val) -> str:
    """Читает настройки из .ini"""
    config = configparser.ConfigParser() # Создаём объект ConfigParser
    config.read(CONFIG, encoding='utf-8')
    try:
        token = config[key][val]
        logging.info(f'Использован {key} {token}')
        return token
    except:
        logging.error(f'Ошибка чтения файла!')
        sys.exit()