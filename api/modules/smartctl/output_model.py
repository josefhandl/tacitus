from pydantic import BaseModel
from typing import List


class Device(BaseModel):
    name: str
    type: str


class Status(BaseModel):
    passed: bool


class Drive(BaseModel):
    device: Device
    model_family: str
    model_name: str
    serial_number: str
    smart_status: Status

class SmartResult(BaseModel):
    result: List[Drive]
