import random
from string import ascii_lowercase, digits
import json

import requests

from .._constructors import _Mailtm_etc

class Mail_tm(_Mailtm_etc):
    """An API Wrapper around the https://mail.tm/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None, password: str=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        password - a password used for authentification
        """
        
        super().__init__(urls={
            "base": "https://api.mail.tm",
            "stream": "https://mercure.mail.tm"
        }, name=name, domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """
        
        r = requests.get("https://api.mail.tm/domains")
        if r.ok:
            return [domain["domain"] for domain in r.json()["hydra:member"]]  

