from __future__ import annotations

from datetime import date as dt_date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class VehicleBase(BaseModel):
    make: str = Field(min_length=1)
    model: str = Field(min_length=1)
    year: int
    purchase_date: dt_date


class VehicleCreate(VehicleBase):
    vin: str = Field(min_length=17, max_length=17)


class VehicleUpdate(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    purchase_date: dt_date | None = None


class VehicleRead(VehicleBase):
    vin: str
    model_config = ConfigDict(from_attributes=True)


class ServiceTypeBase(BaseModel):
    name: str = Field(min_length=1)
    service_interval_months: int | None = None
    service_interval_miles: int | None = None


class ServiceTypeCreate(ServiceTypeBase):
    pass


class ServiceTypeUpdate(BaseModel):
    name: str | None = None
    service_interval_months: int | None = None
    service_interval_miles: int | None = None


class ServiceTypeRead(ServiceTypeBase):
    service_type_id: int
    model_config = ConfigDict(from_attributes=True)


class MaintenanceLogBase(BaseModel):
    date: dt_date
    reported_mileage: int
    cost: Decimal
    notes: str = Field(min_length=1)
    service_type_id: int
    vin: str = Field(min_length=17, max_length=17)


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogUpdate(BaseModel):
    date: dt_date | None = None
    reported_mileage: int | None = None
    cost: Decimal | None = None
    notes: str | None = None
    service_type_id: int | None = None
    vin: str | None = Field(default=None, min_length=17, max_length=17)


class MaintenanceLogRead(MaintenanceLogBase):
    maintenance_id: int
    model_config = ConfigDict(from_attributes=True)


class LatestMileageRead(BaseModel):
    vin: str
    date: dt_date
    reported_mileage: int


class LatestServiceNameRead(BaseModel):
    vin: str
    date: dt_date
    service_name: str


class MileageHistoryRead(BaseModel):
    vin: str
    date: dt_date
    reported_mileage: int


class ServiceHistoryRead(BaseModel):
    vin: str
    date: dt_date
    service_name: str


class TotalSpentRead(BaseModel):
    vin: str
    total_spent: Decimal
