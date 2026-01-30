---
description: Exports Access data and imports it into SQLite via Prisma.
---

# Migrate Database Workflow

1.  **Analysis**: Call `data-migrator` to inspect `.mdb`.
2.  **Schema Gen**: `data-migrator` generates `prisma/schema.prisma`.
3.  **User Review**: Ask user to confirm types (esp. `Decimal` vs `Float`).
4.  **Migration**:
    *   `npx prisma migrate dev --name init`
5.  **Data Export**: Run `mdb-export` (Script) to CSV.
6.  **Data Import**: Run Node.js seed script to load CSVs.
7.  **Validation**: Compare row counts.
