const db = require('../database');

exports.findAll = () => {
    return new Promise((resolve, reject) => {
        // Join Libros and Socios to show loan details
        const sql = `
      SELECT L.Id as LibroId, L.Titulo, L.Autor, S.Id as SocioId, S.Nombre, S.Apellido, 
             L.FecPres, L.FecDev, L.dias 
      FROM Libros L
      JOIN Socios S ON L.Socio = S.Id
      WHERE L.Estado = 'No'
    `;
        db.all(sql, [], (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

exports.create = (data) => {
    return new Promise((resolve, reject) => {
        // data: { socioId: number, libroId: number, dias: number, fecPres: string, fecDev: string }
        const sql = `
      UPDATE Libros 
      SET Estado = 'No', Socio = ?, FecPres = ?, FecDev = ?, dias = ? 
      WHERE Id = ?
    `;
        const params = [data.socioId, data.fecPres, data.fecDev, data.dias, data.libroId];
        console.log('Attempting Prestamo SQL:', sql, params);
        db.run(sql, params, function (err) {
            if (err) {
                console.error('Prestamo SQL Error:', err.message);
                reject(err);
            }
            else {
                console.log('Prestamo registered successfully');
                resolve({ success: true });
            }
        });
    });
};
