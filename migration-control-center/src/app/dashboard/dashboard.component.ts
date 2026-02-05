import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatSelectModule,
        MatCheckboxModule,
        MatProgressBarModule
    ],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
    migrationForm: FormGroup;
    isRunning = signal(false);
    logs = signal<string[]>([]);

    constructor(private fb: FormBuilder) {
        this.migrationForm = this.fb.group({
            migratorVersion: ['v1.0', Validators.required],
            sourcePath: ['vb6-apps/Biblioteca', Validators.required],
            targetPath: ['', Validators.required],
            createRepo: [true]
        });
    }

    runMigration() {
        if (this.migrationForm.valid) {
            this.isRunning.set(true);
            this.logs.update(logs => [...logs, '🚀 Starting Migration Orchestrator...']);

            const config = this.migrationForm.value;
            setTimeout(() => {
                this.logs.update(logs => [...logs, `📂 Analyzing Source: ${config.sourcePath}`]);
            }, 1000);

            setTimeout(() => {
                this.logs.update(logs => [...logs, `🎯 Preparing Target: ${config.targetPath}`]);
            }, 2000);

            setTimeout(() => {
                this.logs.update(logs => [...logs, '⚠️ (Simulation) Backend API not connected yet.']);
                this.isRunning.set(false);
            }, 3500);
        }
    }
}
