// =============================================================================
// CLIENTES LIST COMPONENT - Client management
// =============================================================================

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ClienteService } from '../../services/cliente.service';
import type { Cliente } from '../../models';

@Component({
    selector: 'app-clientes-list',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './clientes-list.component.html',
    styleUrl: './clientes-list.component.css'
})
export class ClientesListComponent implements OnInit {
    private clienteService = inject(ClienteService);

    clientes = this.clienteService.clientes;
    loading = this.clienteService.loading;
    error = this.clienteService.error;

    searchQuery = signal('');
    showForm = signal(false);
    editingCliente = signal<Cliente | null>(null);

    // Form fields
    formNombres = signal('');
    formApellidos = signal('');
    formNroDoc = signal('');
    formDomicilio = signal('');
    formTelefono = signal('');

    async ngOnInit() {
        await this.clienteService.loadAll();
    }

    async search() {
        if (this.searchQuery()) {
            const results = await this.clienteService.search(this.searchQuery());
            // Results are shown inline
        } else {
            await this.clienteService.loadAll();
        }
    }

    openCreateForm() {
        this.resetForm();
        this.editingCliente.set(null);
        this.showForm.set(true);
    }

    openEditForm(cliente: Cliente) {
        this.formNombres.set(cliente.nombres);
        this.formApellidos.set(cliente.apellidos);
        this.formNroDoc.set(cliente.nroDoc || '');
        this.formDomicilio.set(cliente.domicilio || '');
        this.formTelefono.set(cliente.telefono || '');
        this.editingCliente.set(cliente);
        this.showForm.set(true);
    }

    resetForm() {
        this.formNombres.set('');
        this.formApellidos.set('');
        this.formNroDoc.set('');
        this.formDomicilio.set('');
        this.formTelefono.set('');
    }

    closeForm() {
        this.showForm.set(false);
        this.editingCliente.set(null);
        this.resetForm();
    }

    async saveCliente() {
        const data = {
            nombres: this.formNombres(),
            apellidos: this.formApellidos(),
            nroDoc: this.formNroDoc() || undefined,
            domicilio: this.formDomicilio() || undefined,
            telefono: this.formTelefono() || undefined,
        };

        if (this.editingCliente()) {
            await this.clienteService.update(this.editingCliente()!.id, data);
        } else {
            await this.clienteService.create(data as any);
        }

        this.closeForm();
    }

    async deleteCliente(id: number) {
        if (confirm('¿Está seguro de eliminar este cliente?')) {
            await this.clienteService.delete(id);
        }
    }
}
