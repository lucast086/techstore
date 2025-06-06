import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-status-checker',
  templateUrl: './status-checker.component.html',
  styleUrls: ['./status-checker.component.scss'],
  standalone: false,
})
export class StatusCheckerComponent implements OnInit {
  backendStatus: 'loading' | 'connected' | 'error' = 'loading';
  statusMessage = 'Verificando conexión con el backend...';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.checkBackendStatus();
  }

  checkBackendStatus(): void {
    this.backendStatus = 'loading';
    this.statusMessage = 'Verificando conexión con el backend...';

    this.apiService.checkBackendStatus().subscribe({
      next: (response) => {
        this.backendStatus = 'connected';
        this.statusMessage = 'Conexión establecida con el backend';
        console.log('Backend conectado:', response);
      },
      error: (error) => {
        this.backendStatus = 'error';
        this.statusMessage = 'No se pudo conectar con el backend';
        console.error('Error de conexión:', error);
      },
    });
  }
}
