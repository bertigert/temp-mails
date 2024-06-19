from .._constructors import _Tmailor_Tmail_Cloudtempmail

class Tmail_ai(_Tmailor_Tmail_Cloudtempmail):
    """
    An API Wrapper around the https://tmail.ai/ website
    https://tmailor.com/, https://tmail.ai/, https://cloudtempmail.com/ all use the same domains (and maybe servers)
    """

    def __init__(self):
        super().__init__("https://tmail.ai/")
