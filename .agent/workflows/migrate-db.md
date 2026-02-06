---
description: Exports Access data and imports it into SQLite via Prisma. FULLY AUTOMATED - ALL TABLES.
---

// turbo-all

# Migrate Database Workflow v3.0 (Fully Automated)

## Execution Mode

| Setting | Value |
|---------|-------|
| **Confirmation Required** | ❌ NO |
| **Migration Scope** | 🔄 ALL TABLES |
| **Auto-Continue** | ✅ YES |

---

## Step 1: Export ALL Tables from Access

```bash
mkdir -p exports

# Export ALL tables (iterate from schema analysis)
# For each table in VB6_DATABASE.md:
mdb-export database.mdb TableName > exports/tablename.csv
```

---

## Step 2: Generate Complete Prisma Schema

Generate `prisma/schema.prisma` with:
- ALL models from VB6_DATABASE.md
- ALL relationships (foreign keys)
- ALL indexes
- Proper type mappings

```prisma
datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

// ALL models generated here - not just samples
```

---

## Step 3: Run Migrations (Auto)

```bash
npx prisma validate
npx prisma format
npx prisma migrate dev --name init
npx prisma generate
```

---

## Step 4: Seed ALL Data

Generate and run seed script for ALL tables:

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';

const prisma = new PrismaClient();

async function seedTable(tableName: string, csvPath: string) {
  const content = fs.readFileSync(csvPath, 'utf-8');
  const lines = content.split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    const values = lines[i].split(',');
    const data: Record<string, any> = {};
    headers.forEach((h, idx) => {
      data[h] = values[idx]?.trim();
    });
    await (prisma as any)[tableName].create({ data });
  }
  console.log(`✅ Seeded ${tableName}`);
}

async function main() {
  // Seed ALL tables in dependency order
  const tables = [
    // Parent tables first
    // Child tables after
  ];
  
  for (const table of tables) {
    await seedTable(table, `./exports/${table.toLowerCase()}.csv`);
  }
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
```

```bash
npx ts-node prisma/seed.ts
```

---

## Step 5: Verify (Auto)

```bash
# Open Prisma Studio to verify
npx prisma studio &

# Verify counts
npx prisma db execute --stdin <<< "SELECT name, (SELECT COUNT(*) FROM name) as count FROM sqlite_master WHERE type='table';"
```

---

## Auto-Continue

After database migration completes, automatically proceed to UI migration.

**No confirmation required.**
