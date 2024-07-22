import logging

from aiogram import Router, types
from aiogram.filters import Command

from bot.exceptions import CurrencyNotFoundException
from bot.services.redis import RedisService

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("exchange"))
async def handle_exchange(message: types.Message):
    redis_service = RedisService()
    try:
        if not message.text:
            raise ValueError
        _, from_currency, to_currency, amount = message.text.split()
        amount = float(amount)

        if from_currency == to_currency:
            await message.reply("Пожалуйста, укажите две разные валюты для обмена.")
            return

        if from_currency == "RUB" or to_currency == "RUB":
            non_rub_currency = to_currency if from_currency == "RUB" else from_currency
            rate = await redis_service.get_currency_rate(non_rub_currency)
            if rate is None:
                raise CurrencyNotFoundException(non_rub_currency)

            if from_currency == "RUB":
                result = amount / rate
                await message.reply(f"{amount} RUB = {result:.2f} {to_currency}")
            else:
                result = amount * rate
                await message.reply(f"{amount} {from_currency} = {result:.2f} RUB")
        else:
            from_rate = await redis_service.get_currency_rate(from_currency)
            to_rate = await redis_service.get_currency_rate(to_currency)
            if from_rate is None or to_rate is None:
                raise CurrencyNotFoundException(f"{from_rate} | {to_rate}")
            result = (amount * from_rate) / to_rate
            await message.reply(
                f"{amount} {from_currency} = {result:.2f} {to_currency}"
            )

    except ValueError:
        await message.reply("Пожалуйста, используйте формат: /exchange USD RUB 10")
    except CurrencyNotFoundException as e:
        await message.reply(f"Произошло ошибка: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса на обмен: {e}")
        await message.reply("Произошла ошибка при обработке вашего запроса.")


@router.message(Command("rates"))
async def handle_rates(message: types.Message):
    redis_service = RedisService()
    currencies = ["USD", "EUR", "GBP", "JPY", "CNY"]
    rates = []
    for currency in currencies:
        rate = await redis_service.get_currency_rate(currency)
        if rate:
            rates.append(f"{currency}: {rate:.4f}")
    if rates:
        await message.reply(
            "Текущие курсы валют (относительно рубля):\n" + "\n".join(rates)
        )
    else:
        await message.reply("Извините, не удалось получить курсы валют.")
