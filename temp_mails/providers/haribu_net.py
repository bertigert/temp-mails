from .._constructors import _Tempail_etc

class Haribu_net(_Tempail_etc):
    """An API Wrapper around the http://haribu.net/ website"""

    def __init__(self):
        super().__init__(urls={
            "base": "https://lroid.com",
            "kontrol": "https://lroid.com/en/api-kontrol/"
        }, offset_of_email_content=0)
                                                