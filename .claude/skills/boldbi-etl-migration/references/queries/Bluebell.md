# Bluebell

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Bluebell - Shift Hours Dashboard_Bluebell - Shift Hours Dashboard.sql

**Tables referenced:** base, location_totals, shift_attendance, shift_data, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Bluebell - Shift Hours Dashboard
-- Dashboard: Bluebell - Shift Hours Dashboard
-- Category: Bluebell
-- Extracted: 2026-01-29 16:52:57
-- ============================================================

WITH user_acl AS (
    SELECT uuid, organization
    FROM user_details
    WHERE organization = @{{:OrganizationParameter}}
      AND (
            (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
            OR 
            uuid IN (
                SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN (
                    SELECT group_id
                    FROM user_groups ug2
                    WHERE ug2.user_id = @{{:UuidParameter}}
                      AND ug2.has_access = TRUE
                )
                AND ug1.is_active = TRUE
            )
      )
      AND email NOT ILIKE '%@knownuggets.com'
),
shift_data AS (
    SELECT 
        sa."UUID",
        sa."Employee Name",
        sa."Employee ID",
        sa."Shift Location",
        sa."Home Location",
        sa."Designation",
        sa."Job Type",
        sa."Division",
        sa."Department",
        (sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')::date AS shift_date_only,
        COALESCE(sa."Actual Work Duration", 0) AS work_hours,
        sa."Status",
        GREATEST(0, 
            EXTRACT(EPOCH FROM (sa."Scheduled Start Time" AT TIME ZONE 'UTC' - sa."Actual Clockin Time")) / 3600.0
        ) AS early_ot_hours,
        CASE 
            WHEN sa."Actual Clockout Time" <= sa."Scheduled End Time" AT TIME ZONE 'UTC' + interval '24 hours'
            THEN GREATEST(0,
                EXTRACT(EPOCH FROM (sa."Actual Clockout Time" - sa."Scheduled End Time" AT TIME ZONE 'UTC')) / 3600.0
            )
            ELSE 0
        END AS late_ot_hours
    FROM shift_attendance sa
    JOIN user_acl ON sa."UUID" = user_acl.uuid
    WHERE sa.organization = @{{:OrganizationParameter}}
      AND sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' 
          BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
      AND sa."Status" IN ('Present - On Time', 'Present - Late')
      AND sa."Actual Clockin Time" IS NOT NULL
      AND sa."Actual Clockout Time" IS NOT NULL
),
base AS (
    SELECT 
        sd."Shift Location" AS "Location",
        sd."Employee Name",
        sd."Employee ID",
        sd."Designation",
        sd."Job Type",
        sd."Division",
        sd."Home Location",
        CASE WHEN sd."Home Location" = sd."Shift Location" THEN 'Yes' ELSE 'No' END AS "Is Home Location",
        CASE WHEN sd."Home Location" = sd."Shift Location" THEN 'Same Location' ELSE 'Other Location' END AS "Assignment Type",
        to_char(sd.shift_date_only, 'DD/MM/YYYY') AS "Date",
        ROUND(SUM(sd.work_hours)::numeric, 2) AS "Total Work Hours",
        ROUND(SUM(sd.early_ot_hours)::numeric, 2) AS "Early OT Hours",
        ROUND(SUM(sd.late_ot_hours)::numeric, 2) AS "Late OT Hours",
        ROUND(SUM(sd.early_ot_hours + sd.late_ot_hours)::numeric, 2) AS "Daily OT Hours"
    FROM shift_data sd
    GROUP BY 
        sd."Shift Location", 
        sd."Employee Name", 
        sd."Employee ID", 
        sd."Designation", 
        sd."Job Type",
        sd."Division",
        sd."Home Location",
        sd.shift_date_only
),
location_totals AS (
    SELECT
        "Location",
        ROUND(SUM("Total Work Hours")::numeric, 2) AS "Location Total Work Hours",
        ROUND(SUM("Daily OT Hours")::numeric, 2) AS "Location Total OT Hours"
    FROM base
    GROUP BY "Location"
)
SELECT
    b."Location",
    b."Employee Name",
    b."Employee ID",
    b."Designation",
    b."Job Type",
    b."Division",
    b."Home Location",
    b."Is Home Location",
    b."Assignment Type",
    b."Date",
    b."Total Work Hours",
    b."Early OT Hours",
    b."Late OT Hours",
    b."Daily OT Hours",
    lt."Location Total Work Hours",
    lt."Location Total OT Hours"
FROM base b
JOIN location_totals lt
  ON b."Location" = lt."Location"
ORDER BY b."Location", b."Total Work Hours" DESC
```

---
