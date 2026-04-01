from sqlalchemy.orm import Session

from . import models, schemas


def get_vehicles(db: Session) -> list[models.Vehicle]:
    return db.query(models.Vehicle).all()


def get_vehicle(db: Session, vin: str) -> models.Vehicle | None:
    return db.query(models.Vehicle).filter(models.Vehicle.vin == vin).first()


def create_vehicle(db: Session, vehicle_in: schemas.VehicleCreate) -> models.Vehicle:
    vehicle = models.Vehicle(**vehicle_in.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def update_vehicle(
    db: Session, current_vehicle: models.Vehicle, vehicle_in: schemas.VehicleUpdate
) -> models.Vehicle:
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_vehicle, field, value)

    db.add(current_vehicle)
    db.commit()
    db.refresh(current_vehicle)
    return current_vehicle


def delete_vehicle(db: Session, vehicle: models.Vehicle) -> None:
    (
        db.query(models.MaintenanceLog)
        .filter(models.MaintenanceLog.vin == vehicle.vin)
        .delete(synchronize_session=False)
    )
    db.delete(vehicle)
    db.commit()
