import requests

from .._constructors import _WaitForMail, _generate_user_data

class Tempomail_top(_WaitForMail):
    """An API Wrapper around the https://tempomail.top/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()

        r = self._session.get("https://api.tempomail.top/api/v1/getApiKey")
        if not r.ok or '"status":"fail"' in r.text:
            raise Exception("Failed to create email, status", r.status_code)
        
        
        self._apikey = r.json()["body"]["data"]["apiKey"]
        
        self._session.headers = {
            "Authorization": "Bearer " + self._apikey
        }

        r = self._session.get(f"https://api.tempomail.top/api/v1/domains?apiKey={self._apikey}&limit=10&offset=0&domain=")
        if not r.ok or '"status":"fail"' in r.text:
            raise Exception("Failed to create email, status", r.status_code)
        

        self.valid_domains = [domain["name"] for domain in r.json()["body"]["data"]["domains"]]
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.valid_domains)

        r = self._session.post("https://api.tempomail.top/api/v1/mail?apiKey="+self._apikey, json={
            "apiKey": self._apikey,
            "domain": self.domain,
            "mail": self.name
        })
        if not r.ok or '"status":"fail"' in r.text:
            raise Exception("Failed to create email, status", r.status_code, r.text)
        
        

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        s = requests.Session()
        r = s.get("https://api.tempomail.top/api/v1/getApiKey")
        if not r.ok and not '"status":"fail"' in r.text:
            return None
        
        apikey = r.json()["body"]["data"]["apiKey"]
        
        r = s.get(f"https://api.tempomail.top/api/v1/domains?apiKey={apikey}&limit=10&offset=0&domain=")
        if not r.ok and not '"status":"fail"' in r.text:
            return None
        
        return [domain["name"] for domain in r.json()["body"]["data"]["domains"]]


    def get_mail_content(self, mail_id: int | str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://api.tempomail.top/api/v1/mail/messages/message/{mail_id}?mail={self.email}")
        if r.ok:
            data = r.json()["body"]["data"]["messages"][0]["data"]
            return data.get("html", data.get("text"))

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://api.tempomail.top/api/v1/mail/messages?mail={self.email}&offset=0&limit=10")
        
        if r.ok:
            
            return [{
                "id": email["id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"]
            } for email in r.json()["body"]["data"]["messages"]["rows"]]
                                                    