from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Temporarymail_com(_WaitForMail):
    """An API Wrapper around the https://temporarymail.com/ website. Ratelimits"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None, token: str=None):
        """
        Generate an inbox (Cannot be reused for 14 days, unless an access token is provided -> .token)\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        r = self._session.get(f"https://temporarymail.com/api/?action=requestEmailAccess&key={token or ''}&value={self.email}")
        if not r.ok:
            raise Exception("Failed to create email", r.status_code, r.text)
        
        data = r.json()
        if data.get("code") == 403:
            raise Exception("Failed to create email, email is already in use, please provide an access key")
        elif data.get("code") == 429:
            raise Exception("Failed to create email, ratelimited")
        
        self.email = data["address"]
        self.token = data["secretKey"]

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://temporarymail.com/api/?action=getDomains")
        if r.ok:
            return r.json()


    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns the content of a given mail_id {subject: str, content: BeautifulSoup}\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        subject = ""
        r = self._session.post(f"https://temporarymail.com/api/?action=getEmail&value="+mail_id)
        if r.ok:
            subject = r.json()[mail_id]["subject"]
        
        r = self._session.get("https://temporarymail.com/view/?i="+mail_id)
        if not r.ok:
            return
        
        soup = BeautifulSoup(r.text, "lxml")
        content = soup.find("body")

        return {
            "subject": subject,
            "content": content
        }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://temporarymail.com/api/?action=checkInbox&value="+self.token)
        if r.ok:
            data = r.json()
            
            return [{
                "id": email["id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"]
            } for email in data.values()] if data != [] else []
                     