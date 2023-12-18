from typing import Optional
from pydantic import BaseModel


class ZpoolListIn(BaseModel):
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

    def __init__(
        self,
        name,
        size,
        alloc,
        free,
        ckpoint,
        expandsz,
        frag,
        cap,
        dedup,
        health,
        altroot,
    ):
        super().__init__(
            name=name,
            size=size,
            alloc=alloc,
            free=free,
            ckpoint=ckpoint,
            expandsz=expandsz,
            frag=frag,
            cap=cap,
            dedup=dedup,
            health=health,
            altroot=altroot,
        )
