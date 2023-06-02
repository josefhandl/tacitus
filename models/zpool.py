
from typing import Optional
from pydantic import BaseModel

class ZpoolStatus(BaseModel):
    pool: str
    state: str

    def __init__(self,
            pool,
            state):
        super().__init__(
            pool=pool,
            state=state
        )
