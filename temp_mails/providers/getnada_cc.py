import requests

from .._constructors import _WaitForMail, _generate_user_data

class Getnada_cc(_WaitForMail):
    """An API Wrapper around the https://getnada.cc/ website"""

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
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://getnada.cc/api/domains/GwNvKEofrdyS7JTXCzHQ")
        if r.ok:
            return r.json()

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://getnada.cc/api/messages/{self.email}/GwNvKEofrdyS7JTXCzHQ")
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["sender_email"],
                "time": email["date"],
                "subject": email["subject"],
                "content": email["content"]
            } for email in r.json()]
                                                    