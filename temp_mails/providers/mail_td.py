import json
import re

from bs4 import BeautifulSoup
import requests


from .._constructors import _WaitForMail, _generate_user_data

class Mail_td(_WaitForMail):
    """An API Wrapper around the https://mail.td/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None, url: str="https://mail.td/_next/static/chunks/641-ea73fac4f93b3ddb.js"):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains(url=url))
        r = self._session.get("https://mail.td/en/mail/"+self.email)
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self._session.headers = {
            "Authorization": "Bearer " + self._session.cookies.get("auth_token")
        }

    @staticmethod
    def get_valid_domains(url: str="https://mail.td/_next/static/chunks/641-ea73fac4f93b3ddb.js", dynamic_recovery: bool=False) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list\n
        Args:\n
        dynamic_recovery - in case the url is outdated, tell the script to try to update by itself. If true and the script succeeds, the return value is a list with the new script url as the first element and the valid domains as the second element.
        """

        r = requests.get(url) # this isnt completely static
        if r.status_code == 404:
            if not dynamic_recovery:
                raise Exception("The script url needed for valid domains changed, set dynamic_recovery to true if you want the script to try to get the new link")
        
            else:
                r = requests.get("https://mail.td/en/mail")
                if r.ok:
                    soup = BeautifulSoup(r.text, "lxml")
                    scripts = soup.head.find_all(lambda tag: tag.name == "script" and re.match(r'^/_next/static/chunks/\d{3}-[0-9A-Fa-f]{16}\.js$', tag["src"]))

                    for script in scripts:
                        r = requests.get("https://mail.td/"+script["src"])
                        if r.ok and len(d := r.text.split("mailHosts:", 1)) > 1:
                            return ["https://mail.td/"+script["src"], json.loads(d[1].split("]", 1)[0]+"]")]

                    raise Exception("Dynamic recovery failed, you'll need to find the url by yourself")

        if r.ok:
            return json.loads(r.text.split("mailHosts:", 1)[1].split("]", 1)[0]+"]")


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://mail.td/api/api/v1/mailbox/{self.email}/{mail_id}")
        if r.ok:
            data = r.json()["body"]
            return data.get("html", data.get("text"))


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://mail.td/api/api/v1/mailbox/"+self.email)
        
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from"],
                "time": email["date"],
                "subject": email["subject"]
            } for email in r.json()]
                                                    