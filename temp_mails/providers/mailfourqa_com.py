import json
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Mailfourqa_com(_WaitForMail):
    """An API Wrapper around the https://mail4qa.com/ website"""

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

        r = self._session.get("https://console.mail4qa.com/assets/js/app.js")
        if not r.ok:
            raise Exception("Failed to create email")
        
        self._apikey = r.text.split('x-apikey", "', 1)[1].split('"', 1)[0]
        self._session.headers = {
            "X-Apikey": self._apikey
        }


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has 1 domain.
        """
        return ["mail4qa.com"]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://api.mail4qa.com/emails/inbox?mid={mail_id}")
        if r.ok:
            return r.json()["mail_source"]["html"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://api.mail4qa.com/emails/inbox?email={self.name}%40{self.domain}&pagesize=50&cursor=0")
        if r.status_code == 404:
            return []
        elif r.ok:
            data = r.json()
            if data["status"] == "success":
                return [{
                    "id": email["_id"],
                    "from": email["mail_source"]["from"]["value"][0]["address"],
                    "time": email["mail_source"]["date"],
                    "subject": email["mail_source"]["subject"],
                } for email in data["emails"]]
                                                    