import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _Livewire2, GLOBAL_UA

class Tenminuteemails_com(_Livewire2):
    """An API Wrapper around the https://www.10minuteemails.com/ website. From experience very fast."""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        
        super().__init__(
            urls={
                "base": "https://www.10minuteemails.com",
                "mailbox": "https://www.10minuteemails.com/mailbox/",
                "app": "https://www.10minuteemails.com/livewire/message/frontend.app",
                "actions": "https://www.10minuteemails.com/livewire/message/frontend.actions"
            },
            order=-1, name=name, domain=domain, exclude=exclude
            )


    @staticmethod
    def get_valid_domains() -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get("https://www.10minuteemails.com/", headers={"User-Agent": GLOBAL_UA})

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: true" in tag.get("x-data", "") and ( "wire:initial-data" in tag.attrs ))["wire:initial-data"])

            return data["serverMemo"]["data"]["domains"]
