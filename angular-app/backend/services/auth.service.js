const db = require('../database');

exports.login = (username, password) => {
    return new Promise((resolve, reject) => {
        const sql = "SELECT * FROM Usuarios WHERE Username = ?";
        db.get(sql, [username], (err, row) => {
            if (err) {
                reject(err);
            } else {
                if (row && row.Password === password) {
                    resolve({ token: 'fake-jwt-token', username: row.Username });
                } else {
                    resolve(null);
                }
            }
        });
    });
};
