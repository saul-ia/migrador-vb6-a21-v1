const sociosService = require('../services/socios.service');

exports.getAll = async (req, res) => {
    try {
        const socios = await sociosService.findAll();
        res.json(socios);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.getById = async (req, res) => {
    try {
        const socio = await sociosService.findById(req.params.id);
        if (!socio) return res.status(404).json({ message: 'Not found' });
        res.json(socio);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.create = async (req, res) => {
    try {
        const newSocio = await sociosService.create(req.body);
        res.status(201).json(newSocio);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.update = async (req, res) => {
    try {
        const updated = await sociosService.update(req.params.id, req.body);
        res.json(updated);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};

exports.delete = async (req, res) => {
    try {
        await sociosService.delete(req.params.id);
        res.status(204).send();
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};
