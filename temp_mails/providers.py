from time import sleep, time
import requests
import random
import json
from bs4 import BeautifulSoup
from string import ascii_lowercase, digits
import http.client

class tenminemail_com:
    """An API Wrapper around the https://10minemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        r = self._session.post("https://web2.10minemail.com/mailbox")

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["mailbox"]
        self.name, self.domain = self.email.split("@")

        self._token = data["token"]
        self._session.headers["Authorization"] = "Bearer " + self._token



    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://web2.10minemail.com/messages")
        
        if r.ok:
            return r.json()["messages"]

    
    def get_mail_content(self, message_id: str) -> dict:
        """
        Returns the whole mail content of a mail\n
        message_id - id of the message
        """
    
        r = self._session.get("https://web2.10minemail.com/messages/"+message_id)
        if r.ok:
            return r.json()

    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return self.get_mail_content(message_id=data[0]["_id"])
            
            sleep(delay)




class tenminuteemail_com:
    """An API Wrapper around the https://10minutemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    
        
        r = self._session.get("https://10minutemail.com/session/address")
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["address"]
        self.name, self.domain = self.email.split("@")

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://10minutemail.com/messages/messagesAfter/0")
        
        if r.ok:
            return r.json()


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return data[-1]
            
            sleep(delay)



class tenminutemeail_net:
    """An API Wrapper around the https://10minutemail.net/ website"""

    def __init__():
        raise Exception("This service is way too unreliable, use a different one")
    


class internxt_doctcom:
    """An API Wrapper around the https://internxt.com/temporary-email website"""

    def __init__(self):
        """
        Generate a random inbox\n
        There is no possibility to control the name or domain or similar
        """

        self._session = requests.Session()
        
        r = self._session.get("https://internxt.com/api/temp-mail/create-email")
        if not r.ok:
            raise Exception("Error on creation", r, r.text)
        
        data = r.json()
        self.__token = data["token"]
        self.email: str = data["address"]
        self.name, self.domain = self.email.split("@")

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = requests.get(f"https://internxt.com/api/temp-mail/get-inbox?token="+self.__token)
        if r.ok:
            return r.json()["email"]



    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                
                return data[0]
            
            sleep(delay)


class minuteinbox_com:
    """An API Wrapper around the https://10minutemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """

        self._session = requests.Session()
        
        self._session.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    
        r = self._session.get("https://www.minuteinbox.com/index/index")

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = json.loads(r.content.decode("utf-8-sig"))

        self.email: str = data["email"]
        self.name, self.domain = self.email.split("@")



    def get_mail_content(self, message_id: str | int) -> str:
        """
        Returns the whole mail content of a mail\n
        message_id - id of the message\n
        returns the html of the content
        """
    
        r = self._session.get("https://www.minuteinbox.com/email/id/"+str(message_id))
        if r.ok:
            return r.text



    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.minuteinbox.com/index/refresh")
        
        if r.ok:
            # the names of the variables are really fucked so we reformat them
            
            resp = json.loads(r.content.decode("utf-8-sig"))
            data = []
            
            for mail in resp:
                data.append({
                    "id": mail["id"],
                    "time": mail["kdy"],
                    "from": mail["od"],
                    "subject": mail["predmet"]
                })
            
            return data


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return self.get_mail_content(message_id=data[0]["id"])
            
            sleep(delay)


class tempmail_io:
    """An API Wrapper around the https://temp-mail.io/ website"""


    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate a random inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """

        self._session = requests.Session()
        
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self._valid_domains = self._get_valid_domains()
        if domain:
            self.domain = domain if domain in self._valid_domains else random.choice(self._valid_domains)
        else:
            if exclude:
                self._valid_domains = [domain for domain in self._valid_domains if domain not in exclude]
            self.domain = random.choice(self._valid_domains)
        
        r = self._session.post("https://api.internal.temp-mail.io/api/v3/email/new", json={
            "name": self.name,
            "domain": self.domain
        })
        
        if r.ok:
            self.email = f"{self.name}@{self.domain}"
        else:
            raise Exception("Failed to create email, status", r.status_code)

    @staticmethod
    def _get_valid_domains() -> list[str]:
        r = requests.get("https://api.internal.temp-mail.io/api/v4/domains")
        if r.ok:
            return [domain["name"] for domain in r.json()["domains"] if domain["type"] == "public"] 

    def get_inbox(self) -> list[dict]:
        """
        Gets the content of the given email.
        """
        
        r = self._session.get(f"https://api.internal.temp-mail.io/api/v3/email/{self.email}/messages")
        
        if r.ok:
            return r.json()


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return data[0]
            
            sleep(delay)


    def get_mail_content(self, mail_id: str) -> str:
        """
        !! REDUNDANT\n
        EMAIL CONENT IS IN INBOX\n
        Returns the content of a given email_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://api.internal.temp-mail.io/api/v3/message/"+mail_id)
        if r.ok:
            return r.json()
        

class tempmail_org:
    """An API Wrapper around the https://temp-mail.org/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    
        
        r = self._session.post("https://web2.temp-mail.org/mailbox")
    
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["mailbox"]
        self.name, self.domain = self.email.split("@")

        self._token = data["token"]
        self._session.headers["Authorization"] = "Bearer " + self._token

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://web2.temp-mail.org/messages")
        
        if r.ok:
            return r.json()["messages"]

    
    def get_mail_content(self, message_id: str):
        """
        Returns the whole mail content of a mail\n
        message_id - id of the message
        """
    
        r = self._session.get("https://web2.temp-mail.org/messages/"+message_id)
        if r.ok:
            return r.json()

    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return self.get_mail_content(message_id=data[0]["_id"])
            
            sleep(delay)



class tempmailbox_com:
    """An API Wrapper around the https://temp-mailbox.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        self._session = requests.Session()
        
        r = self._session.post(f"https://temp-mailbox.com/messages?{time():.0f}")
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
        if not domain and not name and not exclude:
            self.email = r.json()["mailbox"]
            self.name, self.domain = self.email.split("@")
            return

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        
        self._valid_domains = self._get_valid_domains()
        if domain:
            self.domain = domain if domain in self._valid_domains else random.choice(self._valid_domains)
        else:
            if exclude:
                self._valid_domains = [domain for domain in self._valid_domains if domain not in exclude]
            self.domain = random.choice(self._valid_domains)
        
        self.email = f"{self.name}@{self.domain}"

        data = {
            "name": self.name,
            "domain": self.domain
        }

        r = self._session.post("https://temp-mailbox.com/create", data=data)
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        

    def _get_valid_domains(self) -> list[str]:
        r = requests.get("https://temp-mailbox.com/change")
        if r.ok:
            soup = BeautifulSoup(r.content, "lxml")
            email_options = soup.find_all("option")
            
            return [option["value"] for option in email_options]


    def get_inbox(self) -> list[dict]:
        """
        Gets the content of the given email.
        """
        
        r = self._session.post(f"https://temp-mailbox.com/messages?{time():.0f}")#, data="token="+self.__token)
        if r.ok:
            return r.json()["messages"]


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                
                return data[0]
            
            sleep(delay)


    def get_mail_content(self, mail_id: str) -> str:
        """
        !! REDUNDANT\n
        EMAIL CONENT IS IN INBOX\n
        Returns the content of a given email_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://temp-mailbox.com/message/"+mail_id)
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return soup.find('div', class_='pre').get_text(strip=True)
        

class tenminutesemail_net:
    """An API Wrapper around the https://10minutesemail.net/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    
        r = self._session.get("https://10minutesemail.net/")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self._token = BeautifulSoup(r.content, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        
        r = self._session.post("https://10minutesemail.net/messages", {
            "_token": self._token,
            "captcha": ""
        })
    
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = r.json()

        self.email: str = data["mailbox"]
        self.name, self.domain = self.email.split("@")

    
    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://10minutesemail.net/messages", {
            "_token": self._token,
            "captcha": ""
        })
        
        if r.ok:
            return r.json()["messages"]


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return data[0]
            
            sleep(delay)


class etempmail_net:
    """An API Wrapper around the https://etempmail.net/10minutemail website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate a random inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """

        self._session = requests.Session()
        
        # Get required data for email creation and more
        r = self._session.get("https://etempmail.net/10minutemail")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # Create Email
        soup = BeautifulSoup(r.content, "lxml")
        with open("test.html", "w") as f:
            f.write(r.text)
        data = json.loads(soup.find("div", {"x-data": "{ in_app: false }"})["wire:initial-data"])

        self._valid_domains = data["serverMemo"]["data"]["domains"]
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        
        if domain:
            self.domain = domain if domain in self._valid_domains else random.choice(self._valid_domains)
        else:
            if exclude:
                self._valid_domains = [domain for domain in self._valid_domains if domain not in exclude]
            self.domain = random.choice(self._valid_domains)
        
        self.email = f"{self.name}@{self.domain}"
        
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
                 
        r = self._session.post("https://etempmail.net/livewire/message/frontend.actions_10minutemail", json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        # Create Email End

        # Get the data required for checking messages

        data = json.loads(soup.find("div", {"x-data": "{ show: false, id: 0 }"})["wire:initial-data"])

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

        r = self._session.post("https://etempmail.net/livewire/message/frontend.app", json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)

        new_data = r.json()
        self.__fingerprint__ = data["fingerprint"]
        self.__servermemo__ = data["serverMemo"]
        self.__servermemo__["htmlHash"] = new_data["serverMemo"]["htmlHash"]
        self.__servermemo__["data"].update(new_data["serverMemo"]["data"])
        self.__servermemo__["checksum"] = new_data["serverMemo"]["checksum"]

    @staticmethod
    def _get_valid_domains() -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get("https://etempmail.net/10minutemail")
       
        if r.ok:
            soup = BeautifulSoup(r.content, "lxml")
            data = json.loads(soup.find("div", {"class": "p-3 md:p-0 w-full md:w-2/4 order-2"})["wire:initial-data"])

            return data["serverMemo"]["data"]["domains"]


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        payload = {
            "fingerprint": self.__fingerprint__,
            "serverMemo": self.__servermemo__,
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

        r = self._session.post("https://etempmail.net/livewire/message/frontend.app", json=payload, headers={
            "x-csrf-token": self._token,
            "x-livewire": "true"
        })
        
        if r.ok:
            data = r.json()
            return data["serverMemo"]["data"]["messages"] if "data" in data["serverMemo"] else []


    def wait_for_new_email(self, delay: float=2.0, timeout: int=60) -> dict:
        """
        Waits for a new mail, returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        delay - the delay between each check in seconds\n
        timeout - the time which is allowed to pass before forcefully stopping, smaller than 0 -> no timeout
        """

        if timeout > 0: 
            start = time()
        
        old_length = len(self.get_inbox())

        while True:
            if timeout > 0 and time()-start >= timeout:
                return None
            
            if (len(data := self.get_inbox())) > old_length:
                return data[-1]
            
            sleep(delay)