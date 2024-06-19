from hashlib import sha1
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Fakermail_com(_WaitForMail):
    """An API Wrapper around the https://fakermail.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        NOTE: you cannot receive emails atm so i cannot test anything really. It should work, but i am not sure if the email content in in the inbox.
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        self._email_hash = sha1(self.email.encode()).hexdigest()

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://fakermail.com/api/domains")
        if r.ok:
            return r.json()


    def get_mail_content(self, mail_id: int) -> dict:
        """
        Not sure if needed since no testing possible\n
        Returns the content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        return


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://fakermail.com/api/mail/"+self._email_hash)
        if r.ok:
            return r.json()
