import json
import time
from bs4 import BeautifulSoup
import requests



from .._constructors import _generate_user_data

class Tempmail_cc:
    """An API Wrapper around the https://tempmail.cc/ website"""

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
        Returns a list of valid domains of the service (format: abc.xyz) as a list. Only one domain supported.
        """

        return ["tempmail.cc"]
    

    def get_inbox(self) -> None:
        """
        There is no server sided inbox
        """
        return None

    def wait_for_new_email(self, delay: None=None, timeout: int=60) -> dict:
        """
        Waits for a new mail (using streams), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        delay - not used, simply for compatability
        """

        r = self._session.get("https://tempmail.cc/socket.io/?EIO=3&transport=polling")
        if not r.ok:
            return None

        ws_config = json.loads(r.text[5:])
        
        
        payload = f'42["set shortid","{self.name}"]'
        payload = str(len(payload)) + ":" + payload
        r = self._session.post("https://tempmail.cc/socket.io/?EIO=3&transport=polling&sid="+ws_config["sid"], data=payload, headers={
            "Content-Type": "text/plain;charset=UTF-8"
        })
        if not r.ok:
            return None

        r = self._session.get("https://tempmail.cc/socket.io/?EIO=3&transport=polling&sid="+ws_config["sid"])
        if not r.ok:
            return None
        
        correct_chunk_start = b'\x00'
        data_start = b'\xff'
        chunk = b""
        
        try: 
            for r in self._session.get("https://tempmail.cc/socket.io/?EIO=3&transport=polling&sid="+ws_config["sid"], stream=True, timeout=timeout if timeout > 0 else None):
                chunk+=r
        except requests.exceptions.ReadTimeout:
            return None

        if chunk.startswith(correct_chunk_start) and (d := chunk.split(data_start, 1)[1]).startswith(b"42"):
            data = json.loads(d[2:])
            if data[0] == "mail":
                return {
                    "id": data[1]["connection"]["id"],
                    "from": data[1]["from"][0]["address"],
                    "time": data[1]["date"],
                    "subject": data[1]["subject"],
                    "content": data[1].get("html", data[1].get("text"))
                }
            
        elif chunk == b'{"code":1,"message":"Session ID unknown"}':
            # very rudimentary, you can keep a session alive but that would be too much work
            # there is a small window where the new session is initialized where emails could slip through
            return self.wait_for_new_email(delay=delay, timeout=timeout)
