from time import sleep, time
import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Mailnesia_com(_WaitForMail):
    """An API Wrapper around the https://mailnesia.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has 1 domain.
        """
        return ["mailnesia.com"]

    
    def get_mail_content(self, mail_id: int | str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://mailnesia.com/mailbox/{self.name}/{mail_id}?noheadernofooter=1")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return "".join([str(c) for c in soup.find("div", {"id": "text_html_"+mail_id}).children])


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://mailnesia.com/mailbox/{self.name}?noheadernofooter=1")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            emails = soup.find_all("tr", {"class": "emailheader"})
            return [{
                "id": email["id"],
                "from": (d := email.find_all("td"))[1].text,
                "time": d[0].time["datetime"],
                "subject": d[3].text
            } for email in emails]
        