from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from . import crud_maintenance_logs, crud_service_types, crud_vehicles, schemas
from .database import Base, engine, get_db

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/vehicles", response_model=schemas.VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    existing = crud_vehicles.get_vehicle(db, vehicle.vin)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle with this VIN already exists.",
        )
    return crud_vehicles.create_vehicle(db, vehicle)


@app.get("/vehicles", response_model=list[schemas.VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    return crud_vehicles.get_vehicles(db)


@app.get("/vehicles/{vin}", response_model=schemas.VehicleRead)
def get_vehicle(vin: str, db: Session = Depends(get_db)):
    vehicle = crud_vehicles.get_vehicle(db, vin)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return vehicle


@app.put("/vehicles/{vin}", response_model=schemas.VehicleRead)
def update_vehicle(vin: str, vehicle_in: schemas.VehicleUpdate, db: Session = Depends(get_db)):
    vehicle = crud_vehicles.get_vehicle(db, vin)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    return crud_vehicles.update_vehicle(db, vehicle, vehicle_in)


@app.delete("/vehicles/{vin}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vin: str, db: Session = Depends(get_db)):
    vehicle = crud_vehicles.get_vehicle(db, vin)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    crud_vehicles.delete_vehicle(db, vehicle)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/service-types",
    response_model=schemas.ServiceTypeRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service_type(
    service_type: schemas.ServiceTypeCreate, db: Session = Depends(get_db)
):
    return crud_service_types.create_service_type(db, service_type)


@app.get("/service-types", response_model=list[schemas.ServiceTypeRead])
def list_service_types(db: Session = Depends(get_db)):
    return crud_service_types.get_service_types(db)


@app.get("/service-types/{service_type_id}", response_model=schemas.ServiceTypeRead)
def get_service_type(service_type_id: int, db: Session = Depends(get_db)):
    service_type = crud_service_types.get_service_type(db, service_type_id)
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found."
        )
    return service_type


@app.put("/service-types/{service_type_id}", response_model=schemas.ServiceTypeRead)
def update_service_type(
    service_type_id: int,
    service_type_in: schemas.ServiceTypeUpdate,
    db: Session = Depends(get_db),
):
    service_type = crud_service_types.get_service_type(db, service_type_id)
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found."
        )
    return crud_service_types.update_service_type(db, service_type, service_type_in)


@app.delete("/service-types/{service_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_type(service_type_id: int, db: Session = Depends(get_db)):
    service_type = crud_service_types.get_service_type(db, service_type_id)
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found."
        )
    crud_service_types.delete_service_type(db, service_type)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/maintenance-logs",
    response_model=schemas.MaintenanceLogRead,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_log(
    maintenance_log: schemas.MaintenanceLogCreate, db: Session = Depends(get_db)
):
    if not crud_vehicles.get_vehicle(db, maintenance_log.vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    if not crud_service_types.get_service_type(db, maintenance_log.service_type_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found."
        )
    return crud_maintenance_logs.create_maintenance_log(db, maintenance_log)


@app.get("/maintenance-logs", response_model=list[schemas.MaintenanceLogRead])
def list_maintenance_logs(db: Session = Depends(get_db)):
    return crud_maintenance_logs.get_maintenance_logs(db)


@app.get("/maintenance-logs/{maintenance_id}", response_model=schemas.MaintenanceLogRead)
def get_maintenance_log(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance_log = crud_maintenance_logs.get_maintenance_log(db, maintenance_id)
    if not maintenance_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found."
        )
    return maintenance_log


@app.put("/maintenance-logs/{maintenance_id}", response_model=schemas.MaintenanceLogRead)
def update_maintenance_log(
    maintenance_id: int,
    maintenance_log_in: schemas.MaintenanceLogUpdate,
    db: Session = Depends(get_db),
):
    maintenance_log = crud_maintenance_logs.get_maintenance_log(db, maintenance_id)
    if not maintenance_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found."
        )

    if maintenance_log_in.vin is not None and not crud_vehicles.get_vehicle(db, maintenance_log_in.vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    if (
        maintenance_log_in.service_type_id is not None
        and not crud_service_types.get_service_type(db, maintenance_log_in.service_type_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found."
        )

    return crud_maintenance_logs.update_maintenance_log(db, maintenance_log, maintenance_log_in)


@app.delete("/maintenance-logs/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_log(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance_log = crud_maintenance_logs.get_maintenance_log(db, maintenance_id)
    if not maintenance_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found."
        )
    crud_maintenance_logs.delete_maintenance_log(db, maintenance_log)
    return Response(status_code=status.HTTP_204_NO_CONTENT)