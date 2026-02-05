---
description: Exports Access data and imports it into SQLite via Prisma.
---

// turbo-all

# Migrate Database Workflow v2.0

## Purpose

Convert VB6/Access database to SQLite with Prisma ORM, preserving all data integrity.

---

## Prerequisites

- Analysis phase complete (`VB6_DATABASE.md` available)
- Node.js 24+ installed
- Backend project initialized

---

## Step 1: Export Access Data

### Option A: Using mdbtools (Linux/WSL)
```bash
# Install mdbtools
sudo apt-get install mdbtools

# List tables
mdb-tables database.mdb

# Export each table to CSV
mdb-export database.mdb Socios > data/socios.csv
mdb-export database.mdb Libros > data/libros.csv
mdb-export database.mdb Prestamos > data/prestamos.csv
```

### Option B: Using Access (Windows)
1. Open `.mdb` in Microsoft Access
2. Right-click each table → Export → Text File (CSV)
3. Save to `data/` folder

### Option C: Using Python
```bash
python .agent/scripts/vb6_schema_extractor.py "path/to/project" -o schema.json --pretty
```

---

## Step 2: Create Prisma Schema

Based on `VB6_DATABASE.md`, generate the schema:

```bash
# Initialize Prisma
cd backend
npx prisma init --datasource-provider sqlite

# Edit prisma/schema.prisma with extracted schema
# (backend-architect generates this)
```

### Schema Template
```prisma
datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Socio {
  id        Int       @id @default(autoincrement())
  nombre    String
  direccion String?
  telefono  String?
  email     String?
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
  prestamos Prestamo[]
}

// Add all models from VB6_DATABASE.md
```

---

## Step 3: Validate and Generate

```bash
# Validate schema syntax
npx prisma validate

# Format schema
npx prisma format

# Generate Prisma client
npx prisma generate

# Create database and tables
npx prisma db push
```

---

## Step 4: Seed Data from CSV

Create seed script:

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';

const prisma = new PrismaClient();

async function main() {
  // Read CSV
  const sociosData = fs.readFileSync('data/socios.csv', 'utf-8');
  const lines = sociosData.split('\n').slice(1); // Skip header

  for (const line of lines) {
    if (!line.trim()) continue;
    const [id, nombre, direccion, telefono, email] = line.split(',');
    
    await prisma.socio.create({
      data: {
        nombre: nombre.trim(),
        direccion: direccion?.trim() || null,
        telefono: telefono?.trim() || null,
        email: email?.trim() || null
      }
    });
  }

  console.log('✅ Seeding complete');
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

Run seed:
```bash
npx ts-node prisma/seed.ts
```

---

## Step 5: Verify Migration

```bash
# Open Prisma Studio to inspect data
npx prisma studio

# Run verification queries
npx prisma db execute --stdin <<< "SELECT COUNT(*) FROM Socio;"
```

---

## Validation Checklist

- [ ] All tables exported from Access
- [ ] Prisma schema validates
- [ ] All data imported without errors
- [ ] Row counts match original database
- [ ] Relationships (foreign keys) preserved
- [ ] Test queries return expected results

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Encoding errors | Use `latin1` or `cp1252` when reading CSV |
| Date format issues | Parse with `new Date()` or custom parser |
| Duplicate keys | Clean duplicates before import |
| Missing relations | Import parent tables first |
