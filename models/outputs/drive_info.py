
from typing import Optional, List
from pydantic import BaseModel

class DriveInfo(BaseModel):
    block_device_path: str
    model_family: str
    model_name: str
    serial_number: str
    power_mode: str
    smart_status_passed: bool
    temperature: Optional[str]
    drive_type: str

    def __init__(self,
            block_device_path,
            model_family,
            model_name,
            serial_number,
            power_mode,
            smart_status_passed,
            temperature,
            drive_type):
        super().__init__(
            block_device_path=block_device_path,
            model_family=model_family,
            model_name=model_name,
            serial_number=serial_number,
            power_mode=power_mode,
            smart_status_passed=smart_status_passed,
            temperature=temperature,
            drive_type=drive_type
        )