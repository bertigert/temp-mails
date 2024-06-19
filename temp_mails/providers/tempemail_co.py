import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Tempemail_co(_WaitForMail):
    """An API Wrapper around the https://tempemail.co/ website"""

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

        r = requests.get("https://tempemail.co/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domains = soup.find("select", {"id": "email_domain"})
            return [o["value"] for o in domains.find_all("option")[1:]]


    def get_mail_content(self, mail_id: int | str) -> dict:
        """
        Returns additional information, including the content of a given mail_id as a dict\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://tempemail.co/mail/info?id={mail_id}")
        if r.ok:
            data = r.json()
            return {
                "time": data["mail"]["date"],
                "content": data["mail"]["textHtml"]
            }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        
        r = self._session.get(f"https://tempemail.co/get-mails?mail_id={self.name}%40{self.domain}&unseen=0&is_new=1")
        if r.ok:
            soup = BeautifulSoup(r.json()["mails"], "lxml")
            emails = soup.find("tbody", {"id": "append_email"})
            
            if not emails:
                return []
            
            return [{
                "id": email.a["data-id"],
                "from": email.find("span", {"class": "rhide"}).text,
                "time": email.find("td", {"class": "rtime"}).a.span.text,
                "subject": (d := email.find("td", {"class": "rsubject rhide"}).a).p.text,
                "preview": d.span.text
            } for email in emails.find_all("tr")]
                                                    