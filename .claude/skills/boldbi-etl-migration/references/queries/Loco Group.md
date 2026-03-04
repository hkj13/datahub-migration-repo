# Loco Group

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Loco Group Audit Checklists_Audit Checklist Report.sql

**Tables referenced:** checkpoint_master_sheet_table, with_audit_numbers

**Original Query:**

```sql
-- Data Source: Loco Group Audit Checklists
-- Dashboard: Audit Checklist Report
-- Category: Loco Group
-- Extracted: 2026-01-29 16:59:18
-- ============================================================

WITH with_audit_numbers AS
  (SELECT audit_main_theme,
          store_id,
          audit_submission_knid,
          audit_submission_number,
          audit_started_at,
          audit_submitted_at,
          auditor_name,
          theme,
          CHECKPOINT,
          checkpoint_knid,
          case when result_score is not null then result_score else null end AS result_score,
   case when max_score is not null then max_score else null end AS max_score,
   row_number() OVER (PARTITION BY audit_main_theme,
                                          store_id,
                                          theme,
                                          checkpoint_knid
                             ORDER BY audit_submitted_at) AS audit_number
   FROM checkpoint_master_sheet_table cmst
   WHERE organization_id = 'LOCO-GROUP-fireworks'
  and (audit_submitted_at AT TIME ZONE 'Asia/Singapore') BETWEEN (@{{:Date Range.START}}::TIMESTAMP AT TIME ZONE 'Asia/Singapore') AND ((@{{:Date Range.END}}::TIMESTAMP + interval '1 day') AT TIME ZONE 'Asia/Singapore'))
SELECT audit_main_theme AS "Audit Checklist",
       store_id AS "Store",
       audit_number AS "Audit #",
       audit_submission_number AS "Audit Submission Number",
       auditor_name AS "Auditor",
       to_timestamp(audit_started_at/1000) AT TIME ZONE 'Asia/Singapore' AS "Audit Started At",
                                                        audit_submitted_at AT TIME ZONE 'Asia/Singapore' AS "Audit Submitted At",
                                                                                        theme AS "Audit Area",
                                                                                        CHECKPOINT AS "Checkpoint",
                                                                                                      case when result_score = '' then null else result_score::numeric end AS "Result Score",
                                                                                                      case when result_score = '' then null else max_score::numeric end as "Max Score",
                                                                                                      audit_submission_knid AS "Audit Submission KNID",
                                                                                                      checkpoint_knid AS "Checkpoint KNID"
FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12,
         13
ORDER BY 1,
         2,
         3,
         8,
         9
```

---
