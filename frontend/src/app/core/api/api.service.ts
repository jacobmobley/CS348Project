import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_BASE_URL } from './api.config';
import {
  LatestMileageRead,
  LatestServiceNameRead,
  MileageHistoryRead,
  MaintenanceLog,
  MaintenanceLogCreate,
  ServiceHistoryRead,
  ServiceType,
  ServiceTypeCreate,
  TotalSpentRead,
  Vehicle,
  VehicleCreate
} from './api.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private readonly http: HttpClient) {}

  getVehicles(): Observable<Vehicle[]> {
    return this.http.get<Vehicle[]>(`${API_BASE_URL}/vehicles`);
  }

  createVehicle(payload: VehicleCreate): Observable<Vehicle> {
    return this.http.post<Vehicle>(`${API_BASE_URL}/vehicles`, payload);
  }

  updateVehicle(vin: string, payload: Partial<VehicleCreate>): Observable<Vehicle> {
    return this.http.put<Vehicle>(`${API_BASE_URL}/vehicles/${vin}`, payload);
  }

  deleteVehicle(vin: string): Observable<void> {
    return this.http.delete<void>(`${API_BASE_URL}/vehicles/${vin}`);
  }

  getServiceTypes(): Observable<ServiceType[]> {
    return this.http.get<ServiceType[]>(`${API_BASE_URL}/service-types`);
  }

  createServiceType(payload: ServiceTypeCreate): Observable<ServiceType> {
    return this.http.post<ServiceType>(`${API_BASE_URL}/service-types`, payload);
  }

  getMaintenanceLogs(): Observable<MaintenanceLog[]> {
    return this.http.get<MaintenanceLog[]>(`${API_BASE_URL}/maintenance-logs`);
  }

  createMaintenanceLog(payload: MaintenanceLogCreate): Observable<MaintenanceLog> {
    return this.http.post<MaintenanceLog>(`${API_BASE_URL}/maintenance-logs`, payload);
  }

  updateMaintenanceLog(
    maintenanceId: number,
    payload: Partial<MaintenanceLogCreate>
  ): Observable<MaintenanceLog> {
    return this.http.put<MaintenanceLog>(
      `${API_BASE_URL}/maintenance-logs/${maintenanceId}`,
      payload
    );
  }

  deleteMaintenanceLog(maintenanceId: number): Observable<void> {
    return this.http.delete<void>(`${API_BASE_URL}/maintenance-logs/${maintenanceId}`);
  }

  getLatestMileage(vin: string): Observable<LatestMileageRead> {
    return this.http.get<LatestMileageRead>(`${API_BASE_URL}/maintenance-logs/latest-mileage/${vin}`);
  }

  getLatestServiceName(vin: string): Observable<LatestServiceNameRead> {
    return this.http.get<LatestServiceNameRead>(
      `${API_BASE_URL}/maintenance-logs/latest-service-name/${vin}`
    );
  }

  getServiceHistory(vin: string): Observable<ServiceHistoryRead[]> {
    return this.http.get<ServiceHistoryRead[]>(`${API_BASE_URL}/maintenance-logs/history/service/${vin}`);
  }

  getMileageHistory(vin: string): Observable<MileageHistoryRead[]> {
    return this.http.get<MileageHistoryRead[]>(`${API_BASE_URL}/maintenance-logs/history/mileage/${vin}`);
  }

  getTotalSpent(vin: string): Observable<TotalSpentRead> {
    return this.http.get<TotalSpentRead>(`${API_BASE_URL}/maintenance-logs/total-spent/${vin}`);
  }
}
