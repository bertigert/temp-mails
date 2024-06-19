import requests

from .._constructors import _WaitForMail, _generate_user_data

class Onesecmail_com(_WaitForMail):
    """An API Wrapper around the https://1secmail.com website. https://www.tempemailpro.com/ uses 1secmail it's also supported."""

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

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://www.1secmail.com/api/v1/?action=getDomainList")
        if r.ok:
            return r.json()


    def get_mail_content(self, mail_id: int | str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={self.name}&domain={self.domain}&id={mail_id}")
        if r.ok:
            return r.json()["body"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={self.name}&domain={self.domain}")
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"]
            } for email in r.json()]
                                                    