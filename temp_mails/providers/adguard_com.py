import requests

from .._constructors import _WaitForMail

class Adguard_com(_WaitForMail):
    """An API Wrapper around the https://tempmail.adguard.com/ website"""

    _BASE_URL = "https://tempmail.adguard.com/"

    def __init__(self):
        """
        Generate a random inbox.\nNote that there is a ratelimit
        """
        super().__init__(0)

        self._session = requests.Session()

        r = self._session.post(self._BASE_URL)        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self.email = r.text.split("copyEmailAddress('", 1)[1].split("'", 1)[0]
        self.name, self.domain = self.email.split("@", 1)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """Returns a list of valid domains of the service. This website only has 1 domain"""
        return ["adguard.com"]


    def get_mail_content(self, mail_id: int) -> dict:
        """
        Not sure if needed since no testing possible\n
        Returns the content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        return None


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(self._BASE_URL+"messages?since_message_id=0")
        if r.ok:
            return [{
                "id": email["message_id"],
                "from": email["from"][0]["address"],
                "subject": email["subject"],
                "content": email["content_html"],
                "time": email["time_added_timestamp"]
            } for email in r.json()["emails"][:-1]] # remove welcome mail
