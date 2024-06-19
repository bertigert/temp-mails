from time import sleep, time
from string import ascii_lowercase, digits
import random

import requests
from bs4 import BeautifulSoup


class Mailhole_de():
    """An API Wrapper around the https://mailhole.de/ website, slow in my testing"""

    def __init__(self, name: str=None):
        """
        Generate a random inbox
        name - name for the email, if None a random one is chosen\n
        """
        
        self._session = requests.Session()

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        self.domain = "mailhole.de"

        self.email = f"{self.name}@{self.domain}"

    
    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        Note that the content is a BeautifulSoup object
        """

        r = self._session.get("https://mailhole.de/?"+self.email)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            emails = []
            email_list = soup.find("div", {"id": "email-list"})
            for email in email_list.find_all("a", {"class": "list-group-item list-group-item-action email-list-item"}):
                data = {
                    "time": email.find("small").text,
                    "subject": email.find("p").text.strip(),
                }

                emails.append(data)

            for i, email in enumerate(email_list.find_all("div", {"class": "card-block email-body"})):
                emails[i]["content"] = email
            
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
        
        r = self._session.get(f"https://mailhole.de/?action=has_new_messages&address={self.email}&email_ids=")
        
        if not r.ok:
            return None
        
        old_length = int(r.text)

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            r = self._session.get(f"https://mailhole.de/?action=has_new_messages&address={self.email}&email_ids=")
            if not r.ok:
                return None
            
            if (int(r.text)) > old_length:
                inbox = self.get_inbox()
                if inbox:
                    return inbox[0]

            sleep(delay)
