import requests

from .._constructors import _WaitForMail, _generate_user_data

class Tempdashmail_gg(_WaitForMail):
    """An API Wrapper around the https://temp-mail.gg website."""

    _BASE_URL = "https://temp-mail.gg"

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get(cls._BASE_URL+"/api/settings/domains")
        if r.ok:
            return r.json()["data"]["domains"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"{self._BASE_URL}/api/mailbox?email={self.name}%40{self.domain}")
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from_address"],
                "time": email["received_time"],
                "subject": email["subject"],
                "content": email["html_message"],
            } for email in r.json()["data"]]
                                                    