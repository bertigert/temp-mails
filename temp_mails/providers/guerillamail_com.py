from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Guerillamail_com(_WaitForMail):
    """An API Wrapper around the https://www.guerrillamail.com website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. Note that every domain receives emails for every domain.\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        r = self._session.post("https://www.guerrillamail.com/ajax.php?f=set_email_user", data={
            "email_user": self.name,
            "lang": "en",
            "site": "guerrillamail.com",
            "in": "Set cancel"
        })
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
    
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """
        
        r = requests.get("https://www.guerrillamail.com/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domains = soup.find("select", {"class": "strong"})
            return [domain["value"] for domain in domains.findChildren("option")]

    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.guerrillamail.com/ajax.php?f=fetch_email&email_id=mr_{mail_id}&site=guerrillamail.com&in={self.name}")
        if r.ok:
            return r.json()["mail_body"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.guerrillamail.com/ajax.php?f=get_email_list&offset=0&site=guerrillamail.com&in="+self.name)
        if r.ok:
            emails = r.json()["list"] # we just assume that there are no emails in the email
            
            return [{
                "id": emails[i]["mail_id"],
                "from": emails[i]["mail_from"],
                "time": emails[i]["mail_date"],
                "subject": emails[i]["mail_subject"],
                "preview": emails[i]["mail_excerpt"],
            } for i in range(len(emails)-1)] # remove welcome email
