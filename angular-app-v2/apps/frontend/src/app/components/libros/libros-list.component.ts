// =============================================================================
// LIBROS LIST COMPONENT - Book management
// =============================================================================

import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { LibroService } from '../../services/libro.service';
import type { Libro } from '../../models';

@Component({
    selector: 'app-libros-list',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './libros-list.component.html',
    styleUrl: './libros-list.component.css'
})
export class LibrosListComponent implements OnInit {
    private libroService = inject(LibroService);

    libros = this.libroService.libros;
    loading = this.libroService.loading;
    error = this.libroService.error;

    searchQuery = signal('');
    filterEstado = signal<string>('all');
    showForm = signal(false);
    editingLibro = signal<Libro | null>(null);

    // Form fields
    formTitulo = signal('');
    formAutor = signal('');

    async ngOnInit() {
        await this.libroService.loadAll(true);
    }

    async search() {
        if (this.searchQuery()) {
            const results = await this.libroService.search(this.searchQuery());
            // Results shown inline
        } else {
            await this.libroService.loadAll(true);
        }
    }

    async filterByEstado() {
        const estado = this.filterEstado();
        if (estado === 'disponible') {
            const available = await this.libroService.getAvailable();
            // Show available
        } else if (estado === 'prestado') {
            const loaned = await this.libroService.getLoaned();
            // Show loaned
        } else if (estado === 'vencido') {
            const overdue = await this.libroService.getOverdue();
            // Show overdue
        } else {
            await this.libroService.loadAll(true);
        }
    }

    openCreateForm() {
        this.resetForm();
        this.editingLibro.set(null);
        this.showForm.set(true);
    }

    openEditForm(libro: Libro) {
        this.formTitulo.set(libro.titulo);
        this.formAutor.set(libro.autor || '');
        this.editingLibro.set(libro);
        this.showForm.set(true);
    }

    resetForm() {
        this.formTitulo.set('');
        this.formAutor.set('');
    }

    closeForm() {
        this.showForm.set(false);
        this.editingLibro.set(null);
        this.resetForm();
    }

    async saveLibro() {
        const data = {
            titulo: this.formTitulo(),
            autor: this.formAutor() || undefined,
        };

        if (this.editingLibro()) {
            await this.libroService.update(this.editingLibro()!.id, data);
        } else {
            await this.libroService.create(data as any);
        }

        this.closeForm();
    }

    async deleteLibro(id: number) {
        if (confirm('¿Está seguro de eliminar este libro?')) {
            await this.libroService.delete(id);
        }
    }

    async devolverLibro(id: number) {
        await this.libroService.devolver(id);
    }

    getEstadoClass(estado: string | undefined): string {
        if (!estado || estado === 'disponible') return 'estado-disponible';
        if (estado === 'prestado') return 'estado-prestado';
        return 'estado-default';
    }
}
