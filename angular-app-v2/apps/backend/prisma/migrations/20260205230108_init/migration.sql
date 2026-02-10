-- CreateTable
CREATE TABLE "clave" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "pass" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "cliente" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nombres" TEXT NOT NULL,
    "apellidos" TEXT NOT NULL,
    "nro_doc" TEXT,
    "domicilio" TEXT,
    "telefono" TEXT
);

-- CreateTable
CREATE TABLE "libros" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "titulo" TEXT NOT NULL,
    "autor" TEXT,
    "estado" TEXT,
    "dias" INTEGER,
    "fec_pres" DATETIME,
    "fec_dev" DATETIME,
    "socio_id" INTEGER,
    CONSTRAINT "libros_socio_id_fkey" FOREIGN KEY ("socio_id") REFERENCES "cliente" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);
