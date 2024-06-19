import requests
from .._constructors import _WaitForMail

class Internxt_com(_WaitForMail):
    """An API Wrapper around the https://internxt.com/temporary-email website. Extreme ratelimit."""

    def __init__(self):
        """
            Generate a random inbox\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.get("https://internxt.com/temporary-email")
        if not r.ok:
            raise Exception("Error on creation, status", r, r.text)
        

        r = self._session.get("https://internxt.com/api/temp-mail/create-email")
        if not r.ok:
            raise Exception("Error on creation, status", r, r.text)
        
        data = r.json()
        if not "token" in data:
            raise Exception("Something went wrong on the server side, cant do shit about that (missing token)")
        self._token = data["token"]
        self.email = data["address"]
        self.name, self.domain = self.email.split("@", 1)

    def get_inbox(self) -> list[dict]:
        """
        Returns a list of *new* emails
        """

        r = self._session.get("https://internxt.com/api/temp-mail/get-inbox?token="+self._token)
        
        if r.ok:
            
            return [{
                "id": mail["_id"],
                "time": mail["date"],
                "from": mail["from"],
                "subject": mail["subject"],
                "content": mail["body"]
            } for mail in r.json().get("emails", [])]
