const db = require('../database');

exports.findAll = () => {
    return new Promise((resolve, reject) => {
        db.all("SELECT * FROM Socios", [], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

exports.create = (data) => {
    return new Promise((resolve, reject) => {
        const sql = "INSERT INTO Socios (Nombre, Apellido, DNI, Direccion, Telefono) VALUES (?, ?, ?, ?, ?)";
        const params = [data.Nombre, data.Apellido, data.DNI, data.Direccion, data.Telefono];
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ Id: this.lastID, ...data });
        });
    });
};

exports.update = (id, data) => {
    return new Promise((resolve, reject) => {
        const sql = "UPDATE Socios SET Nombre = ?, Apellido = ?, DNI = ?, Direccion = ?, Telefono = ? WHERE Id = ?";
        const params = [data.Nombre, data.Apellido, data.DNI, data.Direccion, data.Telefono, id];
        db.run(sql, params, function (err) {
            if (err) reject(err);
            else resolve({ Id: id, ...data });
        });
    });
};

exports.delete = (id) => {
    return new Promise((resolve, reject) => {
        db.run("DELETE FROM Socios WHERE Id = ?", [id], function (err) {
            if (err) reject(err);
            else resolve({ Id: id });
        });
    });
};
