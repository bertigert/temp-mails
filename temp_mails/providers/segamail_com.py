import requests

from .._constructors import _WaitForMail, _generate_user_data

class Segamail_com(_WaitForMail):
    """An API Wrapper around the https://1secmail.com website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.post("https://segamail.com/en/getEmailAddress")
        if not r.ok:
            raise Exception("Error creating email, status", r.status_code)
        
        data = r.json()
        self._recover_key = data["recover_key"]
        
        self.email = data["address"]
        self.name, self.domain = self.email.split("@", 1)

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://segamail.com/en/getInbox")
        if r.ok:
            data = r.json()
            mails = len(data)
            return [{
                "id": mails-i,
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"],
                "content": email["body"]
            } for i, email in enumerate(data)]
                                                    