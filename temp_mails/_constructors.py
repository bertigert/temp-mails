from time import sleep, time
from typing import Literal
from string import ascii_lowercase, digits
import random
import json
from base64 import b64decode
import ssl

import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import websocket


def _generate_user_data(name: str=None, domain:str=None, exclude: list[str]=None, valid_domains: list[str]=None, validate_domain: bool=True):
    """Generates a random name and domain for a given temp mail object."""
    
    name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(6, 15))) # some sites do not support names >= 16

    #valid_domains = valid_domains or valid_domains
    if domain:
        if validate_domain:
            domain = domain if domain in valid_domains else random.choice(valid_domains)
    else:
        if exclude:
            valid_domains = [domain for domain in valid_domains if domain not in exclude]
        domain = random.choice(valid_domains)

    email = f"{name}@{domain}"

    return name, domain, email, valid_domains

class _WaitForMail:
    def __init__(self, indx: Literal[0, -1]):
        self.indx = indx

    def wait_for_new_email(self, delay: float=2.0, timeout: int=60, start_length: int=None):
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout\n
        start_length - the length of the inbox without the new email, skips one request, useful if email is received too fast
        """

        if timeout > 0: 
            start = time()
        
        old_length = start_length if start_length is not None else len(self.get_inbox()) 
        
        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return data[self.indx]
            
            sleep(delay)

class CreateSSLAdapterCF(HTTPAdapter):
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

SSLAdapterCF: HTTPAdapter = CreateSSLAdapterCF()

def _deCFEmail(fp): # https://stackoverflow.com/a/58111681
    try:
        r = int(fp[:2],16)
        email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
        return email
    except ValueError:
        pass


class _Livewire(_WaitForMail):
    def __init__(self, urls: str, order: Literal[0, -1], name: str=None, domain: str=None, exclude: list[str]=None):
        super().__init__(order)

        self.urls = urls

        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }


        # Get required data for email creation and more
        r = self._session.get(self.urls["base"])
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # Create Email
        soup = BeautifulSoup(r.text, "lxml")
        
        
        data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: false" in tag.get("x-data", ""))["wire:initial-data"])
        # data = json.loads(soup.find("div", {"x-data": self.strings["first_data"]})["wire:initial-data"])

        self.valid_domains = data["serverMemo"]["data"]["domains"] if domain != "gmail.com" else ["gmail.com"] # scuffed hotfix for websites (atm only https://tmail.io/) which implement their gmail domains seperate from other domains
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.valid_domains)
        
        self._token = soup.find("input", {"type": "hidden"})["value"]

        payload = {
            "fingerprint": data["fingerprint"],
            "serverMemo": data["serverMemo"],
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "syncEmail",
                        "params": [
                            self.email
                        ]
                    }
                }
            ]
        }
                 
        r = self._session.post(self.urls["actions"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # Get the data required for checking messages

        
        data = json.loads(soup.find(lambda tag: (tag.name == "div" or tag.name == "main") and "id: 0" in tag.get("x-data", ""))["wire:initial-data"])
        # data = json.loads(soup.find(self.strings["second_data"][0], {"x-data": self.strings["second_data"][1]})["wire:initial-data"])

        payload = {
            "fingerprint": data["fingerprint"],
            "serverMemo": data["serverMemo"],
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "syncEmail",
                        "params": [
                            self.email
                        ]
                    }
                },
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "fetchMessages",
                        "params": []
                    }
                }
            ]
        }

        r = self._session.post(self.urls["app"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        new_data = r.json()
        
        self._fingerprint = data["fingerprint"]
        self._servermemo = data["serverMemo"]
        self._servermemo["htmlHash"] = new_data["serverMemo"].get("htmlHash", data["serverMemo"]["htmlHash"]) # Tempmail.gg doesnt have it in new_data
        self._servermemo["data"].update(new_data["serverMemo"]["data"])
        self._servermemo["checksum"] = new_data["serverMemo"]["checksum"]

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        payload = {
            "fingerprint": self._fingerprint,
            "serverMemo": self._servermemo,
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "fetchMessages",
                        "params": []
                    }
                }
            ]
        }

        r = self._session.post(self.urls["app"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if r.ok:
            data = r.json()
            return [
                {
                    "id": email["id"],
                    "time": email["date"],
                    "subject": email["subject"],
                    "content": email["content"]
                } 
                for email in data["serverMemo"]["data"]["messages"]
            ] if ("data" in data["serverMemo"] and not "error" in data["serverMemo"]["data"]) else []


class _Livewire2(_WaitForMail):
    def __init__(self, urls: str, order: Literal[0, -1], cf_protx: bool=False, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        strings - dict with elements (+attributes) to search for in order to get data\n
        url - dict with different routes\n
        cf_protx - if the website has a cf protection which requires a different ssl version
        """
        
        super().__init__(order)

        self.urls = urls

        self._session = requests.Session()
        
        if cf_protx:
            self._session.mount("https://", SSLAdapterCF)
        
        self._session.headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }

        r = self._session.get(self.urls["base"])
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        
        data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: true" in tag.get("x-data", ""))["wire:initial-data"])
        # data = json.loads(soup.find("div", {"x-data": self.strings["first_data"]})["wire:initial-data"])

        self.valid_domains = data["serverMemo"]["data"]["domains"]
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.valid_domains)
        self._token = soup.find("input", {"type": "hidden"})["value"]

        
        # prepare email creation
        payload = {
            "fingerprint": data["fingerprint"],
            "serverMemo": data["serverMemo"],
            "updates": [
                {
                    "type": "syncInput",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "name": "user",
                        "value": self.name
                    }
                },
                {
                    "type": "callMethod",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "method": "setDomain",
                        "params": [
                            self.domain
                        ]
                    }
                }
            ]
        }
        
        r = self._session.post(self.urls["actions"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # create email
        data = r.json()
        payload["serverMemo"]["data"].update(data["serverMemo"]["data"])
        payload["updates"] = [
            {
                "type": "callMethod",
                "payload": {
                    "id": "fhdk",
                    "method": "create",
                    "params": []
                }
            }
        ]
        payload["serverMemo"]["checksum"] = data["serverMemo"]["checksum"]
        
        r = self._session.post(self.urls["actions"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # this is for a mail limit/day on some websites
        d = r.json()
        
        if d.get("effects", {}).get("dispatches", [{}])[0].get("data", {}).get("type") == "error": 
            raise Exception("Failed to create email, status:", d.get("effects", {}).get("dispatches", [{}])[0].get("data", {}).get("message"))

        # continue with next steps as usual
        
        r = self._session.get(self.urls["mailbox"], headers={
            "Referer": self.urls["base"],
        })
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")
        data = json.loads(soup.find(lambda tag: tag.name == "div" and "in_app: false" in tag.get("x-data", ""))["wire:initial-data"])
        # data = json.loads(soup.find("div", {"x-data": self.strings["first_data2"]})["wire:initial-data"])

        payload = {
            "fingerprint": data["fingerprint"],
            "serverMemo": data["serverMemo"],
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "syncEmail",
                        "params": [
                            self.email
                        ]
                    }
                }
            ]
        }

        r = self._session.post(self.urls["actions"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        data = json.loads(soup.find(lambda tag: (tag.name == "div" or tag.name == "main") and "id: 0" in tag.get("x-data", ""))["wire:initial-data"])
        # data = json.loads(soup.find(self.strings["second_data"][0], {"x-data": self.strings["second_data"][1]})["wire:initial-data"])

        payload = {
            "fingerprint": data["fingerprint"],
            "serverMemo": data["serverMemo"],
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "syncEmail",
                        "params": [
                            self.email
                        ]
                    }
                },
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "fetchMessages",
                        "params": []
                    }
                }
            ]
        }

        r = self._session.post(self.urls["app"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        new_data = r.json()
        
        if new_data["serverMemo"].get("data", {}).get("error"):
            raise Exception("Failed to create email, error", new_data["serverMemo"]["data"]["error"])

        self._fingerprint = data["fingerprint"]
        self._servermemo = data["serverMemo"]
        self._servermemo["htmlHash"] = new_data["serverMemo"].get("htmlHash", data["serverMemo"]["htmlHash"]) # Tempmail.gg doesnt have it in new_data
        self._servermemo["data"].update(new_data["serverMemo"]["data"])
        self._servermemo["checksum"] = new_data["serverMemo"]["checksum"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """
        
        payload = {
            "fingerprint": self._fingerprint,
            "serverMemo": self._servermemo,
            "updates": [
                {
                    "type": "fireEvent",
                    "payload": {
                        "id": "".join(random.choices(ascii_lowercase+digits, k=4)),
                        "event": "fetchMessages",
                        "params": []
                    }
                }
            ]
        }

        r = self._session.post(self.urls["app"], json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if r.ok:
            data = r.json()
            return [{
                    "id": email["id"],
                    "time": email["date"],
                    "subject": email["subject"],
                    "from": email.get("sender_email"),
                    "content": email["content"]
            } for email in data["serverMemo"]["data"]["messages"]
            ] if ("data" in data["serverMemo"] and not "error" in data["serverMemo"]["data"]) else []



class _Web2(_WaitForMail):
    def __init__(self, urls: dict, cf_protx: bool=False):
        """
        Generate a random inbox
        """
        
        super().__init__(-1)
        self.urls = urls

        self._session = requests.Session()

        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        if cf_protx:
            self._session.mount("https://", SSLAdapterCF)

        r = self._session.post(self.urls["mailbox"])

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["mailbox"]
        self.name, self.domain = self.email.split("@", 1)

        self._token = data["token"]
        self._session.headers["Authorization"] = "Bearer " + self._token


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """

        r = self._session.get(self.urls["messages"])
        
        if r.ok:
            return [
                {
                    "id": mail["_id"],
                    "time": mail["receivedAt"],
                    "from": mail["from"],
                    "subject": mail["subject"],
                    "preview": mail["bodyPreview"]
                }
            for mail in r.json()["messages"]] 

    
    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a mail as a html string\n
        mail_id - id of the message
        """
    
        r = self._session.get(self.urls["messages"]+mail_id)
        
        if r.ok:
            return r.json()["bodyHtml"]



class _Minuteinbox_etc(_WaitForMail):
    def __init__(self, base_url: str):
        """
        Generate a random inbox
        """
        
        super().__init__(0)
        self.base_url = base_url

        self._session = requests.Session()
        
        self._session.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    
        r = self._session.get(base_url+"/index/index")

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = json.loads(r.content.decode("utf-8-sig"))

        self.email: str = data["email"]
        self.name, self.domain = self.email.split("@", 1)


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content as a string
        """
    
        r = self._session.get(f"{self.base_url}/email/id/{mail_id}")
        if r.ok:
            return r.text.split("\n", 1)[1]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(self.base_url+"/index/refresh")
        
        if r.ok:
            # the names of the variables are really fucked so we reformat them
            
            resp = json.loads(r.content.decode("utf-8-sig"))[:-1]
            return [{
                    "id": mail["id"],
                    "time": mail["kdy"],
                    "from": mail["od"],
                    "subject": mail["predmet"]
                } for mail in resp]
            
    



class _Mailcare(_WaitForMail):
    def __init__(self, base_url: str, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        super().__init__(0)
        self.base_url = base_url

        self._session = requests.Session()
        
        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
    
    
    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"{self.base_url}/api/emails/{mail_id}", headers={"Accept": "text/html,text/plain"})
        if r.ok:
            return r.text.split("</a><br>", 1)[1] # remove ad


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """
        
        r = self._session.get(f"{self.base_url}/api/emails?inbox={self.email}")
        
        if r.status_code == 404:
            return []
        if r.ok:
            return r.json()["data"]



class _Tmailor_Tmail_Cloudtempmail:

    def __init__(self, host: Literal["https://tmailor.com/", "https://tmail.ai/", "https://cloudtempmail.com/"]):
        """
        Generate a random inbox
        """
        # pertera.com,ipxwan.com,x1ix.com,1sworld.com,videotoptop.com,bookgame.org,likemovie.net,s3k.net,mp3oxi.com,cloudtempmail.net,nextsuns.com,aluimport.com,happy9toy.com,leechchannel.com

        self._session = requests.Session()
        
        r = self._session.get(host)
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        self.link = r.text.split('web_graph="', 1)[1].split('"', 1)[0]
        
        r = self._session.post(self.link+"/email/wtf", data={"type": "newemail"})
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()
        
        if data["msg"] == "actionblock":
            raise Exception("Ratelimited")

        if data["msg"] == "error_no_domain":
            raise Exception("Failed to create email: " + data["contents"])

        self.email_data = {
            "email": data["email"],
            "create": data["create"],
            "sort": data["sort"],
            "add": data["create"],
            "accesstoken": data["accesstoken"]
        }
        
        self.email = data["email"]
        self.name, self.domain = self.email.split("@", 1)

        # register the email
        def on_message(ws, message: str):
            message = json.loads(message)
            
            if message["msg"] == "welcome":
                ws.send(json.dumps({
                    "action": "newemail",
                    "accesstokenx": "",
                    "accesstoken": self.email_data["accesstoken"]
                }))
                ws.close()

        ws = websocket.WebSocketApp("wss" + self.link.removeprefix("https") +"/wss", on_message=on_message)
        ws.run_forever()


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """
        
        def on_open(ws):
            ws.send(json.dumps({
                    "action": "read",
                    "email": self.email,
                    "accesstoken": self.email_data["accesstoken"],
                    "email_id": mail_id
            }))

        def on_message(ws, message: str):
            message = json.loads(message)
            
            if message["msg"] == "welcome":        
                ws.send(json.dumps({
                    'email': self.email, 
                    'create': self.email_data["create"], 
                    'sort': self.email_data["sort"], 
                    'add': self.email_data["sort"], 
                    'accesstoken': self.email_data["accesstoken"]
                }))

            elif message["msg"] == "updateinbox":
                nonlocal email_data
                
                if message["lists"]:
                    email_data = b64decode(message["lists"][0]["content"]).decode()
                
                ws.close()

        email_data = None

        ws = websocket.WebSocketApp("wss" + self.link.removeprefix("https") +"/wss", on_message=on_message, on_open=on_open)
        ws.run_forever()
        
        return email_data


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        """

        def on_message(ws, message: str):
            message = json.loads(message)
            
            if message["msg"] == "welcome":
                ws.send(json.dumps({
                    'email': self.email, 
                    'create': self.email_data["create"], 
                    'sort': self.email_data["sort"], 
                    'add': self.email_data["sort"], 
                    'accesstoken': self.email_data["accesstoken"]
                }))

            elif message["msg"] == "ok":
                nonlocal email_data
                email_data = []
                
                if message["lists"]:
                    for email in message["lists"]:
                        email_data.append({
                            "id": email["email_id"],
                            "subject": email["subject"],
                            "from": email["sender_email"],
                            "time": email["receive_time"],
                        })
                
                ws.close()

        email_data = None

        ws = websocket.WebSocketApp("wss" + self.link.removeprefix("https") +"/wss", on_message=on_message)
        ws.run_forever()
        
        return email_data
        

    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used
        """

        if timeout > 0: 
            start = time()

        def on_message(ws, message: str):
            nonlocal new_msg
            message = json.loads(message)
            
            match message["msg"]:
                case "welcome":
                    ws.send(json.dumps({
                        'email': self.email, 
                        'create': self.email_data["create"], 
                        'sort': self.email_data["sort"], 
                        'add': self.email_data["sort"], 
                        'accesstoken': self.email_data["accesstoken"]
                    }))

                case "ok":
                    self.email_data["client_key"] = message["client_key"]
                    
                    nonlocal email_data
                    if new_msg:
                        email_data = message["lists"][0]
                        email_data = {
                            "id": email_data["email_id"],
                            "subject": email_data["subject"],
                            "from": email_data["sender_email"],
                            "time": email_data["receive_time"],
                        }
                        ws.close()

                case "checkmailnow":
                    ws.send(json.dumps(self.email_data))
                    new_msg = True

            if timeout > 0 and time()-start >= timeout:
                ws.close()


        def on_error(ws, error):
            if timeout > 0 and time()-start >= timeout:
                ws.close()

        email_data = None
        new_msg = False

        ws = websocket.WebSocketApp("wss" + self.link.removeprefix("https") +"/wss", on_message=on_message, on_error=on_error)
        ws.run_forever(ping_interval=15, ping_payload="ping")
        
        return email_data



class _Fake_trash_mail(_WaitForMail):
    def __init__(self, base_url: str, name: str=None, domain: str=None, exclude: list[str]=None, captcha: str=""):
        """captcha - captcha response, needed for some websites"""
        super().__init__(0)

        self.base_url = base_url.removesuffix("/")
        self._captcha = captcha
        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    
        r = self._session.get(self.base_url)
        
        if r.status_code == 403:
            raise Exception(f"Error, you are ratelimited or captcha blocked on {self.base_url}, please wait.")       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        if "Bot Verification" in r.text:
            raise Exception(f"Error, you need to verify Captcha manually on {self.base_url}.") 

        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        r = self._session.post(self.base_url+"/messages", data={
            "_token": self._token,
            "captcha": self._captcha
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        if not domain and not name and not exclude:    
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)
        
        else:
            self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
            
            r = self._session.post(self.base_url+"/create", data={
                "_token": self._token,
                "name": self.name,
                "domain": self.domain
            })
            if not r.ok:
                raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
            
            r = self._session.post(self.base_url+"/messages", data={
                "_token": self._token,
                "captcha": self._captcha
            })    
            if not r.ok:
                raise Exception("Failed to create email, status", r.status_code)
            
            data = r.json()
            self.email: str = data["mailbox"]
            self.name, self.domain = self.email.split("@", 1)


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post(self.base_url+"/messages", data={
            "_token": self._token,
            "captcha": self._captcha
        })
        
        if r.ok:
            if r.content == b"": # some websites just suck and sometimes return empty data
                return []
            
            return [{
                "id": email["id"],
                "time": email["receivedAt"],
                "subject": email["subject"],
                "content": email["content"]
            } for email in r.json()["messages"]] 
        

class _Tempail_etc:
    def __init__(self, urls: dict[str, str], offset_of_email_content: int=0):
        """
        Generate a random inbox
        """
        # offset_of_email_content - tempmail.net also adds another script before the cloudflare script in the mail content, so we remove that in the end

        self._urls = urls
        self.offset_of_email_content = offset_of_email_content

        self._session = requests.Session()

        r = self._session.get(self._urls["base"])
        if not r.ok:
            raise Exception("Failed to create email, status:", r.status_code)
        if "Verifying your request, please wait..." in r.text:
            raise Exception("Error, you need to verify Captcha manually on "+self._urls["base"])
        
        soup = BeautifulSoup(r.text, "lxml")
        
        self.email = soup.find("input", {"id": "eposta_adres"})["value"]
        self.name, self.domain = self.email.split("@", 1)
        
        data = soup.find("script").text.split('var oturum="', 1)[1]
        self._some_val = data.split('"', 1)[0]
        self._time = data.split('var tarih="', 1)[1].split('"', 1)[0]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(self._urls["base"])
        if not r.ok:
            return None
        if "Verifying your request, please wait..." in r.text:
            raise Exception("Error, you need to verify Captcha manually on "+self._urls["base"])
        
        soup = BeautifulSoup(r.text, "lxml")

        return [{
            "id": email["id"],
            "from": _deCFEmail(email.find("div", {"class": "gonderen"}).span["data-cfemail"]),
            "subject": email.find("div", {"class": "baslik"}).text,
            "time": email.find("div", {"class": "zaman"}).text
        } for email in soup.find_all("li", {"class": "mail"})]
            

    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the whole content of a mail as a html string\n
        mail_id - id of the message
        """
        
        r = self._session.get(self._urls["base"]+"/"+mail_id)
        if not r.ok:
            return None
        if "Verifying your request, please wait..." in r.text:
            raise Exception("Error, you need to verify Captcha manually on "+self._urls["base"])

        r = self._session.get(BeautifulSoup(r.text, "lxml").find("div", {"class": "mail-oku-panel"}).iframe["src"])
        if not r.ok:
            return None
        if "Verifying your request, please wait..." in r.text:
            raise Exception("Error, you need to verify Captcha manually on "+self._urls["base"])

        soup = BeautifulSoup(r.text, "lxml")
        
        google_translate_script = soup.find('script', {'type': 'text/javascript', 'src': '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'})
        cloudflare_script = soup.find('script', {'data-cfasync': 'false'})
        elements_between_scripts = google_translate_script.find_next_siblings()

        elements = []
        for element in elements_between_scripts:
            if element == cloudflare_script:
                break
            elements.append(str(element))
        return "\n".join(elements[:-self.offset_of_email_content]) if self.offset_of_email_content != 0 else "\n".join(elements)


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60):
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """
        if timeout > 0: 
            start = time()
        

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            r = self._session.post(self._urls["kontrol"], data={
                "oturum": self._some_val,
                "tarih": self._time,
                "geri_don": self._urls["base"]
            })
            
            if not r.ok:
                return None
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                self._time = soup.find("script").text.split('tarih="', 1)[1].split('"', 1)[0]
                email = soup.find("li", {"class": "mail"})
                return {
                    "id": email["id"],
                    "from": _deCFEmail(email.find("div", {"class": "gonderen"}).span["data-cfemail"]),
                    "subject": email.find("div", {"class": "baslik"}).text,
                    "time": email.find("div", {"class": "zaman"}).text
                }

            sleep(delay)


class _Generatoremail_etc:
    def __init__(self, base_url: str, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        base_url - base_url, needed for specifying website\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. There is no validation for the domain\n
        exclude - a list of domain to exclude from the random selection\n
        """
        self._baseurl = base_url

        self._session = requests.Session()

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains(), validate_domain=False)


    def get_mail_content(self, mail_id: str, retry: bool=True, retry_delay: int=2, max_retries: int=3, _retries: int=1) -> dict:
        """
        Returns the content of a given mail_id as a BeautifulSoup html object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        try:
            r = self._session.get(f"{self._baseurl}/{self.domain}/{self.name}/{mail_id}")
        except requests.exceptions.ConnectionError:
            if retry:
                if _retries == max_retries:
                    return None

                sleep(retry_delay)
                return self.get_mail_content(mail_id=mail_id, retry=retry, retry_delay=retry_delay, _retries=_retries+1)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("div", {"id": "email-table"})

            return email_list.find("div", {"class": "mess_bodiyy"})
        
    def get_inbox(self, retry: bool=True, retry_delay: int=1, max_retries: int=3, _retries: int=1) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure. If there is 1 email in the inbox, it also returns the content of the email as a BeautifulSoup object. If there are more than 1 email in the inbox, it returns the ids of the emails, but no content\n
        retry - retry if the site refuses to allow a connection (does that sometimes, maybe ratelimit)\n
        retry_delay - how long to wait before a retry\n
        max_retries - how many retries to allow before stopping\n
        """
        try:
            r = self._session.get(f"{self._baseurl}/{self.domain}/{self.name}")
        except requests.exceptions.ConnectionError:
            if retry:
                if _retries == max_retries:
                    return None
                
                sleep(retry_delay)
                return self.get_inbox(retry=retry, retry_delay=retry_delay, _retries=_retries+1)

 
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            
            email_list = soup.find("div", {"id": "email-table"})
            if not email_list:
                return []

            # if there is one email, the whole structure is different, if there are more, there is an href for each email
            if soup.find("span", {"id": "mess_number"}).text == "1": 
                email_data = email_list.find("div", {"class": "list-group-item list-group-item-info"})
                data = {
                    "from": email_data.find("div", {"class": "from_div_45g45gg"}).text,
                    "subject": email_data.find("div", {"class": "subj_div_45g45gg"}).text,
                    "time": email_data.find("div", {"class": "time_div_45g45gg"}).text,
                    "content": email_list.find("div", {"class": "mess_bodiyy"})
                }

                return [data] 
            
            emails = []
            for email in email_list.findChildren("a"):
                data = {
                    "id": email["href"].rsplit("/", 1)[1],
                    "from": email.find("div", {"class": "from_div_45g45gg"}).text,
                    "subject": email.find("div", {"class": "subj_div_45g45gg"}).text,
                    "time": email.find("div", {"class": "time_div_45g45gg"}).text,
                }
                emails.append(data)
        
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

        def on_message(ws: websocket.WebSocketApp, message: str):
            nonlocal manual_stop
            
            if message.startswith("0"):
                ws.send("40")
                
            elif message.startswith("40"):
                ws.send(f'42["watch_for_my_email","{self.email}"]')
        
            elif message.startswith("42"):
                data = json.loads(message[2:])

                if data[0] == "new_email":
                    manual_stop = True
                    ws.close()
                    
                    data = json.loads(data[1])
                    soup = BeautifulSoup(data["tddata"], "lxml")
                    
                    nonlocal email_data
                    email_data = {
                        "id": data["clickgo"].rsplit("/", 1)[1],
                        "from": soup.find("div", {"class": "from_div_45g45gg"}).text,
                        "subject": soup.find("div", {"class": "subj_div_45g45gg"}).text,
                        "time": soup.find("div", {"class": "time_div_45g45gg"}).text
                    }
            
            elif message.startswith("2"): # ping
                ws.send("3")
            
            if timeout > 0 and time()-start >= timeout:
                manual_stop = True
                ws.close()

        def on_close(ws, *args):
            
            if not manual_stop:
                if timeout > 0 and time()-start >= timeout:
                    return None
                
                ws.close()
                ws = websocket.WebSocketApp(f"{self._baseurl.replace("https", "wss", 1)}/socket.io/?EIO=4&transport=websocket", on_message=on_message, on_close=on_close)
                ws.run_forever()

        email_data = None
        manual_stop = False
        ws = websocket.WebSocketApp(f"{self._baseurl.replace("https", "wss", 1)}/socket.io/?EIO=4&transport=websocket", on_message=on_message, on_close=on_close)
        ws.run_forever()
        return email_data

class _Solucioneswc:
    def __init__(self, base_url: str, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        self._baseurl = base_url

        self._session = requests.Session()
        
        # for IDE
        self.name: str
        self.domain: str
        self.email: str
        self.valid_domains: str

        def on_message(ws, msg):
            if msg.startswith("0"): # connected
                ws.send("40")

            elif msg.startswith("2"): # ping
                ws.send("3")

            elif msg.startswith("40"): # gets send out at the beginning
                ws.send('42["get_domains"]')

            elif msg.startswith("42"):
                data = json.loads(msg[2:])
                
                if data[0] == "set_domains_data":
                    self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, [domain["name"] for domain in data[1]])
                    payload = "42"+ json.dumps(["get_email_data", {
                                                "action": "create", 
                                                    "data": {
                                                        "email_alias": self.name,
                                                        "email_domain": self.domain
                                                    }
                                                }])
                    ws.send(payload)

                elif data[0] == "set_visitor_token": # email created
                    self._token = data[1]
                    ws.close()

                elif data[0] == "enable_active_form" or (data[0] == "show_alert" and data[1]["message"] in ("The tempmail is invalid.", f"The {self.domain} emails have expired. You cannot continue to use them.")):
                    raise Exception("Failed to create email, invalid email")

        
        ws = websocket.WebSocketApp("wss://ws.solucioneswc.com:2053/socket.io/?user_token=empty&visitor_token=empty&emails_list=empty&page_type=inbox&EIO=4&transport=websocket", 
                                    on_error=lambda *args: ws.close(), on_message=on_message, 
                                    header={"Origin": self._baseurl}
                                    )
        ws.run_forever(suppress_origin=True)


    def get_mail_content(self, mail_id: str):
        """
        Returns the content of a given mail_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        def on_message(ws, msg):
            if msg.startswith("0"): # connected
                ws.send("40")

            elif msg.startswith("2"): # ping
                ws.send("3")

            elif msg.startswith("40"):
                ws.send("42"+json.dumps([
                    "get_email_message",
                    {
                        "email_address": self.email,
                        "email_message_id": mail_id,
                        "email_message_type": "inbound"
                    }
                ]))
            
            elif msg.startswith("42"):
                data = json.loads(msg[2:])
    
                if data[0] == "open_message":
                    nonlocal email_data
                    email_data = data[1]["email_message_data"]["data"]["content"]
                    ws.close()

        email_data = None
        ws = websocket.WebSocketApp(f"wss://ws.solucioneswc.com:2053/socket.io/?user_token=empty&visitor_token={self._token}&emails_list=empty&page_type=inbox&EIO=4&transport=websocket", 
                                    on_error=lambda *args: ws.close(), on_message=on_message, 
                                    header={"Origin": self._baseurl}
                                    )
        ws.run_forever(suppress_origin=True)
        
        return email_data


    def get_inbox(self, return_content: bool=True) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]\n
        return_content - if the returned data should contain the content. If false we would need to create a new websocket connection to get the content. Not recommended if you have lots of emails and only want the content of some of them.
        """
        
        def on_message(ws, msg):
            if msg.startswith("0"): # connected
                ws.send("40")

            elif msg.startswith("2"): # ping
                ws.send("3")
            
            elif msg.startswith("40"): # sid response
                ws.send('42["initialize_app"]')

            elif msg.startswith("42"):
                nonlocal email_data
                data = json.loads(msg[2:])

                if data[0] == "set_empty_messages_notice": # no emails
                    email_data = []
                    ws.close()

                if data[0] == "insert_email_messages":
                    if return_content: nonlocal content_count
                    
                    email_data = [{
                        "id": str(email["id"]),
                        "time": email["date"],
                        "from": email["sender"]["text"],
                        "subject": email["subject"]
                    } for email in data[1]["email_messages"]]
                    
                    if not return_content or len(email_data) == 0:
                        ws.close()

                    for email in email_data:
                        ws.send("42"+json.dumps([
                        "get_email_message",
                        {
                            "email_address": None,
                            "email_message_id": email["id"],
                            "email_message_type": "inbound"
                        }
                    ]))
                
                elif data[0] == "open_message": # only happens after insert_email_messages and if return_content is true so we can assume email_data and content_count exists
                    content_count+=1
                    
                    for email in email_data:
                        if str(data[1]["email_message_data"]["id"]) == email["id"]:
                            email["content"] = data[1]["email_message_data"]["data"]["content"]
                            break
                    
                    if content_count == len(email_data):
                        ws.close()

        email_data = None
        if return_content: content_count = 0
        
        ws = websocket.WebSocketApp(f"wss://ws.solucioneswc.com:2053/socket.io/?user_token=empty&visitor_token={self._token}&emails_list=empty&page_type=inbox&EIO=4&transport=websocket", 
                                    on_error=lambda *args: ws.close(), on_message=on_message, 
                                    header={"Origin": self._baseurl}
                                    )
        ws.run_forever(suppress_origin=True)
        
        return email_data
        

    def wait_for_new_email(self, delay: None=None, timeout: int=60, return_content: bool=True):
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability\n
        return_content - if the returned data should contain the content. If false we would need to create a new websocket connection to get the content.
        """

        start = time()
        
        def on_message(ws, msg):
            if msg.startswith("0"): # connected
                ws.send("40")

            elif msg.startswith("2"): # ping
                ws.send("3")

            elif msg.startswith("40"): # sid response
                ws.send('42["initialize_app"]')

            elif msg.startswith("42"):
                data = json.loads(msg[2:])
                
                if data[0] == "new_message_notify":
                    nonlocal email_data
                    email_data = {
                        "id": str(data[1]["email_message"]["id"]),
                        "time": data[1]["email_message"]["date"],
                        "from": data[1]["email_message"]["sender"]["text"],
                        "subject": data[1]["email_message"]["subject"]
                    }
                    if not return_content:
                        ws.close()
                    
                    ws.send("42"+json.dumps([
                        "get_email_message",
                        {
                            "email_address": self.email,
                            "email_message_id": email_data["id"],
                            "email_message_type": "inbound"
                        }
                    ]))

                elif data[0] == "open_message": # only happens after new_message_notify so we can assume email_data exists
                    email_data["content"] = data[1]["email_message_data"]["data"]["content"]
                    ws.close()

            if timeout > 0 and time()-start >= timeout:
                ws.close()

        email_data = None
        ws = websocket.WebSocketApp(f"wss://ws.solucioneswc.com:2053/socket.io/?user_token=empty&visitor_token={self._token}&emails_list=empty&page_type=inbox&EIO=4&transport=websocket", 
                                    on_error=lambda *args: ws.close(), on_message=on_message, 
                                    header={"Origin": self._baseurl}
                                    )
        ws.run_forever(suppress_origin=True)
        
        return email_data
    

class _Wptempmail_etc(_WaitForMail):
    def __init__(self, base_url: str, name: str=None, domain:str=None, exclude: list[str]=None):
        super().__init__(0)

        self._baseurl = base_url

        self._session = requests.Session()
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        
        r = self._session.get(self._baseurl)
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        soup = BeautifulSoup(r.text, "lxml")

        if name or domain or exclude:
            data = soup.find("form", {"class": "tm-change-mailbox-form"})
            nonce = data.find("input", {"id": "_wpnonce"})["value"]
            
            self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
            
            t = f"{time()*1000:.0f}" #data.find("input", {"name": "_wp_http_referer"})["value"] # /?_=TIME
            
            r = self._session.post(f"{self._baseurl}/?_={t}", data={
                "tm-action": "change",
                "_wpnonce": nonce,
                "_wp_http_referer": "/?_="+t,
                "tm-mailbox-id": self.name,
                "tm-mailbox-domain": self.domain
            })

            if not r.ok:
                raise Exception("Failed to create email, status", r.status_code)
            
            error = BeautifulSoup(r.content, "lxml").find("span", {"class": "tm-alert-message"})
            if error:
                raise Exception("Failed to create email ('Mailbox is unavailable')")
            

        else:
            self.email = soup.find("button", {"class": "tm-copy-to-clipboard"})["data-clipboard-text"]
            self.name, self.domain = self.email.split("@", 1)

    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns additional info on a given mail_id (time, content; content is a BeautifulSoup object)\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"{self._baseurl}/?tm-message-id={mail_id}")
        if r.ok:
            soup = BeautifulSoup(r.content.decode('utf8','surrogateescape'), "lxml")
            data = soup.find("div", {"class": "tm-message-box"})
            return {
                "time": data.find("div", {"class": "tm-message-date"}).text.strip(),
                "content": data.find("div", {"class": "tm-message-content"}, recursive=False)
            }


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(self._baseurl)
        if r.ok:
            soup = BeautifulSoup(r.content.decode('utf8','surrogateescape'), "lxml")
            emails = soup.find("table", {"class": "tm-inbox"}).tbody
            
            if not emails.find("tr", recursive=False).get("class"):
                return []
            
            return [{
                "from": f.text if ( f := email.find("td", {"class": "tm-inbox-message-from"}).a ).span is None else _deCFEmail(f.span["data-cfemail"]),
                "id": f["href"].split("?tm-message-id=", 1)[1],
                "subject": email.find("td", {"class": "tm-inbox-message-subject"}).text.strip()
            } for email in emails.find_all("tr", recursive=False)]
                        


class _Mailtm_etc:
    def __init__(self, urls: dict, name: str=None, domain:str=None, exclude: list[str]=None, password: str=None):
        self._urls = urls
        
        self._session = requests.Session()
        
        self._session.headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json",
        }

        self.password = password or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        r = self._session.post(self._urls["base"]+"/accounts", json={
            "address": self.email,
            "password": self.password
        })

        if not r.ok:
            raise Exception("Failed to create account, status: ", r.status_code) 
       
        data = r.json()
        self.email = data["address"]
        self._id = data["id"]

        r = self._session.post(self._urls["base"]+"/token", json={
            "address": self.email,
            "password": self.password
        })
        
        if not r.ok:
            raise Exception("Failed to create account, status: ", r.status_code)
        
        data = r.json()
        self._token = data["token"]
        self._session.headers["Authorization"] = "Bearer " + self._token


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given mail_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(self._urls["base"]+"/messages/"+mail_id)
        if r.ok:
            data = r.json()
            return data["html"][0]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """
        
        r = self._session.get(self._urls["base"]+"/messages")
        if r.ok:
            return [
                {
                    "id": msg["id"],
                    "from": msg["from"]["address"],
                    "subject": msg["subject"],
                    "time": msg["createdAt"]
                } 
                for msg in r.json()["hydra:member"]
           ]

    
    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using event streams), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        """
        
        try:
            eoc = b"\n\n"
            chunk = b""
            for r in self._session.get(self._urls["stream"]+"/.well-known/mercure?topic=/accounts/"+self._id, 
                headers={
                    "Accept": "text/event-stream",
                }, 
                stream=True, 
                timeout=timeout
            ):
                chunk += r
                if r.endswith(eoc): # Complete chunk of datareceived
                    for data in chunk.splitlines():
                        if data.startswith(b'data: {"@context":"/contexts/Message'):
                            msg = json.loads(data[6:].decode())
                            return {
                                "id": msg["id"],
                                "from": msg["from"]["address"],
                                "subject": msg["subject"],
                                "time": msg["createdAt"]
                            }

                    chunk = b""

        except requests.exceptions.ConnectionError:
            return None
        
class _Tmmail_etc(_WaitForMail):
    def __init__(self, base_url: str, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)
        self._baseurl = base_url

        self._session = requests.Session()

        r = self._session.get(self._baseurl)
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}")
        
        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        # this request is necessary in order to receive emails 
        r = self._session.post(self._baseurl+"/messages", data={"_token": self._token}) 
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}")
    

        if not domain and not name and not exclude:
            self.email = r.json()["mailbox"]
            self.name, self.domain = self.email.split("@", 1)
            return

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())

        data = {
            "name": self.name,
            "domain": self.domain,
            "_token": self._token
        }

        r = self._session.post(self._baseurl+"/create", data=data)
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox including the content.
        """
        
        r = self._session.post(self._baseurl+"/messages", data={"_token": self._token})
        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from_email"],
                "time": email["receivedAt"],
                "subject": email["subject"],
                "content": email["content"]
            } for email in r.json()["messages"]]