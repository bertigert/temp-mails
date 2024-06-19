from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail

class Tenminutemail_one(_WaitForMail):
    """An API Wrapper around the https://10minutemail.one/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    
        r = self._session.get("https://10minutemail.one")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        r = self._session.post("https://10minutemail.one/messages", data={
            "_token": self._token,
            "captcha": ""
        })
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        self.email: str = data["mailbox"]
        self.name, self.domain = self.email.split("@", 1)
        

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://10minutemail.one/messages", data={
            "_token": self._token,
            "captcha": ""
        })
        
        if r.ok:
            return [{
                "id": email["id"],
                "time": email["receivedAt"],
                "subject": email["subject"],
                "content": email["content"]
            } for email in r.json()["messages"]] 

    
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        return ["cobmk.com"]
        