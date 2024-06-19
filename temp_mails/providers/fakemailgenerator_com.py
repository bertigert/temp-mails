import json
from time import time
from bs4 import BeautifulSoup
import requests
import websocket


from .._constructors import _generate_user_data

class Fakemailgenerator_com():
    """An API Wrapper around the https://www.fakemailgenerator.com/ website"""

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

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://www.fakemailgenerator.com/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            emails = soup.find("ul", {"class": "dropdown-menu"})
            
            return [email.text[1:] for email in emails.find_all("a")]


    def get_mail_content(self, mail_id: int | str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.fakemailgenerator.com/email/{self.domain}/{self.name}/message-{mail_id}/")
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://www.fakemailgenerator.com/inbox/{self.domain}/{self.name}/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("ul", {"id": "email-list"})
            if not email_list:
                return []
            
            emails = []
            for email in email_list.find_all("a"):
                data_divs = email.div.find_all("div", recursive=False)
                emails.append({
                    "id": email["href"].split("message-", 1)[1].replace("/", ""),
                    "from": data_divs[0].p.text,
                    "subject": data_divs[1].p.text,
                    "time": data_divs[2].p.text
                })                               

            return emails

    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        """

        if timeout > 0: 
            start = time()

        r = self._session.get("https://ws.fakemailgenerator.com/socket.io/?EIO=3&transport=polling")
        if not r.ok:
            return None
        
        ws_config = json.loads(r.text[5:])
        
        def on_open(ws: websocket.WebSocketApp):
            ws.send("2probe")

        def on_message(ws: websocket.WebSocketApp, message: str):
            if message == "3probe":
                ws.send("5")
                ws.send(f'42["watch_address", "{self.email}"]')

            elif message.startswith("42"):
                data = json.loads(message[2:])
                if data[0] == "incoming_email" and "emailid" in (email := json.loads(data[1])):
                    nonlocal email_data
                    email_data = {
                        "id": email["emailid"],
                        "from": email["sender"],
                        "time": email["timeonly"],
                        "subject": email["subject"]
                    }
                    ws.close()
        
            if timeout > 0 and time()-start >= timeout:
                ws.close()


        email_data = None
        ws = websocket.WebSocketApp(f"wss://ws.fakemailgenerator.com/socket.io/?EIO=3&transport=websocket&sid="+ws_config["sid"], on_open=on_open, on_message=on_message, on_pong=lambda *args: ws.send("2"))
        ws.run_forever(ping_interval=ws_config["pingInterval"]/1000)
        return email_data