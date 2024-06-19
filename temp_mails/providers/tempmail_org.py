from .._constructors import _Web2

class Tempmail_org(_Web2):
    """An API Wrapper around the https://temp-mail.org/ website"""

    def __init__(self):
        """
        Generate a random inbox
        """
        
        super().__init__(urls={
            "mailbox": "https://web2.temp-mail.org/mailbox/",
            "messages": "https://web2.temp-mail.org/messages/"
        }, cf_protx=True)
        