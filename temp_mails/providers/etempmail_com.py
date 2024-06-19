from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail, _generate_user_data

class Etempmail_com(_WaitForMail):
    """An API Wrapper around the https://etempmail.com/ website"""

    def __init__(self, name: None=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - the name is not customizable, only for compatability\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()

        valid_domains = self.get_valid_domains(True)
        _, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, valid_domains[0])

        
        r = self._session.post("https://etempmail.com/getEmailAddress")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        email = data["address"]
        self.name, domain = email.split("@", 1)
        if domain != self.domain:
            r = self._session.post("https://etempmail.com/changeEmailAddress", data={"id": valid_domains[1][valid_domains[0].index(self.domain)]})
            if not r.ok:
                raise Exception("Failed to create email (domain change), status", r.status_code)
            
        self.email = f"{self.name}@{self.domain}"

        # check if it actually works, their api is stupid and randomly returns shit smh
        try:
            self.get_inbox()
        except requests.exceptions.JSONDecodeError:
            return self.__init__(domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains(_return_id: bool=False) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        _return_id - wether to also return the id of the domain, necessary for specifying a domain on creation
        """

        r = requests.get("https://etempmail.com/script.js")
        if r.ok:
            soup = BeautifulSoup(r.text.split("html: `", 1)[1].split("`", 1)[0], "lxml")
            domain_list = soup.find_all(lambda tag: tag.name == "option" and tag["value"] != "")
            domains = [domain.text for domain in domain_list]
            return domains if not _return_id else (domains, [domain["value"] for domain in domain_list])


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://etempmail.com/getInbox")
        if r.ok:
            emails = r.json()
            return [{
                "from": email["from"],
                "time": email["date"], 
                "subject": email["subject"],
                "content": email["body"]
            } for email in emails]
