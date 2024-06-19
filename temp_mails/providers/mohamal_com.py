from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data, _deCFEmail

class Mohamal_com(_WaitForMail):
    """An API Wrapper around the https://www.mohmal.com/website"""

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

        self._session.post("https://www.mohmal.com/en/create", data={
            "name": self.name, 
            "domain": self.domain
        })

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://www.mohmal.com/en")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("option")]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the html content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://www.mohmal.com/en/message/"+mail_id)
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.mohmal.com/en/inbox")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            
            emails = []
            
            emails_data = soup.find("tbody").findChildren("tr")
            
            if emails_data[0]["class"][0] == "no-messages":
                return []

            for email in emails_data:
                data = {
                    "id": email["data-msg-id"],
                    "subject": email.find("td", {"class": "subject"}).text,
                    "time": email.find("td", {"class": "time"}).text,
                    "from": _deCFEmail(email.find("td", {"class": "sender"}).a.span["data-cfemail"])
                }
                emails.append(data)

            return emails
