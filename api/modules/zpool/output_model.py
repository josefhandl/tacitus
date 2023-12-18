from pydantic import BaseModel
from typing import Optional, List


class ZpoolListOut(BaseModel):
    name: str
    size: str
    alloc: str
    free: str
    frag: str
    cap: str
    health: str

    def __init__(
        self,
        name,
        size,
        alloc,
        free,
        frag,
        cap,
        health,
    ):
        super().__init__(
            name=name,
            size=size,
            alloc=alloc,
            free=free,
            frag=frag,
            cap=cap,
            health=health,
        )


class ZpoolResult(BaseModel):
    result: List[ZpoolListOut]
