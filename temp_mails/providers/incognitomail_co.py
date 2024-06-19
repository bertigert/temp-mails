import requests

from .._constructors import _WaitForMail

class Incognitomail_co(_WaitForMail):
    """An API Wrapper around the https://incognitomail.co/ website"""

    def __init__(self):
        """
        Generate a random inbox.
        """
        
        super().__init__(-1)

        self._session = requests.Session()

        r = self._session.get("https://api.incognitomail.co/inbox/v1/create")        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        self.email = data["id"]
        self.name, self.domain = self.email.split("@", 1)
        self._token = data["token"]
    

    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id (a full link) as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(mail_id)
        if r.ok:
            data = r.json()
            return data.get("html", data.get("text"))


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://api.incognitomail.co/inbox/v1/list", json={
            "inboxId": self.email,
            "inboxToken": self._token
        })
        if r.ok:
            return [{
                "id": email["messageURL"], # this is a full link
                "from": email["sender"]["email"],
                "subject": email["subject"],
                "time": email["date"]
            } for email in r.json()["items"]]
