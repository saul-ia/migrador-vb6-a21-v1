// =============================================================================
// CLAVE ROUTES - Authentication endpoints
// =============================================================================

import { Router } from 'express';
import { claveController } from '../controllers/clave.controller.js';

const router = Router();

// GET /api/claves - Get all passwords
router.get('/', claveController.getAll.bind(claveController));

// GET /api/claves/:id - Get password by ID
router.get('/:id', claveController.getById.bind(claveController));

// POST /api/claves/validate - Validate password
router.post('/validate', claveController.validate.bind(claveController));

// POST /api/claves - Create password
router.post('/', claveController.create.bind(claveController));

// PUT /api/claves/:id - Update password
router.put('/:id', claveController.update.bind(claveController));

// DELETE /api/claves/:id - Delete password
router.delete('/:id', claveController.delete.bind(claveController));

export default router;
