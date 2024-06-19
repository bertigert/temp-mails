import requests
from .._constructors import _Mailcare

class Tempmail_email(_Mailcare):
    """An API Wrapper around the https://tempmail.email/ website"""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        super().__init__(base_url="https://tempmail.email", name=name, domain=domain, exclude=exclude)


    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list
        """

        r = requests.get("https://tempmail.email/api/domains.alternative.config.json")
        if r.ok:
            return [domain[1:] for domain in r.json()["domains"]]
                        