from .._constructors import _Livewire

class Emaildashfree_online(_Livewire):
    """An API Wrapper around the https://email-free.online/ website"""

    _BASE_URL = "https://email-free.online"

    def __init__(self, name: str=None, domain: str=None, exclude: list[str]=None):
        """
            Generate an inbox\n
            Args:\n
            name - name for the email, if None a random one is chosen\n
            domain - the domain to use, domain is prioritized over exclude\n
            exclude - a list of domain to exclude from the random selection\n
        """
        
        super().__init__(
            urls={
                "base": self._BASE_URL,
                "app": self._BASE_URL+"/livewire/message/frontend.app",
                "actions": self._BASE_URL+"/livewire/message/frontend.actions"
            },
            order=0, name=name, domain=domain, exclude=exclude
        )

    @classmethod
    def get_valid_domains(cls) -> list[str]:
        return cls.__bases__[0].get_valid_domains(cls._BASE_URL)
