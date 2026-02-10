// =============================================================================
// API SERVICE - Base HTTP client for all API calls
// =============================================================================

import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
    private http = inject(HttpClient);
    private baseUrl = signal('http://localhost:3000/api');

    get<T>(endpoint: string): Observable<T> {
        return this.http.get<T>(`${this.baseUrl()}/${endpoint}`);
    }

    post<T>(endpoint: string, data: any): Observable<T> {
        return this.http.post<T>(`${this.baseUrl()}/${endpoint}`, data);
    }

    put<T>(endpoint: string, data: any): Observable<T> {
        return this.http.put<T>(`${this.baseUrl()}/${endpoint}`, data);
    }

    delete<T>(endpoint: string): Observable<T> {
        return this.http.delete<T>(`${this.baseUrl()}/${endpoint}`);
    }
}
