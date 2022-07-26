# homework_bot
Telegram бот для проверки статуса домашней работы на Yandex Практикум
## Установка:
```
git clone https://github.com/gazkhul/homework_bot.git
```
```
cd homework_bot && python3 -m venv venv
```
```
source venv/bin/activate
```
```
python3 -m pip install -U pip && pip install -r requirements.txt
```
## Запуск:
```
python homework.py
```
## Docker:
```
docker run -d -e PRACTICUM_TOKEN='<token>' \
            -e TELEGRAM_TOKEN='<token>' \
            -e TELEGRAM_CHAT_ID='<token>' \
            gazkhul/homework-bot
```