// =============================================================================
// APP ROUTES - Angular 21 routing with Layout
// =============================================================================

import { Routes } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './services/auth.service';

// Auth Guard function
const authGuard = () => {
    const auth = inject(AuthService);
    if (auth.checkAuth()) {
        return true;
    }
    window.location.href = '/login';
    return false;
};

export const routes: Routes = [
    {
        path: '',
        redirectTo: 'login',
        pathMatch: 'full'
    },
    {
        path: 'login',
        loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
    },
    // Protected routes with layout
    {
        path: '',
        loadComponent: () => import('./components/layout/layout.component').then(m => m.LayoutComponent),
        canActivate: [() => authGuard()],
        children: [
            {
                path: 'dashboard',
                loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
            },
            {
                path: 'clientes',
                loadComponent: () => import('./components/clientes/clientes-list.component').then(m => m.ClientesListComponent)
            },
            {
                path: 'libros',
                loadComponent: () => import('./components/libros/libros-list.component').then(m => m.LibrosListComponent)
            },
            {
                path: 'prestamos',
                loadComponent: () => import('./components/prestamos/prestamos.component').then(m => m.PrestamosComponent)
            },
            {
                path: 'ayuda',
                loadComponent: () => import('./components/ayuda/ayuda.component').then(m => m.AyudaComponent)
            }
        ]
    },
    {
        path: '**',
        redirectTo: 'login'
    }
];
