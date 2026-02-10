// =============================================================================
// LAYOUT COMPONENT - Main app layout with sidebar navigation
// =============================================================================

import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-layout',
    standalone: true,
    imports: [CommonModule, RouterModule, RouterOutlet],
    templateUrl: './layout.component.html',
    styleUrl: './layout.component.css'
})
export class LayoutComponent {
    private auth = inject(AuthService);

    isAuthenticated = this.auth.isAuthenticated;

    navItems = [
        { path: '/dashboard', icon: '📊', label: 'Dashboard' },
        { path: '/clientes', icon: '👥', label: 'Clientes' },
        { path: '/libros', icon: '📚', label: 'Libros' },
        { path: '/prestamos', icon: '📤', label: 'Préstamos' },
        { path: '/ayuda', icon: '❓', label: 'Ayuda' },
    ];

    logout() {
        this.auth.logout();
        window.location.href = '/login';
    }
}
