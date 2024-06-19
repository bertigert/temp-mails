from bs4 import BeautifulSoup
import requests
from .._constructors import _WaitForMail, _generate_user_data

class Disposableemail_co(_WaitForMail):
    """An API Wrapper around the https://disposableemail.co/ website"""
    
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    
        r = self._session.get("https://disposableemail.co/")
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        r = self._session.get("https://disposableemail.co/messages")
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        if not domain and not name and not exclude:    
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)
        
        else:
            self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
            
            r = self._session.post("https://disposableemail.co/create", data={
                "_token": self._token,
                "name": self.name,
                "domain": self.domain
            })
            if not r.ok:
                raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
            
            r = self._session.get("https://disposableemail.co/messages")    
            if not r.ok:
                raise Exception("Failed to create email, status", r.status_code)
            
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://disposableemail.co/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain["value"] for domain in soup.find("select", {"name": "domain"}).findChildren("option")]


    def get_mail_content(self, mail_id: str) -> BeautifulSoup:
        """
        Returns the content of the mail as a beautiful soup object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """                     
        r = self._session.get("https://disposableemail.co/view/"+mail_id)
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            main = soup.find("p", {"class": "d-flex mb-0"})
            if main: return main.span


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://disposableemail.co/messages")
        if r.ok:
            messages = r.json()["messages"]
            if messages == "":
                return []
            
            soup = BeautifulSoup(messages, "lxml")
            return [
            {
                "id": email["href"].rsplit("/", 1)[1],
                "from": (lis := email.find_all("li"))[0].text.strip(),
                "time": lis[2].text,
                "subject": lis[1].text  
            }
            for email in soup.find_all("a", {"class": "ws-generate-email-1"})]
                                            