const authService = require('../services/auth.service');

exports.login = async (req, res) => {
    try {
        const { username, password } = req.body;
        const result = await authService.login(username, password);

        if (result) {
            res.json(result);
        } else {
            res.status(401).json({ message: 'Credenciales inválidas' });
        }
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};
