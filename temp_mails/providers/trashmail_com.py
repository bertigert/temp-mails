import requests
from bs4 import BeautifulSoup

from .._constructors import _WaitForMail, _generate_user_data


class Trashmail_com(_WaitForMail):
    """An API Wrapper around the https://www.trash-mail.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None, password: str="123"):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        password - a password which is required for some domains
        """
        super().__init__(0)

        self._session = requests.Session()
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        
        valid_domains = self.get_valid_domains(True)
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, valid_domains[0])

        r = self._session.get("https://www.trash-mail.com/inbox/", verify=False)
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        requires_password = valid_domains[1][valid_domains[0].index(self.domain)]
        r = self._session.post("https://www.trash-mail.com/inbox/", data={
            "form-postbox": self.name,
            "form-domain": f"{self.domain}---{requires_password}", # get the flag of the domain
            "form-password": password if requires_password == "1" else ""
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)


    @staticmethod
    def get_valid_domains(_return_flag: bool=False) -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list\n
        _return_flag - also return the flag which determines if the domain requires a password, needed for creation of an email
        """
        
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get("https://www.trash-mail.com/inbox/", verify=False)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            domain_list = soup.find("select", {"id": "form-domain-id"}).findChildren()
            domains = [domain.text for domain in domain_list]
            
            return domains if not _return_flag else (domains, [domain["value"][-1:] for domain in domain_list])


    def get_mail_content(self, mail_id: int | str) -> BeautifulSoup:
        """
        Returns the content of a given mail_id as a Beautifulsoup object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.trash-mail.com/en/mail/message/id/{mail_id}")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return soup.find("div", {"class": "message-content"})

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.trash-mail.com/inbox/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("table", {"class": "table table-striped table-bordered table-hover table-messages"})
            return [{
                    "id": email.a["nr"],
                    "from": email.a.div.find("p", {"class": "message-from"}).text,
                    "subject": email.a.div.find("p", {"class": "message-subject"}).text,
                    "date": email.a.div.find("p", {"class": "message-date"}).text,
                    "preview": email.a.div.find("p", {"class": "message-text"}).text
                } 
                for email in email_list.find_all("td", {"class": "message-td"})
                ] if email_list else []
        