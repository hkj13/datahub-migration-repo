# BoldBI ETL Migration - Claude Code Skill

## Setup Instructions

### Step 1: Place the skill folder

Copy this entire `boldbi-etl-migration` folder to your Claude Code skills directory:

```bash
# Option A: Personal skill (just for you, works across all projects)
cp -r boldbi-etl-migration ~/.claude/skills/boldbi-etl-migration

# Option B: Project skill (shared with team via git)
cp -r boldbi-etl-migration /path/to/your/project/.claude/skills/boldbi-etl-migration
```

### Step 2: Run the setup script to index your SQL queries

This scans your queries folder and generates reference files inside the skill:

```bash
cd ~/.claude/skills/boldbi-etl-migration   # or your project skill path

python scripts/setup_skill.py /Users/hk/CascadeProjects/boldbi_datasources/queries
```

This will:
- Scan every subfolder (category) under `queries/`
- Read all `.sql` files
- Auto-detect camelCase columns that need snake_case conversion
- Generate `references/queries/{category}.md` for each folder
- Generate `references/query_index.md` as a master index

### Step 3: Restart Claude Code

```bash
# Just restart Claude Code and the skill is live
claude
```

### Step 4: Verify

Ask Claude Code:
```
What Skills are available?
```

Then try:
```
Help me migrate the {dashboard_name} dashboard to DataHub
```

---

## Re-running the setup script

Whenever you add new SQL queries or update existing ones, just re-run:

```bash
cd ~/.claude/skills/boldbi-etl-migration
python scripts/setup_skill.py /Users/hk/CascadeProjects/boldbi_datasources/queries
```

It will regenerate all reference files with the latest queries.

---

## Folder Structure After Setup

```
boldbi-etl-migration/
├── SKILL.md                          # Main instructions (Claude reads this first)
├── README.md                         # This file
├── references/
│   ├── migration_reference.md        # Troubleshooting, patterns, examples
│   ├── query_index.md                # Auto-generated master index
│   └── queries/                      # Auto-generated per-category query files
│       ├── category_a.md
│       ├── category_b.md
│       └── ...
├── templates/
│   └── pipeline_template.yml         # YML template for DataHub ingestion
└── scripts/
    └── setup_skill.py                # Run this to index your SQL queries
```

## How It Works When Someone Asks to Migrate

1. Claude reads `query_index.md` to find the right category
2. Claude reads `queries/{category}.md` to get the original SQL
3. Claude generates the migrated SQL (snake_case + new table refs)
4. Claude walks the user through the checklist: PREP > COPY > UPDATE > VALIDATE > APPLY > CLEANUP
5. Claude flags any red flags (skipping backup, editing original directly, etc.)
