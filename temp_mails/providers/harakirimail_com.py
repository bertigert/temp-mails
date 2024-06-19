import requests

from .._constructors import _WaitForMail, _generate_user_data

class Harakirimail_com(_WaitForMail):
    """An API Wrapper around the https://harakirimail.com/ website"""

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
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has 1 domain.
        """
        return ["harakirimail.com"]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://harakirimail.com/api/v1/email/"+mail_id)
        if r.ok:
            return r.json()["bodyhtml"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://harakirimail.com/api/v1/inbox/"+self.name)
        if r.ok:
            return [{
                "id": email["_id"],
                "from": email["from"],
                "time": email["received"],
                "subject": email["subject"]
            } for email in r.json()["emails"]]
                                                    