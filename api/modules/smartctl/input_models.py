from typing import Optional, List, ForwardRef
from pydantic import BaseModel


class Device(BaseModel):
    name: str
    type: str


class SmartStatus(BaseModel):
    passed: bool


class SmartTemperature(BaseModel):
    current: int


class SmartctlRoot(BaseModel):
    device: Device
    model_family: Optional[str] = ""
    model_name: str
    serial_number: str
    smart_status: SmartStatus
    temperature: Optional[SmartTemperature] = 0


BlockDeviceRef = ForwardRef("BlockDevice")


class BlockDevice(BaseModel):
    name: str
    type: str
    mountpoint: Optional[str]
    children: Optional[List[BlockDeviceRef]] = list()


class LsblkRoot(BaseModel):
    blockdevices: Optional[List[BlockDevice]]
