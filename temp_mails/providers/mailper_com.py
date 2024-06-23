import json
from time import sleep, time
from datetime import datetime, timedelta, UTC

import requests
import websocket

from .._constructors import _generate_user_data

class Mailper_com():
    """An API Wrapper around the https://mailper.com/ website. Very fast from experience. See create_email function."""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None, _token_data: dict=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        _token_data - a dict containing information about a session, see self.create_email()
        """

        self.name, self.domain, self.email, self.valid_domains = _generate_user_data(name, domain, exclude, self.get_valid_domains())
        
        self._session = requests.Session()
        self._session.headers = {
            "Referer": "https://mailper.com/"
        }

        if _token_data:
            if time() > _token_data["expires_at"]: # token expired
                r = self._session.post("https://securetoken.googleapis.com/v1/token?key=AIzaSyBxM0cu2Zr7W6Nz0r7PBzf6gy2GvkowBnM", json={
                    "grant_type": "refresh_token",
                    "refresh_token": _token_data["refresh_token"]
                })
                if not r.ok:
                    raise Exception("Failed to refresh the access token")
                
                data = r.json()
                self._token_data = {
                    "token": data["id_token"],
                    "expires_at": time()+int(data["expires_in"]),
                    "refresh_token": data["refresh_token"]
                }
            else:
                self._token_data = _token_data
        else:
            r = self._session.post("https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyBxM0cu2Zr7W6Nz0r7PBzf6gy2GvkowBnM", json={
                "returnSecureToken": True
            })
            
            if not r.ok:
                raise Exception("Failed to create account for email, status", r.status_code)
            
            data = r.json()
            self._token_data = {
                "token": data["idToken"],
                "expires_at": time()+int(data["expiresIn"]),
                "refresh_token": data["refreshToken"]
            }

        self._session.headers = {
            "Authorization": "Bearer "+self._token_data["token"]
        }

        r = self._session.post("https://api.mailper.com/graphql", json={
            "operationName": "CreateMailbox",
            "variables": {
                "input": {
                    "address": self.email,
                    "expiresAt": (datetime.now(UTC) + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                }
            },
            "query": "mutation CreateMailbox($input: CreateMailboxInput!) {\n  createMailbox(input: $input) {\n    ...MailboxFragment\n  }\n}\n\nfragment MailboxFragment on Mailbox {\n  id\n  address\n  user\n}"
        })
        self._mailbox_id = r.json()["data"]["createMailbox"]["id"]
        
        self._ws = websocket.create_connection("wss://api.mailper.com/graphql", header={
            "Sec-Websocket-Protocol": "graphql-ws"
        })

        init = {
            "type": "connection_init",
            "payload": {
                "Authorization": "Bearer "+self._token_data["token"]
            }
        }
        subscribe = {
            "id": "1",
            "type": "start",
            "payload": {
                "variables": {},
                "extensions": {},
                "operationName": "MessageCreated",
                "query": "subscription MessageCreated {\n  messageCreated {\n    ...MessageFragment\n  }\n}\n\nfragment MessageFragment on Message {\n  id\n  from {\n    ...MessageAddressFragment\n  }\n\n  subject\n  text\n  html\n  date\n}\n\nfragment MessageAddressFragment on MessageAddress {\n  address\n}"
            }
        }

        self._ws.send(json.dumps(init))
        self._ws.recv()
        self._ws.send(json.dumps(subscribe))


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list. This website only has 1 domain.
        """
        return ["mailper.com"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox
        """
        
        r = self._session.post("https://api.mailper.com/graphql", json={
            "operationName": "Messages",
            "variables": {
                "mailbox": self._mailbox_id,
                "offset": 0
            },
            "query": "query Messages($mailbox: String, $limit: Int, $offset: Int) {\n  messages(mailbox: $mailbox, limit: $limit, offset: $offset) {\n    ...MessageFragment\n  }\n}\n\nfragment MessageFragment on Message {\n  id\n  from {\n    ...MessageAddressFragment\n  }\n  subject\n  text\n  html\n  date\n}\n\nfragment MessageAddressFragment on MessageAddress {\n  name\n  address\n}"
        })

        if r.ok:
            return [{
                "id": email["id"],
                "from": email["from"][0]["address"],
                "time": email["date"],
                "subject": email["subject"],
                "content": email.get("html", email.get("text"))
            } for email in r.json()["data"]["messages"]]


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
            
            if data["type"] == "data":
                return {
                    "id": (d := data["payload"]["data"]["messageCreated"])["id"],
                    "from": d["from"][0]["address"],
                    "time": d["date"],
                    "subject": d["subject"],
                    "content": d.get("html", d.get("text"))
                }
            
            if timeout > 0 and time()-start >= timeout:
                return None
            

    def create_email(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Creates a new email with an existent session, making the creation quicker.\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        
        return Mailper_com(name=name, domain=domain, exclude=exclude, _token_data=self._token_data)