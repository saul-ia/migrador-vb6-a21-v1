const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.resolve(__dirname, 'dev_native.db');

const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database ' + dbPath + ': ' + err.message);
    } else {
        console.log('Connected to the SQLite database (Native).');
        initTables();
    }
});

function initTables() {
    db.serialize(() => {
        // Usuarios
        db.run(`CREATE TABLE IF NOT EXISTS Usuarios (
      Id INTEGER PRIMARY KEY AUTOINCREMENT,
      Username TEXT UNIQUE,
      Password TEXT
    )`);

        // Socios
        db.run(`CREATE TABLE IF NOT EXISTS Socios (
      Id INTEGER PRIMARY KEY AUTOINCREMENT,
      Nombre TEXT,
      Apellido TEXT,
      DNI TEXT,
      Direccion TEXT,
      Email TEXT,
      Telefono TEXT
    )`);

        // Libros (Updated with Loan fields to match VB6 logic)
        db.run(`CREATE TABLE IF NOT EXISTS Libros (
      Id INTEGER PRIMARY KEY AUTOINCREMENT,
      Titulo TEXT,
      Autor TEXT,
      ISBN TEXT UNIQUE,
      Estado TEXT DEFAULT 'Disponible',
      Socio INTEGER,
      FecPres TEXT,
      FecDev TEXT,
      dias INTEGER,
      FOREIGN KEY(Socio) REFERENCES Socios(Id)
    )`, (err) => {
            if (!err) {
                // Ensure columns exist if table was created before
                const cols = ['Socio INTEGER', 'FecPres TEXT', 'FecDev TEXT', 'dias INTEGER'];
                cols.forEach(col => {
                    db.run(`ALTER TABLE Libros ADD COLUMN ${col}`, (alterErr) => {
                        // Ignore error if column already exists
                    });
                });
            }
        });

        console.log('Tables initialized.');

        // Seed Admin
        seedAdmin();
    });
}

function seedAdmin() {
    db.get("SELECT Count(*) as count FROM Usuarios", [], (err, row) => {
        if (err) return console.error(err.message);
        if (row.count === 0) {
            console.log('Seeding admin user...');
            db.run("INSERT INTO Usuarios (Username, Password) VALUES (?, ?)", ['admin', '123'], (err) => {
                if (err) console.error(err.message);
                else console.log('Admin user created (admin/123).');
            });
        }
    });
}

module.exports = db;
