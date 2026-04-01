import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../core/api/api.service';
import {
  MileageHistoryRead,
  MaintenanceLog,
  ServiceType,
  ServiceHistoryRead,
  Vehicle
} from '../../core/api/api.models';

type RecordsTab = 'service-records' | 'vehicles';
type ServiceTypeOption = { id: number; name: string };
type ReportModalType = 'vehicle' | 'service';
type VehicleReportSection = {
  id: string;
  title: string;
  isLoading: boolean;
  lines: string[];
  error: string;
  graphData: MileageHistoryRead[] | null;
};

@Component({
  selector: 'app-records-table',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './records-table.component.html',
  styleUrl: './records-table.component.scss'
})
export class RecordsTableComponent implements OnInit {
  private readonly apiService = inject(ApiService);

  activeTab: RecordsTab = 'vehicles';
  showVehicleModal = false;
  showLogModal = false;
  showServiceTypeModal = false;
  showReportModal = false;
  showVehicleReportPreviewModal = false;
  showServiceTypeDropdown = false;
  editingVehicleVin: string | null = null;
  editingLogId: number | null = null;
  selectedVehicleForReport: Vehicle | null = null;
  reportModalTitle = 'Generate Report';
  reportModalType: ReportModalType = 'service';
  vehicleReportSections: VehicleReportSection[] = [];
  vehicleReportOptions = {
    includeVehicleYear: true,
    includeVehicleMake: true,
    includeVehicleModel: true,
    includeVehicleVin: true,
    includeVehiclePurchaseDate: true,
    includeMostRecentMileage: true,
    includeMostRecentService: true,
    includeAllServices: false,
    includeMileageGraph: false,
    includeTotalMoneySpent: true
  };
  serviceTypeSearch = '';
  serviceTypeOptions: ServiceTypeOption[] = [];

  vehicleForm = {
    vin: '',
    make: '',
    model: '',
    year: '',
    purchase_date: ''
  };

  logForm = {
    date: '',
    reported_mileage: '',
    cost: '',
    notes: '',
    service_type_id: '',
    vin: ''
  };

  serviceTypeForm = {
    name: '',
    service_interval_months: '',
    service_interval_miles: ''
  };

  vehicles: Vehicle[] = [];
  maintenanceLogs: MaintenanceLog[] = [];
  isLoadingVehicles = false;
  isLoadingLogs = false;
  isLoadingServiceTypes = false;
  isSavingVehicle = false;
  isSavingLog = false;
  isSavingServiceType = false;
  vehicleLoadError = '';
  logLoadError = '';
  serviceTypeLoadError = '';
  vehicleSubmitError = '';
  logSubmitError = '';
  serviceTypeSubmitError = '';
  deletingVehicleVins = new Set<string>();
  deletingLogIds = new Set<number>();

  ngOnInit(): void {
    this.loadVehicles();
    this.loadMaintenanceLogs();
    this.loadServiceTypes();
  }

  setTab(tab: RecordsTab): void {
    this.activeTab = tab;
  }

  onAddClick(): void {
    if (this.activeTab === 'vehicles') {
      this.onAddVehicle();
      return;
    }

    this.onAddLog();
  }

  onAddVehicle(): void {
    this.editingVehicleVin = null;
    this.vehicleForm = {
      vin: '',
      make: '',
      model: '',
      year: '',
      purchase_date: ''
    };
    this.vehicleSubmitError = '';
    this.showVehicleModal = true;
  }

  onAddLog(): void {
    this.editingLogId = null;
    this.logForm = {
      date: '',
      reported_mileage: '',
      cost: '',
      notes: '',
      service_type_id: '',
      vin: ''
    };
    if (!this.isLoadingServiceTypes && this.serviceTypeOptions.length === 0) {
      this.loadServiceTypes();
    }
    this.showServiceTypeDropdown = false;
    this.serviceTypeSearch = '';
    this.logSubmitError = '';
    this.showLogModal = true;
  }

  closeVehicleModal(): void {
    this.editingVehicleVin = null;
    this.vehicleSubmitError = '';
    this.showVehicleModal = false;
  }

  closeLogModal(): void {
    this.editingLogId = null;
    this.showServiceTypeDropdown = false;
    this.logSubmitError = '';
    this.showLogModal = false;
  }

  submitVehicleForm(): void {
    this.isSavingVehicle = true;
    this.vehicleSubmitError = '';

    const payload = {
      vin: this.vehicleForm.vin.trim(),
      make: this.vehicleForm.make.trim(),
      model: this.vehicleForm.model.trim(),
      year: Number(this.vehicleForm.year),
      purchase_date: this.vehicleForm.purchase_date
    };

    const request$ = this.editingVehicleVin
      ? this.apiService.updateVehicle(this.editingVehicleVin, {
          make: payload.make,
          model: payload.model,
          year: payload.year,
          purchase_date: payload.purchase_date
        })
      : this.apiService.createVehicle(payload);

    request$.subscribe({
      next: () => {
        this.isSavingVehicle = false;
        this.closeVehicleModal();
        this.loadVehicles();
      },
      error: () => {
        this.isSavingVehicle = false;
        this.vehicleSubmitError = 'Unable to save vehicle. Please check your input and try again.';
      }
    });
  }

  submitLogForm(): void {
    const vin = this.logForm.vin.trim();
    const notes = this.logForm.notes.trim();
    const reportedMileage = Number(this.logForm.reported_mileage);
    const serviceTypeId = Number(this.logForm.service_type_id);
    const costNumber = Number(this.logForm.cost);

    if (!this.logForm.date) {
      this.logSubmitError = 'Date is required.';
      return;
    }

    if (!Number.isFinite(reportedMileage) || reportedMileage < 0) {
      this.logSubmitError = 'Reported mileage must be a valid non-negative number.';
      return;
    }

    if (!Number.isFinite(costNumber) || costNumber < 0) {
      this.logSubmitError = 'Cost must be a valid non-negative number.';
      return;
    }

    if (!Number.isFinite(serviceTypeId) || serviceTypeId <= 0) {
      this.logSubmitError = 'Please choose a service type.';
      return;
    }

    if (vin.length !== 17) {
      this.logSubmitError = 'Vehicle VIN must be exactly 17 characters.';
      return;
    }

    if (notes.length === 0) {
      this.logSubmitError = 'Notes are required.';
      return;
    }

    this.isSavingLog = true;
    this.logSubmitError = '';

    const payload = {
      date: this.logForm.date,
      reported_mileage: reportedMileage,
      cost: costNumber.toFixed(2),
      notes,
      service_type_id: serviceTypeId,
      vin
    };

    const request$ = this.editingLogId
      ? this.apiService.updateMaintenanceLog(this.editingLogId, payload)
      : this.apiService.createMaintenanceLog(payload);

    request$.subscribe({
      next: () => {
        this.isSavingLog = false;
        this.closeLogModal();
        this.loadMaintenanceLogs();
      },
      error: (error: HttpErrorResponse) => {
        this.isSavingLog = false;
        this.logSubmitError =
          this.getApiErrorMessage(error) ||
          'Unable to save service log. Please check your input and try again.';
      }
    });
  }

  onServiceTypeSearchChange(value: string): void {
    this.serviceTypeSearch = value;
    this.logForm.service_type_id = '';
    this.showServiceTypeDropdown = true;
  }

  selectServiceType(option: ServiceTypeOption): void {
    this.logForm.service_type_id = String(option.id);
    this.serviceTypeSearch = `${option.name} (ID: ${option.id})`;
    this.showServiceTypeDropdown = false;
  }

  onAddServiceTypeClick(): void {
    this.showServiceTypeDropdown = false;
    this.serviceTypeSubmitError = '';
    this.showServiceTypeModal = true;
  }

  onGenerateLogReport(): void {
    this.reportModalType = 'service';
    this.reportModalTitle = 'Generate Service Record Report';
    this.showReportModal = true;
  }

  closeReportModal(): void {
    this.showReportModal = false;
  }

  closeVehicleReportPreviewModal(): void {
    this.showVehicleReportPreviewModal = false;
    this.vehicleReportSections = [];
    this.selectedVehicleForReport = null;
  }

  submitGenerateReport(): void {
    // Placeholder for report generation implementation.
    if (this.reportModalType === 'vehicle') {
      if (!this.selectedVehicleForReport) {
        return;
      }

      this.vehicleReportSections = this.buildSelectedVehicleReportSections(
        this.selectedVehicleForReport
      );
      this.showReportModal = false;
      this.showVehicleReportPreviewModal = true;
      this.loadVehicleReportSectionData(this.selectedVehicleForReport.vin);
      console.info('Generate vehicle report clicked', this.vehicleReportOptions);
    } else {
      console.info('Generate service report clicked');
      this.closeReportModal();
    }
  }

  onEditVehicle(vehicle: Vehicle): void {
    this.editingVehicleVin = vehicle.vin;
    this.vehicleForm = {
      vin: vehicle.vin,
      make: vehicle.make,
      model: vehicle.model,
      year: String(vehicle.year),
      purchase_date: vehicle.purchase_date
    };
    this.vehicleSubmitError = '';
    this.showVehicleModal = true;
  }

  onDeleteVehicle(vehicle: Vehicle): void {
    if (this.deletingVehicleVins.has(vehicle.vin)) {
      return;
    }

    const confirmed = window.confirm(`Delete vehicle ${vehicle.vin}?`);
    if (!confirmed) {
      return;
    }

    this.deletingVehicleVins.add(vehicle.vin);
    this.apiService.deleteVehicle(vehicle.vin).subscribe({
      next: () => {
        this.deletingVehicleVins.delete(vehicle.vin);
        this.loadVehicles();
      },
      error: () => {
        this.deletingVehicleVins.delete(vehicle.vin);
        window.alert('Unable to delete vehicle right now.');
      }
    });
  }

  onGenerateVehicleReport(vehicle: Vehicle): void {
    this.selectedVehicleForReport = vehicle;
    this.reportModalType = 'vehicle';
    this.reportModalTitle = 'Generate Vehicle Report';
    this.showReportModal = true;
  }

  onEditLog(log: MaintenanceLog): void {
    if (!this.isLoadingServiceTypes && this.serviceTypeOptions.length === 0) {
      this.loadServiceTypes();
    }

    this.editingLogId = log.maintenance_id;
    this.logForm = {
      date: log.date,
      reported_mileage: String(log.reported_mileage),
      cost: String(log.cost),
      notes: log.notes,
      service_type_id: String(log.service_type_id),
      vin: log.vin
    };
    this.serviceTypeSearch = `Service Type ID: ${log.service_type_id}`;
    const selected = this.serviceTypeOptions.find(
      (option) => option.id === log.service_type_id
    );
    if (selected) {
      this.serviceTypeSearch = `${selected.name} (ID: ${selected.id})`;
    }
    this.showServiceTypeDropdown = false;
    this.logSubmitError = '';
    this.showLogModal = true;
  }

  onDeleteLog(log: MaintenanceLog): void {
    if (this.deletingLogIds.has(log.maintenance_id)) {
      return;
    }

    const confirmed = window.confirm(`Delete service record #${log.maintenance_id}?`);
    if (!confirmed) {
      return;
    }

    this.deletingLogIds.add(log.maintenance_id);
    this.apiService.deleteMaintenanceLog(log.maintenance_id).subscribe({
      next: () => {
        this.deletingLogIds.delete(log.maintenance_id);
        this.loadMaintenanceLogs();
      },
      error: () => {
        this.deletingLogIds.delete(log.maintenance_id);
        window.alert('Unable to delete service record right now.');
      }
    });
  }

  closeServiceTypeModal(): void {
    this.serviceTypeSubmitError = '';
    this.showServiceTypeModal = false;
  }

  submitServiceTypeForm(): void {
    this.isSavingServiceType = true;
    this.serviceTypeSubmitError = '';

    const payload = {
      name: this.serviceTypeForm.name.trim(),
      service_interval_months: this.serviceTypeForm.service_interval_months
        ? Number(this.serviceTypeForm.service_interval_months)
        : null,
      service_interval_miles: this.serviceTypeForm.service_interval_miles
        ? Number(this.serviceTypeForm.service_interval_miles)
        : null
    };

    this.apiService.createServiceType(payload).subscribe({
      next: (createdServiceType) => {
        this.isSavingServiceType = false;
        this.loadServiceTypes();
        this.selectServiceType({
          id: createdServiceType.service_type_id,
          name: createdServiceType.name
        });
        this.closeServiceTypeModal();
      },
      error: () => {
        this.isSavingServiceType = false;
        this.serviceTypeSubmitError =
          'Unable to save service type. Please check your input and try again.';
      }
    });
  }

  private loadVehicles(): void {
    this.isLoadingVehicles = true;
    this.vehicleLoadError = '';

    this.apiService.getVehicles().subscribe({
      next: (vehicles) => {
        this.vehicles = vehicles;
        this.isLoadingVehicles = false;
      },
      error: () => {
        this.vehicleLoadError = 'Unable to load vehicles right now.';
        this.isLoadingVehicles = false;
      }
    });
  }

  private loadMaintenanceLogs(): void {
    this.isLoadingLogs = true;
    this.logLoadError = '';

    this.apiService.getMaintenanceLogs().subscribe({
      next: (logs) => {
        this.maintenanceLogs = logs;
        this.isLoadingLogs = false;
      },
      error: () => {
        this.logLoadError = 'Unable to load service records right now.';
        this.isLoadingLogs = false;
      }
    });
  }

  private loadServiceTypes(): void {
    this.isLoadingServiceTypes = true;
    this.serviceTypeLoadError = '';

    this.apiService.getServiceTypes().subscribe({
      next: (serviceTypes: ServiceType[]) => {
        this.serviceTypeOptions = serviceTypes.map((serviceType) => ({
          id: serviceType.service_type_id,
          name: serviceType.name
        }));
        this.isLoadingServiceTypes = false;
      },
      error: () => {
        this.serviceTypeLoadError = 'Unable to load service types right now.';
        this.isLoadingServiceTypes = false;
      }
    });
  }

  private getApiErrorMessage(error: HttpErrorResponse): string | null {
    const detail = error?.error?.detail;

    if (!detail) {
      return null;
    }

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0];
      if (first?.msg && Array.isArray(first?.loc)) {
        const fieldPath = first.loc.slice(1).join('.');
        return `${fieldPath}: ${first.msg}`;
      }
      if (first?.msg) {
        return first.msg;
      }
    }

    return null;
  }

  get filteredServiceTypeOptions(): ServiceTypeOption[] {
    const query = this.serviceTypeSearch.trim().toLowerCase();
    if (!query) {
      return this.serviceTypeOptions;
    }

    return this.serviceTypeOptions.filter(
      (option) =>
        option.name.toLowerCase().includes(query) || String(option.id).includes(query)
    );
  }

  getServiceTypeName(serviceTypeId: number): string {
    const match = this.serviceTypeOptions.find((option) => option.id === serviceTypeId);
    return match ? match.name : `Service Type #${serviceTypeId}`;
  }

  private buildSelectedVehicleReportSections(vehicle: Vehicle): VehicleReportSection[] {
    const sections: VehicleReportSection[] = [];

    if (this.vehicleReportOptions.includeVehicleYear) {
      sections.push({
        id: 'vehicle-year',
        title: 'Year',
        isLoading: false,
        lines: [String(vehicle.year)],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeVehicleMake) {
      sections.push({
        id: 'vehicle-make',
        title: 'Make',
        isLoading: false,
        lines: [vehicle.make],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeVehicleModel) {
      sections.push({
        id: 'vehicle-model',
        title: 'Model',
        isLoading: false,
        lines: [vehicle.model],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeVehicleVin) {
      sections.push({
        id: 'vehicle-vin',
        title: 'VIN',
        isLoading: false,
        lines: [vehicle.vin],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeVehiclePurchaseDate) {
      sections.push({
        id: 'vehicle-purchase-date',
        title: 'Purchase Date',
        isLoading: false,
        lines: [vehicle.purchase_date],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeMostRecentMileage) {
      sections.push({
        id: 'most-recent-mileage',
        title: 'Most recent mileage',
        isLoading: true,
        lines: [],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeMostRecentService) {
      sections.push({
        id: 'most-recent-service',
        title: 'Most recent service',
        isLoading: true,
        lines: [],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeAllServices) {
      sections.push({
        id: 'all-services',
        title: 'All services',
        isLoading: true,
        lines: [],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeMileageGraph) {
      sections.push({
        id: 'mileage-graph',
        title: 'All mileage (graph form)',
        isLoading: true,
        lines: [],
        error: '',
        graphData: null
      });
    }
    if (this.vehicleReportOptions.includeTotalMoneySpent) {
      sections.push({
        id: 'total-money-spent',
        title: 'Total money spent',
        isLoading: true,
        lines: [],
        error: '',
        graphData: null
      });
    }

    return sections;
  }

  private loadVehicleReportSectionData(vin: string): void {
    if (this.vehicleReportOptions.includeMostRecentMileage) {
      this.setVehicleReportSectionLoading('most-recent-mileage', true);
      this.apiService.getLatestMileage(vin).subscribe({
        next: (result) => {
          this.setVehicleReportSectionData('most-recent-mileage', [
            `Date: ${result.date}`,
            `Mileage: ${result.reported_mileage}`
          ]);
        },
        error: () => {
          this.setVehicleReportSectionError(
            'most-recent-mileage',
            'Unable to load most recent mileage.'
          );
        }
      });
    }

    if (this.vehicleReportOptions.includeMostRecentService) {
      this.setVehicleReportSectionLoading('most-recent-service', true);
      this.apiService.getLatestServiceName(vin).subscribe({
        next: (result) => {
          this.setVehicleReportSectionData('most-recent-service', [
            `Date: ${result.date}`,
            `Service: ${result.service_name}`
          ]);
        },
        error: () => {
          this.setVehicleReportSectionError(
            'most-recent-service',
            'Unable to load most recent service.'
          );
        }
      });
    }

    if (this.vehicleReportOptions.includeAllServices) {
      this.setVehicleReportSectionLoading('all-services', true);
      this.apiService.getServiceHistory(vin).subscribe({
        next: (result: ServiceHistoryRead[]) => {
          const lines = result.map((item) => `${item.date}: ${item.service_name}`);
          this.setVehicleReportSectionData(
            'all-services',
            lines.length > 0 ? lines : ['No service history found.']
          );
        },
        error: () => {
          this.setVehicleReportSectionError('all-services', 'Unable to load service history.');
        }
      });
    }

    if (this.vehicleReportOptions.includeTotalMoneySpent) {
      this.setVehicleReportSectionLoading('total-money-spent', true);
      this.apiService.getTotalSpent(vin).subscribe({
        next: (result) => {
          this.setVehicleReportSectionData('total-money-spent', [`$${result.total_spent}`]);
        },
        error: () => {
          this.setVehicleReportSectionError('total-money-spent', 'Unable to load total spent.');
        }
      });
    }

    if (this.vehicleReportOptions.includeMileageGraph) {
      this.setVehicleReportSectionLoading('mileage-graph', true);
      this.apiService.getMileageHistory(vin).subscribe({
        next: (result: MileageHistoryRead[]) => {
          this.setVehicleReportSectionGraphData('mileage-graph', result);
        },
        error: () => {
          this.setVehicleReportSectionError('mileage-graph', 'Unable to load mileage history.');
        }
      });
    }
  }

  private setVehicleReportSectionLoading(sectionId: string, isLoading: boolean): void {
    const section = this.vehicleReportSections.find((item) => item.id === sectionId);
    if (!section) {
      return;
    }

    section.isLoading = isLoading;
    if (isLoading) {
      section.error = '';
    }
  }

  private setVehicleReportSectionData(sectionId: string, lines: string[]): void {
    const section = this.vehicleReportSections.find((item) => item.id === sectionId);
    if (!section) {
      return;
    }

    section.isLoading = false;
    section.error = '';
    section.lines = lines;
    section.graphData = null;
  }

  private setVehicleReportSectionError(sectionId: string, message: string): void {
    const section = this.vehicleReportSections.find((item) => item.id === sectionId);
    if (!section) {
      return;
    }

    section.isLoading = false;
    section.error = message;
    section.lines = [];
    section.graphData = null;
  }

  private setVehicleReportSectionGraphData(
    sectionId: string,
    graphData: MileageHistoryRead[]
  ): void {
    const section = this.vehicleReportSections.find((item) => item.id === sectionId);
    if (!section) {
      return;
    }

    section.isLoading = false;
    section.error = '';
    section.lines = [];
    section.graphData = graphData;
  }

  getMileageGraphPoints(section: VehicleReportSection): string {
    if (!section.graphData || section.graphData.length === 0) {
      return '';
    }

    const width = 640;
    const height = 240;
    const leftPad = 44;
    const rightPad = 16;
    const topPad = 16;
    const bottomPad = 28;
    const chartWidth = width - leftPad - rightPad;
    const chartHeight = height - topPad - bottomPad;

    const mileageValues = section.graphData.map((item) => item.reported_mileage);
    const minMileage = Math.min(...mileageValues);
    const maxMileage = Math.max(...mileageValues);
    const range = maxMileage - minMileage || 1;

    return section.graphData
      .map((point, index) => {
        const x = leftPad + (index / Math.max(section.graphData!.length - 1, 1)) * chartWidth;
        const y =
          topPad + chartHeight - ((point.reported_mileage - minMileage) / range) * chartHeight;
        return `${x},${y}`;
      })
      .join(' ');
  }

  getMileageGraphMin(section: VehicleReportSection): number | null {
    if (!section.graphData || section.graphData.length === 0) {
      return null;
    }
    return Math.min(...section.graphData.map((item) => item.reported_mileage));
  }

  getMileageGraphMax(section: VehicleReportSection): number | null {
    if (!section.graphData || section.graphData.length === 0) {
      return null;
    }
    return Math.max(...section.graphData.map((item) => item.reported_mileage));
  }

  getMileageGraphStartDate(section: VehicleReportSection): string {
    if (!section.graphData || section.graphData.length === 0) {
      return '';
    }
    return section.graphData[0].date;
  }

  getMileageGraphEndDate(section: VehicleReportSection): string {
    if (!section.graphData || section.graphData.length === 0) {
      return '';
    }
    return section.graphData[section.graphData.length - 1].date;
  }
}
