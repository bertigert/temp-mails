from .._constructors import _Tempail_etc

class Tempmail_net(_Tempail_etc):
    """An API Wrapper around the https://tempmail.net/ website"""

    def __init__(self):
        super().__init__(urls={
            "base": "https://tempmail.net",
            "kontrol": "https://tempmail.net/en/api/kontrol/"
        }, offset_of_email_content=1)
