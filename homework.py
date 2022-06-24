import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
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
        logger.info('Сообщение успешно отправлено.')
    except Exception as error:
        logger.error(f'Сообщение не отправлено {error}')


def get_api_answer(current_timestamp):
    """GET-запрос к API Я.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logger.error(f'API не доступен: {error}')
        raise SystemError(f'API не доступен: {error}')

    if answer.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        logger.error(f'HTTP ERROR: {answer.status_code}')
        raise Exception(f'HTTP ERROR: {answer.status_code}')
    elif answer.status_code != HTTPStatus.OK:
        logger.error(f'HTTP ERROR: {answer.status_code}')
        raise Exception(f'HTTP ERROR: {answer.status_code}')
    return answer.json()


def check_response(response):
    """Проверяет ответ API на корректность и возвращает список работ."""
    if type(response) is not dict:
        logger.error('Некорректный тип данных')
        raise TypeError('Некорректный тип данных')

    try:
        homeworks = response['homeworks']
    except KeyError as error:
        logger.error(f'Список работ не доступен: {error}')

    if homeworks[0] is None:
        logger.error('Данные отсутствуют.')
        raise IndexError('Данные отсутствуют.')
    return homeworks


def parse_status(homework):
    """Проверка статуса проверки последней работы."""
    homework_name = homework[0]['homework_name']
    homework_status = homework[0]['status']

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
            logger.critical(f'Отсутствует переменная {var}')
            return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    if not check_tokens():
        raise SystemExit('Критическая ошибка.')

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            send_message(bot, message)
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
