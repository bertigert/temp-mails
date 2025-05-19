from .._constructors import _Tmail_Cloudtempmail

class Cloudtempmail_com(_Tmail_Cloudtempmail):
    """
    An API Wrapper around the https://cloudtempmail.com/ website
    https://tmail.ai/, https://cloudtempmail.com/ all use the same domains (and maybe servers)
    """

    def __init__(self):
        super().__init__("https://cloudtempmail.com/")
