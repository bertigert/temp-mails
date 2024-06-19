from .._constructors import _Minuteinbox_etc

class Fakemail_net(_Minuteinbox_etc):
    """An API Wrapper around the https://www.fakemail.net/ website"""
    
    def __init__(self):
        super().__init__(base_url="https://www.fakemail.net")
