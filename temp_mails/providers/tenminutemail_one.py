from .._constructors import _Web

class Tenminutemail_one(_Web):
    """An API Wrapper around the https://10minutemail.one/ website"""

    URLS ={
        "base": "https://10minutemail.one",
        "api": "https://web.10minutemail.one/",
    }

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        super().__init__(urls=self.URLS, name=name, domain=domain, exclude=exclude)

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        return cls.__bases__[0].get_valid_domains(cls.URLS["base"])