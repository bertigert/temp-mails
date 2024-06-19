import threading
from time import time
import json

import requests
import websocket

from .._constructors import _generate_user_data

class Inboxes_com():
    """An API Wrapper around the https://inboxes.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        r = self.get_inbox()
        if r == None:
            raise Exception("Failed to create email")

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://inboxes.com/api/v2/domain")
        if r.ok:
            return [email["qdn"] for email in r.json()["domains"]]


    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns additional information about an email\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://inboxes.com/api/v2/message/"+mail_id)
        
        if r.ok:
            data = r.json()
            return {
                "from": data["f"],
                "content": data["html"]
            }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://inboxes.com/api/v2/inbox/"+self.email)
        if r.ok:
            return [{
                "id": email["uid"],
                "from": email["f"],
                "time": email["cr"],
                "subject": email["s"],
                "preview": email["ph"]
            } for email in r.json()["msgs"]]
        

    def wait_for_new_email(self, delay: None=None, timeout: int=60, is_ready_event: threading.Event=None) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        is_ready_event - used for indicating that the function is ready to receive emails
        """
        if timeout > 0: 
            start = time()

        r = self._session.get("https://inboxes.com/socket.io/?EIO=4&transport=polling")
        if not r.ok:
            return None
        
        ws_config = json.loads(r.text[1:])
        
        r = self._session.post("https://inboxes.com/socket.io/?EIO=4&transport=polling&sid="+ws_config["sid"], data="40")
        if not r.ok:
            return None
        
        def on_open(ws: websocket.WebSocketApp):
            ws.send("2probe")
            
        def on_message(ws: websocket.WebSocketApp, message: str):
            
            if message == "2":
                ws.send("3")
                
            if message == "3probe":
                ws.send("5")
                ws.send(f'42["join_room","{self.email}"]')
                if is_ready_event: is_ready_event.set()

            elif message.startswith("42"):
                data = json.loads(message[2:])
                if data[0] == "ping" and data[1] == "hi":
                    nonlocal email_data
                    inbox = self.get_inbox()
                    if data:
                        email_data = inbox[0]
                    ws.close()
        
            if timeout > 0 and time()-start >= timeout:
                ws.close()

        email_data = None
        ws = websocket.WebSocketApp(f"wss://inboxes.com/socket.io/?EIO=4&transport=websocket&sid="+ws_config["sid"], 
                                    on_open=on_open, on_message=on_message)
        ws.run_forever(suppress_origin=True)
        return email_data