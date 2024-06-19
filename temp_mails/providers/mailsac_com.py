import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Mailsac_com(_WaitForMail):
    """An API Wrapper around the https://mailsac.com/ website"""

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
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name=name, domain=domain, exclude=exclude, valid_domains=self.get_valid_domains())


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """
        return ["mailsac.com"]


    def get_mail_content(self):
        raise Exception("Email content is not possible to retrieve without an account. It is only possible to see the content of the latest email (which is automatically done in get_inbox)")


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://mailsac.com/inbox/{self.name}%40{self.domain}")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            inbox = soup.find_all("div", {"class": "container-fluid"}, limit=2)[1].script.text
            
            data = json.loads(inbox.split("window.__seedInboxMessages = ", 1)[1].rsplit(";\nwindow.__inboxUntil = null")[0])
 
            if data:
                emails = [{
                    "id": email["_id"],
                    "from": email["from"][0]["address"],
                    "time": email["received"],
                    "subject": email["subject"],
                } for email in data]

                emails[0]["content"] = data[0]["body"] # only for latest mail
                return emails
            else:
                return []