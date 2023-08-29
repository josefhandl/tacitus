
from typing import Optional, List
from pydantic import BaseModel

class WireguardPeer(BaseModel):
    peer: str
    endpoint: Optional[str]
    transfer: Optional[str]

    def __init__(self,
            peer,
            endpoint,
            transfer):
        super().__init__(
            peer=peer,
            endpoint=endpoint,
            transfer=transfer
        )

class WireguardStatus(BaseModel):
    interface: str
    peers: Optional[List[WireguardPeer]]

    def __init__(self,
            interface,
            peers):
        super().__init__(
            interface=interface,
            peers=peers
        )
