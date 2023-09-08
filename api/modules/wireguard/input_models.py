from typing import Optional, List
from pydantic import BaseModel


class WireguardPeerTransfer(BaseModel):
    received: str
    sent: str

    def __init__(self,
            received,
            sent):
        super().__init__(
            received=received,
            sent=sent
        )

class WireguardPeer(BaseModel):
    peer: str
    endpoint: Optional[str]
    allowed_ips: str
    latest_handshake: Optional[str]
    transfer: Optional[WireguardPeerTransfer]

    def __init__(self,
            peer,
            endpoint,
            allowed_ips,
            latest_handshake,
            transfer):
        super().__init__(
            peer=peer,
            endpoint=endpoint,
            allowed_ips=allowed_ips,
            latest_handshake=latest_handshake,
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
