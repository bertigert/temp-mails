from .._constructors import _Tmailor_Tmail_Cloudtempmail

class Tmailor_com(_Tmailor_Tmail_Cloudtempmail):
    """
    An API Wrapper around the https://tmailor.com/ website.\n
    https://tmailor.com/, https://tmail.ai/, https://cloudtempmail.com/ all use the same domains (and maybe servers)
    
    """

    def __init__(self):
        super().__init__("https://tmailor.com/")
