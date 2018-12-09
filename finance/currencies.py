import urllib
import logging

import requests

from django.conf import settings
from django.utils import timezone

from stats.models import CurrencySummary

logger = logging.getLogger(__file__)


def save_rates(rates, currency):
    CurrencySummary.objects.create(
        base=settings.BASE_CURRENCY,
        currency=currency,
        base_rate=rates[settings.BASE_CURRENCY],
        currency_rate=rates[currency]
    )


def request_rates(currency):
    url = urllib.parse.urljoin(
        settings.CURRENCY_API,
        'latest'
    )
    params = {
        'access_key': settings.CURRENCY_API_KEY,
        'symbols': ",".join([currency, settings.BASE_CURRENCY])
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if data['success']:
        return data['rates']
    else:
        logger.error("Couldn't retrieve currencies for transaction. CHack API reference.")


def get_rates(currency):
    if CurrencySummary.objects.filter(
            date=timezone.now().date(),
            base=settings.BASE_CURRENCY,
            currency=currency).exists():
        summary = CurrencySummary.objects.get(
            date=timezone.now().date(),
            base=settings.BASE_CURRENCY,
            currency=currency)
        return {
            settings.BASE_CURRENCY: summary.base_rate,
            currency: summary.currency_rate
        }
    else:
        rates = request_rates(currency)
        save_rates(rates, currency)
        return rates


def convert_to_base(amount, currency):
    rates = get_rates(currency)
    return amount * rates[settings.BASE_CURRENCY] / rates[currency]


def convert_from_base(amount, currency):
    rates = get_rates(currency)
    return amount * rates[currency] / rates[settings.BASE_CURRENCY]