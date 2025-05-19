from time import time
import json
import hmac
from hashlib import sha256
import requests

from .._constructors import _WaitForMail


def _encode_timestamp_data(_data):
    _data["key"] = hmac.new(b"2N(PphSU<U*?Uh]pd{4--V", json.dumps(_data, separators=(",", ":")).encode("utf-8"), sha256).hexdigest() # not sure if the key is fully static, has been for like half a year
    return _data

class Incognitomail_co(_WaitForMail):
    """An API Wrapper around the https://incognitomail.co/ website"""

    _BASE_URL = "https://api.incognitomail.co"

    def __init__(self):
        """
        Generate a random inbox.
        """
        
        super().__init__(-1)

        self._session = requests.Session()
    
        data = _encode_timestamp_data({
            "ts": int(time() * 1000)
        })

        r = self._session.post(self._BASE_URL+"/inbox/v2/create", data=json.dumps(data), headers= {
            'content-type': 'text/plain;charset=UTF-8',
        })        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code, r.text)
        
        data = r.json()
        self.email = data["id"]
        self.name, self.domain = self.email.split("@", 1)
        self._token = data["token"]
        
    @staticmethod
    def get_valid_domains() -> list[str]:
        """Returns a list of valid domains of the service. This website only has 1 domain"""

        return ["mailfast.pro"]

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

        data = _encode_timestamp_data({
            "inboxId": self.email,
            "inboxToken": self._token,
            "ts": int(time() * 1000)
        })

        r = self._session.post(self._BASE_URL+"/inbox/v1/list", json=data)
        
        if r.ok:
            return [{
                "id": email["messageURL"], # this is a full link
                "from": email["sender"]["email"],
                "subject": email["subject"],
                "time": email["date"]
            } for email in r.json()["items"]]
