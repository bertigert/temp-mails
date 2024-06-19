import json
import random
from string import ascii_lowercase, digits
from time import time
import threading

import requests
import websocket

class Byom_de():
    """An API Wrapper around the https://www.byom.de/ website. From experience very fast."""

    def __init__(self, name: str=None, domain: None=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - not used, simply for compatability
        exclude - a list of domain to exclude from the random selection\n
        """

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        self.domain = "byom.de"
        self.email = f"{self.name}@{self.domain}"

        self._session = requests.Session()

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (only byom.de)
        """
        return ["byom.de"]

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        """
        
        r = self._session.get(f"https://api.byom.de/mails/{self.name}")
        if r.ok:
            return [{
                "from": email["from"],
                "time": email["created_at"],
                "subject": email["subject"],
                "content": email["html"],
            } for email in r.json()]


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60, is_ready_event: threading.Event=None):
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability\n
        is_ready_event - used for indicating that the function is ready to receive emails
        """
        if timeout > 0: start = time()        

        r = self._session.get("https://byom-notifier.herokuapp.com/faye?message=%5B%7B%22channel%22%3A%22%2Fmeta%2Fhandshake%22%2C%22version%22%3A%221.0%22%2C%22supportedConnectionTypes%22%3A%5B%22websocket%22%2C%22eventsource%22%2C%22long-polling%22%2C%22cross-origin-long-polling%22%2C%22callback-polling%22%5D%2C%22id%22%3A%221%22%7D%5D")
        if not r.ok:
            return None
        
        data = json.loads(r.text[19:-3])

        def on_open(ws):
            ws.send(json.dumps([{"channel":"/meta/connect","clientId": data["clientId"],"connectionType":"websocket","id": "4"}]))
            ws.send(json.dumps([{"channel":"/meta/subscribe","clientId": data["clientId"],"subscription":f"/messages/{self.name}"}]))
            if is_ready_event: is_ready_event.set()

        def on_message(ws, msg):
            msg = json.loads(msg)[0]
            
            if msg["channel"] == "/meta/connect":
                ws.send(json.dumps([{"channel":"/meta/connect","clientId": data["clientId"],"connectionType":"websocket","id": str(int(msg["id"])+1)}]))

            if msg["channel"] == f"/messages/{self.name}" and msg["data"] == "New mail":
                nonlocal email_data
                emails = self.get_inbox()
                if emails:
                    email_data = emails[-1]
                ws.close()

            if timeout > 0 and time()-start >= timeout:
                ws.close()
                

        email_data = None
        ws = websocket.WebSocketApp(f"wss://byom-notifier.herokuapp.com/faye", 
                                        on_message=on_message, on_open=on_open
                                    )
        ws.run_forever()
        
        return email_data