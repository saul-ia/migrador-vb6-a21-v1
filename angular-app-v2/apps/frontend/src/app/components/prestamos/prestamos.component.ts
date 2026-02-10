// =============================================================================
// PRESTAMOS COMPONENT - Loan management (migrated from VB6 FrmPres)
// =============================================================================

import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { LibroService } from '../../services/libro.service';
import { ClienteService } from '../../services/cliente.service';
import type { Libro, Cliente } from '../../models';

@Component({
    selector: 'app-prestamos',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './prestamos.component.html',
    styleUrl: './prestamos.component.css'
})
export class PrestamosComponent implements OnInit {
    private libroService = inject(LibroService);
    private clienteService = inject(ClienteService);

    loanedBooks = signal<Libro[]>([]);
    availableBooks = signal<Libro[]>([]);
    clientes = this.clienteService.clientes;
    loading = signal(true);

    showLoanForm = signal(false);
    selectedLibroId = signal<number | null>(null);
    selectedClienteId = signal<number | null>(null);
    dias = signal(7);

    // VB6 Feature: Track pending loans for selected client
    clientPendingLoans = signal<Libro[]>([]);
    showPendingWarning = signal(false);

    // Computed: Calculate return date from days (VB6: DateAdd("d", Val(txtdias), Now()))
    returnDate = computed(() => {
        const date = new Date();
        date.setDate(date.getDate() + this.dias());
        return date;
    });

    async ngOnInit() {
        this.loading.set(true);
        await Promise.all([
            this.loadLoanedBooks(),
            this.loadAvailableBooks(),
            this.clienteService.loadAll()
        ]);
        this.loading.set(false);
    }

    private async loadLoanedBooks() {
        const books = await this.libroService.getLoaned();
        this.loanedBooks.set(books);
    }

    private async loadAvailableBooks() {
        const books = await this.libroService.getAvailable();
        this.availableBooks.set(books);
    }

    openLoanForm() {
        this.selectedLibroId.set(null);
        this.selectedClienteId.set(null);
        this.dias.set(7);
        this.clientPendingLoans.set([]);
        this.showPendingWarning.set(false);
        this.showLoanForm.set(true);
    }

    closeLoanForm() {
        this.showLoanForm.set(false);
    }

    // VB6 Feature: Validate client has no pending overdue loans (cmdcons_Click)
    async onClientSelected(clienteId: number) {
        this.selectedClienteId.set(clienteId);

        // Find loans for this client
        const pendingLoans = this.loanedBooks().filter(
            libro => libro.socioId === clienteId
        );

        this.clientPendingLoans.set(pendingLoans);

        // VB6: "Este Socio Tiene X libros no devueltos"
        if (pendingLoans.length > 0) {
            this.showPendingWarning.set(true);
        } else {
            this.showPendingWarning.set(false);
        }
    }

    async createLoan() {
        if (!this.selectedLibroId() || !this.selectedClienteId()) {
            return;
        }

        await this.libroService.prestar({
            libroId: this.selectedLibroId()!,
            socioId: this.selectedClienteId()!,
            dias: this.dias()
        });

        await this.loadLoanedBooks();
        await this.loadAvailableBooks();
        this.closeLoanForm();
    }

    async returnBook(libroId: number) {
        await this.libroService.devolver(libroId);
        await this.loadLoanedBooks();
        await this.loadAvailableBooks();
    }

    isOverdue(libro: Libro): boolean {
        if (!libro.fecDev) return false;
        return new Date(libro.fecDev) < new Date();
    }

    // Helper to count overdue books for a client
    getOverdueCount(): number {
        return this.clientPendingLoans().filter(l => this.isOverdue(l)).length;
    }
}
