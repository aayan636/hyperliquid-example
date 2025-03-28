# Note: Since we did not have access to a Key which had access to the given API, this file always returns no content, so hasn't been tested.

from contexts.base import Context
from constants.constants import SOCIAL_MEDIA_API
from utils import config_reader

import requests

class SocialMediaContext(Context):
    def __init__(self, url: str = SOCIAL_MEDIA_API):
        self.url = url
        self.api_key = config_reader.read_config()["coin_market_cap_api_key"]
        self.trending_data = None

    def fetch_data(self) -> None:
        headers = {
            'Accept': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            self.trending_data = response.json()

    def context_for_llm(self) -> str:
        return f"""
        Relevant News from Social Media
        -------------------------------
        {self.trending_data}
        """
