import requests
from .._constructors import _WaitForMail, SSLAdapterCF


class Tenminuteemail_com(_WaitForMail):
    """An API Wrapper around the https://10minutemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        self._session.mount("https://", SSLAdapterCF)

        r = self._session.get("https://10minutemail.com/session/address")
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["address"]
        self.name, self.domain = self.email.split("@", 1)

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://10minutemail.com/messages/messagesAfter/0")
        
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["sender"],
                "time": email["sentDate"],
                "content": email["bodyHtmlContent"]
            } for email in r.json()]
        