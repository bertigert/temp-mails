from time import time
from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Dismailbox_com(_WaitForMail):
    """An API Wrapper around the https://dismailbox.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.post(f"https://dismailbox.com/messages?{time():.0f}")
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
        if not domain and not name and not exclude:
            self.email = r.json()["mailbox"]
            self.name, self.domain = self.email.split("@", 1)
            return

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        data = {
            "name": self.name,
            "domain": self.domain
        }

        r = self._session.post("https://dismailbox.com/create", data=data)
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://dismailbox.com/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_options = soup.find_all("option")
            
            return [option["value"] for option in email_options]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox including the content
        """
        
        r = self._session.post(f"https://dismailbox.com/messages?{time():.0f}")#, data="token="+self._token)
        if r.ok:
            return [ {
                "id": mail["id"],
                "from": mail["from_email"],
                "subject": mail["subject"],
                "content": mail["content"]
            } for mail in r.json()["messages"]] 
        
Tempmailbox_com = Dismailbox_com