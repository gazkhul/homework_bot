import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
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
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except exceptions.SendMessageError as error:
        raise SystemError(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """GET-запрос к API Я.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        raise SystemError(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {answer.status_code}'
            f'ERROR: {error}'
        )
    if answer.status_code != HTTPStatus.OK:
        raise exceptions.HTTPError(f'HTTP ERROR: {answer.status_code}')
    return answer.json()


def check_response(response):
    """Проверяет ответ API на корректность и возвращает список работ."""
    if not isinstance(response, dict):
        raise TypeError('Некорректный тип данных.')
    try:
        homeworks = response['homeworks']
        logger.info('Список работ доступен.')
    except KeyError as error:
        logger.error(f'Список работ не доступен: {error}')
    if homeworks is None:
        logger.error('Данные отсутствуют.')
        raise IndexError('Данные отсутствуют.')
    elif type(homeworks) is not list:
        logger.error('Некорректный тип данных.')
        raise TypeError('Некорректный тип данных.')
    return homeworks


def parse_status(homework):
    """Проверка статуса последней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        logger.debug('Неизвестный статус.')
        raise KeyError(f'Неизвестный статус: {homework_status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    logger.info('Бот запущен.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_err_msg = ''

    if not check_tokens():
        logger.critical('Бот остановлен.')
        raise SystemExit('Выход из программы.')
    logger.info('Токен найден.')

    while check_tokens() is True:
        try:
            response = get_api_answer(current_timestamp)
            logger.info('Получен ответ от сервера.')
            homework = check_response(response)
            for status in homework:
                message = parse_status(status)
                send_message(bot, message)
                logger.info('Сообщение успешно отправлено.')
        except SystemError as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message != last_err_msg:
                send_message(bot, message)
                logger.info('Сообщение с ошибкой отправлено.')
                last_err_msg = message
            else:
                logger.error(message)
        finally:
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
