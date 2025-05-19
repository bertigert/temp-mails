from .._constructors import _Minuteinbox_etc

class Disposablemail_com(_Minuteinbox_etc):
    """An API Wrapper around the https://www.disposablemail.com/ website"""
    def __init__(self):
        super().__init__(base_url="https://www.disposablemail.com", needs_cookie_and_token=True)

    @classmethod
    def get_valid_domains(cls) -> None:
        return cls.__bases__[0].get_valid_domains()
    