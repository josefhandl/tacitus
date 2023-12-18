from pydantic import BaseModel
from typing import Optional, List
from .input_models import ZpoolList


class ZpoolResult(BaseModel):
    result: List[ZpoolList]
