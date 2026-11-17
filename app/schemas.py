
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RideCreate(BaseModel):

    rider_id: int

    pickup: str

    drop_location: str = Field(alias="drop")

    model_config = ConfigDict(populate_by_name=True)


class RideResponse(BaseModel):

    ride_id: int = Field(alias="rideId")

    rider_id: int

    pickup: str

    drop_location: str = Field(alias="drop")

    status: str

    assigned_driver_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
