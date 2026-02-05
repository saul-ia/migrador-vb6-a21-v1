const db = require('../database');

exports.findAll = () => {
    return new Promise((resolve, reject) => {
        db.all("SELECT * FROM Libros", [], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

exports.create = (data) => {
    return new Promise((resolve, reject) => {
        const sql = "INSERT INTO Libros (Titulo, Autor, Estado) VALUES (?, ?, ?)";
        const params = [data.Titulo, data.Autor, 'Disponible']; // Default
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ Id: this.lastID, ...data });
        });
    });
};

exports.update = (id, data) => {
    return new Promise((resolve, reject) => {
        const sql = "UPDATE Libros SET Titulo = ?, Autor = ?, Estado = ? WHERE Id = ?";
        const params = [data.Titulo, data.Autor, data.Estado || 'Disponible', id];
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ Id: id, ...data });
        });
    });
};

exports.delete = (id) => {
    return new Promise((resolve, reject) => {
        db.run("DELETE FROM Libros WHERE Id = ?", [id], function (err) {
            if (err) reject(err);
            else resolve({ Id: id });
        });
    });
};
