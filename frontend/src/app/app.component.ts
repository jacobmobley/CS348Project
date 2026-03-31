import { Component } from '@angular/core';
import { RecordsTableComponent } from './components/records-table/records-table.component';

@Component({
  selector: 'app-root',
  imports: [RecordsTableComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {}
