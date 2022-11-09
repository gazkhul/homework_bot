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

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        raise exceptions.SendMessageError(
            f'Ошибка отправки сообщения: {error}'
        )


def get_api_answer(current_timestamp):
    """GET-запрос к API Я.Практикум."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        raise exceptions.RequestToAPIError(
            f'Сбой в работе программы: Эндпоинт {ENDPOINT} недоступен.'
            f'Код ответа API: {answer.status_code}'
            f'ERROR: {error}'
        )
    if answer.status_code != HTTPStatus.OK:
        raise requests.exceptions.HTTPError(
            f'HTTP ERROR: {answer.status_code}'
        )
    return answer.json()


def check_response(response):
    """Проверяет ответ API на корректность и возвращает список работ."""
    if not isinstance(response, dict):
        raise TypeError('Некорректный тип данных.')

    if 'homeworks' not in response or 'current_date' not in response:
        raise exceptions.KeyNotFoundInResponseError(
            'Список работ или дата недоступны.'
        )

    homeworks = response['homeworks']

    if homeworks is None or not isinstance(homeworks, list):
        raise exceptions.IncorrectTypeError(
            'Некорректный тип данных в списке домашек.'
        )
    return homeworks


def parse_status(homework):
    """Проверка статуса последней работы."""
    if 'homework_name' not in homework or 'status' not in homework:
        raise KeyError(
            'Отсутствует имя или статус в домашней работе.'
        )

    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        raise exceptions.IncorrectStatusError(
            f'Неизвестный статус: {homework_status}'
        )

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    env_var = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]

    for token in env_var:
        if (len(str(token)) == 0) or (token is None):
            return False
    return True


def main():
    """Основная логика работы бота."""
    logger.info('Бот запущен.')

    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения.')
        raise SystemExit('Программа принудительно остановлена.')

    logger.debug('Токен найден, продолжаем.')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_err_msg = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.debug('API Я.Практикум доступен.')
            homeworks = check_response(response)
            logger.debug('Список домашек доступен.')
            if len(homeworks) != 0:
                message = parse_status(homeworks[0])
                logger.debug('Статус домашней работы изменился.')
                send_message(bot, message)
                logger.info('Сообщение успешно отправлено.')
            else:
                logger.debug('Статус последней работы не изменился.')
        except exceptions.MainFunctionError as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message != last_err_msg:
                send_message(bot, message)
                logger.info('Сообщение с ошибкой отправлено.')
                last_err_msg = message
        finally:
            current_timestamp = response['current_date']
            logger.debug(f'Ожидаем {RETRY_TIME} секунд.')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
