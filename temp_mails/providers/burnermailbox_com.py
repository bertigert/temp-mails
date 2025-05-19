from .._constructors import _Livewire2

class Burnermailbox_com(_Livewire2):
    """An API Wrapper around the https://burnermailbox.com/ website."""

    _BASE_URL = "https://burnermailbox.com"

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
                "mailbox": self._BASE_URL+"/mailbox/",
                "app": self._BASE_URL+"/livewire/message/frontend.app",
                "actions": self._BASE_URL+"/livewire/message/frontend.actions"
            },
            order=0, name=name, domain=domain, exclude=exclude
            )


    @staticmethod
    def get_valid_domains() -> list[str] | None:
        """Returns a list of a valid domains, None if failure. Only one domain"""
       
        return ["kihasl.com"]
