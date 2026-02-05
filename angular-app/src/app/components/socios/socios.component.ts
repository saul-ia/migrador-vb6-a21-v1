import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { SocioDialogComponent } from '../socio-dialog/socio-dialog.component';

export interface Socio {
    Id: number;
    Nombre: string;
    Apellido: string;
    DNI: string;
    Direccion?: string;
    Email?: string;
    Telefono?: string;
}

@Component({
    selector: 'app-socios',
    standalone: true,
    imports: [
        CommonModule,
        MatCardModule,
        MatButtonModule,
        MatTableModule,
        MatIconModule,
        MatDialogModule
    ],
    templateUrl: './socios.component.html',
    styleUrl: './socios.component.scss'
})
export class SociosComponent implements OnInit {
    private http = inject(HttpClient);
    private dialog = inject(MatDialog);

    displayedColumns: string[] = ['Id', 'Nombre', 'Apellido', 'DNI', 'Telefono', 'Acciones'];
    dataSource: Socio[] = [];

    ngOnInit() {
        this.fetchSocios();
    }

    fetchSocios() {
        this.http.get<Socio[]>('/api/socios')
            .subscribe(data => {
                this.dataSource = data;
            });
    }

    openDialog(socio?: Socio) {
        const dialogRef = this.dialog.open(SocioDialogComponent, {
            width: '500px',
            data: socio ? { ...socio } : null
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                if (socio) {
                    this.updateSocio(socio.Id, result);
                } else {
                    this.createSocio(result);
                }
            }
        });
    }

    createSocio(socio: Socio) {
        this.http.post<Socio>('/api/socios', socio)
            .subscribe(() => {
                this.fetchSocios();
            });
    }

    updateSocio(id: number, socio: Socio) {
        this.http.put<Socio>(`/api/socios/${id}`, socio)
            .subscribe(() => {
                this.fetchSocios();
            });
    }

    deleteSocio(id: number) {
        if (confirm('¿Está seguro de eliminar este socio?')) {
            this.http.delete(`/api/socios/${id}`)
                .subscribe(() => {
                    this.fetchSocios();
                });
        }
    }
}
