from bs4 import BeautifulSoup
import requests

from .._constructors import _Wptempmail_etc

class Tmpmail_co(_Wptempmail_etc):
    """An API Wrapper around the https://tmpmail.co/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://tmpmail.co", name=name, domain=domain, exclude=exclude)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service
        """

        return ["tmpmail.co"]

