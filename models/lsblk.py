
from typing import List, Optional, ForwardRef
from pydantic import BaseModel, validator, BaseConfig
from pydantic.fields import ModelField
from pydantic.typing import is_union, get_args, get_origin

BlockDeviceRef = ForwardRef("BlockDevice")

class BlockDevice(BaseModel):
    name: str
    type: str
    mountpoints: List[Optional[str]]
    children: Optional[List[BlockDeviceRef]]

class LsblkRoot(BaseModel):
    blockdevices: List[BlockDevice]
