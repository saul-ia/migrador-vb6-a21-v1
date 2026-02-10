// =============================================================================
// LIBRO ROUTES - Book and Loan endpoints
// =============================================================================

import { Router } from 'express';
import { libroController } from '../controllers/libro.controller.js';

const router = Router();

// GET /api/libros - Get all books
router.get('/', libroController.getAll.bind(libroController));

// GET /api/libros/search?q=query - Search books
router.get('/search', libroController.search.bind(libroController));

// GET /api/libros/available - Get available books
router.get('/available', libroController.getAvailable.bind(libroController));

// GET /api/libros/loaned - Get loaned books
router.get('/loaned', libroController.getLoaned.bind(libroController));

// GET /api/libros/overdue - Get overdue books
router.get('/overdue', libroController.getOverdue.bind(libroController));

// GET /api/libros/stats - Get book statistics
router.get('/stats', libroController.getStats.bind(libroController));

// GET /api/libros/:id - Get book by ID
router.get('/:id', libroController.getById.bind(libroController));

// POST /api/libros - Create book
router.post('/', libroController.create.bind(libroController));

// POST /api/libros/prestar - Loan a book
router.post('/prestar', libroController.prestar.bind(libroController));

// PUT /api/libros/:id - Update book
router.put('/:id', libroController.update.bind(libroController));

// PUT /api/libros/:id/devolver - Return a book
router.put('/:id/devolver', libroController.devolver.bind(libroController));

// DELETE /api/libros/:id - Delete book
router.delete('/:id', libroController.delete.bind(libroController));

export default router;
