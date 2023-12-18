from .._model_base.router import BaseRouter
from ...utilities.terminal import run_cmd
from .input_modes import ZpoolListIn
from .output_model import ZpoolListOut, ZpoolResult
import json
import re
from typing import List


class Zpool(BaseRouter):
    PREFIX = "/zpool"

    async def get_root(self) -> ZpoolResult:
        zpool_raw = run_cmd("zpool list")

        p_group_part = r"([^\s]+)\s+"
        p_groups = rf"^{p_group_part * 10}([^\s]+)$"

        result = list()
        for line in zpool_raw.stdout.decode().split("\n"):
            if match := re.match(p_groups, line):
                if match.group(1) == "NAME":
                    continue

                # Create list of groups and replace '-' with None
                data = [None if g == "-" else g for g in match.groups()]
                # Unpack list using input model
                parsed_zpool = ZpoolListIn(*data)

                # Save parsed zpool into the output model
                result.append(
                    ZpoolListOut(
                        parsed_zpool.name,
                        parsed_zpool.size,
                        parsed_zpool.alloc,
                        parsed_zpool.free,
                        parsed_zpool.frag,
                        parsed_zpool.cap,
                        parsed_zpool.health
                    )
                )

        return {"result": [json.loads(s.model_dump_json()) for s in result]}


router = Zpool()
