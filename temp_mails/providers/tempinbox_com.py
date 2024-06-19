from time import sleep, time

from bs4 import BeautifulSoup
import requests

from .._constructors import SSLAdapterCF

class Tempinbox_com():
    """An API Wrapper around the https://temp-inbox.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        
        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        self._session.mount("https://", SSLAdapterCF)

        r = self._session.get("https://temp-inbox.com/")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        self.email = soup.find("input", {"id": "tempInbox"})["value"]
        
        self.name, self.domain = self.email.split("@", 1)

    
    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        Note that the content is a BeautifulSoup object
        """

        r = self._session.get("https://temp-inbox.com/")

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            emails = []
            for head in soup.find_all("tr", {"class": "rowHead"}):
                sender, subject = head.find_all("td")
                emails.append({
                    "subject": subject.text,
                    "from": sender.text
                })

            for i, head in enumerate(soup.find_all("td", {"class": "messageBody"})):
                emails[i]["content"] = head.div

            return emails
        
    def wait_for_new_email(self, delay: float=2.0, timeout: int=60):
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """
        if timeout > 0: 
            start = time()
        
        r = self._session.get("https://temp-inbox.com/checker.php?email="+self.email)
        
        if not r.ok:
            return None

        old_length = int(r.text)

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            r = self._session.get("https://temp-inbox.com/checker.php?email="+self.email)
            if not r.ok:
                return None

            if (int(r.text)) > old_length:
                inbox = self.get_inbox()
                if inbox:
                    return inbox[0]

            sleep(delay)
                                                                                    