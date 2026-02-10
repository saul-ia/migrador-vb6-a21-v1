// =============================================================================
// LOGIN COMPONENT - Password authentication
// =============================================================================

import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './login.component.html',
    styleUrl: './login.component.css'
})
export class LoginComponent {
    private auth = inject(AuthService);
    private router = inject(Router);

    password = signal('');
    error = signal<string | null>(null);
    loading = signal(false);

    async login() {
        if (!this.password()) {
            this.error.set('Ingrese la contraseña');
            return;
        }

        this.loading.set(true);
        this.error.set(null);

        const success = await this.auth.login(this.password());

        this.loading.set(false);

        if (success) {
            this.router.navigate(['/dashboard']);
        } else {
            this.error.set('Contraseña incorrecta');
        }
    }
}
