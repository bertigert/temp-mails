import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _Livewire

class Etempmail_net(_Livewire):
    """An API Wrapper around the https://etempmail.net/ website"""

    _BASE_URL = "https://etempmail.net/"

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
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
                "base": self._BASE_URL,
                "app": self._BASE_URL+"/livewire/message/frontend.app",
                "actions": self._BASE_URL+"/livewire/message/frontend.actions"
            },
            order=-1, name=name, domain=domain, exclude=exclude
        )

    @classmethod
    def get_valid_domains(cls) -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get(cls._BASE_URL+"/10minutemail")
       
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: false" in tag.get("x-data", "") and ( "wire:initial-data" in tag.attrs ))["wire:initial-data"])

            return data["serverMemo"]["data"]["domains"]
