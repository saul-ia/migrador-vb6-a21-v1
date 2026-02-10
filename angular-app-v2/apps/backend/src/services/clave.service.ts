// =============================================================================
// CLAVE SERVICE - Password/Authentication table operations
// =============================================================================

import { prisma } from '../server.js';
import type { Clave } from '@prisma/client';

export class ClaveService {
    /**
     * Get all claves (passwords)
     */
    async findAll(): Promise<Clave[]> {
        return prisma.clave.findMany();
    }

    /**
     * Find clave by ID
     */
    async findById(id: number): Promise<Clave | null> {
        return prisma.clave.findUnique({ where: { id } });
    }

    /**
     * Validate password
     */
    async validatePassword(pass: string): Promise<boolean> {
        const clave = await prisma.clave.findFirst({
            where: { pass },
        });
        return clave !== null;
    }

    /**
     * Create new clave
     */
    async create(data: { pass: string }): Promise<Clave> {
        return prisma.clave.create({ data });
    }

    /**
     * Update clave
     */
    async update(id: number, data: { pass: string }): Promise<Clave> {
        return prisma.clave.update({ where: { id }, data });
    }

    /**
     * Delete clave
     */
    async delete(id: number): Promise<Clave> {
        return prisma.clave.delete({ where: { id } });
    }
}

export const claveService = new ClaveService();
