import requests

from .._constructors import _WaitForMail, _generate_user_data

class Anonymmail_net(_WaitForMail):
    """An API Wrapper around the https://anonymmail.net/ website"""

    _BASE_URL = "https://anonymmail.net"

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
        r = self._session.head(self._BASE_URL)
        if not r.ok:
            raise Exception("Failed to create email session")

        self._session.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
        }

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        r = self._session.post(self._BASE_URL+"/api/create", data={
            "email": self.email
        })
        
        if not r.ok or not r.json()["success"]:
            raise Exception("Failed to create email")


    @classmethod
    def get_valid_domains(cls) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """
        s = requests.Session()
        s.head(cls._BASE_URL)

        r = s.post(cls._BASE_URL+"/api/getDomains", headers={
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
        }, data=None)
        
        if r.ok:
            return [domain["domain"] for domain in r.json()]
            


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]. Note that this provider only stores a single email on their servers.
        """

        r = self._session.post(self._BASE_URL+"/api/get", data={
            "email": self.email
        })
        if r.ok:
            return [{
                "id": email["token"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"],
                "content": email["body"]
            } for email in r.json()[self.email]["emails"]]
                                                    