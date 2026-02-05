const express = require('express');
const router = express.Router();
const prestamosController = require('../controllers/prestamos.controller');

router.get('/', prestamosController.getAll);
router.post('/', prestamosController.create);

module.exports = router;
