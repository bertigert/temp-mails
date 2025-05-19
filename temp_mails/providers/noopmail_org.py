from httpx import request
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Noopmail_org(_WaitForMail):
    """An API Wrapper around the https://noopmail.org/ website"""

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
        Returns a list of valid domains of the service (format: abc.xyz) as a list. Only 1 domain.
        """
        r = requests.get("https://noopmail.org/api/d", headers={
            "Accept": "application/json, text/plain, */*",
        })
        if r.ok:
            return [domain for domain in r.json()]

    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://noopmail.org/api/i/"+mail_id)
        if r.ok:
            return r.json()["html"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://noopmail.org/api/c", json={
            "e": self.name,
            "d": self.domain
        })
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"],
                "preview": email["text"]
            } for email in r.json()]
                                                    