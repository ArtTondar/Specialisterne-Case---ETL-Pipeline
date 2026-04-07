# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union
from uuid import UUID

class MeasurementBase(BaseModel):
    station_id: Optional[Union[int, UUID]]  # DMI: station_id, Sensors: reader_id
    sensor: str  # DMI, BME280, DS18B20, SCD41
    location: Optional[str]  # for BME280/DS18B20 inside/outside
    parameter: str  # temperature, humidity, pressure, co2
    value: float
    observed_at: datetime

    class Config:
        orm_mode = True

class Station(BaseModel):
    station_id: Union[int, UUID]

    class Config:
        orm_mode = True