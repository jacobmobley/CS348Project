from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vin: Mapped[str] = mapped_column(String(17), primary_key=True, index=True)
    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan"
    )


class ServiceType(Base):
    __tablename__ = "service_types"

    service_type_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    service_interval_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    service_interval_miles: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(
        back_populates="service_type"
    )


class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    maintenance_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    reported_mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    service_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("service_types.service_type_id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    vin: Mapped[str] = mapped_column(
        String(17),
        ForeignKey("vehicles.vin", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_type: Mapped[ServiceType] = relationship(back_populates="maintenance_logs")
    vehicle: Mapped[Vehicle] = relationship(back_populates="maintenance_logs")
