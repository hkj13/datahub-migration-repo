# SaladStop

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## SaladStop Who's On Leave Today_SaladStop CORP Staff Leaves.sql

**Tables referenced:** home, s, user_details

**Original Query:**

```sql
-- Data Source: SaladStop Who's On Leave Today
-- Dashboard: SaladStop CORP Staff Leaves
-- Category: SaladStop
-- Extracted: 2026-01-29 16:58:16
-- ============================================================

WITH s AS
  (SELECT DISTINCT ON (shift_id) *
   FROM "shifts_SaladStop-galaxy" s
   WHERE is_planning = 'false'
     AND leave_type_id IS NOT NULL
     AND location_id = 'CORP'
     AND is_leave_request = 'false'
     AND start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' > date_trunc('Month', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Singapore' - interval '1 month')
   ORDER BY shift_id,
            id DESC)
SELECT user_id,
       shift_id,
       ud.first_name||' ' ||ud.last_name AS "Staff Name",
       ud.department AS "Department",
       ud.designation AS "Designation",
       location_id AS "Location",
       (start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')::date AS "Leave Date",
       CASE
           WHEN half_day_leave_type IS NOT NULL THEN upper(half_day_leave_type) || ' Only'
           ELSE 'Full Day'
       END AS "Full Day or Half Day",
       CASE
           WHEN leave_type_id ILIKE '%travel%' THEN 'Travel'
           WHEN leave_type_id ILIKE '%work from home%' THEN 'WFH'
           ELSE 'On Leave'
       END AS "Absence Type"
FROM s
JOIN user_details ud ON s.user_id = ud.uuid
WHERE (is_deleted = 'false'
       OR is_deleted IS NULL)
```

---
