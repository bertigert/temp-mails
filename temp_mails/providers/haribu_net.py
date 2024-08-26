from .._constructors import _Tempail_etc

class Haribu_net(_Tempail_etc):
    """An API Wrapper around the https://haribu.net/ website"""

    def __init__(self):
        super().__init__(urls={
            "base": "https://haribu.net",
            "kontrol": "https://haribu.net/en/api-kontrol/"
        }, offset_of_email_content=0)
                                                