const librosService = require('../services/libros.service');

exports.getAll = async (req, res) => {
    try {
        const libros = await librosService.findAll();
        res.json(libros);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.getById = async (req, res) => {
    try {
        const libro = await librosService.findById(req.params.id);
        if (!libro) return res.status(404).json({ message: 'Not found' });
        res.json(libro);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.create = async (req, res) => {
    try {
        const newLibro = await librosService.create(req.body);
        res.status(201).json(newLibro);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.update = async (req, res) => {
    try {
        const updated = await librosService.update(req.params.id, req.body);
        res.json(updated);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.delete = async (req, res) => {
    try {
        await librosService.delete(req.params.id);
        res.status(204).send();
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};
