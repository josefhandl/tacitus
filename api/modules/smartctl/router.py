from ..model_base.router import BaseRouter
from .model import SmartctlRoot


class Smartctl(BaseRouter):
    PREFIX = "/smartctl"

    async def get_root(self) -> SmartctlRoot:
        return {"test": 4}


router = Smartctl()

