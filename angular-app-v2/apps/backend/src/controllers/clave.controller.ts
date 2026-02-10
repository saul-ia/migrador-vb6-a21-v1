// =============================================================================
// CLAVE CONTROLLER - Authentication endpoints
// =============================================================================

import type { Request, Response } from 'express';
import { claveService } from '../services/clave.service.js';

export class ClaveController {
    async getAll(_req: Request, res: Response) {
        try {
            const claves = await claveService.findAll();
            res.json(claves);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve claves' });
        }
    }

    async getById(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const clave = await claveService.findById(id);
            if (!clave) {
                return res.status(404).json({ error: 'Clave not found' });
            }
            res.json(clave);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve clave' });
        }
    }

    async validate(req: Request, res: Response) {
        try {
            const { pass } = req.body;
            if (!pass) {
                return res.status(400).json({ error: 'Password required' });
            }
            const valid = await claveService.validatePassword(pass);
            res.json({ valid });
        } catch (error) {
            res.status(500).json({ error: 'Validation failed' });
        }
    }

    async create(req: Request, res: Response) {
        try {
            const { pass } = req.body;
            if (!pass) {
                return res.status(400).json({ error: 'Password required' });
            }
            const clave = await claveService.create({ pass });
            res.status(201).json(clave);
        } catch (error) {
            res.status(500).json({ error: 'Failed to create clave' });
        }
    }

    async update(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const { pass } = req.body;
            if (!pass) {
                return res.status(400).json({ error: 'Password required' });
            }
            const clave = await claveService.update(id, { pass });
            res.json(clave);
        } catch (error) {
            res.status(500).json({ error: 'Failed to update clave' });
        }
    }

    async delete(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            await claveService.delete(id);
            res.status(204).send();
        } catch (error) {
            res.status(500).json({ error: 'Failed to delete clave' });
        }
    }
}

export const claveController = new ClaveController();
