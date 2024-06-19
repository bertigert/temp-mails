from bs4 import BeautifulSoup
import requests

from .._constructors import _Fake_trash_mail

class Emailtenmin_com(_Fake_trash_mail):
    """An API Wrapper around the https://email10min.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://email10min.com", name=name, domain=domain, exclude=exclude)

    
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://email10min.com/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find("select", {"name": "domain"}).findChildren("option")]
        