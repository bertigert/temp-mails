import json

import websocket

from .._constructors import _Solucioneswc

class Correotemporal_org(_Solucioneswc):
    """An API Wrapper around the https://correotemporal.org/ website."""

    def __init__(self, name: str=None, domain:str=None, exclude: list[str]=None):
        """
        Generate an inbox\n
        Args:\n
        name - name for the email, if None a random one is chosen\n
        domain - the domain to use, domain is prioritized over exclude\n
        exclude - a list of domain to exclude from the random selection\n
        """

        super().__init__(base_url="https://correotemporal.org", name=name, domain=domain, exclude=exclude)

    @staticmethod
    def get_valid_domains() -> list[str]:
        """
        Returns a list of valid domains of the service (format: abc.xyz) as a list.\n
        It is prefered if you use the valid_domains list of an already initialised mail object.
        """
        
        def on_message(ws, msg):
            if msg.startswith("0"): # connected
                ws.send("40")

            elif msg.startswith("2"): # ping
                ws.send("3")

            elif msg.startswith("40"): # gets send out at the beginning
                ws.send('42["get_domains"]')

            elif msg.startswith("42"):
                data = json.loads(msg[2:])
                
                if data[0] == "set_domains_data":
                    nonlocal valid_domains
                    valid_domains = [domain["name"] for domain in data[1]]
                    ws.close()
        
        valid_domains = None
        ws = websocket.WebSocketApp("wss://ws.solucioneswc.com:2053/socket.io/?user_token=empty&visitor_token=empty&emails_list=empty&page_type=inbox&EIO=4&transport=websocket", 
                                    on_error=lambda *args: ws.close(), on_message=on_message, 
                                    header={"Origin": "https://correotemporal.org"}
                                    )
        ws.run_forever(suppress_origin=True)
        
        return valid_domains


 