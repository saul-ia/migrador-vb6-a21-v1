// =============================================================================
// DASHBOARD COMPONENT - Main dashboard with stats
// =============================================================================

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { LibroService } from '../../services/libro.service';
import { ClienteService } from '../../services/cliente.service';
import { AuthService } from '../../services/auth.service';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, RouterModule],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
    private libroService = inject(LibroService);
    private clienteService = inject(ClienteService);
    private auth = inject(AuthService);

    stats = this.libroService.stats;
    totalClientes = signal(0);
    overdueBooks = signal<any[]>([]);
    loading = signal(true);

    async ngOnInit() {
        this.loading.set(true);
        await Promise.all([
            this.libroService.loadStats(),
            this.loadClienteCount(),
            this.loadOverdueBooks()
        ]);
        this.loading.set(false);
    }

    private async loadClienteCount() {
        await this.clienteService.loadAll();
        this.totalClientes.set(this.clienteService.clientes().length);
    }

    private async loadOverdueBooks() {
        const overdue = await this.libroService.getOverdue();
        this.overdueBooks.set(overdue);
    }

    logout() {
        this.auth.logout();
    }
}
