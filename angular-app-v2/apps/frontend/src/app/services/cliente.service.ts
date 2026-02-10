// =============================================================================
// CLIENTE SERVICE - Client/Member operations
// =============================================================================

import { Injectable, inject, signal, computed } from '@angular/core';
import { ApiService } from './api.service';
import type { Cliente } from '../models';

@Injectable({ providedIn: 'root' })
export class ClienteService {
    private api = inject(ApiService);

    private _clientes = signal<Cliente[]>([]);
    private _loading = signal(false);
    private _error = signal<string | null>(null);

    clientes = computed(() => this._clientes());
    loading = computed(() => this._loading());
    error = computed(() => this._error());

    async loadAll(includeLibros = false): Promise<void> {
        this._loading.set(true);
        this._error.set(null);
        try {
            const result = await this.api.get<Cliente[]>(`clientes?includeLibros=${includeLibros}`).toPromise();
            this._clientes.set(result || []);
        } catch (e: any) {
            this._error.set(e.message || 'Failed to load clients');
        } finally {
            this._loading.set(false);
        }
    }

    async getById(id: number): Promise<Cliente | null> {
        try {
            return await this.api.get<Cliente>(`clientes/${id}`).toPromise() || null;
        } catch {
            return null;
        }
    }

    async search(query: string): Promise<Cliente[]> {
        try {
            return await this.api.get<Cliente[]>(`clientes/search?q=${encodeURIComponent(query)}`).toPromise() || [];
        } catch {
            return [];
        }
    }

    async create(data: Omit<Cliente, 'id'>): Promise<Cliente | null> {
        try {
            const result = await this.api.post<Cliente>('clientes', data).toPromise();
            if (result) {
                this._clientes.update(list => [...list, result]);
            }
            return result || null;
        } catch {
            return null;
        }
    }

    async update(id: number, data: Partial<Cliente>): Promise<Cliente | null> {
        try {
            const result = await this.api.put<Cliente>(`clientes/${id}`, data).toPromise();
            if (result) {
                this._clientes.update(list => list.map(c => c.id === id ? result : c));
            }
            return result || null;
        } catch {
            return null;
        }
    }

    async delete(id: number): Promise<boolean> {
        try {
            await this.api.delete(`clientes/${id}`).toPromise();
            this._clientes.update(list => list.filter(c => c.id !== id));
            return true;
        } catch {
            return false;
        }
    }
}
