from bs4 import BeautifulSoup
import requests

from .._constructors import _Wptempmail_etc

class Schutzmail_de(_Wptempmail_etc):
    """An API Wrapper around the https://schutz-mail.de/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://schutz-mail.de/", name=name, domain=domain, exclude=exclude)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get(f"https://schutz-mail.de/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain["value"] for domain in soup.find("select", {"class": "tm-mailbox-domain-select"}).find_all("option", recursive=False)]

