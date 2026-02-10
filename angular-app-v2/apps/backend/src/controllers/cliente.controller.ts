// =============================================================================
// CLIENTE CONTROLLER - Client/Member endpoints
// =============================================================================

import type { Request, Response } from 'express';
import { clienteService } from '../services/cliente.service.js';

export class ClienteController {
    async getAll(req: Request, res: Response) {
        try {
            const includeLibros = req.query.includeLibros === 'true';
            const clientes = await clienteService.findAll(includeLibros);
            res.json(clientes);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve clients' });
        }
    }

    async getById(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const includeLibros = req.query.includeLibros === 'true';
            const cliente = await clienteService.findById(id, includeLibros);
            if (!cliente) {
                return res.status(404).json({ error: 'Client not found' });
            }
            res.json(cliente);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve client' });
        }
    }

    async search(req: Request, res: Response) {
        try {
            const query = req.query.q as string;
            if (!query) {
                return res.status(400).json({ error: 'Search query required' });
            }
            const clientes = await clienteService.search(query);
            res.json(clientes);
        } catch (error) {
            res.status(500).json({ error: 'Search failed' });
        }
    }

    async create(req: Request, res: Response) {
        try {
            const { nombres, apellidos, nroDoc, domicilio, telefono } = req.body;
            if (!nombres || !apellidos) {
                return res.status(400).json({ error: 'Nombres and apellidos required' });
            }
            const cliente = await clienteService.create({
                nombres,
                apellidos,
                nroDoc,
                domicilio,
                telefono,
            });
            res.status(201).json(cliente);
        } catch (error) {
            res.status(500).json({ error: 'Failed to create client' });
        }
    }

    async update(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const { nombres, apellidos, nroDoc, domicilio, telefono } = req.body;
            const cliente = await clienteService.update(id, {
                nombres,
                apellidos,
                nroDoc,
                domicilio,
                telefono,
            });
            res.json(cliente);
        } catch (error) {
            res.status(500).json({ error: 'Failed to update client' });
        }
    }

    async delete(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            await clienteService.delete(id);
            res.status(204).send();
        } catch (error: any) {
            if (error.message?.includes('active loans')) {
                return res.status(400).json({ error: error.message });
            }
            res.status(500).json({ error: 'Failed to delete client' });
        }
    }

    async count(_req: Request, res: Response) {
        try {
            const count = await clienteService.count();
            res.json({ count });
        } catch (error) {
            res.status(500).json({ error: 'Failed to count clients' });
        }
    }
}

export const clienteController = new ClienteController();
