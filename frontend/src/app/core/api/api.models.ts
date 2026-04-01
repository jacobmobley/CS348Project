export interface Vehicle {
  vin: string;
  make: string;
  model: string;
  year: number;
  purchase_date: string;
}

export interface VehicleCreate {
  vin: string;
  make: string;
  model: string;
  year: number;
  purchase_date: string;
}

export interface ServiceType {
  service_type_id: number;
  name: string;
  service_interval_months: number | null;
  service_interval_miles: number | null;
}

export interface ServiceTypeCreate {
  name: string;
  service_interval_months: number | null;
  service_interval_miles: number | null;
}

export interface MaintenanceLog {
  maintenance_id: number;
  date: string;
  reported_mileage: number;
  cost: string;
  notes: string;
  service_type_id: number;
  vin: string;
}

export interface MaintenanceLogCreate {
  date: string;
  reported_mileage: number;
  cost: string;
  notes: string;
  service_type_id: number;
  vin: string;
}

export interface LatestMileageRead {
  vin: string;
  date: string;
  reported_mileage: number;
}

export interface LatestServiceNameRead {
  vin: string;
  date: string;
  service_name: string;
}

export interface ServiceHistoryRead {
  vin: string;
  date: string;
  service_name: string;
}

export interface MileageHistoryRead {
  vin: string;
  date: string;
  reported_mileage: number;
}

export interface TotalSpentRead {
  vin: string;
  total_spent: string;
}
