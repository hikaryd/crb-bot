class BotException(Exception): ...


class CurrencyNotFoundException(BotException):
    def __init__(self, currency: str):
        message = f"Не найден курс для {currency}."
        super().__init__(message)
