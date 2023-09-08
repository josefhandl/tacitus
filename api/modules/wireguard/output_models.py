from pydantic import BaseModel
from .input_models import WireguardStatus
from typing import List


class WireGuardResult(BaseModel):
    result: List[WireguardStatus]