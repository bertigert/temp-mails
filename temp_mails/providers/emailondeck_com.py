from bs4 import BeautifulSoup
import requests

from .._constructors import _WaitForMail

class Emailondeck_com(_WaitForMail):
    """An API Wrapper around the https://www.emailondeck.com/ website"""

    def __init__(self):
        """
        Generate a random inbox, please note that the site has a ratelimit for inboxes/hour
        """
        super().__init__(0)

        # All of this is reversed from the chrome extension, the website uses a different, captcha protected API

        self._session = requests.Session()
    
        r = self._session.get("https://www.emailondeck.com/ajax/ce-new-email.php")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self.email, self._token = r.text.split("|", 1)
        self.name, self.domain = self.email.split("@", 1)
        
    
    def get_mail_content(self, mail_id: str | int) -> BeautifulSoup:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content as a BeautifulSoup Object
        """
    
        r = self._session.get("https://www.emailondeck.com/email_iframe.php?msg_id="+str(mail_id))
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return soup.find("div", {"id": "inbox_message"})

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://www.emailondeck.com/ajax/messages.php")
        
        if r.ok:
            if r.text[0] == "0":
                return []
                        
            soup = BeautifulSoup(r.text.split("|", 3)[3], "lxml")

            emails = []
            for email in soup.find_all("div", {"class": "inbox_rows msglink"}):
                data = {
                    "id": email["name"],
                    "from": email.find("td", {"class": "desktop_only inbox_td_from"}).text,
                    "subject": email.find("td", {"class": "desktop_only inbox_td_subject"}).text,
                    "time": email.find("td", {"class": "inbox_td_received"}).text

                }
                emails.append(data)
            
            return emails
