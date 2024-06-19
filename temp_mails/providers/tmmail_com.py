from bs4 import BeautifulSoup
import requests

from .._constructors import _Tmmail_etc

class Tmmail_com(_Tmmail_etc):
    """An API Wrapper around the https://tm-mail.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url="https://tm-mail.com", name=name, domain=domain, exclude=exclude)

        
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://tm-mail.com/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_options = soup.find_all("option")
            
            return [option["value"] for option in email_options]
        