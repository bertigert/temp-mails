from .._constructors import _Tempail_etc

class Tempail_com(_Tempail_etc):
    """An API Wrapper around the https://tempail.com website"""

    def __init__(self):
        super().__init__(urls={
            "base": "https://tempail.com",
            "kontrol": "https://tempail.com/en/api/kontrol/"
        }, offset_of_email_content=0)
                                                