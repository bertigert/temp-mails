import requests

from .._constructors import _WaitForMail, _generate_user_data

class Mintemail_com(_WaitForMail):
    """An API Wrapper around the https://1secmail.com website"""

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

        return ["cj.MintEmail.com"]


    def get_mail_content(self, mail_id: int | str) -> dict:
        """
        Returns additional (all of the) information about the email\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.mintemail.com/m/src/email.php?id={mail_id}&email={self.name}&domain={self.domain}")
        
        if r.ok:
            data = r.json()[0]
            data = {
                "id": data["id"],
                "time": data["date"],
                "from": data["from"][2:-1],
                "subject": data["subject"]
            }

            r = self._session.get(f"https://www.mintemail.com/m/src/emailHtml.php?id={mail_id}&email={self.name}&domain={self.domain}")
            if r.ok:
                data["content"] = r.text
            
            return data



    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...].\nNote that this website only returns the ids
        """

        r = self._session.get(f"https://www.mintemail.com/m/src/checkemail.php?email={self.name}&domain={self.domain}")
        if r.ok:
            return [] if r.text == " " else [{"id": email_id} for email_id in r.text[1:].split(",")]

            
                                                    