import { Routes } from '@angular/router';
import { MainLayoutComponent } from './components/main-layout/main-layout.component';
import { Form1Component } from './components/form1/form1.component';
import { SociosComponent } from './components/socios/socios.component';
import { LoginComponent } from './components/login/login.component';
import { PrestamosComponent } from './components/prestamos/prestamos';
import { authGuard } from './auth.guard';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [authGuard],
        children: [
            { path: '', redirectTo: 'form1', pathMatch: 'full' },
            { path: 'form1', component: Form1Component },
            { path: 'socios', component: SociosComponent },
            { path: 'prestamos', component: PrestamosComponent }
        ]
    },
    { path: '**', redirectTo: '' }
];
