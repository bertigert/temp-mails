import html
from bs4 import BeautifulSoup
import requests


from .._constructors import _WaitForMail, _generate_user_data


class Tempr_email(_WaitForMail):
    """An API Wrapper around the https://tempr.email/ website"""
    # NOTE: They block dev tools (you cant read emails)
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
        
        valid_domains = self.get_valid_domains(True)
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, valid_domains[0])

        r = self._session.post("https://tempr.email/", data={
            "LocalPart": self.name,
            "DomainType": "public",
            "DomainId": valid_domains[1][valid_domains[0].index(self.domain)],
            "PrivateDomain": "",
            "Password": "",
            "LoginButton": "",
            "CopyAndPaste": self.email
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)


    @staticmethod
    def get_valid_domains(_return_id: bool=False) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list\n
        _return_id - wether to return the domain id or not (required for creating the email)
        """
        
        r = requests.get("https://tempr.email/")

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domain_list = soup.find("select", {"id": "LoginDomainId"}).findChildren()
            domains = [html.unescape(domain.text.removesuffix(" (PW)").strip()) for domain in domain_list]
            
            return domains if not _return_id else (domains, [domain["value"] for domain in domain_list])
        
            
    def get_mail_content(self, mail_id: str) -> BeautifulSoup:
        """
        Returns the content of a given mail_id as a beautifulsoup object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """                     
        r = self._session.get(f"https://tempr.email/message-{mail_id}-mailVersion=html.htm")
        if r.ok:
            r = self._session.get(f"https://tempr.email/public/messages/getHtmlMessage.php?file=htmlMessage-{mail_id}_UTF-8.htm")
            soup = BeautifulSoup(r.text, "lxml")
            return soup.body


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://tempr.email/inbox.htm")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("div", {"id": "Inbox"})
            return [
                {
                    "id": email.input["value"],
                    "time": (t := email.find("div", {"class": "Date"}).find_all("span"))[0].text + " " + t[1].text,
                    "from": (h := email.find("div", {"class": "Head"}).a.get_text(separator="|").split("|", 1))[0],
                    "subject": h[1]
                } 
                for email in email_list.find_all("div", recursive=False)
            ] if email_list else []
        