// =============================================================================
// CLIENTE ROUTES - Client/Member endpoints
// =============================================================================

import { Router } from 'express';
import { clienteController } from '../controllers/cliente.controller.js';

const router = Router();

// GET /api/clientes - Get all clients
router.get('/', clienteController.getAll.bind(clienteController));

// GET /api/clientes/search?q=query - Search clients
router.get('/search', clienteController.search.bind(clienteController));

// GET /api/clientes/count - Get client count
router.get('/count', clienteController.count.bind(clienteController));

// GET /api/clientes/:id - Get client by ID
router.get('/:id', clienteController.getById.bind(clienteController));

// POST /api/clientes - Create client
router.post('/', clienteController.create.bind(clienteController));

// PUT /api/clientes/:id - Update client
router.put('/:id', clienteController.update.bind(clienteController));

// DELETE /api/clientes/:id - Delete client
router.delete('/:id', clienteController.delete.bind(clienteController));

export default router;
