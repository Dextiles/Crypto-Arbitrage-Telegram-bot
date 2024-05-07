import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_tradable_currencies() -> list:
    data = get_session().get('https://api.coinbase.com/v2/currencies/crypto').json()
    return [currency['code'] for currency in data['data']]

