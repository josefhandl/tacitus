from pydantic import BaseModel
from typing import Optional


class PoolList(BaseModel):
    name: str
    size: str
    alloc: str
    free: str
    ckpoint: Optional[str]
    expandsz: Optional[str]
    frag: str
    cap: str
    dedup: str
    health: str
    altroot: Optional[str]