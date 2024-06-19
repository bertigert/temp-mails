import requests
from .._constructors import _WaitForMail, _generate_user_data

class Tempmail_io(_WaitForMail):
    """An API Wrapper around the https://temp-mail.io/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
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
        
        r = self._session.post("https://api.internal.temp-mail.io/api/v3/email/new", json={
            "name": self.name,
            "domain": self.domain
        })
        
        if r.ok:
            self.email = f"{self.name}@{self.domain}"
        else:
            raise Exception("Failed to create email, status", r.status_code)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://api.internal.temp-mail.io/api/v4/domains")
        if r.ok:
            return [domain["name"] for domain in r.json()["domains"] if domain["type"] == "public"] 

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox including the content
        """
        
        r = self._session.get(f"https://api.internal.temp-mail.io/api/v3/email/{self.email}/messages")
        
        if r.ok:
            return r.json()


    def get_mail_content(self, mail_id: str) -> str:
        """
        !! REDUNDANT\n
        Email content is in inbox if the email contains html\n
        Returns the content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://api.internal.temp-mail.io/api/v3/message/"+mail_id)
        if r.ok:
            return r.json()
                        