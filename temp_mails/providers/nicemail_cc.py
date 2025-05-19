from .._constructors import _Web

class Nicemail_cc(_Web):
    """An API Wrapper around the https://nicemail.cc/ website"""

    URLS ={
        "base": "https://nicemail.cc",
        "api": "https://web.nicemail.cc/",
    }

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        super().__init__(urls=self.URLS, name=name, domain=domain, exclude=exclude)

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        return cls.__bases__[0].get_valid_domains(cls.URLS["base"])