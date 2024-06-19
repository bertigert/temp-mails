import json
from time import sleep, time
from datetime import datetime, timedelta, UTC

import requests
import websocket

from .._constructors import _generate_user_data

class Mailinator_com():
    """An API Wrapper around the https://www.mailinator.com/ website. Very fast from experience. See create_email function."""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        self._session = requests.Session()
        self._session.get("https://www.mailinator.com/v4/public/inboxes.jsp?to="+self.name)
        
        
        self._ws = websocket.create_connection("wss://www.mailinator.com/ws/fetchpublic", cookie="JSESSIONID="+self._session.cookies.get("JSESSIONID"))
        self._ws.send('{"cmd":"sub","channel":"' + self.name + '"}')
        
        while json.loads(self._ws.recv())["channel"] != "initial_msgs":
            pass

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has 1 domain.
        """
        return ["mailinator.com"]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://www.mailinator.com/fetch_public?msgid="+mail_id)
        if r.ok:
            return r.json()["data"]["parts"][1]["body"]
        

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox. Note that it takes a few seconds from receiving an email for this to update.
        """
        
        self._ws.send('{"cmd":"sub","channel":"' + self.name + '"}')
        while ( d := json.loads(self._ws.recv()) )["channel"] != "initial_msgs":
            pass

        return [{
            "id": email["id"],
            "from": email["fromfull"],
            "time": email["time"],
            "subject": email["subject"]
        } for email in d["msgs"]]


    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        """
        
        if timeout > 0:
            start = time()

        while True:
            data = json.loads(self._ws.recv())
            
            if data["channel"] == "msg":
                return {
                    "id": data["id"],
                    "from": data["fromfull"],
                    "time": f"{time()*1000-data["seconds_ago"]:.0f}",
                    "subject": data["subject"]
                }
            
            if timeout > 0 and time()-start >= timeout:
                return None
            