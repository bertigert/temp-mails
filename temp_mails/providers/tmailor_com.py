import json
from time import time
import requests
import websocket

from .._constructors import GLOBAL_UA

class Tmailor_com():
    """
    An API Wrapper around the https://tmailor.com/ website.
    """
    def __init__(self):
            """
            Generate a random inbox
            """
           
            self._session = requests.Session()
            self._session.headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9,de-DE;q=0.8,de;q=0.7",
                "origin": "https://tmailor.com",
                "user-agent": GLOBAL_UA
            }

            self._link = "https://tmailor.com"
            
            r = self._session.post(self._link+"/api/", json={
                "action": "newemail",
                "curentToken": "",
                "google_code": "",
                "wat": "",
                "f": ""
            })
            if not r.ok:
                raise Exception("Failed to create email, status", r.status_code)
            
            data = r.json()
            
            if data["client-block"] == 1:
                raise Exception("Error creating email", data["msg"])

            self._email_data = {
                "email": data["email"],
                "create": data["create"],
                "sort": data["sort"],
                "client-block": 0,
                "accesstoken": data["accesstoken"]
            }
            self._token = None
            
            self.email = data["email"]
            self.name, self.domain = self.email.split("@", 1)


    def _set_token(self):
        def on_open(ws):
            ws.send(json.dumps(self._email_data))
        
        def on_message(ws, message: str):
            message = json.loads(message)
            
            if "k" in message:
                self._token = message["k"]
                ws.close()

        ws = websocket.WebSocketApp("wss" + self._link.removeprefix("https") +"/wss", on_message=on_message, on_open=on_open)
        ws.run_forever()


    def get_mail_content(self, mail_id: list[str]) -> dict[str]:
        """
        Returns the content of a given mail_id (full subject, content)\n
        Args:\n
        mail_id - the id of the mail you want the content of ( [email_id, other_email_id] )
        """
       
        if not self._token:
            self._set_token()

        r = self._session.post(self._link+"/api/", json={
            "action": "read",
            "accesstoken": self._email_data["accesstoken"],
            "email_token": mail_id[1],
            "email_code": mail_id[0],
            "wat": self._token,
            "f": ""
        })

        if r.ok and (d := r.json())["msg"] == "ok":
            return {
                "subject": d["data"]["subject"],
                "content": d["data"]["body"]
            }
            

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        """

        if not self._token:
            self._set_token()
        
        r = self._session.post(self._link+"/api/", json={
            "action": "listinbox",
            "accesstoken": self._email_data["accesstoken"],
            "wat": self._token,
            "f": ""
        })
        
        if r.ok and (d := r.json())["msg"] == "ok":
            return [{
                "id": ( email["id"], email["email_id"] ),
                "time": email["receive_time"],
                "from": email["sender_email"],
                "subject": email["subject"]
            } for email in d["data"].values()] if d["data"] else []
        

    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used
        """

        if timeout > 0: 
            start = time()

        def on_open(ws):
            ws.send(json.dumps(self._email_data))

        def on_message(ws, message: str):
            nonlocal email_data
                
            if message == "newinbox":
                email_data = self.get_inbox()[0] # k is (hopefully) always sent before newinbox
                ws.close()
                
            message = json.loads(message)
            
            if "k" in message:
                self._token = message["k"]

            if timeout > 0 and time()-start >= timeout:
                ws.close()

        def on_error(ws, error):
            if timeout > 0 and time()-start >= timeout:
                ws.close()

        email_data = None

        ws = websocket.WebSocketApp("wss" + self._link.removeprefix("https") +"/wss", on_message=on_message, on_error=on_error, on_open=on_open)
        ws.run_forever(ping_interval=10, ping_payload="ping")
        
        return email_data