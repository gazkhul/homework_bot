class SendMessageError(Exception):
    """Проблема с отправкой сообщения."""

    pass


class HTTPError(Exception):
    """Неверный ответ сервера."""

    pass
