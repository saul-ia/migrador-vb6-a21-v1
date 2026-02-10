// =============================================================================
// AYUDA COMPONENT - Help page (migrated from frmAYUDA)
// =============================================================================

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-ayuda',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './ayuda.component.html',
    styleUrl: './ayuda.component.css'
})
export class AyudaComponent {
    sections = [
        {
            title: '📚 Gestión de Libros',
            items: [
                'Ver listado completo de libros',
                'Buscar por título o autor',
                'Filtrar por estado (Disponible/Prestado)',
                'Agregar nuevos libros',
                'Editar información de libros existentes',
                'Eliminar libros del sistema'
            ]
        },
        {
            title: '👥 Gestión de Clientes (Socios)',
            items: [
                'Ver listado de clientes registrados',
                'Buscar por ID o apellido',
                'Agregar nuevos clientes',
                'Editar datos de clientes',
                'Ver historial de préstamos'
            ]
        },
        {
            title: '📤 Préstamos',
            items: [
                'Registrar nuevo préstamo',
                'Seleccionar libro disponible',
                'Seleccionar cliente (socio)',
                'Definir días de préstamo',
                'Ver préstamos activos',
                'Identificar préstamos vencidos'
            ]
        },
        {
            title: '↩️ Devoluciones',
            items: [
                'Devolver libro desde lista de préstamos',
                'Devolver libro desde pantalla de libros',
                'El libro vuelve a estado "Disponible"'
            ]
        },
        {
            title: '🔐 Seguridad',
            items: [
                'Acceso protegido por contraseña',
                'Cerrar sesión desde el menú lateral'
            ]
        }
    ];
}
