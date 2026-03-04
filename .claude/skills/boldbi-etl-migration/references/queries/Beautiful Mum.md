# Beautiful Mum

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Beautiful Mum Attendance Performance_Employee Categorization.sql

**Tables referenced:** shift_attendance

**Original Query:**

```sql
-- Data Source: Beautiful Mum Attendance Performance
-- Dashboard: Employee Categorization
-- Category: Beautiful Mum
-- Extracted: 2026-01-29 16:58:22
-- ============================================================

SELECT "UUID",
       "Employee Name",
       "Employee ID",
       "Division",
       "Sub Division",
       "Home Location",
       "Department",
       "Designation",
       to_char(date_trunc('Month', "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'), 'YYYY-MM') AS "Month",
       sum("Scheduled Count") AS "Scheduled Shifts",
       sum("Present Count") AS "Present Shifts",
       sum("Late Count") AS "Late Shifts",
       sum("Leave Count") + sum("Scheduled Count") - sum("Present Count") AS "Leaves"
FROM shift_attendance
WHERE organization = 'beatifulmum-sunflower'
  AND "Shift ID" NOT ILIKE '%Off%'
  AND "Shift ID" NOT ILIKE '%PublicHoliday%'
  and "Scheduled Start Time" AT TIME ZONE 'UTC' < current_timestamp
  and "Employee Name" not ilike '%know%'
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
ORDER BY 4,
         5,
         6,
         2,
         9
```

---
