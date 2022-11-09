# homework_bot
![python](https://img.shields.io/badge/python-3.7-blue) ![docker](https://img.shields.io/badge/docker-20.10.21-blue) [![homework_bot CI/CD](https://github.com/gazkhul/homework_bot/actions/workflows/tests_on_push.yaml/badge.svg?branch=master)](https://github.com/gazkhul/homework_bot/actions/workflows/tests_on_push.yaml)
### О проекте:
Telegram бот для проверки статуса домашней работы на Яндекс Практикум
### Установка:
- Клонировать репозиторий:
```
git clone https://github.com/gazkhul/homework_bot.git
```
- Перейти в директорию с проектом:
```
cd homework_bot && python3 -m venv venv
```
- Активировать виртуальное окружение:
```
source venv/bin/activate
```
- Установить зависимости:
```
python3 -m pip install -U pip && pip install -r requirements.txt
```
- Отредактировать env-файл:

```
nano .env
```

```
# Шаблон env-файла:
PRACTICUM_TOKEN = ''
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = ''
```
### Запуск:
```
python homework.py
```
### Docker:
```
docker run --env-file .env -d gazkhul/homework-bot
```