import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

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
        raise SystemError(f'Ошибка отправки сообщения: {error}')


def get_api_answer(current_timestamp):
    """GET-запрос к API Я.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as error:
        raise SystemError(
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
    elif 'homeworks' not in response:
        raise KeyError('Список работ не доступен')

    homeworks = response['homeworks']

    if homeworks is None:
        raise IndexError('Данные отсутствуют.')
    elif not isinstance(homeworks, list):
        raise TypeError('Некорректный тип данных.')
    return homeworks


def parse_status(homework):
    """Проверка статуса последней работы."""
    if 'homework_name' and 'status' not in homework:
        raise KeyError('Отсутствую данные последней работы')

    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(f'Неизвестный статус: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info('Бот запущен.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_err_msg = ''
    env_var = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }

    for key, token in env_var.items():
        if len(token) == 0:
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {key}.'
            )
            raise SystemExit('Программа принудительно остановлена.')
        else:
            logger.info(f'{key} найден, продолжаем.')

    while check_tokens() is True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if len(homework) > 0:
                for status in homework:
                    if status not in HOMEWORK_VERDICTS:
                        logger.error(f'{status} - неизвестный статус.')
                    else:
                        logger.info('Получен статус последней работы.')
                    message = parse_status(status)
                    send_message(bot, message)
                    logger.info('Сообщение успешно отправлено.')
            else:
                logger.debug('В ответе отсутствуют новые статусы.')
        except SystemError as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message != last_err_msg:
                send_message(bot, message)
                logger.info('Сообщение с ошибкой отправлено.')
                last_err_msg = message
        finally:
            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
