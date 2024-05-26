import requests

from settings import API_KEY_FOREX
from application.services.cache_service import CacheService


class ApiRateService:
    def __init__(self):
        self.cache = CacheService()

    def _calculate_rate(self, key: str):
        url = f"https://api.polygon.io/v2/aggs/ticker/{key}/prev?adjusted=true&apiKey={API_KEY_FOREX}"
        response = requests.get(url)
        try:
            response.raise_for_status()
            rate = response.json()["results"][0]["c"]
            self.cache.set(key=key, value=str(rate), exp=None)
        except:
            rate = 0.01

        return float(rate)

    def get_rate(self, origin_currency_name: str, destination_currency_name: str):
        if origin_currency_name == destination_currency_name:
            return 1.0
        key = f"C:{origin_currency_name}{destination_currency_name}"
        if self.cache.exists(key):
            rate = self.cache.get(key)
        else:
            rate = self._calculate_rate(key)

        return float(rate)