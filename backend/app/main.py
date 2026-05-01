from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import crud_maintenance_logs, crud_service_types, crud_vehicles, schemas
from .database import Base, engine, get_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/vehicles/search", response_model=list[schemas.VehicleRead])
def search_vehicles(
    q: str = Query(..., min_length=1, description="Search text for VIN, make, model, or year"),
    db: Session = Depends(get_db),
):
    return crud_vehicles.search_vehicles(db, q)


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


@app.get("/maintenance-logs/search", response_model=list[schemas.MaintenanceLogRead])
def search_maintenance_logs(
    q: str = Query(
        ..., min_length=1, description="Search text for VIN, notes, or service type name"
    ),
    db: Session = Depends(get_db),
):
    return crud_maintenance_logs.search_maintenance_logs(db, q)


@app.get(
    "/maintenance-logs/history/mileage/{vin}", response_model=list[schemas.MileageHistoryRead]
)
def list_mileage_history(vin: str, db: Session = Depends(get_db)):
    if not crud_vehicles.get_vehicle(db, vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    history = crud_maintenance_logs.get_mileage_history(db, vin)
    return [
        {"vin": log.vin, "date": log.date, "reported_mileage": log.reported_mileage}
        for log in history
    ]


@app.get(
    "/maintenance-logs/history/service/{vin}", response_model=list[schemas.ServiceHistoryRead]
)
def list_service_history(vin: str, db: Session = Depends(get_db)):
    if not crud_vehicles.get_vehicle(db, vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    history = crud_maintenance_logs.get_service_history(db, vin)
    return [
        {"vin": log.vin, "date": log.date, "service_name": service_name}
        for log, service_name in history
    ]


@app.get("/maintenance-logs/total-spent/{vin}", response_model=schemas.TotalSpentRead)
def get_total_spent_for_vin(vin: str, db: Session = Depends(get_db)):
    if not crud_vehicles.get_vehicle(db, vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    total_spent = crud_maintenance_logs.get_total_spent_by_vin(db, vin)
    return {"vin": vin, "total_spent": total_spent}


@app.get("/maintenance-logs/{maintenance_id}", response_model=schemas.MaintenanceLogRead)
def get_maintenance_log(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance_log = crud_maintenance_logs.get_maintenance_log(db, maintenance_id)
    if not maintenance_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found."
        )
    return maintenance_log


@app.get("/maintenance-logs/latest-mileage/{vin}", response_model=schemas.LatestMileageRead)
def get_latest_mileage_for_vin(vin: str, db: Session = Depends(get_db)):
    if not crud_vehicles.get_vehicle(db, vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    latest_log = crud_maintenance_logs.get_latest_maintenance_log_by_vin(db, vin)
    if not latest_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No maintenance logs found for this VIN.",
        )

    return {"vin": vin, "date": latest_log.date, "reported_mileage": latest_log.reported_mileage}


@app.get(
    "/maintenance-logs/latest-service-name/{vin}",
    response_model=schemas.LatestServiceNameRead,
)
def get_latest_service_name_for_vin(vin: str, db: Session = Depends(get_db)):
    if not crud_vehicles.get_vehicle(db, vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")

    latest_service = crud_maintenance_logs.get_latest_service_name_by_vin(db, vin)
    if not latest_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No maintenance logs found for this VIN.",
        )

    service_name, service_date = latest_service
    return {"vin": vin, "date": service_date, "service_name": service_name}


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