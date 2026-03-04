---
name: boldbi-etl-migration
description: "Migrate BoldBI dashboard datasource queries from direct database connections to a DataHub central warehouse. Use this skill whenever the user mentions BoldBI migration, DataHub ETL, YML pipeline setup, dashboard query migration, converting SQL queries to snake_case for DataHub, updating table references from schema.table to database_schema.table, or validating migrated dashboards. Also trigger when the user asks to migrate a specific dashboard by name or category, wants to see original vs migrated queries side by side, needs a migration checklist, or asks about YML pipeline configuration. This skill contains a full index of existing dashboard SQL queries organized by category."
---

# BoldBI ETL Migration Skill

Guides users through migrating BoldBI dashboard datasource queries from direct database connections to a DataHub central data warehouse. Contains indexed copies of all existing SQL queries for quick lookup and transformation.

## How This Skill Works

1. User says which dashboard or category they want to migrate.
2. You look up the original queries from `references/queries/{category}.md`.
3. You generate the migrated query (snake_case columns, updated table refs).
4. You provide a step-by-step checklist the user follows in BoldBI.
5. You guide validation before applying to the original dashboard.

## File Structure

```
references/
  query_index.md           <- Master index: all queries by category
  queries/{category}.md    <- Original SQL queries per category
  migration_reference.md   <- Troubleshooting, patterns, flow diagram
templates/
  pipeline_template.yml    <- YML template for DataHub ingestion
```

---

## Step 1: Identify What to Migrate

When the user wants to migrate a dashboard:

1. Read `references/query_index.md` to find the relevant category and queries.
2. Read the specific `references/queries/{category}.md` file to get the original SQL.
3. Confirm with the user: "I found N queries under {category}. Ready to proceed?"

If the user gives a dashboard name that does not match a category, search across all category files.

---

## Step 2: Generate Migrated Queries

For each SQL query, apply these transformations:

### Table References
```
BEFORE: {schema}.{table}
AFTER:  {database}_{schema}.{table}

Example:
  public.users         -> antenna_public.users
  data_team.user_flat  -> antenna_data_team.user_flat
```

Ask the user for the database name if not obvious from context.

### Column Names (CRITICAL)
DataHub converts ALL column names to snake_case. Every camelCase column must be converted AND aliased to preserve dashboard widget bindings:

```sql
-- BEFORE
SELECT u.firstName, u.lastName, u.createdAt
FROM public.users u

-- AFTER
SELECT
    u.first_name AS "firstName",
    u.last_name AS "lastName",
    u.created_at AS "createdAt"
FROM antenna_public.users u
```

This applies everywhere: SELECT, WHERE, JOIN ON, ORDER BY, GROUP BY, HAVING.

### Conversion Rules
- `camelCase` -> `camel_case` (e.g., `firstName` -> `first_name`)
- Consecutive capitals: `userID` -> `user_id`, `slaID` -> `sla_id`
- Already snake_case: leave unchanged
- In SELECT: add `AS "originalName"` alias
- In WHERE/JOIN/ORDER BY: just use snake_case (no alias needed)

### Present to User
Show the original and migrated query side by side so the user can verify before applying. Format:

```
DASHBOARD: {name}
DATASOURCE: {filename}
DATABASE: {db_name}

--- ORIGINAL ---
{original SQL}

--- MIGRATED ---
{migrated SQL}

CHANGES MADE:
- Table: public.X -> {db}_public.X (list each)
- Column: camelCase -> snake_case AS "camelCase" (list each)
```

---

## Step 3: YML Pipeline (if not already done)

If the database has not been ingested into DataHub yet, guide the user through YML setup.

1. Read `templates/pipeline_template.yml` and show a filled-in version.
2. Walk through the upload: DataHub UI > Ingestion > Sources > Create > File Upload > Run Now.
3. Verify: Datasets > search schema name > confirm tables visible.

### Separate YMLs per schema
If a database has multiple schemas (e.g., `public` and `data_team`), create one YML per schema:
- `{db}_public.yml` with `schema: "public"`, `destination_schema: "{db}_public"`
- `{db}_data_team.yml` with `schema: "data_team"`, `destination_schema: "{db}_data_team"`

### Troubleshooting
| Error | Fix |
|-------|-----|
| YAML syntax error | Use 2 spaces, not tabs |
| Connection refused | Check credentials in db_credentials.yml |
| Schema not found | Verify exact schema name in source DB |
| Permission denied | Request read access from DBA |

---

## Step 4: Migration Checklist

Present this checklist to the user. Walk through one step at a time. Do not skip steps.

### PREP
- [ ] Open original dashboard in BoldBI. Confirm it loads.
- [ ] Note dashboard name and folder location.
- [ ] Count total widgets: ____
- [ ] Export data from 2-3 key widgets (screenshot or Excel). Save as reference.

### COPY (never edit the original first)
- [ ] Click More Options (three dots) > Save As
- [ ] Name: "[ORIGINAL NAME] - TEST MIGRATION"
- [ ] Open TEST copy in edit mode

### UPDATE (on TEST copy only)
For each datasource:
- [ ] Click datasource in Data Sources panel
- [ ] Click "Edit Data Source" to see the query
- [ ] **BACKUP: Copy entire query to a text file** (do this for EVERY datasource)
- [ ] Paste the migrated query (from Step 2)
- [ ] Click Run/Preview. Confirm data appears.
- [ ] Save datasource
- [ ] Repeat for ALL datasources

### VALIDATE
- [ ] Save TEST dashboard. Exit edit mode. Reopen.
- [ ] Data loads without errors
- [ ] Widget count matches original: ____
- [ ] Numbers match exported reference data (within 1% tolerance)
- [ ] All filters and parameters work correctly

**If validation fails:** STOP. Debug the issue. Return to UPDATE. Do NOT proceed to APPLY.

### APPLY (only after validation passes)
- [ ] Open ORIGINAL dashboard in edit mode
- [ ] For each datasource: copy query from TEST copy, paste into ORIGINAL
- [ ] Test and save each datasource
- [ ] Save ORIGINAL dashboard. Test end-to-end.
- [ ] **Dashboard ID unchanged = user access permissions preserved**

### CLEANUP
- [ ] Delete TEST MIGRATION copy
- [ ] Update migration tracker: mark as MIGRATED

---

## Critical Rules

1. **NEVER edit the original dashboard directly.** Always create a TEST copy first.
2. **NEVER change the dashboard ID.** Update the original, do not replace it.
3. **ALWAYS backup queries** before editing any datasource.
4. **NEVER skip validation.** Compare data before applying to original.
5. **ALWAYS alias snake_case columns** back to camelCase in SELECT to preserve widget bindings.

---

## Red Flags (stop the user immediately)

- User wants to edit the original dashboard without a test copy
- User skipping the backup step
- User skipping validation
- Data numbers differ by more than 1% after migration
- User creating a new dashboard instead of updating the original

---

## For detailed troubleshooting, query examples, and execution flow diagram

Read `references/migration_reference.md`.
