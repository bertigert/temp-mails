import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Anonymmail_net(_WaitForMail):
    """An API Wrapper around the https://anonymmail.net/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        r = self._session.post("https://anonymmail.net/api/create", data={
            "email": self.email
        })
        if not r.ok or '"success":false' in r.text:
            raise Exception("Failed to create email, status", r.status_code, r.text)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://anonymmail.net/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domains_elem = soup.find("select", {"id": "domainName"}).find_all("option")
            return [domain["value"] for domain in domains_elem]

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post(f"https://anonymmail.net/api/get", data={
            "email": self.email
        })
        
        if r.ok:
            return [{
                "id": email["token"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"],
                "content": email["body"]
            } for email in r.json()[self.email]["emails"]]
                                                    