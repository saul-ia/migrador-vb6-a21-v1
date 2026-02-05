import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { LibroDialogComponent } from '../libro-dialog/libro-dialog.component';

export interface Libro {
    Id: number;
    Titulo: string;
    Autor: string;
    Estado: string;
}

@Component({
    selector: 'app-form1',
    standalone: true,
    imports: [
        CommonModule,
        MatCardModule,
        MatButtonModule,
        MatTableModule,
        MatIconModule,
        MatDialogModule
    ],
    templateUrl: './form1.component.html',
    styleUrl: './form1.component.scss'
})
export class Form1Component implements OnInit {
    private http = inject(HttpClient);
    private dialog = inject(MatDialog);

    displayedColumns: string[] = ['Id', 'Titulo', 'Autor', 'Estado', 'Acciones'];
    dataSource: Libro[] = [];

    ngOnInit() {
        this.fetchLibros();
    }

    fetchLibros() {
        this.http.get<Libro[]>('/api/libros')
            .subscribe(data => {
                this.dataSource = data;
            });
    }

    openDialog(libro?: Libro) {
        const dialogRef = this.dialog.open(LibroDialogComponent, {
            width: '500px',
            data: libro ? { ...libro } : null
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result) {
                if (libro) {
                    this.updateLibro(libro.Id, result);
                } else {
                    this.createLibro(result);
                }
            }
        });
    }

    createLibro(libro: any) {
        this.http.post<Libro>('/api/libros', libro)
            .subscribe(() => {
                this.fetchLibros();
            });
    }

    updateLibro(id: number, libro: Libro) {
        this.http.put<Libro>(`/api/libros/${id}`, libro)
            .subscribe(() => {
                this.fetchLibros();
            });
    }

    deleteLibro(id: number) {
        if (confirm('¿Está seguro de eliminar este libro?')) {
            this.http.delete(`/api/libros/${id}`)
                .subscribe(() => {
                    this.fetchLibros();
                });
        }
    }
}
