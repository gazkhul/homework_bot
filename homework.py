import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='homework_bot.log',
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('homework_bot.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения с текущим статусом проверки."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info('Сообщение успешно отправлено.')
    except Exception as error:
        logging.error(f'Сообщение не отправлено {error}')


def get_api_answer(current_timestamp):
    """GET-запрос к API Я.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logger.error(f'API не доступен: {error}')
    else:
        if answer.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            raise Exception(f'HTTP ERROR: {answer.status_code}')
    return answer.json()


def check_response(response):
    """Проверяет ответ API на корректность и возвращает список работ."""
    if type(response) is not dict:
        raise TypeError('Некорректный ответ')
    try:
        homeworks = response['homeworks']
    except Exception as error:
        logger.error(f'Список работ не доступен: {error}')
    return homeworks


def parse_status(homework):
    """Проверка статуса проверки последней работы."""
    try:
        homework_name = homework['homeworks'][0]['lesson_name']
    except Exception as error:
        logger.error(f'Список работ не доступен: {error}')

    try:
        homework_status = homework['homeworks'][0]['status']
    except Exception as error:
        logger.error(f'Статус работы не доступен: {error}')

    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f'Неизвестный статус: {homework_status}')

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    env_variables = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    for var, val in env_variables.items():
        if val is None:
            logging.critical(f'Отсутствует переменная {var}')
            return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
