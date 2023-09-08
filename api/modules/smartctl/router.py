from ..model_base.router import BaseRouter
from .input_models import SmartctlRoot, LsblkRoot, BlockDevice
from ...utilities.terminal import run_cmd
import json
from pydantic import ValidationError
from loguru import logger
from typing import List
import re
from fastapi import HTTPException


class Smartctl(BaseRouter):
    PREFIX = "/smartctl"

    async def get_root(self) -> dict:
        # (lsblk) get all block devices
        lsblk_json = run_cmd("lsblk --json --output NAME,TYPE,MOUNTPOINT --tree")
        if not lsblk_json:
            raise HTTPException(status_code=500, detail="Cannot get block devices")

        # fill models with json
        try:
            lsblk_data = LsblkRoot.model_validate(json.loads(lsblk_json.stdout.decode()))
        except ValidationError as ex:
            logger.error(f"Validation the lsblk failed. Exception: {ex}")
            raise HTTPException(status_code=500, detail="Validation the lsblk failed")
        except Exception as ex:
            logger.error(ex)
            raise HTTPException(status_code=500, detail="Unknown error")

        # filter block devices to find only physical disks
        disks: List[BlockDevice] = list()
        for bd in lsblk_data.blockdevices:
            if bd.type == "disk":
                disks.append(bd)
                print(bd.children)

        # (hdparm) get power mode but avoid to wake up the drives
        # it is also possible to use smartctl, but it requires to know device type to avoid wake up
        # (e.g. USB drives are problematic)
        power_modes = dict()
        for d in disks:
            power_mode = "null"

            hdparm_raw = run_cmd(f"hdparm -C /dev/{d.name}")
            if hdparm_raw:
                r_power_mode = r"^ drive state is:\s+(\w+)"

                for line in hdparm_raw.stdout.decode().split('\n'):
                    if match := re.match(r_power_mode, line):
                        power_mode = match.group(1)

            power_modes[f"/dev/{d.name}"] = power_mode

        # get health from all of the physical disks
        smarts: List[SmartctlRoot] = list()
        for d in disks:
            smartctl_json = run_cmd(f"smartctl -i -a --json /dev/{d.name}", [0, 4, 64, 68, 128])  # -d sat
            if not smartctl_json:
                continue

            try:
                smartctl_data = SmartctlRoot.model_validate(json.loads(smartctl_json.stdout.decode()))
                smarts.append(smartctl_data)
            except ValidationError as ex:
                logger.error(f"Validation the smartctl failed with /dev/{d.name} disk. Exception: {ex}")
                raise HTTPException(status_code=500, detail="Validation the smartctl failed")
            except Exception as ex:
                logger.error(ex)
                raise HTTPException(status_code=500, detail="Unknown error")

        return {"result": [json.loads(s.model_dump_json()) for s in smarts]}


router = Smartctl()
