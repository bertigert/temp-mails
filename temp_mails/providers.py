from time import sleep, time
from typing import Literal
from string import ascii_lowercase, digits
import random
import json
import requests
from bs4 import BeautifulSoup
import websocket

class _WaitForMail:
    """
        A parent class to wait for a new email
    """
    def __init__(self, indx: Literal[0, -1]):
        self.indx = indx

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
                return data[self.indx]
            
            sleep(delay)


class Tenminemail_com(_WaitForMail):
    """An API Wrapper around the https://10minemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(-1)

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
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """

        r = self._session.get("https://web2.10minemail.com/messages")
        
        if r.ok:
            return r.json()["messages"]

    
    def get_mail_content(self, mail_id: str) -> dict:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message
        """
    
        r = self._session.get("https://web2.10minemail.com/messages/"+mail_id)
        if r.ok:
            return r.json()



class Tenminuteemail_com(_WaitForMail):
    """An API Wrapper around the https://10minutemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(-1)

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



class Tenminutemeail_net:
    """An API Wrapper around the https://10minutemail.net/ website"""

    def __init__(self):
        raise Exception("This service is way too unreliable, use a different one")
    


class Internxt_doctcom(_WaitForMail):
    """An API Wrapper around the https://internxt.com/temporary-email website"""

    def __init__(self):
        """
            Generate a random inbox\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.get("https://internxt.com/api/temp-mail/create-email")
        if not r.ok:
            raise Exception("Error on creation", r, r.text)
        
        data = r.json()
        self._token = data["token"]
        self.email = data["address"]
        self.name, self.domain = self.email.split("@")

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://internxt.com/api/temp-mail/get-inbox?token="+self._token)
        
        if r.ok:
            return r.json()["emails"]


class Minuteinbox_com(_WaitForMail):
    """An API Wrapper around the https://www.minuteinbox.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(0)

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


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content as a string
        """
    
        r = self._session.get("https://www.minuteinbox.com/email/id/"+str(mail_id))
        if r.ok:
            return r.text.split("\n", maxsplit=1)[1]


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


class Tempmail_io(_WaitForMail):
    """An API Wrapper around the https://temp-mail.io/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate a random inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)
        
        r = self._session.post("https://api.internal.temp-mail.io/api/v3/email/new", json={
            "name": self.name,
            "domain": self.domain
        })
        
        if r.ok:
            self.email = f"{self.name}@{self.domain}"
        else:
            raise Exception("Failed to create email, status", r.status_code)

    @staticmethod
    def get_valid_domains() -> list[str]:
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


    def get_mail_content(self, mail_id: str) -> str:
        """
        !! REDUNDANT\n
        Email content is in inbox if the email contains html\n
        Returns the content of a given email_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://api.internal.temp-mail.io/api/v3/message/"+mail_id)
        if r.ok:
            return r.json()
        

class Tempmail_org(_WaitForMail):
    """An API Wrapper around the https://temp-mail.org/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(-1)

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

    
    def get_mail_content(self, mail_id: str):
        """
        Returns the whole content of a mail\n
        mail_id - id of the message
        """
    
        r = self._session.get("https://web2.temp-mail.org/messages/"+mail_id)
        if r.ok:
            return r.json()


class Tempmailbox_com(_WaitForMail):
    """An API Wrapper around the https://temp-mailbox.com/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        r = self._session.post(f"https://temp-mailbox.com/messages?{time():.0f}")
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        
        if not domain and not name and not exclude:
            self.email = r.json()["mailbox"]
            self.name, self.domain = self.email.split("@")
            return

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        
        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)
        
        self.email = f"{self.name}@{self.domain}"

        data = {
            "name": self.name,
            "domain": self.domain
        }

        r = self._session.post("https://temp-mailbox.com/create", data=data)
        if not r.ok:
            raise Exception(f"Something went wrong on Email Creation, status: {r.status_code}, response content:\n{r.text}")
        

    def get_valid_domains(self) -> list[str]:
        r = requests.get("https://temp-mailbox.com/change")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_options = soup.find_all("option")
            
            return [option["value"] for option in email_options]


    def get_inbox(self) -> list[dict]:
        """
        Gets the content of the given email.
        """
        
        r = self._session.post(f"https://temp-mailbox.com/messages?{time():.0f}")#, data="token="+self._token)
        if r.ok:
            return r.json()["messages"]
        


class Tenminutesemail_net(_WaitForMail):
    """An API Wrapper around the https://10minutesemail.net/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self._session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    
        r = self._session.get("https://10minutesemail.net/")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self._token = BeautifulSoup(r.text, "lxml").find("meta", {"name": "csrf-token"})["content"]
        
        
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



class Etempmail_net(_WaitForMail):
    """An API Wrapper around the https://etempmail.net/ website"""

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None, life_time: Literal[5, 10, 15, 20, 30, 60]=None):
        """
            Generate a random inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
            life_time - time for which the email is avaiable in minutes
        """
        super().__init__(-1)

        self._session = requests.Session()
        
        # Get required data for email creation and more
        r = self._session.get("https://etempmail.net/" + ((str(life_time) + "minutemail") if life_time else ""))
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        # Create Email
        soup = BeautifulSoup(r.text, "lxml")
        
        data = json.loads(soup.find("div", {"x-data": "{ in_app: false }"})["wire:initial-data"])

        self.valid_domains = data["serverMemo"]["data"]["domains"]
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)
        
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
    def get_valid_domains() -> list[str] | None:
        """
            Returns a list of a valid domains, None if failure
        """
        r = requests.get("https://etempmail.net/10minutemail")
       
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            data = json.loads(soup.find("div", {"x-data": "{ in_app: false }"})["wire:initial-data"])

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



class Disposablemail_com(_WaitForMail):
    """An API Wrapper around the https://www.disposablemail.com/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self._session.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    
        r = self._session.get("https://www.disposablemail.com/index/index")

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = json.loads(r.content.decode("utf-8-sig"))

        self.email: str = data["email"]
        self.name, self.domain = self.email.split("@")


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content
        """
    
        r = self._session.get("https://www.disposablemail.com/email/id/"+str(mail_id))
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.disposablemail.com/index/refresh")
        
        if r.ok:
            # the names of the variables are really fucked so we reformat them
            
            resp = json.loads(r.content.decode("utf-8-sig"))
            data = []
            
            for email in resp:
                data.append({
                    "id": email["id"],
                    "time": email["kdy"],
                    "from": email["od"],
                    "subject": email["predmet"]
                })
            
            return data



class Emailondeck_com(_WaitForMail):
    """An API Wrapper around the https://www.emailondeck.com/ website"""

    def __init__(self):
        """
        Generate a random inbox, please note that the site has a ratelimit for inboxes/hour
        """
        super().__init__(0)

        # All of this is reversed from the chrome extension, the website uses a different captcha protected API

        self._session = requests.Session()
    
        r = self._session.get("https://www.emailondeck.com/ajax/ce-new-email.php")
       
        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        self.email, self._token = r.text.split("|")
        self.name, self.domain = self.email.split("@")
        
    
    def get_mail_content(self, mail_id: str | int) -> BeautifulSoup:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content as a BeautifulSoup Object
        """
    
        r = self._session.get("https://www.emailondeck.com/email_iframe.php?msg_id="+str(mail_id))
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return soup.find("div", {"id": "inbox_message"})

    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.post("https://www.emailondeck.com/ajax/messages.php")
        
        if r.ok:
            if r.text[0] == "0":
                return []
                        
            soup = BeautifulSoup(r.text.split("|", maxsplit=3)[3], "lxml")

            emails = []
            for email in soup.find_all("div", {"class": "inbox_rows msglink"}):
                data = {
                    "id": email["name"],
                    "from": email.find("td", {"class": "desktop_only inbox_td_from"}).text,
                    "subject": email.find("td", {"class": "desktop_only inbox_td_subject"}).text,
                    "time": email.find("td", {"class": "inbox_td_received"}).text

                }
                emails.append(data)
            
            return emails



class Onesecmail_com(_WaitForMail):
    """An API Wrapper around the https://1secmail.com website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)

        self.email = f"{self.name}@{self.domain}"

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://www.1secmail.com/api/v1/?action=getDomainList")
        if r.ok:
            return r.json()


    def get_mail_content(self, mail_id: int) -> dict:
        """
        Returns the content of a given email_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={self.name}&domain={self.domain}&id={mail_id}")
        if r.ok:
            return r.json()


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={self.name}&domain={self.domain}")
        if r.ok:
            return r.json()



class Mohamal_com(_WaitForMail):
    """An API Wrapper around the https://www.mohmal.com/website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(-1)

        self._session = requests.Session()
     
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)

        self.email = f"{self.name}@{self.domain}"

        self._session.post("https://www.mohmal.com/en/create", data={
            "name": self.name, 
            "domain": self.domain
        })

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://www.mohmal.com/en")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("option")]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the html content of a given email_id\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://www.mohmal.com/en/message/"+mail_id)
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.mohmal.com/en/inbox")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            
            emails = []
            
            emails_data = soup.find("tbody").findChildren("tr")
            
            if emails_data[0]["class"][0] == "no-messages":
                return []
            
            # https://stackoverflow.com/a/58111681
            def deCFEmail(fp):
                try:
                    r = int(fp[:2],16)
                    email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
                    return email
                except ValueError:
                    pass

            for email in emails_data:
                data = {
                    "id": email["data-msg-id"],
                    "subject": email.find("td", {"class": "subject"}).text,
                    "time": email.find("td", {"class": "time"}).text,
                    "from": deCFEmail(email.find("td", {"class": "sender"}).a.span["data-cfemail"])
                }
                emails.append(data)

            return emails



class Fakemail_net(_WaitForMail):
    """An API Wrapper around the https://www.fakemail.net/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self._session.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    
        r = self._session.get("https://www.fakemail.net/index/index")

        if not r.ok:
            raise Exception("Failed to create email, status", r.status_code)
        
        data = json.loads(r.content.decode("utf-8-sig"))

        self.email: str = data["email"]
        self.name, self.domain = self.email.split("@")


    def get_mail_content(self, mail_id: str | int) -> str:
        """
        Returns the whole content of a mail\n
        mail_id - id of the message\n
        returns the html of the content
        """
    
        r = self._session.get("https://www.fakemail.net/email/id/"+str(mail_id))
        if r.ok:
            return r.text


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...]
        """

        r = self._session.get("https://www.fakemail.net/index/refresh")
        
        if r.ok:
            # the names of the variables are really fucked so we reformat them
            
            resp = json.loads(r.content.decode("utf-8-sig"))
            data = []
            
            for email in resp:
                data.append({
                    "id": email["id"],
                    "time": email["kdy"],
                    "from": email["od"],
                    "subject": email["predmet"]
                })
            
            return data



class Tempmail_email(_WaitForMail):
    """An API Wrapper around the https://tempmail.email/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)

        self.email = f"{self.name}@{self.domain}"

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://tempmail.email/api/domains.alternative.config.json")
        if r.ok:
            return [domain[1:] for domain in r.json()["domains"]]


    def get_mail_content(self, mail_id: str) -> str:
        """
        Returns the content of a given email_id as a html string\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get("https://tempmail.email/api/emails/"+mail_id, headers={"Accept": "text/html,text/plain"})
        if r.ok:
            return r.text.split("</a><br>")[1] # remove ad


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """

        r = self._session.get("https://tempmail.email/api/emails?inbox="+self.email)
        
        if r.status_code == 404:
            return []
        elif r.ok:
            return r.json()["data"]



class Tempmail_plus(_WaitForMail):
    """An API Wrapper around the https://tempmail.plus/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(0)

        self._session = requests.Session()
        
        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))

        self.valid_domains = self.get_valid_domains()
        if domain:
            self.domain = domain if domain in self.valid_domains else random.choice(self.valid_domains)
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)

        self.email = f"{self.name}@{self.domain}"

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://tempmail.plus/en/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("div", {"class": "dropdown-menu"})[1].findChildren("button")]
        

    def get_mail_content(self, mail_id: str | int) -> dict:
        """
        Returns the content of a given email_id as a dict with data about the email\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        r = self._session.get(f"https://tempmail.plus/api/mails/{mail_id}?email={self.name}%40{self.domain}&epin=")
        if r.ok:
            return r.json()


    def get_inbox(self) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure
        """

        r = self._session.get(f"https://tempmail.plus/api/mails?email={self.name}%40{self.domain}&limit=100&epin=")
        
        if r.ok:
            return r.json()["mail_list"]



class Generator_email:
    """An API Wrapper around the https://generator.email/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate a random inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude. There is no validation for the domain\n
        exclude - a list of domain to exclude from the random selection\n
        """

        self._session = requests.Session()

        self.name = name or "".join(random.choices(ascii_lowercase+digits, k=random.randint(8, 16)))
        
        if domain:
            self.domain = domain
        else:
            if exclude:
                self.valid_domains = [domain for domain in self.valid_domains if domain not in exclude]
            self.domain = random.choice(self.valid_domains)

        self.email = f"{self.name}@{self.domain}"

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list.\nThis is not a complete list but a random selection.
        """

        r = requests.get("https://generator.email/")
        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            return [domain.text for domain in soup.find_all("div", {"class": "e7m tt-suggestion"})]
        

    def get_mail_content(self, mail_id: str, retry: bool=True, retry_delay: int=1, max_retries: int=3, _retries: int=1) -> dict:
        """
        Returns the content of a given email_id as a BeautifulSoup html object\n
        Args:\n
        mail_id - the id of the mail you want the content of
        """

        try:
            r = self._session.get(f"https://generator.email/{self.domain}/{self.name}/{mail_id}")
        except requests.exceptions.ConnectionError:
            if retry:
                if _retries == max_retries:
                    return None

                sleep(retry_delay)
                return self.get_mail_content(mail_id=mail_id, retry=retry, retry_delay=retry_delay, _retries=_retries+1)

        if r.ok:
            soup = BeautifulSoup(r.text, "lxml")
            email_list = soup.find("div", {"id": "email-table"})

            return email_list.find("div", {"class": "e7m mess_bodiyy"})
        
    def get_inbox(self, retry: bool=True, retry_delay: int=1, max_retries: int=3, _retries: int=1) -> list[dict]:
        """
        Returns the inbox of the email as a list with mails as dicts list[dict, dict, ...], None if failure. If there is 1 email in the inbox, it also returns the content of the email as a BeautifulSoup object. If there are more than 1 email in the inbox, it returns the ids of the emails, but no content\n
        retry - retry if the site refuses to allow a connection (does that sometimes, maybe ratelimit)\n
        retry_delay - how long to wait before a retry\n
        max_retries - how many retries to allow before stopping\n
        """

        try:
            r = self._session.get(f"https://generator.email/{self.domain}/{self.name}")
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
                email_data = email_list.find("div", {"class": "e7m list-group-item list-group-item-info"})
                data = {
                    "from": email_data.find("div", {"class": "e7m from_div_45g45gg"}).text,
                    "subject": email_data.find("div", {"class": "e7m subj_div_45g45gg"}).text,
                    "time": email_data.find("div", {"class": "e7m time_div_45g45gg"}).text,
                    "content": email_list.find("div", {"class": "e7m mess_bodiyy"})
                }

                return [data]
                        
            
            emails = []
            for email in email_list.findChildren("a"):
                data = {
                    "id": email["href"].rsplit("/", maxsplit=1)[1],
                    "from": email.find("div", {"class": "e7m from_div_45g45gg"}).text,
                    "subject": email.find("div", {"class": "e7m subj_div_45g45gg"}).text,
                    "time": email.find("div", {"class": "e7m time_div_45g45gg"}).text,
                }
                emails.append(data)
        
            return emails
        
    def wait_for_new_email(self, timeout: int=60) -> dict:
        """
        Waits for a new mail (using websockets), returns the data of the incoming email, None if timeout is hit or an error occurs\n
        Args:\n
        timeout - the time which is allowed to pass before forcefully stopping, <=0 -> no timeout. Note that it does not stop at exactly the time due to being sync
        """

        # The website uses websockets, for simplicity and less dependencies, we use no websockets
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
                        "id": data["clickgo"].rsplit("/", maxsplit=1)[1],
                        "from": soup.find("div", {"class": "from_div_45g45gg"}),
                        "subject": soup.find("div", {"class": "subj_div_45g45gg"}),
                        "time": soup.find("div", {"class": "time_div_45g45gg"})
                    }
            
            elif message.startswith("2"): # ping
                ws.send("3")
            
            if timeout > 0 and time()-start >= timeout:
                manual_stop = True
                ws.close()

        def on_error(ws, error: KeyError):
            print("\n------ WEBSOCKET ENCOUNTERED ERROR (Generator_email) ------\n" + str(error))

        def on_close(ws, *args):
            
            if not manual_stop:
                if timeout > 0 and time()-start >= timeout:
                    return None
                
                ws.close()
                ws = websocket.WebSocketApp("wss://generator.email/socket.io/?EIO=4&transport=websocket", on_message=on_message, on_error=on_error, on_close=on_close)
                ws.run_forever()

        email_data = None
        manual_stop = False
        ws = websocket.WebSocketApp("wss://generator.email/socket.io/?EIO=4&transport=websocket", on_message=on_message, on_error=on_error, on_close=on_close)
        ws.run_forever()
        return email_data
