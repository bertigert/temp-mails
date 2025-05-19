from .._constructors import _Solucioneswc

class Tempmail_ninja(_Solucioneswc):
    """An API Wrapper around the https://tempmail.ninja/ website."""

    _BASE_URL = "https://tempmail.ninja"

    def __init__(self):
        """
        Generate a random inbox\n
        """

        super().__init__(base_url=self._BASE_URL)
