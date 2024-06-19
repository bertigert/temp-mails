import json
import random
from string import ascii_lowercase, digits

from bs4 import BeautifulSoup
import requests

from .._constructors import _Livewire
class Tmail_io(_Livewire):
    """An API Wrapper around the https://tmail.io/ website. Also supports gmail.com emails. Take a look at the website if you don't know what this means."""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox (max 10/time period)\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
            Note:\n
            If the domain is chosen to be gmail, a random gmail is chosen from the list of the website. The name provided as an argument is used as an suffix for a random gmail (eg. randomemail+yourname@gmail.com)
        """
        if domain == "gmail.com":
            self.valid_gmails = self.get_valid_domains(gmail=True)
            
            super().__init__(
                urls={
                    "base": "https://tmail.io/",
                    "app": "https://tmail.io/livewire/message/gmail.app",
                    "actions": "https://tmail.io/livewire/message/gmail.actions"
                },
                order=-1, name=f"{random.choice(self.valid_gmails).removesuffix('@gmail.com')}+{name or "".join(random.choices(ascii_lowercase+digits, k=6))}", domain="gmail.com", exclude=[]
            )
            
        else:
            super().__init__(
                urls={
                    "base": "https://tmail.io/",
                    "app": "https://tmail.io/livewire/message/frontend.app",
                    "actions": "https://tmail.io/livewire/message/frontend.actions"
                },
                order=-1, name=name, domain=domain, exclude=exclude
            )

    @staticmethod
    def get_valid_domains(gmail: bool=False) -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure\n
            Args:\n
            gmail - if gmail is true, valid emails for the gmail.com domain are returned (e.g. [mail1@gmail.com, mail2@gmail.com]), else normal valid domains are returned.
        """
        if gmail:
            r = requests.get("https://tmail.io/temporary-disposable-gmail")
        else:
            r = requests.get("https://tmail.io/")
       
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: false" in tag.get("x-data", ""))["wire:initial-data"])

            return data["serverMemo"]["data"]["accounts"] if gmail else data["serverMemo"]["data"]["domains"]
