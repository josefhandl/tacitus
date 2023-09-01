from typing import Optional, List
from pydantic import BaseModel

class Device(BaseModel):
    name: str
    type: str

class SmartStatus(BaseModel):
    passed: bool

class SmartctlRoot(BaseModel):
    device: Device
    model_family: Optional[str] = ''
    model_name: str
    serial_number: str
    smart_status: SmartStatus


class PartitionModel(BaseModel):
    classic_path: str
    id: str
    uuid: str
    mountpoint: str

class DiskModel(BaseModel):
    classic_path: str
    id: str
    uuid: str
    partitions: List[PartitionModel]

