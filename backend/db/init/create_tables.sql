CREATE TABLE IF NOT EXISTS vehicles (
  vin           VARCHAR(17) PRIMARY KEY,
  make          TEXT NOT NULL,
  model         TEXT NOT NULL,
  year          INTEGER NOT NULL,
  purchase_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS service_types (
  service_type_id         BIGSERIAL PRIMARY KEY,
  name                    TEXT NOT NULL,
  service_interval_months INTEGER NULL,
  service_interval_miles  INTEGER NULL
);

CREATE TABLE IF NOT EXISTS maintenance_logs (
  maintenance_id   BIGSERIAL PRIMARY KEY,
  date             DATE NOT NULL,
  reported_mileage INTEGER NOT NULL,
  cost             NUMERIC(10, 2) NOT NULL,
  notes            TEXT NOT NULL,
  service_type_id  BIGINT NOT NULL,
  vin              VARCHAR(17) NOT NULL,
  CONSTRAINT fk_maintenance_service_type
    FOREIGN KEY (service_type_id) REFERENCES service_types(service_type_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_maintenance_vehicle
    FOREIGN KEY (vin) REFERENCES vehicles(vin)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_maintenance_logs_vin
  ON maintenance_logs(vin);

CREATE INDEX IF NOT EXISTS idx_maintenance_logs_service_type_id
  ON maintenance_logs(service_type_id);

