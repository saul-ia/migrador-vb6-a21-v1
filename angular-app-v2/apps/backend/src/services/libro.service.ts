// =============================================================================
// LIBRO SERVICE - Book and Loan operations
// =============================================================================

import { prisma } from '../server.js';
import type { Libro, Cliente } from '@prisma/client';

export interface LibroWithSocio extends Libro {
    socio?: Cliente | null;
}

export interface CreateLibroDto {
    titulo: string;
    autor?: string;
    estado?: string;
    dias?: number;
    fecPres?: Date;
    fecDev?: Date;
    socioId?: number;
}

export interface UpdateLibroDto {
    titulo?: string;
    autor?: string;
    estado?: string;
    dias?: number;
    fecPres?: Date;
    fecDev?: Date;
    socioId?: number;
}

export interface PrestamoDto {
    libroId: number;
    socioId: number;
    dias: number;
}

export class LibroService {
    /**
     * Get all books with optional socio info
     */
    async findAll(includeSocio = false): Promise<LibroWithSocio[]> {
        return prisma.libro.findMany({
            include: includeSocio ? { socio: true } : undefined,
            orderBy: { titulo: 'asc' },
        });
    }

    /**
     * Find book by ID
     */
    async findById(id: number, includeSocio = false): Promise<LibroWithSocio | null> {
        return prisma.libro.findUnique({
            where: { id },
            include: includeSocio ? { socio: true } : undefined,
        });
    }

    /**
     * Search books by title or author
     */
    async search(query: string): Promise<Libro[]> {
        return prisma.libro.findMany({
            where: {
                OR: [
                    { titulo: { contains: query } },
                    { autor: { contains: query } },
                ],
            },
            orderBy: { titulo: 'asc' },
        });
    }

    /**
     * Get available books (not loaned)
     */
    async findAvailable(): Promise<Libro[]> {
        return prisma.libro.findMany({
            where: {
                OR: [
                    { estado: 'disponible' },
                    { estado: null },
                    { socioId: null },
                ],
            },
            orderBy: { titulo: 'asc' },
        });
    }

    /**
     * Get loaned books
     */
    async findLoaned(): Promise<LibroWithSocio[]> {
        return prisma.libro.findMany({
            where: { estado: 'prestado' },
            include: { socio: true },
            orderBy: { fecPres: 'desc' },
        });
    }

    /**
     * Get overdue books
     */
    async findOverdue(): Promise<LibroWithSocio[]> {
        const now = new Date();
        return prisma.libro.findMany({
            where: {
                estado: 'prestado',
                fecDev: { lt: now },
            },
            include: { socio: true },
            orderBy: { fecDev: 'asc' },
        });
    }

    /**
     * Create new book
     */
    async create(data: CreateLibroDto): Promise<Libro> {
        return prisma.libro.create({
            data: {
                ...data,
                estado: data.estado || 'disponible',
            },
        });
    }

    /**
     * Update book
     */
    async update(id: number, data: UpdateLibroDto): Promise<Libro> {
        return prisma.libro.update({ where: { id }, data });
    }

    /**
     * Delete book
     */
    async delete(id: number): Promise<Libro> {
        return prisma.libro.delete({ where: { id } });
    }

    /**
     * Loan a book (Préstamo)
     */
    async prestar(data: PrestamoDto): Promise<Libro> {
        const libro = await prisma.libro.findUnique({ where: { id: data.libroId } });
        if (!libro) {
            throw new Error('Book not found');
        }
        if (libro.estado === 'prestado') {
            throw new Error('Book is already loaned');
        }

        const fecPres = new Date();
        const fecDev = new Date();
        fecDev.setDate(fecDev.getDate() + data.dias);

        return prisma.libro.update({
            where: { id: data.libroId },
            data: {
                estado: 'prestado',
                socioId: data.socioId,
                dias: data.dias,
                fecPres,
                fecDev,
            },
        });
    }

    /**
     * Return a book (Devolución)
     */
    async devolver(libroId: number): Promise<Libro> {
        return prisma.libro.update({
            where: { id: libroId },
            data: {
                estado: 'disponible',
                socioId: null,
                dias: null,
                fecPres: null,
                fecDev: null,
            },
        });
    }

    /**
     * Get book counts by status
     */
    async getStats(): Promise<{ total: number; disponibles: number; prestados: number; vencidos: number }> {
        const [total, disponibles, prestados, vencidos] = await Promise.all([
            prisma.libro.count(),
            prisma.libro.count({ where: { OR: [{ estado: 'disponible' }, { estado: null }] } }),
            prisma.libro.count({ where: { estado: 'prestado' } }),
            prisma.libro.count({ where: { estado: 'prestado', fecDev: { lt: new Date() } } }),
        ]);
        return { total, disponibles, prestados, vencidos };
    }
}

export const libroService = new LibroService();
