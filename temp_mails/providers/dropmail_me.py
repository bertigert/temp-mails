import json
from time import time

import requests
import websocket


class Dropmail_me():
    """An API Wrapper around the https://dropmail.me/ website. Very fast from experience."""

    def __init__(self):
        """
        Generate a random inbox\n
        """
        ### This is based on pure websockets
        
        self._session = requests.Session()

        self._ws = websocket.create_connection("wss://dropmail.me/websocket")
        self._ws.settimeout(60)

        self.valid_domains = self.sid = None
        while not self.valid_domains and not self.sid:
            r = self._ws.recv()
            if r.startswith("S"): # some id
                self._sid = json.loads(r[1:])["id"]
            elif r.startswith("A"): # random email
                self.email, self._password = r[1:].split(":", 1)
                self.name, self.domain = self.email.split("@", 1)
            elif r.startswith("D"):
                self.valid_domains = r[1:].split(",")
        
    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://dropmail.me/download/clean_html/web:{self._sid}/{mail_id}")
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        There is no server sided inbox
        """
        return None

    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        """
        
        self._ws.settimeout(timeout)
        
        if timeout > 0: 
            start = time()

        while True:
            r = self._ws.recv()
            if r.startswith("I"):
                data = json.loads(r[1:])
                self._ws.settimeout(60)
                return {
                    "id": data["ref"],
                    "from": data["from_mail"],
                    "time": data["received"],
                    "subject": data["subject"],
                    "preview": data.get("text", "")
                }

            if timeout > 0 and time()-start >= timeout:
                return None
            
            