class SendMessageError(Exception):
    """Проблема с отправкой сообщения."""

    pass


class EndpointError(Exception):
    """Не получен ответ от сервера."""

    pass


class HTTPError(Exception):
    """Неверный ответ сервера."""

    pass
