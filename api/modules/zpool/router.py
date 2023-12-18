from .._model_base.router import BaseRouter
from ...utilities.terminal import run_cmd
from .input_models import ZpoolList
from .output_models import ZpoolResult
import json
import re
from typing import List


class Zpool(BaseRouter):
    PREFIX = "/zpool"

    async def get_root(self) -> ZpoolResult:
        zpool_raw = run_cmd("zpool list -H -o name,size,allocated,free,fragmentation,capacity,health")

        p_group_part = r"([^\s]+)\s+"
        p_groups = rf"^{p_group_part * 6}([^\s]+)$" # The number is count of properties minus one

        result = list()
        for line in zpool_raw.stdout.decode().split("\n"):
            if match := re.match(p_groups, line):
                # Unpack list using input model
                result.append(ZpoolList(*match.groups()))

        return {"result": [json.loads(s.model_dump_json()) for s in result]}


router = Zpool()
