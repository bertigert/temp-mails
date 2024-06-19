from typing import Literal
import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _Livewire

class Tenminutesemail_net(_Livewire):
    """An API Wrapper around the https://10minutesemail.net/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None, life_time: Literal[5, 10, 15, 20, 30, 60]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
            life_time - time for which the email is avaiable in minutes
        """
        
        super().__init__(
            urls={
                "base": "https://10minutesemail.net/",
                "app": "https://10minutesemail.net/livewire/message/frontend.app",
                "actions": "https://10minutesemail.net/livewire/message/frontend.actions"
            },
            order=0, name=name, domain=domain, exclude=exclude
        )

    @staticmethod
    def get_valid_domains() -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get("https://10minutesemail.net/")
       
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: false" in tag.get("x-data", ""))["wire:initial-data"])

            return data["serverMemo"]["data"]["domains"]
