const prestamosService = require('../services/prestamos.service');

exports.getAll = async (req, res) => {
    try {
        const data = await prestamosService.findAll();
        res.json(data);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};

exports.create = async (req, res) => {
    try {
        const result = await prestamosService.create(req.body);
        res.status(201).json(result);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};
