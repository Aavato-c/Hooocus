import os, sys
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURR_DIR.split("db")[0])

from uuid import UUID
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator

from db.utils import get_timestamp, get_uuid
from typing import Any

BaseModel.model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

class BaseModel(BaseModel):
    @field_validator("id", mode="before", check_fields=False)  # Before the field is set
    def check_id(cls, v):
        if type(v) == UUID:
            return v
        elif type(v) == str:
            return UUID(v)
        else:
            raise ValueError("ID must be a UUID")


class SharedBase(BaseModel):
    id: str | UUID = Field(default_factory=get_uuid)
    created_at: float
    updated_at: float
    soft_delete: Optional[bool] = False

# ===================== ImageOrder =====================
class ImageOrderInDb(SharedBase):
    """Image model

    The image order model is used to store image generation information in the database.
    The status of the order might be fulfilled, pending, or failed. 

    Args:
        id (UUID): A UUID for the ImageOrder.
        created_at (float): The timestamp when the user was created.
        updated_at (float): The timestamp when the user was last updated.
        soft_delete (bool): A flag to indicate if the image has been soft-deleted.
        generation_data (JSON): The data used to generate the image.
        image_uri (Optional[str]): The URI of the image.
        has_been_generated (bool): A flag to indicate if the image has been generated.
    """

    image_uri: Optional[str] = None
    generation_data: object | dict
    has_been_generated: bool = False

class ImageOrderInCreate(BaseModel):
    """ImageOrderInCreate

    Args:
        id (Optional[UUID]): The ID of the image
        created_at (Optional[float]): The timestamp of when the image was created
        updated_at (Optional[float]): The timestamp of when the image was last updated
        soft_delete (Optional[bool]): Whether the image is soft deleted
        generation_data (Dict[str, Any]): The data used to generate the image
        image_uri (Optional[str]): The URI of the image
        has_been_generated (Optional[bool]): Whether the image has been generated

    """

    id: UUID = Field(default_factory=get_uuid)
    created_at: float = Field(default_factory=get_timestamp)
    updated_at: float = Field(default_factory=get_timestamp)
    soft_delete: Optional[bool] = False

    generation_data: object | dict
    image_uri: Optional[str] = None
    has_been_generated: Optional[bool] = False
    
    
class ImageOrderInResponse(SharedBase):
    """ImageOrderInResponse

    Args:
        id (UUID): The ID of the image
        created_at (float): The timestamp of when the image was created
        updated_at (float): The timestamp of when the image was last updated
        soft_delete (bool): Whether the image is soft deleted
        generation_data (Dict[str, Any]): The data used to generate the image
        image_uri (Optional[str]): The URI of the image
        has_been_generated (bool): Whether the image has been generated

    """
    generation_data: object | dict
    image_uri: Optional[str] = None
    has_been_generated: bool