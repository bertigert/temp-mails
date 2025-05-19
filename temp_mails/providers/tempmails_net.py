import time
from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data, GLOBAL_UA

class Tempmails_net(_WaitForMail):
    """An API Wrapper around the https://tempmails.net/ website"""

    _BASE_URL = "https://tempmails.net"

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        info: the custom name and domain is normally locked behind a (luckily clientsided) paywall
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self._session.headers = {
            "user-agent": GLOBAL_UA,
        }
    
        r = self._session.get(self._BASE_URL)
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code, r.text)

        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        self._session.headers["x-csrf-token"] = self._token
        self._session.headers["x-requested-with"] = "XMLHttpRequest"

        r = self._session.get(f"{self._BASE_URL}/messages?_={int(time.time()*1000)}")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code, r.text)
        
        if not domain and not name and not exclude:    
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)
        
        else:
            self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
            
            r = self._session.post(self._BASE_URL+"/create", data={
                "_token": self._token,
                "name": self.name,
                "domain": self.domain
            })
            if not r.ok:
                raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
            
            r = self._session.get(f"{self._BASE_URL}/messages?_={int(time.time()*1000)}")    
            if not r.ok:
                raise Exception("Failed to create email, status", r.status_code)
            
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)


    @classmethod
    def get_valid_domains(cls) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """
        s = requests.Session()
        r = s.get(cls._BASE_URL+"/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain["value"] for domain in soup.find("select", {"name": "domain"}).findChildren("option")]


    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns additional information to the email\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """                     
        r = self._session.get(self._BASE_URL+"/view/"+mail_id)
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            main = soup.find("div", {"class": "textHolder text-center"})
            return {
                "time": main.find_all("span")[-1].text.strip(),
                "content": "".join(str(elem) for elem in main.find("p", {"class": "head"}).find_next_siblings())
            }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"{self._BASE_URL}/messages?_={int(time.time()*1000)}")
        if r.ok:
            messages = r.json()["messages"]
            if messages == "":
                return []
            
            soup = BeautifulSoup(messages, "lxml")
            return [
            {
                "id": email["href"].rsplit("/", 1)[1],
                "from": (lis := email.find_all("li"))[0].text.strip(),
                "subject": lis[1].text  
            } for email in soup.find_all("a", {"class": "email"})]
                                            