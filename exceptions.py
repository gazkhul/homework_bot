class SendMessageError(Exception):
    """Проблема с отправкой сообщения."""

    pass


class RequestToAPIError(Exception):
    """Ошибка запроса к API."""

    pass


class IncorrectStatusError(Exception):
    """Передан неизвестный статус."""

    pass


class MainFunctionError(Exception):
    """Что-то пошло не так."""

    pass


class IncorrectTypeError(Exception):
    """Сломан список домашек."""

    pass


class KeyNotFoundInResponseError(Exception):
    """Отсутствует обязательный ключ."""

    pass
