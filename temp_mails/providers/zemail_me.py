import json

from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, GLOBAL_UA, _generate_user_data

class Zemail_me(_WaitForMail):
    """An API Wrapper around the https://zemail.me website"""

    _BASE_URL = "https://zemail.me"

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        super().__init__(-1)

        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": GLOBAL_UA,
            "X-Livewire": "",
        }

        r = self._session.get(self._BASE_URL)
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        r = self._session.get(self._BASE_URL+"/mailbox")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        soup = BeautifulSoup(r.text, "lxml")
        
        
        data = json.loads(soup.find(lambda tag: tag.name == "span" and tag.get("wire:snapshot", "").startswith('{"data":{"username":')).get("wire:snapshot"))

        self.valid_domains = [domain for domain in data["data"]["domains"][0]]

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.valid_domains)
        
        self._token = soup.find("script", {"data-update-uri": "/livewire/update"})["data-csrf"]

        self._next_snapshot = soup.find(lambda tag: tag.name == "div" and "id: 0" in tag.get("x-data", "") ).get("wire:snapshot")

        payload = {
            "_token": self._token,
            "components": [
                {
                    "snapshot": self._next_snapshot,
                    "updates": {},
                    "calls": [
                        {
                            "path": "",
                            "method": "__dispatch",
                            "params": [
                                "syncMailbox",
                                [
                                    self.email
                                ]
                            ]
                        }
                    ]
                }
            ]
        }
                 
        r = self._session.post(self._BASE_URL+"/livewire/update", json=payload)

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        self._next_snapshot = data["components"][0]["snapshot"]        


    @classmethod
    def get_valid_domains(cls) -> list[str]:
        """Returns a list of valid domains of the service. This website only has 1 domain"""

        r = requests.get(cls._BASE_URL)
       
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find(lambda tag: tag.name == "span" and tag.get("wire:snapshot", "").startswith('{"data":{"username":')).get("wire:snapshot"))
            return [domain for domain in data["data"]["domains"][0]]
        
        

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        payload = {
            "_token": self._token,
            "components": [
                {
                    "snapshot": self._next_snapshot,
                    "updates": {},
                    "calls": [
                        {
                            "path": "",
                            "method": "__dispatch",
                            "params": [
                                "fetchMessages",
                                {}
                            ]
                        }
                    ]
                }
            ]
        }

        r = self._session.post(self._BASE_URL+"/livewire/update", json=payload)
        
        if r.ok:
            self._next_snapshot = r.json()["components"][0]["snapshot"]
            data = json.loads(self._next_snapshot)
            return [
                {
                    "id": email[0]["id"],
                    "from": email[0]["sender_email"],
                    "time": email[0]["timestamp"][0],
                    "subject": email[0]["subject"],
                    "content": email[0]["content"]
                }
                for email in data["data"]["messages"][0]
            ]