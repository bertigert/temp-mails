import requests

from .._constructors import _WaitForMail

class Maildax_com(_WaitForMail):
    """An API Wrapper around the https://maildax.com/ website"""

    def __init__(self):
        """
        Generate an random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.post("https://api2.maildax.com/email")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        self.email = data["email"]
        self.name, self.domain = self.email.split("@", 1)
        self._secret = data["secret"]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://api2.maildax.com/email/mail/{mail_id}?secret={self._secret}")
        if r.ok:
            return r.json()["data"]["html"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://api2.maildax.com/email/mails?email={self.email}&secret={self._secret}")
        if r.ok:
            return [{
                "id": email["_id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"],
                "preview": email["text"]
            } for email in r.json()["data"]]
                                                    