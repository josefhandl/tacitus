from .._model_base.router import BaseRouter
from .input_models import SmartctlRoot, LsblkRoot, BlockDevice
from .output_models import DrivesResult, DriveInfo
from ...utilities.terminal import run_cmd
import json
from pydantic import ValidationError
from loguru import logger
from typing import List, Dict
import re
from fastapi import HTTPException


class Drives(BaseRouter):
    PREFIX = "/drives"

    async def get_root(self) -> DrivesResult:
        # (lsblk) get all block devices
        lsblk_json = run_cmd("lsblk --json --output NAME,TYPE,MOUNTPOINT --tree")
        if not lsblk_json:
            msg = f"Cannot get block devices"
            logger.error(msg)
            raise HTTPException(status_code=500, detail=msg)

        # Fill models with json
        try:
            lsblk_data = LsblkRoot.model_validate(json.loads(lsblk_json.stdout.decode()))
        except ValidationError as ex:
            msg = f"Validation the lsblk failed. Exception: {ex}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail=msg)
        except Exception as ex:
            msg = f"Unknown error. Exception: {ex}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail=msg)

        # Filter block devices to find only physical disks
        disks: List[BlockDevice] = list()
        for bd in lsblk_data.blockdevices:
            if bd.type == "disk":
                disks.append(bd)

        # (hdparm) get power mode but avoid to wake up the drives
        # It is also possible to use smartctl, but it requires to know device type to avoid wake up
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

        # (smartctl) get health from all of the physical disks
        smarts: Dict[SmartctlRoot] = dict()
        for d in disks:
            smartctl_json = run_cmd(f"api/wrappers/w_smartctl /dev/{d.name}", [0, 4, 64, 68, 128])  # -d sat
            if not smartctl_json:
                logger.warning(f"Failed to obtain S.M.A.R.T. info from /dev/{d.name} disk")
                continue

            # Fill models from smartctl output
            try:
                smartctl_data = SmartctlRoot.model_validate(json.loads(smartctl_json.stdout.decode()))
                smarts[d.name] = smartctl_data
            except ValidationError as ex:
                msg = f"Validation the smartctl failed with /dev/{d.name} disk. Exception: {ex}"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)
            except Exception as ex:
                msg = f"Unknown error. Exception: {ex}"
                logger.error(msg)
                raise HTTPException(status_code=500, detail=msg)

        # convert Lsblk models, power modes and smartctl models into the final model ready for output
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


router = Drives()
