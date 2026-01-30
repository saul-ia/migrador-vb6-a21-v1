def map_access_to_sqlite(access_type):
    """
    Maps MS Access Data Types to SQLite/Prisma Types.
    """
    normalization_map = {
        "Text": "String",
        "Memo": "String",
        "Byte": "Int",
        "Integer": "Int",
        "Long": "Int",
        "Single": "Float",
        "Double": "Float",
        "Currency": "Decimal",
        "AutoNumber": "Int @id @default(autoincrement())",
        "Date/Time": "DateTime",
        "Yes/No": "Boolean",
        "OLE Object": "Bytes",
        "Hyperlink": "String"
    }
    return normalization_map.get(access_type, "String") // Default to String

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(map_access_to_sqlite(sys.argv[1]))
    else:
        print("Provide an Access type name.")
