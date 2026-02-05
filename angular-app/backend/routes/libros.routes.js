const express = require('express');
const router = express.Router();
const librosController = require('../controllers/libros.controller');

router.get('/', librosController.getAll);
router.get('/:id', librosController.getById);
router.post('/', librosController.create);
router.put('/:id', librosController.update);
router.delete('/:id', librosController.delete);

module.exports = router;
