// =============================================================================
// CLIENTE SERVICE - Client/Member operations
// =============================================================================

import { prisma } from '../server.js';
import type { Cliente, Libro } from '@prisma/client';

export interface ClienteWithLibros extends Cliente {
    libros?: Libro[];
}

export interface CreateClienteDto {
    nombres: string;
    apellidos: string;
    nroDoc?: string;
    domicilio?: string;
    telefono?: string;
}

export interface UpdateClienteDto {
    nombres?: string;
    apellidos?: string;
    nroDoc?: string;
    domicilio?: string;
    telefono?: string;
}

export class ClienteService {
    /**
     * Get all clients with optional libro count
     */
    async findAll(includeLibros = false): Promise<ClienteWithLibros[]> {
        return prisma.cliente.findMany({
            include: includeLibros ? { libros: true } : undefined,
            orderBy: { apellidos: 'asc' },
        });
    }

    /**
     * Find client by ID
     */
    async findById(id: number, includeLibros = false): Promise<ClienteWithLibros | null> {
        return prisma.cliente.findUnique({
            where: { id },
            include: includeLibros ? { libros: true } : undefined,
        });
    }

    /**
     * Search clients by name
     */
    async search(query: string): Promise<Cliente[]> {
        return prisma.cliente.findMany({
            where: {
                OR: [
                    { nombres: { contains: query } },
                    { apellidos: { contains: query } },
                    { nroDoc: { contains: query } },
                ],
            },
            orderBy: { apellidos: 'asc' },
        });
    }

    /**
     * Create new client
     */
    async create(data: CreateClienteDto): Promise<Cliente> {
        return prisma.cliente.create({ data });
    }

    /**
     * Update client
     */
    async update(id: number, data: UpdateClienteDto): Promise<Cliente> {
        return prisma.cliente.update({ where: { id }, data });
    }

    /**
     * Delete client (only if no active loans)
     */
    async delete(id: number): Promise<Cliente> {
        // Check for active loans
        const activeLoans = await prisma.libro.count({
            where: { socioId: id, estado: 'prestado' },
        });

        if (activeLoans > 0) {
            throw new Error('Cannot delete client with active loans');
        }

        return prisma.cliente.delete({ where: { id } });
    }

    /**
     * Get client count
     */
    async count(): Promise<number> {
        return prisma.cliente.count();
    }
}

export const clienteService = new ClienteService();
