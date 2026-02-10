// =============================================================================
// LIBRO SERVICE - Book and Loan operations
// =============================================================================

import { Injectable, inject, signal, computed } from '@angular/core';
import { ApiService } from './api.service';
import type { Libro, LibroStats, PrestamoCreate } from '../models';

@Injectable({ providedIn: 'root' })
export class LibroService {
    private api = inject(ApiService);

    private _libros = signal<Libro[]>([]);
    private _stats = signal<LibroStats | null>(null);
    private _loading = signal(false);
    private _error = signal<string | null>(null);

    libros = computed(() => this._libros());
    stats = computed(() => this._stats());
    loading = computed(() => this._loading());
    error = computed(() => this._error());

    async loadAll(includeSocio = false): Promise<void> {
        this._loading.set(true);
        this._error.set(null);
        try {
            const result = await this.api.get<Libro[]>(`libros?includeSocio=${includeSocio}`).toPromise();
            this._libros.set(result || []);
        } catch (e: any) {
            this._error.set(e.message || 'Failed to load books');
        } finally {
            this._loading.set(false);
        }
    }

    async loadStats(): Promise<void> {
        try {
            const result = await this.api.get<LibroStats>('libros/stats').toPromise();
            this._stats.set(result || null);
        } catch {
            this._stats.set(null);
        }
    }

    async getById(id: number): Promise<Libro | null> {
        try {
            return await this.api.get<Libro>(`libros/${id}?includeSocio=true`).toPromise() || null;
        } catch {
            return null;
        }
    }

    async getAvailable(): Promise<Libro[]> {
        try {
            return await this.api.get<Libro[]>('libros/available').toPromise() || [];
        } catch {
            return [];
        }
    }

    async getLoaned(): Promise<Libro[]> {
        try {
            return await this.api.get<Libro[]>('libros/loaned').toPromise() || [];
        } catch {
            return [];
        }
    }

    async getOverdue(): Promise<Libro[]> {
        try {
            return await this.api.get<Libro[]>('libros/overdue').toPromise() || [];
        } catch {
            return [];
        }
    }

    async search(query: string): Promise<Libro[]> {
        try {
            return await this.api.get<Libro[]>(`libros/search?q=${encodeURIComponent(query)}`).toPromise() || [];
        } catch {
            return [];
        }
    }

    async create(data: Omit<Libro, 'id'>): Promise<Libro | null> {
        try {
            const result = await this.api.post<Libro>('libros', data).toPromise();
            if (result) {
                this._libros.update(list => [...list, result]);
            }
            return result || null;
        } catch {
            return null;
        }
    }

    async update(id: number, data: Partial<Libro>): Promise<Libro | null> {
        try {
            const result = await this.api.put<Libro>(`libros/${id}`, data).toPromise();
            if (result) {
                this._libros.update(list => list.map(l => l.id === id ? result : l));
            }
            return result || null;
        } catch {
            return null;
        }
    }

    async delete(id: number): Promise<boolean> {
        try {
            await this.api.delete(`libros/${id}`).toPromise();
            this._libros.update(list => list.filter(l => l.id !== id));
            return true;
        } catch {
            return false;
        }
    }

    async prestar(data: PrestamoCreate): Promise<Libro | null> {
        try {
            const result = await this.api.post<Libro>('libros/prestar', data).toPromise();
            if (result) {
                this._libros.update(list => list.map(l => l.id === result.id ? result : l));
                await this.loadStats();
            }
            return result || null;
        } catch {
            return null;
        }
    }

    async devolver(id: number): Promise<Libro | null> {
        try {
            const result = await this.api.put<Libro>(`libros/${id}/devolver`, {}).toPromise();
            if (result) {
                this._libros.update(list => list.map(l => l.id === result.id ? result : l));
                await this.loadStats();
            }
            return result || null;
        } catch {
            return null;
        }
    }
}
