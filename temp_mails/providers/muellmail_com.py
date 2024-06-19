from time import sleep, time

from bs4 import BeautifulSoup
import requests

from .._constructors import _generate_user_data

class Muellmail_com():
    """An API Wrapper around the https://muellmail.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        self._session = requests.Session()
        r = self._session.get("https://muellmail.com/api/auth/session")
        if not r.ok:
            raise Exception("Failed to create email, status:", r.status_code)

        r = self._session.get("https://muellmail.com/api/auth/csrf")
        if not r.ok:
            raise Exception("Failed to create email, status:", r.status_code)
        
        self._token = r.json()["csrfToken"]
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        r = self._session.post("https://muellmail.com/api/auth/callback/anon?", data={
            "redirect": "false",
            "muellmail": self.email,
            "csrfToken": self._token,
            "callbackUrl": "https://muellmail.com/#/"+self.email,
            "json": "true"
        })

        if not r.ok:
            raise Exception("Failed to create email, status:", r.status_code)

        r = self._session.get("https://muellmail.com/api/auth/session")


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://muellmail.com/")
        
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("div", {"id": "generateMail"}).find_all("option")
            return [email["value"] for email in email_list]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://muellmail.com/graphql", json={
            "operationName": "MailQuery",
            "variables": {
                "offset": 0,
                "limit": 100
            },
            "query": "query MailQuery($offset: Int!, $limit: Int!) {\n  emails(orderBy: {createdAt: desc}, offset: $offset, limit: $limit) {\n    id\n    subject\n    sender\n    createdAt\n    html\n    text\n    }\n}"
        })

        if r.ok: 
            return r.json()["data"]["emails"]
        

    def wait_for_new_email(self, delay: float=2.0, timeout: int=60):
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """
        if timeout > 0: 
            start = time()
        
        r = self._session.post("https://muellmail.com/graphql", json={
            "operationName": "Query",
            "variables": {},
            "query": "query Query {\n  emailsCount\n}"
        })

        if not r.ok:
            return None

        old_length = int(r.json()["data"]["emailsCount"])

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            r = self._session.post("https://muellmail.com/graphql", json={
                "operationName": "Query",
                "variables": {},
                "query": "query Query {\n  emailsCount\n}"
            })
            
            if not r.ok:
                return None

            if (int(r.json()["data"]["emailsCount"])) > old_length:
                inbox = self.get_inbox()
                if inbox:
                    return inbox[0]

            sleep(delay)
