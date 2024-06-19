from datetime import datetime

from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Yopmail_com(_WaitForMail): # max 15 mails/page
    """An API Wrapper around the https://yopmail.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. Note that every domain gets forwarded to yopmail.com\n
        exclude - a list of domain to exclude from the random selection\n
        """
        
        super().__init__(0)

        self._session = requests.Session()

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        r = self._session.get("https://yopmail.com/en/")
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
        self._token = BeautifulSoup(r.text, "lxml").find("input", {"id": "yp"})["value"]
        self._token2 = None

        r = self._session.post("https://yopmail.com/en/", data={
            "yp": self._token,
            "login": self.name
        })
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
       
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://yopmail.com/en/domain?d=all")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("body", {"class": "yscrollbar"}).div
            
            return [email.text[1:] for email in email_list.findChildren()]


    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns more detailed information of a given mail_id as a dict\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://yopmail.com/en/mail?b={self.name}&id=m{mail_id}", cookies={
            "ytime": f"{datetime.now():%H:%M}"
        })

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email = soup.find(lambda tag: tag.name == "div" and tag.get("class") == ["fl"])
            return {
                "subject": email.find("div", {"class": "ellipsis nw b f18"}).text,
                "from": (spans := email.find_all("span", {"class": "ellipsis"}))[0].text.removeprefix("<").removesuffix(">").strip(),
                "time": spans[1].text,
                "content": soup.find("div", {"id": "mail"})
            }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox
        """
        
        if not self._token2:    
            r = self._session.get("https://yopmail.com/ver/9.2/webmail.js")
            if not r.ok:
                return
            self._token2 = r.text.split("&yj=", 1)[1].split("&", 1)[0]

        r = self._session.get("https://yopmail.com/en/inbox", params={
            'login': self.name,
            'p': '1',
            'd': '',
            'ctrl': '',
            'yp': self._token,
            'yj': self._token2,
            'v': '9.2',
            'r_c': '',
            'id': '',
            'ad': '0',
        }, cookies={
            "ytime": f"{datetime.now():%H:%M}" # fuck you, you hidden thing
        })
        
        if not r.ok:
            return None
        
        if r.text.find("w.finrmail(-1") != -1:
            raise Exception("Error, you need to verify Captcha manually on https://yopmail.com/")

        soup = BeautifulSoup(r.text, "lxml")
        emails = soup.find_all("div", {"class": "m"})
        return [{
            "id": email["id"],
            "time": email.find("span", {"class": "lmh"}).text,
            "subject": email.find("span", {"class": "lmf"}).text,
            "preview": email.find("div", {"class": "lms"}).text
        } 
        for email in emails]
    