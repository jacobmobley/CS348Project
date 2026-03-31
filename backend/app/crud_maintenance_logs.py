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
