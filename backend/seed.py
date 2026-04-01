from __future__ import annotations

import argparse
import random
import string
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.database import Base, SessionLocal, engine
from app.models import MaintenanceLog, ServiceType, Vehicle

VALID_VIN_CHARS = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
VEHICLE_MAKES_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma", "Highlander"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit"],
    "Ford": ["F-150", "Escape", "Mustang", "Explorer", "Focus"],
    "Chevrolet": ["Silverado", "Malibu", "Equinox", "Tahoe", "Cruze"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Frontier", "Pathfinder"],
    "Subaru": ["Outback", "Forester", "Impreza", "Crosstrek", "Legacy"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona"],
    "Kia": ["Optima", "Soul", "Sportage", "Sorento", "Forte"],
}
SERVICE_TYPE_CATALOG = [
    ("Oil Change", 6, 5000),
    ("Tire Rotation", 6, 6000),
    ("Brake Inspection", 12, 12000),
    ("Brake Pad Replacement", None, 30000),
    ("Battery Check", 12, 12000),
    ("Air Filter Replacement", 12, 15000),
    ("Spark Plug Replacement", None, 60000),
    ("Transmission Service", 36, 45000),
    ("Coolant Flush", 24, 30000),
    ("Wheel Alignment", 12, 12000),
    ("AC Service", 24, None),
    ("Serpentine Belt Replacement", None, 70000),
]
NOTE_TEMPLATES = [
    "Completed routine service with no additional issues found.",
    "Customer requested standard maintenance and general inspection.",
    "Performed service and topped off all fluids.",
    "Observed normal wear for mileage; recommended follow-up at next interval.",
    "Road test completed after service, vehicle operating as expected.",
    "Verified repair quality and updated maintenance records.",
]


@dataclass
class SeedConfig:
    vehicles: int
    logs_per_vehicle: int
    random_seed: int
    wipe_existing: bool


def parse_args() -> SeedConfig:
    parser = argparse.ArgumentParser(
        description="Seed the database with valid test vehicles and maintenance logs."
    )
    parser.add_argument(
        "--vehicles",
        type=int,
        default=25,
        help="Number of vehicles to create (default: 25).",
    )
    parser.add_argument(
        "--logs-per-vehicle",
        type=int,
        default=8,
        help="Maintenance logs to create per vehicle (default: 8).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=348,
        help="Random seed for deterministic data generation (default: 348).",
    )
    parser.add_argument(
        "--wipe-existing",
        action="store_true",
        help="Delete existing vehicles, service types, and maintenance logs first.",
    )
    args = parser.parse_args()

    if args.vehicles <= 0:
        parser.error("--vehicles must be greater than 0.")
    if args.logs_per_vehicle < 0:
        parser.error("--logs-per-vehicle must be 0 or greater.")

    return SeedConfig(
        vehicles=args.vehicles,
        logs_per_vehicle=args.logs_per_vehicle,
        random_seed=args.seed,
        wipe_existing=args.wipe_existing,
    )


def random_vin(rng: random.Random, used_vins: set[str]) -> str:
    while True:
        vin = "".join(rng.choice(VALID_VIN_CHARS) for _ in range(17))
        if vin not in used_vins:
            used_vins.add(vin)
            return vin


def random_purchase_date(rng: random.Random, year: int) -> date:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    return start + timedelta(days=rng.randint(0, (end - start).days))


def random_service_cost(rng: random.Random, service_name: str) -> Decimal:
    base_ranges = {
        "Oil Change": (35, 95),
        "Tire Rotation": (25, 70),
        "Brake Inspection": (40, 110),
        "Brake Pad Replacement": (180, 420),
        "Battery Check": (20, 55),
        "Air Filter Replacement": (30, 90),
        "Spark Plug Replacement": (140, 330),
        "Transmission Service": (180, 450),
        "Coolant Flush": (110, 280),
        "Wheel Alignment": (80, 210),
        "AC Service": (130, 360),
        "Serpentine Belt Replacement": (120, 320),
    }
    low, high = base_ranges.get(service_name, (45, 160))
    value = Decimal(str(rng.uniform(low, high)))
    return value.quantize(Decimal("0.01"))


def seed_database(config: SeedConfig) -> None:
    rng = random.Random(config.random_seed)
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if config.wipe_existing:
            session.query(MaintenanceLog).delete()
            session.query(ServiceType).delete()
            session.query(Vehicle).delete()
            session.commit()

        used_vins = {vin for (vin,) in session.query(Vehicle.vin).all()}

        existing_services = session.query(ServiceType).all()
        existing_names = {service.name for service in existing_services}
        for name, months, miles in SERVICE_TYPE_CATALOG:
            if name in existing_names:
                continue
            session.add(
                ServiceType(
                    name=name,
                    service_interval_months=months,
                    service_interval_miles=miles,
                )
            )
        session.commit()
        existing_services = session.query(ServiceType).all()

        vehicles: list[Vehicle] = []
        for _ in range(config.vehicles):
            make = rng.choice(list(VEHICLE_MAKES_MODELS.keys()))
            model = rng.choice(VEHICLE_MAKES_MODELS[make])
            year = rng.randint(2008, date.today().year)
            vehicle = Vehicle(
                vin=random_vin(rng, used_vins),
                make=make,
                model=model,
                year=year,
                purchase_date=random_purchase_date(rng, year),
            )
            vehicles.append(vehicle)

        session.add_all(vehicles)
        session.commit()

        created_logs = 0
        for vehicle in vehicles:
            current_date = vehicle.purchase_date + timedelta(days=rng.randint(90, 220))
            mileage = rng.randint(8_000, 45_000)

            for _ in range(config.logs_per_vehicle):
                service_type = rng.choice(existing_services)
                mileage += rng.randint(2_500, 9_000)
                current_date += timedelta(days=rng.randint(60, 220))
                if current_date > date.today():
                    current_date = date.today()

                session.add(
                    MaintenanceLog(
                        date=current_date,
                        reported_mileage=mileage,
                        cost=random_service_cost(rng, service_type.name),
                        notes=rng.choice(NOTE_TEMPLATES),
                        service_type_id=service_type.service_type_id,
                        vin=vehicle.vin,
                    )
                )
                created_logs += 1

        session.commit()

        print(f"Seed complete.")
        print(f"Service types available: {len(existing_services)}")
        print(f"Vehicles created: {len(vehicles)}")
        print(f"Maintenance logs created: {created_logs}")
    finally:
        session.close()


if __name__ == "__main__":
    seed_database(parse_args())
