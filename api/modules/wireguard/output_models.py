from pydantic import BaseModel
from .input_models import WireguardStatus
from typing import List


class WireguardResult(BaseModel):
    result: List[WireguardStatus]
