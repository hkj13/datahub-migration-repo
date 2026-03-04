# BoldBI ETL Migration - Detailed Reference

This file contains the full troubleshooting tables, query transformation examples, common patterns, and execution flow for the BoldBI to DataHub migration.

---

## Full Query Transformation Example

**BEFORE (direct database connection):**
```sql
SELECT u.firstName, u.lastName, l.locationName
FROM public.users u
JOIN public.locations l ON u.locationId = l.id
WHERE u.isActive = true
```

**AFTER (DataHub connection):**
```sql
SELECT 
    u.first_name AS "firstName", 
    u.last_name AS "lastName", 
    l.location_name AS "locationName"
FROM antenna_public.users u
JOIN antenna_public.locations l ON u.location_id = l.id
WHERE u.is_active = true
```

Key changes:
1. Table references: `public.X` became `antenna_public.X`
2. Column names: `camelCase` became `snake_case`
3. Aliases: `AS "originalName"` preserves dashboard widget bindings
4. Join conditions: column names in ON clauses also need snake_case conversion

---

## Common Patterns Reference

| Type | Old Pattern | New Pattern |
|------|-------------|-------------|
| Public tables | `public.{table}` | `{db}_public.{table}` |
| Data team tables | `data_team.{table}` | `{db}_data_team.{table}` |
| Column names | `firstName` | `first_name AS "firstName"` |
| Joins | `ON a.userId = b.id` | `ON a.user_id = b.id` |

---

## Troubleshooting

### Phase 1 (YML Pipeline) Errors

| Error | Cause | Fix |
|-------|-------|-----|
| YAML syntax error | Wrong indentation | Use 2 spaces, not tabs |
| Connection refused | Cannot reach database | Check credentials, contact Engineering |
| Schema not found | Wrong schema name | Verify exact schema name in source DB |
| Permission denied | No access | Request read access from DBA |

### Phase 2-3 (Dashboard Migration) Errors

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| No data returned | Table name wrong | Check table exists in DataHub |
| Column not found | Not using snake_case | Check exact column name in DataHub |
| Numbers don't match | Query logic changed | Compare queries line by line |
| Filter broken | Using old column name | Update filter to snake_case |
| Permission error | User access issue | Check DataHub permissions |
| Widget missing data | Datasource not updated | Verify all datasources were migrated |

---

## Execution Flow

```
START MIGRATION
      |
      v
PHASE 1: YML PIPELINE
  - Create YML file
  - Upload to DataHub
  - Verify tables extracted
      |
      v
PHASE 2: PREP
  - Open original dashboard
  - Export reference data
  - Create TEST copy
      |
      v
PHASE 3: UPDATE TEST COPY
  - Back up each query
  - Update table references
  - Update column names to snake_case
  - Test each datasource
      |
      v
PHASE 4: VALIDATE
  - Compare data with reference
  - Test all filters
  - Confirm widget count matches
      |
      v
  Valid? --No--> Debug, return to UPDATE
      |
     Yes
      |
      v
PHASE 5: APPLY TO ORIGINAL
  - Copy queries to original
  - Save original dashboard
  - Delete TEST copy
  - Update tracker
      |
      v
   COMPLETE
```

---

## Red Flags to Watch For

These situations should trigger an immediate warning to the user:

1. **Editing the original dashboard directly** without creating a test copy first. Stop the user and insist on the test copy workflow.
2. **Skipping the backup step.** Every query must be copied to a text file before editing.
3. **Skipping validation.** The test copy must be compared against original data before applying changes.
4. **Significant data mismatches** (more than 1% difference). This indicates a query logic error that must be investigated.
5. **Creating a new dashboard instead of updating the original.** This breaks user access permissions tied to the dashboard ID.
