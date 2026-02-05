import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
    selector: 'app-login',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatCardModule,
        MatButtonModule,
        MatInputModule,
        MatFormFieldModule
    ],
    templateUrl: './login.component.html',
    styleUrl: './login.component.scss'
})
export class LoginComponent {
    private fb = inject(FormBuilder);
    private http = inject(HttpClient);
    private router = inject(Router);

    form = this.fb.group({
        username: ['', Validators.required],
        password: ['', Validators.required]
    });

    errorMsg = '';

    login() {
        if (this.form.valid) {
            this.http.post<any>('/api/auth/login', this.form.value)
                .subscribe({
                    next: (res) => {
                        localStorage.setItem('token', res.token); // Simple demo auth
                        this.router.navigate(['/']);
                    },
                    error: (err) => {
                        this.errorMsg = 'Usuario o contraseña incorrectos';
                    }
                });
        }
    }
}
