import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _Livewire2

class Burnermailbox_com(_Livewire2):
    """An API Wrapper around the https://burnermailbox.com/ website."""

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
                "base": "https://burnermailbox.com",
                "mailbox": "https://burnermailbox.com/mailbox/",
                "app": "https://burnermailbox.com/livewire/message/frontend.app",
                "actions": "https://burnermailbox.com/livewire/message/frontend.actions"
            },
            order=0, name=name, domain=domain, exclude=exclude
            )


    @staticmethod
    def get_valid_domains() -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get("https://burnermailbox.com/", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"})

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: true" in tag.get("x-data", "") and ( "wire:initial-data" in tag.attrs ))["wire:initial-data"])
            
            return data["serverMemo"]["data"]["domains"]
