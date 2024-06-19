from .._constructors import _Tempail_etc

class Lroid_com(_Tempail_etc):
    """An API Wrapper around the https://lroid.com/ website"""

    def __init__(self):
        super().__init__(urls={
            "base": "https://lroid.com",
            "kontrol": "https://lroid.com/en/api-kontrol/"
        }, offset_of_email_content=0)
                                                