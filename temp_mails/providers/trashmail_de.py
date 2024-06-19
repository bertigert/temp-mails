import requests
from xml.etree import ElementTree

from .._constructors import _WaitForMail, _generate_user_data

class Trashmail_de(_WaitForMail):
    """An API Wrapper around the https://www.trashmail.de/ website. See https://github.com/msoftware/Trash-Mail/"""
    
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

        return ["trashmail.de"]


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the content of the mail as a html string
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.trashmail.de/mail.php?search={self.name}&nr={mail_id}")
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("http://trashmail.de/inbox-api.php?name="+self.name)
        
        if r.ok:
            root = ElementTree.fromstring(r.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}  # Namespace dictionary
            
            emails = []
            
            for entry in root.findall('atom:entry', ns):
                mail_id = entry.find('atom:id', ns).text
                if mail_id.startswith("urn:uuid"): # only is like this on the "0 Mails in Inbox" entry
                    return []
                
                data = {}
                data_string = entry.find('atom:content', ns).text
                
                for line in data_string.strip().split("\n"):
                    k, v = (part.strip() for part in line.split("=>"))
                    match k:
                        case "subject" | "from":
                            data[k] = v
                            continue
                        case "date":
                            data["time"] = v
                            continue
                        case "msgno":
                            data["id"] = v
                            continue
                emails.append(data)
            
            return emails

                                                   