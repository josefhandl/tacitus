
from typing import List, Optional, ForwardRef
from pydantic import BaseModel, validator, BaseConfig
#from pydantic.fields import ModelField
#from pydantic.typing import is_union, get_args, get_origin

BlockDeviceRef = ForwardRef("BlockDevice")

class BlockDevice(BaseModel):
    name: str
    type: str
    mountpoint: Optional[str]
    children: Optional[List[BlockDeviceRef]] = list()

class LsblkRoot(BaseModel):
    blockdevices: Optional[List[BlockDevice]]
