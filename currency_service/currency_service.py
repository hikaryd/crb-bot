import asyncio
import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime, time, timedelta

import aiohttp
import redis

CB_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_xml(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


def parse_xml(xml_string):
    root = ET.fromstring(xml_string)
    date = root.attrib["Date"]
    currencies = {}
    for valute in root.findall("Valute"):
        char_code = valute.find("CharCode").text
        nominal = int(valute.find("Nominal").text)
        value = float(valute.find("Value").text.replace(",", "."))
        unit_rate = value / nominal
        currencies[char_code] = unit_rate
    return date, currencies


def update_redis(date, currencies):
    pipeline = redis_client.pipeline()
    pipeline.set("last_update", date)
    for char_code, value in currencies.items():
        pipeline.set(f"currency:{char_code}", value)
    pipeline.execute()


async def update_currency_rates():
    try:
        xml_string = await fetch_xml(CB_URL)
        date, currencies = parse_xml(xml_string)
        update_redis(date, currencies)
        logger.info(f"Курсы валют обновлены на дату: {date}")
    except Exception as e:
        logger.error(f"Произошла ошибка при обновлении курсов валют: {e}")


async def main():
    while True:
        now = datetime.now()
        target_time = time(hour=0, minute=5)

        if now.time() >= target_time:
            await update_currency_rates()
            tomorrow = datetime.combine(now.date() + timedelta(days=1), target_time)
            seconds_until_tomorrow = (tomorrow - now).total_seconds()
            await asyncio.sleep(seconds_until_tomorrow)
        else:
            target_datetime = datetime.combine(now.date(), target_time)
            seconds_to_wait = (target_datetime - now).total_seconds()
            await asyncio.sleep(seconds_to_wait)


if __name__ == "__main__":
    asyncio.run(main())
