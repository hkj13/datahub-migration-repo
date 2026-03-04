#!/usr/bin/env python3
"""
Scan SQL queries folder and generate queries_data.js for the migration web app.

Usage:
    python generate_app_data.py /path/to/queries/folder

Output:
    queries_data.js (in the same directory as this script's parent)
"""

import os
import sys
import re
import json
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert camelCase/PascalCase to snake_case."""
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def detect_camel_columns(sql: str) -> list:
    """Find camelCase identifiers in SQL that need snake_case conversion."""
    camel_pattern = re.compile(r'\b([a-z]+[A-Z][a-zA-Z]*)\b')
    sql_keywords = {
        'as', 'on', 'in', 'is', 'or', 'and', 'not', 'null', 'true', 'false',
        'between', 'like', 'inner', 'outer', 'left', 'right', 'cross',
        'natural', 'using', 'where', 'having', 'order', 'group', 'limit',
        'offset', 'union', 'except', 'intersect', 'varchar', 'integer',
        'boolean', 'timestamp', 'interval', 'select', 'from', 'join',
        'into', 'values', 'update', 'delete', 'insert', 'create', 'alter',
        'drop', 'table', 'index', 'view', 'case', 'when', 'then', 'else',
        'end', 'cast', 'coalesce', 'isnull', 'ifnull', 'nullif',
        'getDate', 'dateAdd', 'dateDiff', 'getUTCDate', 'dateTime',
        'groupBy', 'orderBy', 'forEach', 'indexOf', 'toString',
        'valueOf', 'parseInt', 'parseFloat', 'isNaN', 'isNull',
        'noLock', 'readUncommitted', 'rowNumber', 'charIndex',
        'subString', 'upperCase', 'lowerCase', 'trimEnd', 'trimStart',
        'endsWith', 'startsWith', 'nVarchar', 'bigInt', 'tinyInt',
        'smallInt', 'uniqueIdentifier', 'primaryKey', 'foreignKey',
    }
    found = set()
    for match in camel_pattern.finditer(sql):
        col = match.group(1)
        if col.lower() not in {k.lower() for k in sql_keywords}:
            found.add(col)
    return sorted(found)


def detect_table_refs(sql: str) -> list:
    """Find schema.table references in SQL."""
    pattern = re.compile(
        r'(?:FROM|JOIN)\s+([a-zA-Z_]\w*\.[a-zA-Z_]\w*)',
        re.IGNORECASE
    )
    return sorted(set(m.group(1) for m in pattern.finditer(sql)))


def scan_queries(queries_path: str) -> dict:
    """Scan all .sql files and return structured data."""
    queries_dir = Path(queries_path)
    if not queries_dir.exists():
        print(f"ERROR: Path not found: {queries_dir}")
        sys.exit(1)

    categories = {}
    total = 0

    for item in sorted(queries_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            cat_name = item.name
            queries = []

            for sql_file in sorted(item.glob("*.sql")):
                try:
                    content = sql_file.read_text(encoding='utf-8').strip()
                    camel_cols = detect_camel_columns(content)
                    table_refs = detect_table_refs(content)

                    queries.append({
                        "name": sql_file.stem,
                        "filename": sql_file.name,
                        "sql": content,
                        "camel_columns": camel_cols,
                        "snake_columns": {c: to_snake_case(c) for c in camel_cols},
                        "table_refs": table_refs
                    })
                    total += 1
                except Exception as e:
                    print(f"  WARNING: Could not read {sql_file}: {e}")

            if queries:
                categories[cat_name] = queries

    # Also check root level .sql files
    root_queries = []
    for sql_file in sorted(queries_dir.glob("*.sql")):
        try:
            content = sql_file.read_text(encoding='utf-8').strip()
            camel_cols = detect_camel_columns(content)
            table_refs = detect_table_refs(content)
            root_queries.append({
                "name": sql_file.stem,
                "filename": sql_file.name,
                "sql": content,
                "camel_columns": camel_cols,
                "snake_columns": {c: to_snake_case(c) for c in camel_cols},
                "table_refs": table_refs
            })
            total += 1
        except Exception as e:
            print(f"  WARNING: Could not read {sql_file}: {e}")

    if root_queries:
        categories["_uncategorized"] = root_queries

    print(f"Scanned {total} queries across {len(categories)} categories.")
    return categories


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_app_data.py /path/to/queries/folder")
        sys.exit(1)

    queries_path = sys.argv[1]
    output_path = Path(__file__).parent / "queries_data.js"

    data = scan_queries(queries_path)

    js_content = f"const QUERIES_DATA = {json.dumps(data, indent=2)};"

    output_path.write_text(js_content, encoding='utf-8')
    print(f"Generated: {output_path}")
    print(f"Now open index.html in a browser or deploy to GitHub Pages.")


if __name__ == "__main__":
    main()
