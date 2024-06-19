import json
import threading
from time import time

from bs4 import BeautifulSoup
import requests
import websocket

from .._constructors import _generate_user_data

class Mailseven_io():
    """An API Wrapper around the https://www.mail7.io/ website"""

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
        
        r = self._session.get("https://console.mail7.io/admin/inbox/inbox")
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        self._apikey = soup.find("span", {"class": "headerData"}).script.text.split('apikey: "', 1)[1].split('"', 1)[0]
        
    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has one domain.
        """
        return ["mail7.io"]
    


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://api.mail7.io/inbox?callback=INBOX&apikey={self._apikey}&to={self.name}&domain={self.domain}")
        if r.ok:
            data = json.loads(r.text[6:-1])
            if data["status"] == "success":
                return [{
                    "id": email["_id"],
                    "from": email["mail_source"]["from"]["value"][0]["address"],
                    "time": email["mail_source"]["date"],
                    "subject": email["mail_source"]["subject"],
                    "content": email["mail_source"]["html"]
                } for email in data["data"]]

    def wait_for_new_email(self, delay: None=None, timeout: int=60, is_ready_event: threading.Event=None) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        is_ready_event - used for indicating that the function is ready to receive emails
        """
        # the websocket receives emails for every inbox, privacy not stonks

        if timeout > 0: 
            start = time()

        def on_open(ws: websocket.WebSocketApp):
            ws.send("2probe")
            ws.send("5")
            if is_ready_event: is_ready_event.set()
            
        def on_message(ws: websocket.WebSocketApp, message: str):
            
            if message.startswith("42"):
                nonlocal manual_stop
                data = json.loads(message[2:])
                
                if data[0].startswith("get_inbox"): #== f"get_inbox{self.email}":
                    nonlocal email_data
                    email = data[1]["data"][0]
                    
                    email_data = {
                        "id": email["_id"],
                        "from": email["mail_source"]["from"]["value"][0]["address"],
                        "time": email["mail_source"]["date"],
                        "subject": email["mail_source"]["subject"],
                        "content": email["mail_source"]["html"]
                    }

                    #print(f"Email received from {email_data["from"]} to {email["to_username"]} with subject {email_data["subject"]}")
                    
                    if email["mail_source"]["to"]["value"][0]["address"] == self.email:
                        manual_stop = True
                        ws.close()
           
            if timeout > 0 and time()-start >= timeout:
                manual_stop = True
                ws.close()

        def on_close(ws, *args):
            if not manual_stop:
                if timeout > 0 and time()-start >= timeout:
                    return None
                
                ws.close()
                
                ws = websocket.WebSocketApp(f"wss://api.mail7.io/socket.io/?EIO=3&transport=websocket", 
                                            on_open=on_open, on_message=on_message, on_pong=lambda *args: ws.send("2"), on_close=on_close)
                ws.run_forever(ping_interval=25, ping_timeout=20)
                
        email_data = None
        manual_stop = False
        
        ws = websocket.WebSocketApp(f"wss://api.mail7.io/socket.io/?EIO=3&transport=websocket", 
                                    on_open=on_open, on_message=on_message, on_pong=lambda *args: ws.send("2"), on_close=on_close)
        ws.run_forever(ping_interval=25, ping_timeout=20)
        
        return email_data