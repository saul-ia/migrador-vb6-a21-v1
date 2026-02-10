// =============================================================================
// AUTH SERVICE - Authentication using Clave
// =============================================================================

import { Injectable, inject, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AuthService {
    private api = inject(ApiService);
    private router = inject(Router);

    private _isAuthenticated = signal(false);
    isAuthenticated = computed(() => this._isAuthenticated());

    async login(password: string): Promise<boolean> {
        try {
            const result = await this.api.post<{ valid: boolean }>('claves/validate', { pass: password }).toPromise();
            if (result?.valid) {
                this._isAuthenticated.set(true);
                localStorage.setItem('auth', 'true');
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }

    logout(): void {
        this._isAuthenticated.set(false);
        localStorage.removeItem('auth');
        this.router.navigate(['/login']);
    }

    checkAuth(): boolean {
        const auth = localStorage.getItem('auth');
        if (auth === 'true') {
            this._isAuthenticated.set(true);
            return true;
        }
        return false;
    }
}
