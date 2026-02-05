const db = require('./backend/database');

function check() {
    db.all("SELECT * FROM Socios", [], (err, socios) => {
        console.log('Socios:', socios.length, socios);
        db.all("SELECT * FROM Libros", [], (err, libros) => {
            console.log('Libros:', libros.length, libros);
            process.exit(0);
        });
    });
}

setTimeout(check, 1000);
