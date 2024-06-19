import requests
from bs4 import BeautifulSoup

from .._constructors import _Generatoremail_etc

class Tempm_com(_Generatoremail_etc):
    """An API Wrapper around the https://tempm.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. There is no validation for the domain\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://tempm.com", name=name, domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list.\nThis is not a complete list but a random selection.
        """

        r = requests.get("https://tempm.com/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("div", {"class": "e7m tt-suggestion"})]