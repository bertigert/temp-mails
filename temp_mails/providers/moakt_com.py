import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Moakt_com(_WaitForMail):
    """An API Wrapper around the https://moakt.com/ website. Fast from experience."""

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

        self._session.post("https://moakt.com/en/inbox", data={
            "domain": self.domain,
            "username": self.name,
            "setemail": "Create",
            "preferred_domain": "" # ?
        })


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://moakt.com/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            emails = soup.find("select", {"id": "domains"}).find_all("option")
            return [email["value"] for email in emails]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://moakt.com/en/email/{mail_id}/content/")
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://moakt.com/en/inbox")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("div", {"id": "email_message_list"})
            return [{
                "id": email.td.a["href"].rsplit("/", 1)[1],
                "from": email.find("td", {"id": "email-sender"}).text[1:-1],
                "subject": email.td.a.text
            } for email in email_list.find_all("tr")[1:-3]]
                                                    