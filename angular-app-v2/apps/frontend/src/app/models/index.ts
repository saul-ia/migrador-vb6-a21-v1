// =============================================================================
// MODELS - TypeScript interfaces matching Prisma schema
// =============================================================================

export interface Clave {
    id: number;
    pass: string;
}

export interface Cliente {
    id: number;
    nombres: string;
    apellidos: string;
    nroDoc?: string;
    domicilio?: string;
    telefono?: string;
    libros?: Libro[];
}

export interface Libro {
    id: number;
    titulo: string;
    autor?: string;
    estado?: string;
    dias?: number;
    fecPres?: string;
    fecDev?: string;
    socioId?: number;
    socio?: Cliente;
}

export interface PrestamoCreate {
    libroId: number;
    socioId: number;
    dias: number;
}

export interface LibroStats {
    total: number;
    disponibles: number;
    prestados: number;
    vencidos: number;
}
