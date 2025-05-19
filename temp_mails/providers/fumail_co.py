import requests
from bs4 import BeautifulSoup

from .._constructors import _Eztempmail_etc, GLOBAL_UA

class Fumail_co(_Eztempmail_etc):
    """An API Wrapper around the https://www.fumail.co/ website. Has potential to fail, work with retries in get_inbox"""

    _BASE_URL = "https://www.fumail.co"

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. There is no validation for the domain\n
        exclude - a list of domain to exclude from the random selection\n
        NOTE: Custom domains/names may be broken
        """
        super().__init__(base_url=self._BASE_URL, name=name, domain=domain, exclude=exclude)

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        r = requests.get(cls._BASE_URL, headers={"User-Agent": GLOBAL_UA})
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain["value"] for domain in soup.find("select", {"id": "name_domain"}).find("optgroup").find_all("option")]