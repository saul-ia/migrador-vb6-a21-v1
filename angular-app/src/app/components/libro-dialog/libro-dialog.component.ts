import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

@Component({
    selector: 'app-libro-dialog',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatDialogModule,
        MatButtonModule,
        MatFormFieldModule,
        MatInputModule
    ],
    templateUrl: './libro-dialog.component.html',
    styleUrl: './libro-dialog.component.scss'
})
export class LibroDialogComponent implements OnInit {
    private fb = inject(FormBuilder);
    private dialogRef = inject(MatDialogRef<LibroDialogComponent>);
    public data = inject(MAT_DIALOG_DATA);

    form = this.fb.group({
        Titulo: ['', Validators.required],
        Autor: ['', Validators.required]
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
