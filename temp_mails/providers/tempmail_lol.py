from string import ascii_lowercase, digits
import random

import requests

from .._constructors import _WaitForMail

class Tempmail_lol(_WaitForMail):
    """An API Wrapper around the https://tempmail.lol/ website"""

    def __init__(self, name: str=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        """
        super().__init__(0)

        self._session = requests.Session()

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        r = self._session.post("https://api.tempmail.lol/v2/inbox/create", data={
                "community": True,
                "prefix": self.name
            })
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}")
        
        data = r.json()
        self.email, self.name, self.domain = data["address"], *(data["address"].split("@"))
        self._token = data["token"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox including the content.\n
        Note that the inbox is only stored locally, only new emails are returned.
        """
        
        r = self._session.get("https://api.tempmail.lol/v2/inbox?token="+self._token)
        if r.ok:
            data = r.json()["emails"]
            return [{
                "id": email["_id"],
                "from": email["from"],
                "subject": email["subject"],
                "time": email["date"],
                "content": email.get("html", email["body"])
            } for email in data]
                        