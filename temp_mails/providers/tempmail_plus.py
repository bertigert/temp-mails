from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Tempmail_plus(_WaitForMail):
    """An API Wrapper around the https://tempmail.plus/ website"""

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
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://tempmail.plus/en/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("div", {"class": "dropdown-menu"})[1].findChildren("button")]
        

    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the content of a given mail as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://tempmail.plus/api/mails/{mail_id}?email={self.name}%40{self.domain}&epin=")
        if r.ok:
            return r.json()["html"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """

        r = self._session.get(f"https://tempmail.plus/api/mails?email={self.name}%40{self.domain}&limit=100&epin=")
        
        if r.ok:
            return [{
                "id": mail["mail_id"],
                "time": mail["time"],
                "from": mail["from_mail"],
                "subject": mail["subject"]
            } for mail in r.json()["mail_list"]]
        