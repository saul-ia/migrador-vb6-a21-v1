---
name: db-transform
description: Techniques for migrating Access Databases to SQLite.
allowed-tools: run_command, mcp_db-usuarios_query
---

# Database Transformation Guide

## Access Data Types Map
| Access (.mdb) | SQLite / Prisma | Notes |
| Link | String | |
| Byte | Int | |
| Integer | Int | |
| Long | Int | |
| Currency | Decimal | |
| Single, Double | Float | |
| Date/Time | DateTime | |
| Text (255) | String | |
| Memo | String | |
| Yes/No | Boolean | 0=False, -1=True (Convert -1 to 1) |
| OLE Object | Blob | Consider storing files on disk instead |

## Migration Steps
1.  **Export**: Use `mdb-export` (tools like MDB Tools) to get CSVs.
2.  **Clean**: Remove Windows-1252 artifacts.
3.  **Seed**: Read CSV in Node.js and use `prisma.model.createMany`.

## Prisma Schema Patterns
*   **Renaming**: use `@@map("TBL_OLD_NAME")` to keep DB table names if needed, but rename the Model Class to PascalCase.
    ```prisma
    model User {
       ...
       @@map("TBL_USUARIOS")
    }
    ```
