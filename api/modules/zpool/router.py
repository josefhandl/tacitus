from ..model_base.router import BaseRouter
from ...utilities.terminal import run_cmd
from .input_modes import ZpoolList
from .output_model import PoolList
import json
import re


class Zpool(BaseRouter):
    PREFIX = "/zpool"

    async def get_list(self) -> PoolList:
        zpool_raw = run_cmd("zpool list")

        p_group_part =  r"([^\s]+)\s+"
        p_groups = rf'^{p_group_part * 10}([^\s]+)$'

        for line in zpool_raw.stdout.decode().split('\n'):
            if match := re.match(p_groups, line):
                if match.group(1) == 'NAME':
                    continue

                # create list of groups and replace '-' with None
                data = [None if g == '-' else g for g in match.groups()]
                # unpack list to the constructor
                result = ZpoolList(*data)

                return json.loads(result.model_dump_json())



router = Zpool()
