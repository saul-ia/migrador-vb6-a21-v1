import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

interface Socio { Id: number; Nombre: string; Apellido: string; }
interface Libro { Id: number; Titulo: string; Autor: string; Estado: string; }
interface Prestamo { LibroId: number; Titulo: string; SocioId: number; Nombre: string; Apellido: string; FecPres: string; FecDev: string; dias: number; }

@Component({
  selector: 'app-prestamos',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatTableModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: './prestamos.html',
  styleUrl: './prestamos.scss',
})
export class PrestamosComponent implements OnInit {
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);
  private snackBar = inject(MatSnackBar);

  socios: Socio[] = [];
  libros: Libro[] = [];
  prestamos: Prestamo[] = [];
  displayedColumns: string[] = ['Libro', 'Socio', 'Fecha', 'Devolucion', 'Dias'];

  form = this.fb.group({
    socioId: [null as number | null, Validators.required],
    libroId: [null as number | null, Validators.required],
    dias: [7, [Validators.required, Validators.min(1)]]
  });

  ngOnInit() {
    this.fetchData();
  }

  fetchData() {
    this.http.get<Socio[]>('/api/socios').subscribe(data => this.socios = data);
    this.http.get<Libro[]>('/api/libros').subscribe(data => {
      this.libros = data.filter(l => l.Estado === 'Disponible');
    });
    this.http.get<Prestamo[]>('/api/prestamos').subscribe(data => this.prestamos = data);
  }

  registrar() {
    if (this.form.valid) {
      const val = this.form.value;
      const now = new Date();
      const fecPres = now.toLocaleDateString();
      const devDate = new Date();
      devDate.setDate(now.getDate() + (val.dias || 0));
      const fecDev = devDate.toLocaleDateString();

      const body = {
        ...val,
        fecPres,
        fecDev
      };

      this.http.post('/api/prestamos', body).subscribe({
        next: () => {
          this.snackBar.open('Préstamo registrado con éxito', 'OK', { duration: 3000 });
          this.form.reset({ dias: 7 });
          this.fetchData();
        },
        error: (err) => {
          console.error('Error al registrar préstamo:', err);
          this.snackBar.open('Error al registrar préstamo: ' + (err.error?.message || err.message), 'Cerrar', { duration: 5000 });
        }
      });
    }
  }
}
