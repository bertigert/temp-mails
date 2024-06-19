import requests
from .._constructors import _Mailcare

class Cryptogmail_com(_Mailcare):
    """An API Wrapper around the https://cryptogmail.com/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        super().__init__(base_url="https://cryptogmail.com", name=name, domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://cryptogmail.com/api/domains.config.json")
        if r.ok:
            return [domain[1:] for domain in r.json()["domains"]]
