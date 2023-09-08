from ..model_base.router import BaseRouter
from ...utilities.terminal import run_cmd
from .input_modes import ZpoolList, ZpoolStatus
from .output_model import PoolList, PoolStatuses
import json
import re
from typing import List


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


    async def get_status(self) -> PoolStatuses:
        zpool_raw = run_cmd("zpool status")

        p_pool =  r"^  pool:\s+([\w_\-\.]+)"
        p_state = r"^ state:\s+(\w+)"

        statuses: List[ZpoolStatus] = list()

        pool = None
        state = None

        for line in zpool_raw.stdout.decode().split('\n'):
            # "pool"
            if match := re.match(p_pool,  line):
                # if pool is already set, save the last round (and start a new one)
                if pool:
                    statuses.append(ZpoolStatus(
                        pool,
                        state
                    ))
                    pool = None

                pool = match.group(1)

            # "state"
            if match := re.match(p_state, line):
                state = match.group(1)

        statuses.append(ZpoolStatus(
            pool,
            state
        ))

        return {
            "pools": [json.loads(s.model_dump_json()) for s in statuses]
        }


router = Zpool()
