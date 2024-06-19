from base64 import b64decode
from urllib.parse import unquote as urldecode

from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Mailgolem_com(_WaitForMail):
    """An API Wrapper around the https://mailgolem.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
        """
        super().__init__(0)

        self._session = requests.Session()

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        r = self._session.get("https://mailgolem.com/")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        self._token = soup.find("meta", {"name": "csrf-token"})["content"]


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (only mailgolem.com)
        """
        return ["mailgolem.com"]


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://mailgolem.com/view/{mail_id}")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            body_script = soup.find("script", {"data-cfasync": "false"})
            b64_data = body_script.next_sibling.text.split('decodeURIComponent(atob("', 1)[1].split('"', 1)[0]
            return urldecode(b64decode(b64_data).decode())

    def get_inbox(self) -> list[dict]:
        """
        Returns a list of *new* emails
        """

        r = self._session.post("https://mailgolem.com/fetch-emails/"+self.email, data={"_token": self._token})
        
        if r.ok:
            return [{
                "id": mail["id"],
                "time": mail["created_at"],
                "from": mail["from"],
                "subject": mail["subject"],
            } for mail in r.json()]
