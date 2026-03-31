from sqlalchemy.orm import Session

from . import models, schemas


def get_service_types(db: Session) -> list[models.ServiceType]:
    return db.query(models.ServiceType).all()


def get_service_type(db: Session, service_type_id: int) -> models.ServiceType | None:
    return (
        db.query(models.ServiceType)
        .filter(models.ServiceType.service_type_id == service_type_id)
        .first()
    )


def create_service_type(
    db: Session, service_type_in: schemas.ServiceTypeCreate
) -> models.ServiceType:
    service_type = models.ServiceType(**service_type_in.model_dump())
    db.add(service_type)
    db.commit()
    db.refresh(service_type)
    return service_type


def update_service_type(
    db: Session,
    current_service_type: models.ServiceType,
    service_type_in: schemas.ServiceTypeUpdate,
) -> models.ServiceType:
    update_data = service_type_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_service_type, field, value)

    db.add(current_service_type)
    db.commit()
    db.refresh(current_service_type)
    return current_service_type


def delete_service_type(db: Session, service_type: models.ServiceType) -> None:
    db.delete(service_type)
    db.commit()
