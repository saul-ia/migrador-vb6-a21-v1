const db = require('./backend/database');

function checkColumns() {
    db.all("PRAGMA table_info(Libros)", [], (err, rows) => {
        if (err) {
            console.error(err);
            process.exit(1);
        }
        console.log('Columns in Libros:', rows.map(r => r.name));
        process.exit(0);
    });
}

setTimeout(checkColumns, 1000);
