from bs4 import BeautifulSoup
import requests

from .._constructors import _Generatoremail_etc

class Mailtemp_com(_Generatoremail_etc):
    """An API Wrapper around the https://mail-temp.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. There is no validation for the domain\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://mail-temp.com", name=name, domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list.\nThis is not a complete list but a random selection.
        """
        r = requests.get("https://mail-temp.com/")
        soup = BeautifulSoup(r.text, "lxml")
        domain_list = soup.find("div", {"class": "e7m tt-suggestions"}).find_all("div", {"class": "e7m tt-suggestion"})
        
        return [domain.p.text for domain in domain_list]