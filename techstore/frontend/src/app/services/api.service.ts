import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Verifica si el backend está activo
   * @returns Observable con estado de la API
   */
  checkBackendStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/`);
  }
}
