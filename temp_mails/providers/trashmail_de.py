from .._constructors import _Fake_trash_mail

class Trashmail_de(_Fake_trash_mail):
    """An API Wrapper around the https://www.trashmail.de/ website"""

    _BASE_URL = "https://www.trashmail.de"

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        super().__init__(base_url=self._BASE_URL, name=name, domain=domain, exclude=exclude)

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        return cls.__bases__[0].get_valid_domains(cls._BASE_URL)
