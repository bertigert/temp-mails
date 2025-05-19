from .._constructors import _Solucioneswc

class Correotemporal_org(_Solucioneswc):
    """An API Wrapper around the https://correotemporal.org/ website."""

    _BASE_URL = "https://correotemporal.org"

    def __init__(self):
        """
        Generate a random inbox\n
        """

        super().__init__(base_url=self._BASE_URL)
