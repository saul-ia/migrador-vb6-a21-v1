const express = require('express');
const router = express.Router();
const sociosController = require('../controllers/socios.controller');

router.get('/', sociosController.getAll);
router.get('/:id', sociosController.getById);
router.post('/', sociosController.create);
router.put('/:id', sociosController.update);
router.delete('/:id', sociosController.delete);

module.exports = router;
