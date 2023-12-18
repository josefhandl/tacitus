from .._model_base.router import BaseRouter
from .input_models import SmartctlRoot, LsblkRoot, BlockDevice
from .output_model import SmartResult, DriveInfo
from ...utilities.terminal import run_cmd
import json
from pydantic import ValidationError
from loguru import logger
from typing import List, Dict
import re
from fastapi import HTTPException


class Smartctl(BaseRouter):
    PREFIX = "/smartctl"

    async def get_root(self) -> SmartResult:
        # (lsblk) get all block devices
        lsblk_json = run_cmd("lsblk --json --output NAME,TYPE,MOUNTPOINT --tree")
        if not lsblk_json:
            logger.error(f"Cannot get block devices")
            raise HTTPException(status_code=500, detail="Cannot get block devices")

        # fill models with json
        try:
            lsblk_data = LsblkRoot.model_validate(json.loads(lsblk_json.stdout.decode()))
        except ValidationError as ex:
            logger.error(f"Validation the lsblk failed. Exception: {ex}")
            raise HTTPException(status_code=500, detail="Validation the lsblk failed")
        except Exception as ex:
            logger.error(f"Unknown error. Exception: {ex}")
            raise HTTPException(status_code=500, detail="Unknown error")

        # filter block devices to find only physical disks
        disks: List[BlockDevice] = list()
        for bd in lsblk_data.blockdevices:
            if bd.type == "disk":
                disks.append(bd)

        # (hdparm) get power mode but avoid to wake up the drives
        # it is also possible to use smartctl, but it requires to know device type to avoid wake up
        # (e.g. USB drives are problematic)
        power_modes = dict()
        for d in disks:
            power_mode = "null"

            hdparm_raw = run_cmd(f"api/wrappers/w_hdparm /dev/{d.name}")
            if hdparm_raw:
                r_power_mode = r"^ drive state is:\s+(\w+)"

                for line in hdparm_raw.stdout.decode().split("\n"):
                    if match := re.match(r_power_mode, line):
                        power_mode = match.group(1)

            power_modes[d.name] = power_mode

        # get health from all of the physical disks
        smarts: Dict[SmartctlRoot] = dict()
        for d in disks:
            smartctl_json = run_cmd(f"api/wrappers/w_smartctl /dev/{d.name}", [0, 4, 64, 68, 128])  # -d sat
            if not smartctl_json:
                continue

            try:
                smartctl_data = SmartctlRoot.model_validate(json.loads(smartctl_json.stdout.decode()))
                smarts[d.name] = smartctl_data
            except ValidationError as ex:
                logger.error(f"Validation the smartctl failed with /dev/{d.name} disk. Exception: {ex}")
                raise HTTPException(status_code=500, detail="Validation the smartctl failed")
            except Exception as ex:
                logger.error(ex)
                raise HTTPException(status_code=500, detail="Unknown error")

        # convert Lsblk models, power modes and Smartctl models into the final model ready for output
        result: List[DriveInfo] = list()
        for physical_disk in disks:
            block_device_path = physical_disk.name
            power_mode = power_modes[block_device_path]
            smartctl_model = smarts[block_device_path]
            temperature = None
            if hasattr(smartctl_model, "temperature") and smartctl_model.temperature:
                temperature = str(smartctl_model.temperature.current)

            result.append(
                DriveInfo(
                    block_device_path,
                    smartctl_model.model_family,
                    smartctl_model.model_name,
                    smartctl_model.serial_number,
                    power_mode,
                    smartctl_model.smart_status.passed,
                    temperature,
                    smartctl_model.device.type,
                )
            )

        return {"result": [json.loads(di.model_dump_json()) for di in result]}


router = Smartctl()
