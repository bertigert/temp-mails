import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data

class Mailcatch_com(_WaitForMail):
    """An API Wrapper around the http://mailcatch.com/ website."""
    
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
        Returns a list of valid domains of the service (only 1 domain)
        """

        return ["mailcatch.com"]
    

    def get_mail_content(self, mail_id: str) -> BeautifulSoup:
        """
        Returns the content of the mail as a beautiful soup object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """                     
        
        r = self._session.get(f"http://mailcatch.com/en/temporary-mail-content?box={self.name}&show={mail_id}")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            end = soup.find("script", {"src": "/js/jquery-1.3.1.min.js"})
            return "".join( reversed( list( map(str, end.previous_siblings) ) ) )


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("http://mailcatch.com/en/temporary-inbox-rss?box="+self.name)
        if r.ok:
            return [
                {
                    "id": email.find("link").text.rsplit("show=", 1)[1],
                    "from": email.find("author").text,
                    "subject": email.find("title").text,
                    "time": email.find("pubDate").text,
                } 
                for email in ET.fromstring(r.text).find("channel").findall("item")
            ]

                                                   