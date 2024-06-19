import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Tempinbox_me(_WaitForMail):
    """An API Wrapper around the https://temp-inbox.me website"""

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

        # -1 requests
        r = self._session.get("https://temp-inbox.me/")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        domains = soup.find("select", {"name": "selected_domain"})
        self.valid_domains = [domain["value"] for domain in domains.find_all("option")]

        self._token = soup.find("meta", {"name": "csrf-token"})["content"]

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.valid_domains)

        r = self._session.post("https://temp-inbox.me/create/inbox", data={
            "_token": self._token,
            "userName": self.name,
            "selected_domain": self.domain,
            "email": self.email
        })
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://temp-inbox.me/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domains = soup.find("select", {"name": "selected_domain"})
            
            return [domain["value"] for domain in domains.find_all("option")]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://temp-inbox.me/getemails")
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from_email"],
                "time": email["received_at"],
                "subject": email["email_Subject"],
                "content": email.get("htmlBody", email.get("textBody"))
            } for email in r.json()]
                                                    