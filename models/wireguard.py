
from typing import Optional
from pydantic import BaseModel

class WireguardStatus(BaseModel):
    peer: str
    transfer: str

    def __init__(self,
            peer,
            transfer):
        super().__init__(
            peer=peer,
            transfer=transfer
        )
