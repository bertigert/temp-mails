import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Eyepaste_com(_WaitForMail):
    """An API Wrapper around the https://www.eyepaste.com/ website."""
    
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
        Returns a list of valid domains of the service (only 1 domain)
        """

        return ["eyepaste.com"]
    

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://www.eyepaste.com/inbox/{self.email}.rss")
        
        if r.ok:
            return [
                {
                    "id": i,
                    "from": (info := ( data := BeautifulSoup( email.find("description").text, "lxml" ).find_all("p", limit=2) )[0].text.split(" From: ", 1)[1].split(" To: ", 1))[0].strip(),
                    "subject": (info := info[1].split(" Subject: ", 1)[1].split(" Date: ", 1))[0].strip(),
                    "time": info[1].strip().rsplit(" ", 1)[0],
                    "content": " ".join( map(str, data[1].find_next_siblings()) )
                } 
                for i, email in enumerate(ET.fromstring(r.text).find("channel").findall("item"))
            ]

                                                   