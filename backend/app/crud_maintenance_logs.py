from datetime import date as dt_date

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


def get_maintenance_logs(db: Session) -> list[models.MaintenanceLog]:
    return db.query(models.MaintenanceLog).all()


def get_maintenance_log(db: Session, maintenance_id: int) -> models.MaintenanceLog | None:
    return (
        db.query(models.MaintenanceLog)
        .filter(models.MaintenanceLog.maintenance_id == maintenance_id)
        .first()
    )


def get_latest_maintenance_log_by_vin(
    db: Session, vin: str
) -> models.MaintenanceLog | None:
    return (
        db.query(models.MaintenanceLog)
        .filter(models.MaintenanceLog.vin == vin)
        .order_by(models.MaintenanceLog.date.desc(), models.MaintenanceLog.maintenance_id.desc())
        .first()
    )


def get_latest_service_name_by_vin(db: Session, vin: str) -> tuple[str, dt_date] | None:
    latest_log = get_latest_maintenance_log_by_vin(db, vin)
    if not latest_log:
        return None

    service_type = (
        db.query(models.ServiceType)
        .filter(models.ServiceType.service_type_id == latest_log.service_type_id)
        .first()
    )
    if not service_type:
        return None

    return (service_type.name, latest_log.date)


def get_mileage_history(db: Session, vin: str) -> list[models.MaintenanceLog]:
    return (
        db.query(models.MaintenanceLog)
        .filter(models.MaintenanceLog.vin == vin)
        .order_by(models.MaintenanceLog.date.desc(), models.MaintenanceLog.maintenance_id.desc())
        .all()
    )


def get_service_history(db: Session, vin: str) -> list[tuple[models.MaintenanceLog, str]]:
    return (
        db.query(models.MaintenanceLog, models.ServiceType.name)
        .join(
            models.ServiceType,
            models.ServiceType.service_type_id == models.MaintenanceLog.service_type_id,
        )
        .filter(models.MaintenanceLog.vin == vin)
        .order_by(models.MaintenanceLog.date.desc(), models.MaintenanceLog.maintenance_id.desc())
        .all()
    )


def get_total_spent_by_vin(db: Session, vin: str):
    return (
        db.query(func.coalesce(func.sum(models.MaintenanceLog.cost), 0))
        .filter(models.MaintenanceLog.vin == vin)
        .scalar()
    )


def create_maintenance_log(
    db: Session, maintenance_log_in: schemas.MaintenanceLogCreate
) -> models.MaintenanceLog:
    maintenance_log = models.MaintenanceLog(**maintenance_log_in.model_dump())
    db.add(maintenance_log)
    db.commit()
    db.refresh(maintenance_log)
    return maintenance_log


def update_maintenance_log(
    db: Session,
    current_maintenance_log: models.MaintenanceLog,
    maintenance_log_in: schemas.MaintenanceLogUpdate,
) -> models.MaintenanceLog:
    update_data = maintenance_log_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_maintenance_log, field, value)

    db.add(current_maintenance_log)
    db.commit()
    db.refresh(current_maintenance_log)
    return current_maintenance_log


def delete_maintenance_log(db: Session, maintenance_log: models.MaintenanceLog) -> None:
    db.delete(maintenance_log)
    db.commit()
