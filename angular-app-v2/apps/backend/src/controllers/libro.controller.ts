// =============================================================================
// LIBRO CONTROLLER - Book and Loan endpoints
// =============================================================================

import type { Request, Response } from 'express';
import { libroService } from '../services/libro.service.js';

export class LibroController {
    async getAll(req: Request, res: Response) {
        try {
            const includeSocio = req.query.includeSocio === 'true';
            const libros = await libroService.findAll(includeSocio);
            res.json(libros);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve books' });
        }
    }

    async getById(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const includeSocio = req.query.includeSocio === 'true';
            const libro = await libroService.findById(id, includeSocio);
            if (!libro) {
                return res.status(404).json({ error: 'Book not found' });
            }
            res.json(libro);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve book' });
        }
    }

    async search(req: Request, res: Response) {
        try {
            const query = req.query.q as string;
            if (!query) {
                return res.status(400).json({ error: 'Search query required' });
            }
            const libros = await libroService.search(query);
            res.json(libros);
        } catch (error) {
            res.status(500).json({ error: 'Search failed' });
        }
    }

    async getAvailable(_req: Request, res: Response) {
        try {
            const libros = await libroService.findAvailable();
            res.json(libros);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve available books' });
        }
    }

    async getLoaned(_req: Request, res: Response) {
        try {
            const libros = await libroService.findLoaned();
            res.json(libros);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve loaned books' });
        }
    }

    async getOverdue(_req: Request, res: Response) {
        try {
            const libros = await libroService.findOverdue();
            res.json(libros);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve overdue books' });
        }
    }

    async getStats(_req: Request, res: Response) {
        try {
            const stats = await libroService.getStats();
            res.json(stats);
        } catch (error) {
            res.status(500).json({ error: 'Failed to retrieve stats' });
        }
    }

    async create(req: Request, res: Response) {
        try {
            const { titulo, autor, estado, dias, fecPres, fecDev, socioId } = req.body;
            if (!titulo) {
                return res.status(400).json({ error: 'Titulo required' });
            }
            const libro = await libroService.create({
                titulo,
                autor,
                estado,
                dias,
                fecPres: fecPres ? new Date(fecPres) : undefined,
                fecDev: fecDev ? new Date(fecDev) : undefined,
                socioId,
            });
            res.status(201).json(libro);
        } catch (error) {
            res.status(500).json({ error: 'Failed to create book' });
        }
    }

    async update(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const { titulo, autor, estado, dias, fecPres, fecDev, socioId } = req.body;
            const libro = await libroService.update(id, {
                titulo,
                autor,
                estado,
                dias,
                fecPres: fecPres ? new Date(fecPres) : undefined,
                fecDev: fecDev ? new Date(fecDev) : undefined,
                socioId,
            });
            res.json(libro);
        } catch (error) {
            res.status(500).json({ error: 'Failed to update book' });
        }
    }

    async delete(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            await libroService.delete(id);
            res.status(204).send();
        } catch (error) {
            res.status(500).json({ error: 'Failed to delete book' });
        }
    }

    async prestar(req: Request, res: Response) {
        try {
            const { libroId, socioId, dias } = req.body;
            if (!libroId || !socioId || !dias) {
                return res.status(400).json({ error: 'libroId, socioId, and dias required' });
            }
            const libro = await libroService.prestar({ libroId, socioId, dias });
            res.json(libro);
        } catch (error: any) {
            if (error.message) {
                return res.status(400).json({ error: error.message });
            }
            res.status(500).json({ error: 'Failed to loan book' });
        }
    }

    async devolver(req: Request, res: Response) {
        try {
            const id = parseInt(String(req.params.id), 10);
            const libro = await libroService.devolver(id);
            res.json(libro);
        } catch (error) {
            res.status(500).json({ error: 'Failed to return book' });
        }
    }
}

export const libroController = new LibroController();
