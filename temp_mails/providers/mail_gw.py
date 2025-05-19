from .._constructors import _Mailtm_etc

class Mail_gw(_Mailtm_etc):
    """An API Wrapper around the https://mail.gw/ website"""

    _BASE_URL = "https://api.mail.gw"

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
            "base": self._BASE_URL,
            "stream": self._BASE_URL
        }, name=name, domain=domain, exclude=exclude)

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        return cls.__bases__[0].get_valid_domains(cls._BASE_URL)
