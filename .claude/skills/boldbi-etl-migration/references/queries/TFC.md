# TFC

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## TFC Audit Checklist_Audit Checklist Report.sql

**Tables referenced:** Entrance, checkpoint_master_sheet_table, scores, theme_weights, with_audit_numbers

**Original Query:**

```sql
-- Data Source: TFC Audit Checklist
-- Dashboard: Audit Checklist Report
-- Category: TFC
-- Extracted: 2026-01-29 16:59:19
-- ============================================================

WITH theme_weights AS
  (SELECT 'Customer experience- In Dining & Online' AS theme,
          0.1 AS weight
   UNION SELECT '5 S Checklist - Coverage from Entrance ,Live Kitchens ,Storage areas & Processing areas',
                0.05
   UNION SELECT 'Visual Management-Walking Talking ( Quality ,Delivery, Safety )',
                0.05
   UNION SELECT 'GMP',
                0.15
   UNION SELECT 'Hygiene & Sanitation-Coverage from Entrance ,Live Kitchens ,Storage areas, Wash rooms /Washing areas & Processing areas',
                0.15
   UNION SELECT 'Facility and Equipment Check Coverage -'||'- Furniture Fixtures, Utilities , Processing eqts',
                0.07
   UNION SELECT 'Inventory Management -covers all Fresh products, IP and finished items & Expired food and food disposal Management',
                0.05
   UNION SELECT 'Quality Processes at Incoming',
                0.05
   UNION SELECT 'A. Legal & Statutory',
                0.1
   UNION SELECT 'B. Environment, Health & Safety Practices',
                0.03
   UNION SELECT 'Training & Development',
                0.1
   UNION SELECT 'Management review , FSMS Programme and its implementation',
                0.1),
     scores AS
  (SELECT audit_main_theme,
          store_id,
          audit_submission_knid,
          audit_submission_number,
          audit_started_at,
          audit_submitted_at,
          auditor_name,
          CASE
              WHEN theme IN ('EMPLOYEE HYGIENE',
                             'FOOD, UTENSILS AND EQUIPMENT HANDLING',
                             'PEST CONTROL',
                             'Entrance section',
                             'Coffee and parotta section',
                             'Sweet & Savoury counter',
                             'Beverage counter',
                             'Dosa counter',
                             'IDLI counter',
                             'Store room',
                             'Refrigerator',
                             'Pot wash area',
                             'Grinding section',
                             'Delivery counter',
                             'Utility section',
                             'Rest Rooms',
                             'GARBAGE DISPOSAL AREA',
                             'RECORDS') THEN 'GMP'
              ELSE theme
          END AS theme,
          CHECKPOINT,
          checkpoint_knid,
          sum(result_score::numeric) AS score
   FROM checkpoint_master_sheet_table cmst
   WHERE audit_main_theme = 'TFC Audit Checklist  - Final'
     AND organization_id = 'The-Filter-Coffee-cartwheel'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10),
     with_audit_numbers AS
  (SELECT audit_main_theme,
          store_id,
          audit_submission_knid,
          audit_submission_number,
          audit_started_at,
          audit_submitted_at,
          auditor_name,
          scores.theme,
          scores.checkpoint,
          scores.checkpoint_knid,
          scores.score,
          scores.score*tw.weight AS weighted_score,
          row_number() OVER (PARTITION BY scores.audit_main_theme,
                                          scores.store_id,
                                          scores.theme,
                                          scores.checkpoint_knid
                             ORDER BY scores.audit_submitted_at) AS audit_number
   FROM scores
   JOIN theme_weights tw ON scores.theme = tw.theme)
SELECT audit_main_theme AS "Audit Checklist",
       store_id AS "Store",
       audit_number AS "Audit #",
       audit_submission_number AS "Audit Submission Number",
       auditor_name AS "Auditor",
       to_timestamp(audit_started_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Audit Started At",
                                                        audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                                                                        theme AS "Audit Area",
                                                                                        CHECKPOINT AS "Checkpoint",
                                                                                                      score AS "Audit Score",
                                                                                                      weighted_score AS "Weighted Score",
                                                                                                      audit_submission_knid AS "Audit Submission KNID",
                                                                                                      checkpoint_knid AS "Checkpoint KNID"
FROM with_audit_numbers
WHERE (audit_submitted_at AT TIME ZONE 'Asia/Kolkata') BETWEEN (@{{:Date Range.START}}::TIMESTAMP AT TIME ZONE 'Asia/Kolkata') AND ((@{{:Date Range.END}}::TIMESTAMP + interval '1 day') AT TIME ZONE 'Asia/Kolkata')
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
HAVING audit_number >= max(audit_number) -3
ORDER BY 1,
         2,
         3 DESC,
         8,
         9
```

---
