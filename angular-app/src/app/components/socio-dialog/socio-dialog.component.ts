import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

@Component({
    selector: 'app-socio-dialog',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatDialogModule,
        MatButtonModule,
        MatFormFieldModule,
        MatInputModule
    ],
    templateUrl: './socio-dialog.component.html',
    styleUrl: './socio-dialog.component.scss'
})
export class SocioDialogComponent implements OnInit {
    private fb = inject(FormBuilder);
    private dialogRef = inject(MatDialogRef<SocioDialogComponent>);
    public data = inject(MAT_DIALOG_DATA);

    form = this.fb.group({
        Nombre: ['', Validators.required],
        Apellido: ['', Validators.required],
        DNI: ['', Validators.required],
        Direccion: [''],
        Telefono: [''],
        Email: ['', [Validators.email]]
    });

    ngOnInit() {
        if (this.data) {
            this.form.patchValue(this.data);
        }
    }

    save() {
        if (this.form.valid) {
            this.dialogRef.close(this.form.value);
        }
    }

    cancel() {
        this.dialogRef.close();
    }
}
