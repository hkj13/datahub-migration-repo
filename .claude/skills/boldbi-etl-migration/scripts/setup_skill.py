#!/usr/bin/env python3
"""
BoldBI ETL Migration Skill - Setup Script
==========================================
Scans your local SQL queries folder and generates reference files
for the Claude Code skill.

Usage:
    python scripts/setup_skill.py /path/to/queries/folder

Example:
    python scripts/setup_skill.py /Users/hk/CascadeProjects/boldbi_datasources/queries
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime


def to_snake_case(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case."""
    # Insert underscore before uppercase letters
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def extract_query_metadata(sql_content: str) -> dict:
    """Extract table names and column names from a SQL query."""
    tables = set()
    columns = set()

    # Find table references: schema.table or just table after FROM/JOIN
    table_pattern = re.compile(
        r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)',
        re.IGNORECASE
    )
    for match in table_pattern.finditer(sql_content):
        schema = match.group(1).rstrip('.') if match.group(1) else None
        table = match.group(2)
        if schema:
            tables.add(f"{schema}.{table}")
        else:
            tables.add(table)

    # Find camelCase column names (potential snake_case conversion needed)
    camel_pattern = re.compile(r'\b([a-z]+[A-Z][a-zA-Z]*)\b')
    for match in camel_pattern.finditer(sql_content):
        col = match.group(1)
        # Filter out SQL keywords and common words
        if col.lower() not in ('as', 'on', 'in', 'is', 'or', 'and', 'not',
                                'null', 'true', 'false', 'between', 'like',
                                'inner', 'outer', 'left', 'right', 'cross',
                                'natural', 'using', 'where', 'having',
                                'order', 'group', 'limit', 'offset',
                                'union', 'except', 'intersect', 'varchar',
                                'integer', 'boolean', 'timestamp', 'interval'):
            columns.add(col)

    return {
        'tables': sorted(tables),
        'camel_columns': sorted(columns),
        'snake_columns': sorted(set(to_snake_case(c) for c in columns))
    }


def generate_category_file(category_name: str, sql_files: list, output_path: Path):
    """Generate a markdown reference file for one category folder."""
    lines = []
    lines.append(f"# {category_name}\n")
    lines.append(f"> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append(f"**Total queries:** {len(sql_files)}\n")
    lines.append("---\n")

    for sql_file, sql_content in sql_files:
        filename = os.path.basename(sql_file)
        metadata = extract_query_metadata(sql_content)

        lines.append(f"## {filename}\n")

        if metadata['tables']:
            lines.append(f"**Tables referenced:** {', '.join(metadata['tables'])}\n")

        if metadata['camel_columns']:
            lines.append("**Columns needing snake_case conversion:**\n")
            for col in metadata['camel_columns']:
                lines.append(f"- `{col}` -> `{to_snake_case(col)}` (alias: `{to_snake_case(col)} AS \"{col}\"`)\n")
            lines.append("")

        lines.append("**Original Query:**\n")
        lines.append("```sql")
        lines.append(sql_content.strip())
        lines.append("```\n")
        lines.append("---\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Created: {output_path}")


def generate_index(categories: dict, output_path: Path):
    """Generate master index of all queries by category."""
    lines = []
    lines.append("# Dashboard Queries Index\n")
    lines.append(f"> Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    total_queries = sum(len(files) for files in categories.values())
    lines.append(f"**Total categories:** {len(categories)}  ")
    lines.append(f"**Total queries:** {total_queries}\n")
    lines.append("---\n")

    # Summary table
    lines.append("| Category | Query Count | Queries |")
    lines.append("|----------|-------------|---------|")
    for cat_name, sql_files in sorted(categories.items()):
        query_names = ', '.join(os.path.basename(f) for f, _ in sql_files)
        lines.append(f"| [{cat_name}](queries/{cat_name}.md) | {len(sql_files)} | {query_names} |")

    lines.append("\n---\n")

    # Quick lookup: all table references across all queries
    lines.append("## All Table References\n")
    lines.append("| Table | Found In |")
    lines.append("|-------|----------|")

    table_map = {}  # table -> list of (category, filename)
    for cat_name, sql_files in categories.items():
        for sql_file, sql_content in sql_files:
            metadata = extract_query_metadata(sql_content)
            for table in metadata['tables']:
                if table not in table_map:
                    table_map[table] = []
                table_map[table].append(f"{cat_name}/{os.path.basename(sql_file)}")

    for table, locations in sorted(table_map.items()):
        lines.append(f"| `{table}` | {', '.join(locations)} |")

    lines.append("\n---\n")

    # Quick lookup: all camelCase columns needing conversion
    lines.append("## All Columns Needing snake_case Conversion\n")
    lines.append("| Original | snake_case | Found In |")
    lines.append("|----------|------------|----------|")

    col_map = {}  # camelCol -> list of locations
    for cat_name, sql_files in categories.items():
        for sql_file, sql_content in sql_files:
            metadata = extract_query_metadata(sql_content)
            for col in metadata['camel_columns']:
                if col not in col_map:
                    col_map[col] = []
                col_map[col].append(f"{cat_name}/{os.path.basename(sql_file)}")

    for col, locations in sorted(col_map.items()):
        lines.append(f"| `{col}` | `{to_snake_case(col)}` | {', '.join(set(locations))} |")

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Created: {output_path}")


def scan_queries_folder(queries_path: str, skill_path: str):
    """Main function: scan queries folder and generate all reference files."""
    queries_dir = Path(queries_path)
    skill_dir = Path(skill_path)
    ref_queries_dir = skill_dir / "references" / "queries"

    if not queries_dir.exists():
        print(f"ERROR: Queries folder not found: {queries_dir}")
        sys.exit(1)

    print(f"\nScanning: {queries_dir}")
    print(f"Output:   {ref_queries_dir}\n")

    # Clean old generated query references
    if ref_queries_dir.exists():
        for f in ref_queries_dir.glob("*.md"):
            f.unlink()

    categories = {}

    # Walk through category folders
    for item in sorted(queries_dir.iterdir()):
        if item.is_dir() and not item.name.startswith('.'):
            cat_name = item.name
            sql_files = []

            for sql_file in sorted(item.glob("*.sql")):
                try:
                    content = sql_file.read_text(encoding='utf-8')
                    sql_files.append((str(sql_file), content))
                except Exception as e:
                    print(f"  WARNING: Could not read {sql_file}: {e}")

            if sql_files:
                categories[cat_name] = sql_files
                generate_category_file(
                    cat_name,
                    sql_files,
                    ref_queries_dir / f"{cat_name}.md"
                )
            else:
                print(f"  Skipped (no .sql files): {cat_name}/")

    # Also check for .sql files directly in the root (not in subfolders)
    root_sql = []
    for sql_file in sorted(queries_dir.glob("*.sql")):
        try:
            content = sql_file.read_text(encoding='utf-8')
            root_sql.append((str(sql_file), content))
        except Exception as e:
            print(f"  WARNING: Could not read {sql_file}: {e}")

    if root_sql:
        categories["_root"] = root_sql
        generate_category_file(
            "_root (uncategorized)",
            root_sql,
            ref_queries_dir / "_root.md"
        )

    if not categories:
        print("ERROR: No .sql files found in any subfolder.")
        sys.exit(1)

    # Generate master index
    generate_index(categories, skill_dir / "references" / "query_index.md")

    print(f"\nDone! {sum(len(f) for f in categories.values())} queries indexed across {len(categories)} categories.")
    print(f"\nNext steps:")
    print(f"  1. Review the generated files in {ref_queries_dir}")
    print(f"  2. Copy the skill folder to your Claude Code skills directory:")
    print(f"     cp -r {skill_dir} ~/.claude/skills/boldbi-etl-migration")
    print(f"  3. Restart Claude Code")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/setup_skill.py /path/to/queries/folder")
        print("Example: python scripts/setup_skill.py /Users/hk/CascadeProjects/boldbi_datasources/queries")
        sys.exit(1)

    queries_folder = sys.argv[1]
    # Skill root is one level up from scripts/
    skill_root = str(Path(__file__).parent.parent)
    scan_queries_folder(queries_folder, skill_root)
