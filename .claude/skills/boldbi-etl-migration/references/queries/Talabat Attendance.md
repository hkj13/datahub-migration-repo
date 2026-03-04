# Talabat Attendance

> Auto-generated on 2026-03-04 08:13

**Total queries:** 9

---

## Key Arabia Dashboard new_Key Arabia - Roster Dashboard.sql

**Tables referenced:** LATERAL, base, fci_edit, first_clock_in, last_clock_out, lco_edit, shift_attendance, time_events_clockin, time_events_clockout

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: Key Arabia Dashboard new
-- Dashboard: Key Arabia - Roster Dashboard
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:27
-- ============================================================

WITH base AS (
  SELECT 
    "Shift ID",
    "Shift Name",
    InitCap(CASE
      WHEN "Status" = 'On Leave'
      THEN substring("Shift ID", 11 + length("Shift Location"), 
                     length("Shift ID") - length("UUID") - length("Shift Location")-11)
      ELSE NULL
    END) AS "Leave Tags",
    "UUID",
    "Employee Name",
    "Employee ID" AS "Talabat ID",
    "Designation" AS "User Type",
    "Department",
    CASE
      WHEN "Job Type" ILIKE '%3PL' THEN '3PL'
      ELSE 'Talabat'
    END AS "Picker Type",
    CASE
      WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
      WHEN "Job Type" ILIKE '%- 3PL' THEN rtrim("Job Type", '- 3PL')
      ELSE 'Others'
    END AS "Agency",
    "Division" AS "Country",
    "Sub Division" AS "Chain",
    branch.branch_id AS "Shift Branch ID",
    branch.branch_name AS "Shift Branch Name",
    "Shift Location",
    "Clockin Geofence" AS "Clockin Location",
    "Clockout Geofence" AS "Clockout Location",
    "Status",
    CASE
      WHEN "Division" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
      THEN "Scheduled Start Time" + interval '3 hours'
      ELSE "Scheduled Start Time" + interval '4 hours'
    END AS "Scheduled Start Time",
    CASE
      WHEN "Division" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
      THEN "Scheduled End Time" + interval '3 hours'
      ELSE "Scheduled End Time" + interval '4 hours'
    END AS "Scheduled End Time",
    "Scheduled Break Hours",
    CASE
      WHEN "Status" != 'On Leave' 
      THEN ((extract(epoch FROM "Scheduled End Time"))::numeric - 
            (extract(epoch FROM "Scheduled Start Time"))::numeric)/3600
      ELSE 0
    END AS "Scheduled Hours incl Break",
    CASE
      WHEN "Status" != 'On Leave' 
      THEN ((extract(epoch FROM "Scheduled End Time"))::numeric - 
            (extract(epoch FROM "Scheduled Start Time"))::numeric)/3600 - "Scheduled Break Hours"
      ELSE 0
    END AS "Scheduled Hours excl Break",
    CASE
      WHEN "Division" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
      THEN "Actual Clockin Time" + interval '3 hours'
      ELSE "Actual Clockin Time" + interval '4 hours'
    END AS "Actual Clockin Time",
    CASE
      WHEN "Division" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
      THEN "Actual Clockout Time" + interval '3 hours'
      ELSE "Actual Clockout Time" + interval '4 hours'
    END AS "Actual Clockout Time",
    "Actual Break Hours",
    "Actual Work Duration",
    CASE
      WHEN "Actual Clockin Time" IS NOT NULL
           AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' 
      THEN ((extract(epoch FROM "Actual Clockin Time"))::numeric - 
            (extract(epoch FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/60
      ELSE 0
    END AS "Late Mins",
    CASE
      WHEN "Actual Clockin Time" IS NOT NULL
           AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' 
      THEN ceiling(((extract(epoch FROM "Actual Clockin Time"))::numeric - 
                    (extract(epoch FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/3600)
      ELSE 0
    END AS "Late Hours",
    CASE
      WHEN "Actual Clockout Time" IS NOT NULL
           AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins' 
      THEN ceiling(((extract(epoch FROM "Scheduled End Time" - interval '15 mins'))::numeric - 
                    (extract(epoch FROM "Actual Clockout Time"))::numeric)/3600)
      ELSE 0
    END AS "Early Clockout Hours",
    "Scheduled Count",
    "Leave Count",
    "Present Count",
    "Absent Count"
  FROM shift_attendance sa
  LEFT JOIN LATERAL (
    SELECT 
      (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
      regexp_replace(sa."Shift Location", '^\d+\s*-\s*(.*)', '\1') AS branch_name
    WHERE sa."Shift Location" ~ '^\d+' 
  ) branch ON TRUE
  WHERE organization = 'talabat-cartwheel'
    AND "Scheduled Start Time" + interval '3 hours' 
        BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
    AND sa."Shift Location" ~ '^\d+'
    AND "Department" = 'Key Arabia'  -- MOVED HERE: Filter early!
),
-- OPTIMIZATION: Only get clock-in events for shifts in base (456 vs 14K+)
first_clock_in AS (
  SELECT DISTINCT ON (tec.shift_id, tec.uuid) 
    tec.shift_id,
    tec.uuid,
    tec.selfie,
    tec.details
  FROM base b
  INNER JOIN time_events_clockin tec ON b."Shift ID" = tec.shift_id AND b."UUID" = tec.uuid
  ORDER BY tec.shift_id, tec.uuid, tec.ci_time
),
fci_edit AS (
  SELECT 
    fci.shift_id,
    fci.uuid,
    to_timestamp((fci.details->>'editedAt')::bigint/1000) AS edited_at,
    fci.details->>'editedByUsername' AS edited_by,
    to_timestamp((fci.details->>'originalDeviceTime')::bigint/1000) AS original_ci_time
  FROM first_clock_in fci
  WHERE fci.details->>'isEdited' = 'true'
),
-- OPTIMIZATION: Only get clock-out events for shifts in base
last_clock_out AS (
  SELECT DISTINCT ON (tec.shift_id, tec.uuid) 
    tec.shift_id,
    tec.uuid,
    tec.details
  FROM base b
  INNER JOIN time_events_clockout tec ON b."Shift ID" = tec.shift_id AND b."UUID" = tec.uuid
  ORDER BY tec.shift_id, tec.uuid, tec.co_time DESC
),
lco_edit AS (
  SELECT 
    lco.shift_id,
    lco.uuid,
    to_timestamp((lco.details->>'editedAt')::bigint/1000) AS edited_at,
    lco.details->>'editedByUsername' AS edited_by,
    to_timestamp((lco.details->>'originalDeviceTime')::bigint/1000) AS original_co_time
  FROM last_clock_out lco
  WHERE lco.details->>'isEdited' = 'true'
)
SELECT 
  base.*, 
  Coalesce("Shift Name", "Leave Tags") as "Shift",
  CASE
    WHEN "Status" IN ('On Leave', 'Absent') THEN "Status"
    WHEN "Late Mins" > 0 THEN 'Present - Late'
    ELSE 'Present - On Time'
  END AS "Modified Status",
  CASE
    WHEN (fci.selfie ILIKE '%Photofailed%' or fci.selfie is null) THEN 'No Selfie Image'
    ELSE 'Selfie Available'
  END AS "Selfie Status",
  fci.selfie as "Selfie Image Link",
  CASE
    WHEN "Actual Work Duration" > 0
         AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
         AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' 
    THEN ceiling("Actual Work Duration" - "Scheduled Hours excl Break" - (1/6))
    ELSE 0
  END AS "Overtime Hours",
  CASE
    WHEN "Actual Work Duration" > 0
         AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
         AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' 
    THEN 1
    ELSE 0
  END AS "Overtime Count",
  CASE
    WHEN "Actual Work Duration" > 0
         AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) 
    THEN ceiling("Scheduled Hours excl Break" - "Actual Work Duration" - (1/6))
    ELSE 0
  END AS "Undertime Hours",
  CASE
    WHEN "Actual Work Duration" > 0
         AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) 
    THEN 1
    ELSE 0
  END AS "Undertime Count",
  CASE
    WHEN "Late Hours" > 0 THEN 1
    ELSE 0
  END AS "Late Count",
  CASE
    WHEN "Early Clockout Hours" > 0 THEN 1
    ELSE 0
  END AS "Early Clockout Count",
  CASE
    WHEN "Country" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
    THEN fci_edit.edited_at + interval '3 hours'
    ELSE fci_edit.edited_at + interval '4 hours'
  END AS "First CI Edited At",
  fci_edit.edited_by AS "First CI Edited By",
  CASE
    WHEN "Country" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
    THEN fci_edit.original_ci_time + interval '3 hours'
    ELSE fci_edit.original_ci_time + interval '4 hours'
  END AS "Original First CI",
  CASE
    WHEN "Country" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
    THEN lco_edit.edited_at + interval '3 hours'
    ELSE lco_edit.edited_at + interval '4 hours'
  END AS "Last CO Edited At",
  lco_edit.edited_by AS "Last CO Edited By",
  CASE
    WHEN "Country" IN ('Qatar', 'Kuwait', 'Egypt', 'Bahrain', 'Oman', 'Jordan') 
    THEN lco_edit.original_co_time + interval '3 hours'
    ELSE lco_edit.original_co_time + interval '4 hours'
  END AS "Original Last CO",
  case when base."Clockin Location" != base."Clockout Location" then 'Different' else 'Same' end as "CI-CO Same Location?"
FROM base
LEFT OUTER JOIN first_clock_in fci 
  ON base."Shift ID" = fci.shift_id AND base."UUID" = fci.uuid
LEFT OUTER JOIN fci_edit 
  ON base."Shift ID" = fci_edit.shift_id AND base."UUID" = fci_edit.uuid
LEFT OUTER JOIN lco_edit 
  ON base."Shift ID" = lco_edit.shift_id AND base."UUID" = lco_edit.uuid
ORDER BY 10, 11, 12, 19, 9, 4
```

---

## Key Arabia Weekly shifts report_Key Arabia - Roster Dashboard.sql

**Tables referenced:** params, per_day, pivot_base, shift_attendance, shifts, users_in_week, week_dates, weekly_totals

**Original Query:**

```sql
-- Data Source: Key Arabia Weekly shifts report
-- Dashboard: Key Arabia - Roster Dashboard
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:27
-- ============================================================

WITH params AS (
    SELECT
        (date_trunc('week', CURRENT_DATE)::date + 7) AS week_monday,  -- next Monday
        (date_trunc('week', CURRENT_DATE)::date + 13) AS week_sunday  -- next Sunday
),
week_dates AS (
    SELECT g::date AS shift_date
    FROM params p,
         generate_series(p.week_monday, p.week_sunday, interval '1 day') g
),
shifts AS (
    SELECT
        s."Employee ID" AS employee_id,
        s."Employee Name" AS name,
        s."Shift Name" AS shift_name,
        s."Scheduled Start Time" AS start_time,
        s."Scheduled End Time" AS end_time,
        s."Shift Location" AS shift_location,
        COALESCE(NULLIF(s."Scheduled Break Hours",0),1) AS break_hours, -- default 1 if null or 0
        s."Scheduled Start Time"::date AS shift_date,
        (EXTRACT(epoch FROM (s."Scheduled End Time" - s."Scheduled Start Time"))/60)::int AS minutes,
        ROW_NUMBER() OVER (PARTITION BY s."Employee ID", s."Scheduled Start Time"::date ORDER BY s."Scheduled Start Time") AS shift_num
    FROM shift_attendance s
    JOIN params p ON TRUE
    WHERE s."Department" = 'Key Arabia'
      AND s."Scheduled Start Time"::date BETWEEN p.week_monday AND p.week_sunday
),
per_day AS (
    SELECT
        employee_id,
        name,
        shift_date,
        STRING_AGG(
            shift_name || E'\n' ||
            TO_CHAR(start_time, 'HH12:MIAM') || ' - ' || TO_CHAR(end_time, 'HH12:MIAM') || E'\n' ||
            'Break: ' || (break_hours * 60)::int || ' mins' || E'\n' ||
            shift_location,
            E'\n\n' ORDER BY start_time
        ) AS day_shifts,
        SUM(minutes) AS day_minutes
    FROM shifts
    GROUP BY employee_id, name, shift_date
),
users_in_week AS (
    SELECT DISTINCT employee_id, name FROM shifts
),
weekly_totals AS (
    SELECT employee_id, COALESCE(SUM(minutes),0) AS total_minutes
    FROM shifts
    GROUP BY employee_id
),
pivot_base AS (
    SELECT
        u.employee_id,
        u.name,
        wd.shift_date,
        COALESCE(pd.day_shifts, '') AS day_shifts,
        COALESCE(wt.total_minutes, 0) AS total_minutes
    FROM users_in_week u
    CROSS JOIN week_dates wd
    LEFT JOIN per_day pd
        ON pd.employee_id = u.employee_id AND pd.shift_date = wd.shift_date
    LEFT JOIN weekly_totals wt
        ON wt.employee_id = u.employee_id
)
SELECT
    (pb.name || E'\n\n' ||
     LPAD(((pb.total_minutes/60))::text, 2, '0') || ':' ||
     LPAD(((pb.total_minutes%60))::text, 2, '0') || ' hrs/40:00 hrs'
    ) AS "Name",

    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 0 THEN pb.day_shifts END) AS "Mon",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 1 THEN pb.day_shifts END) AS "Tue",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 2 THEN pb.day_shifts END) AS "Wed",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 3 THEN pb.day_shifts END) AS "Thu",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 4 THEN pb.day_shifts END) AS "Fri",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 5 THEN pb.day_shifts END) AS "Sat",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 6 THEN pb.day_shifts END) AS "Sun"

FROM pivot_base pb
GROUP BY pb.name, pb.total_minutes
ORDER BY pb.name
```

---

## OM_Attendance_Tracking _monthly_Attendance Tracking.sql

**Tables referenced:** LATERAL, base, first_clock_in, last_clock_out, shift_attendance, time_events_clockin, time_events_clockout, user_details

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: OM_Attendance_Tracking _monthly
-- Dashboard: Attendance Tracking
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:25
-- ============================================================

WITH base AS (
  SELECT 
    "Shift ID",
    "Shift Name",
    InitCap(CASE
      WHEN "Status" = 'On Leave'
        THEN substring("Shift ID", 11 + length("Shift Location"), length("Shift ID") - length("UUID") - length("Shift Location")-11)
      ELSE NULL
    END) AS "Leave Tags",
    "UUID",
    "Employee Name",
    "Employee ID" AS "Talabat ID",
    "Designation" AS "User Type",
    "Department",
    CASE WHEN "Job Type" ILIKE '%3PL' THEN '3PL' ELSE 'Talabat' END AS "Picker Type",
    CASE 
      WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
      WHEN "Department" = 'Almasia' THEN 'Almasia'
      WHEN "Department" = 'Dynamic' THEN 'Dynamic'
      WHEN "Department" = 'Mazoon' THEN 'Mazoon'
      WHEN "Department" = 'Pillars' THEN 'Pillars'
      WHEN "Department" = 'TFIL' THEN 'TFIL'
      ELSE 'Others'
    END AS "Agency",
    "Division" AS "Country",
    "Sub Division" AS "Chain",
    branch.branch_id AS "Shift Branch ID",
    branch.branch_name AS "Shift Branch Name",
    "Shift Location",
    "Clockin Geofence" AS "Clockin Location",
    "Clockout Geofence" AS "Clockout Location",
    "Status",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled Start Time" + interval '3 hours'
         ELSE "Scheduled Start Time" + interval '4 hours'
    END AS "Scheduled Start Time",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled End Time" + interval '3 hours'
         ELSE "Scheduled End Time" + interval '4 hours'
    END AS "Scheduled End Time",
    DATE_TRUNC('month', 
      CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled Start Time" + interval '3 hours'
           ELSE "Scheduled Start Time" + interval '4 hours'
      END
    ) AS "Month Start Date",

    "Scheduled Break Hours",
    CASE WHEN "Status" != 'On Leave' THEN ((extract(epoch FROM "Scheduled End Time") - extract(epoch FROM "Scheduled Start Time"))/3600)::numeric ELSE 0 END AS "Scheduled Hours incl Break",
    CASE WHEN "Status" != 'On Leave' THEN ((extract(epoch FROM "Scheduled End Time") - extract(epoch FROM "Scheduled Start Time"))/3600 - "Scheduled Break Hours")::numeric ELSE 0 END AS "Scheduled Hours excl Break",
    
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Actual Clockin Time" + interval '3 hours'
         ELSE "Actual Clockin Time" + interval '4 hours' 
    END AS "Actual Clockin Time",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Actual Clockout Time" + interval '3 hours'
         ELSE "Actual Clockout Time" + interval '4 hours' 
    END AS "Actual Clockout Time",
    
    "Actual Break Hours",
    "Actual Work Duration",
    
    CASE 
      WHEN "Actual Clockin Time" IS NOT NULL AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins'
      THEN ((extract(epoch FROM "Actual Clockin Time") - extract(epoch FROM "Scheduled Start Time" + interval '15 mins')) / 60)
      ELSE 0
    END AS "Late Mins",
    CASE 
      WHEN "Actual Clockin Time" IS NOT NULL AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins'
      THEN ceiling((extract(epoch FROM "Actual Clockin Time") - extract(epoch FROM "Scheduled Start Time" + interval '15 mins')) / 3600)
      ELSE 0
    END AS "Late Hours",
    CASE 
      WHEN "Actual Clockout Time" IS NOT NULL AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins'
      THEN ceiling((extract(epoch FROM "Scheduled End Time" - interval '15 mins') - extract(epoch FROM "Actual Clockout Time")) / 3600)
      ELSE 0
    END AS "Early Clockout Hours",
    
    "Scheduled Count", "Leave Count", "Present Count", "Absent Count"
    
  FROM shift_attendance sa
  LEFT JOIN LATERAL (
    SELECT 
      (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
      regexp_replace(sa."Shift Location", '^\d+\s*-\s*(.*)', '\1') AS branch_name
    WHERE sa."Shift Location" ~ '^\d+'
  ) branch ON TRUE
  WHERE organization = 'talabat-cartwheel'
    AND "Scheduled Start Time" + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
    AND sa."Shift Location" ~ '^\d+'
),

     first_clock_in AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.selfie,
   					  tec.details
   FROM time_events_clockin tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND ci_time + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.ci_time),
     fci_edit AS
  (SELECT fci.shift_id,
          fci.uuid,
          to_timestamp((fci.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             fci.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((fci.details->>'originalDeviceTime')::bigint/1000) AS original_ci_time
   FROM first_clock_in fci
   WHERE fci.details->>'isEdited' = 'true'),
     last_clock_out AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.details
   FROM time_events_clockout tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND co_time + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 day'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.co_time DESC),
     lco_edit AS
  (SELECT lco.shift_id,
          lco.uuid,
          to_timestamp((lco.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             lco.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((lco.details->>'originalDeviceTime')::bigint/1000) AS original_co_time
   FROM last_clock_out lco
   WHERE lco.details->>'isEdited' = 'true')

SELECT 
  base."Month Start Date",
  "Employee Name",
  "Talabat ID",
  "Department","Country",
  SUM(base."Scheduled Count") AS "Scheduled Count",
  SUM(CASE WHEN base."Status" = 'On Leave' THEN 1 ELSE 0 END) AS "On Leave Count",
  SUM(CASE WHEN base."Status" = 'Absent' THEN 1 ELSE 0 END) AS "Absent Count",
  SUM(CASE WHEN base."Status" NOT IN ('On Leave', 'Absent') THEN 1 ELSE 0 END) AS "Present Count",
  SUM(CASE WHEN base."Actual Clockin Time" IS NOT NULL AND base."Actual Clockin Time" > base."Scheduled Start Time" + interval '15 mins' THEN 1 ELSE 0 END) AS "Late Count",
  SUM(CASE WHEN base."Actual Clockout Time" < base."Scheduled End Time" - interval '15 mins' THEN 1 ELSE 0 END) AS "Early Clockout Count",
  SUM(CASE 
    WHEN base."Actual Work Duration" > base."Scheduled Hours excl Break" + (1/6)
      AND base."Actual Clockout Time" > base."Scheduled End Time" + interval '10 mins'
    THEN ceiling(base."Actual Work Duration" - base."Scheduled Hours excl Break" - (1/6)) ELSE 0 END) AS "Overtime Hours",
  SUM(CASE 
    WHEN base."Actual Work Duration" < base."Scheduled Hours excl Break" - (1/6)
    THEN ceiling(base."Scheduled Hours excl Break" - base."Actual Work Duration" - (1/6)) ELSE 0 END) AS "Undertime Hours"
FROM base
group by 1,2,3,4,5
order by 1
```

---

## OM_Attendance_Tracking_weekly_Attendance Tracking.sql

**Tables referenced:** LATERAL, base, first_clock_in, last_clock_out, shift_attendance, time_events_clockin, time_events_clockout, user_details

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: OM_Attendance_Tracking_weekly
-- Dashboard: Attendance Tracking
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:25
-- ============================================================

WITH base AS (
  SELECT 
    "Shift ID",
    "Shift Name",
    InitCap(CASE
      WHEN "Status" = 'On Leave'
        THEN substring("Shift ID", 11 + length("Shift Location"), length("Shift ID") - length("UUID") - length("Shift Location")-11)
      ELSE NULL
    END) AS "Leave Tags",
    "UUID",
    "Employee Name",
    "Employee ID" AS "Talabat ID",
    "Designation" AS "User Type",
    "Department",
    CASE WHEN "Job Type" ILIKE '%3PL' THEN '3PL' ELSE 'Talabat' END AS "Picker Type",
    CASE 
      WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
      WHEN "Department" = 'Almasia' THEN 'Almasia'
      WHEN "Department" = 'Dynamic' THEN 'Dynamic'
      WHEN "Department" = 'Mazoon' THEN 'Mazoon'
      WHEN "Department" = 'Pillars' THEN 'Pillars'
      WHEN "Department" = 'TFIL' THEN 'TFIL'
      ELSE 'Others'
    END AS "Agency",
    "Division" AS "Country",
    "Sub Division" AS "Chain",
    branch.branch_id AS "Shift Branch ID",
    branch.branch_name AS "Shift Branch Name",
    "Shift Location",
    "Clockin Geofence" AS "Clockin Location",
    "Clockout Geofence" AS "Clockout Location",
    "Status",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled Start Time" + interval '3 hours'
         ELSE "Scheduled Start Time" + interval '4 hours'
    END AS "Scheduled Start Time",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled End Time" + interval '3 hours'
         ELSE "Scheduled End Time" + interval '4 hours'
    END AS "Scheduled End Time",
    
    -- Add Week Start Date
    DATE_TRUNC('week', 
      CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Scheduled Start Time" + interval '3 hours'
           ELSE "Scheduled Start Time" + interval '4 hours'
      END
    ) AS "Week Start Date",

    "Scheduled Break Hours",
    CASE WHEN "Status" != 'On Leave' THEN ((extract(epoch FROM "Scheduled End Time") - extract(epoch FROM "Scheduled Start Time"))/3600)::numeric ELSE 0 END AS "Scheduled Hours incl Break",
    CASE WHEN "Status" != 'On Leave' THEN ((extract(epoch FROM "Scheduled End Time") - extract(epoch FROM "Scheduled Start Time"))/3600 - "Scheduled Break Hours")::numeric ELSE 0 END AS "Scheduled Hours excl Break",
    
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Actual Clockin Time" + interval '3 hours'
         ELSE "Actual Clockin Time" + interval '4 hours' 
    END AS "Actual Clockin Time",
    CASE WHEN "Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') THEN "Actual Clockout Time" + interval '3 hours'
         ELSE "Actual Clockout Time" + interval '4 hours' 
    END AS "Actual Clockout Time",
    
    "Actual Break Hours",
    "Actual Work Duration",
    
    CASE 
      WHEN "Actual Clockin Time" IS NOT NULL AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins'
      THEN ((extract(epoch FROM "Actual Clockin Time") - extract(epoch FROM "Scheduled Start Time" + interval '15 mins')) / 60)
      ELSE 0
    END AS "Late Mins",
    CASE 
      WHEN "Actual Clockin Time" IS NOT NULL AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins'
      THEN ceiling((extract(epoch FROM "Actual Clockin Time") - extract(epoch FROM "Scheduled Start Time" + interval '15 mins')) / 3600)
      ELSE 0
    END AS "Late Hours",
    CASE 
      WHEN "Actual Clockout Time" IS NOT NULL AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins'
      THEN ceiling((extract(epoch FROM "Scheduled End Time" - interval '15 mins') - extract(epoch FROM "Actual Clockout Time")) / 3600)
      ELSE 0
    END AS "Early Clockout Hours",
    
    "Scheduled Count", "Leave Count", "Present Count", "Absent Count"
    
  FROM shift_attendance sa
  LEFT JOIN LATERAL (
    SELECT 
      (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
      regexp_replace(sa."Shift Location", '^\d+\s*-\s*(.*)', '\1') AS branch_name
    WHERE sa."Shift Location" ~ '^\d+'
  ) branch ON TRUE
  WHERE organization = 'talabat-cartwheel'
    AND "Scheduled Start Time" + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
    AND sa."Shift Location" ~ '^\d+'
),

     first_clock_in AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.selfie,
   					  tec.details
   FROM time_events_clockin tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND ci_time + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.ci_time),
     fci_edit AS
  (SELECT fci.shift_id,
          fci.uuid,
          to_timestamp((fci.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             fci.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((fci.details->>'originalDeviceTime')::bigint/1000) AS original_ci_time
   FROM first_clock_in fci
   WHERE fci.details->>'isEdited' = 'true'),
     last_clock_out AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.details
   FROM time_events_clockout tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND co_time + interval '3 hours' BETWEEN @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.START}}::TIMESTAMP AND @{{:Talabat Attendance Master Export-copy_1743831301.Date Range.END}}::TIMESTAMP + INTERVAL '1 day'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.co_time DESC),
     lco_edit AS
  (SELECT lco.shift_id,
          lco.uuid,
          to_timestamp((lco.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             lco.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((lco.details->>'originalDeviceTime')::bigint/1000) AS original_co_time
   FROM last_clock_out lco
   WHERE lco.details->>'isEdited' = 'true')

SELECT 
  base."Week Start Date",
  "Employee Name",
  "Talabat ID",
  "Department",
  "Country",
   SUM(base."Scheduled Count") AS "Scheduled Count",
  SUM(CASE WHEN base."Status" = 'On Leave' THEN 1 ELSE 0 END) AS "On Leave Count",
  SUM(CASE WHEN base."Status" = 'Absent' THEN 1 ELSE 0 END) AS "Absent Count",
  SUM(CASE WHEN base."Status" NOT IN ('On Leave', 'Absent') THEN 1 ELSE 0 END) AS "Present Count",
  SUM(CASE WHEN base."Actual Clockin Time" IS NOT NULL AND base."Actual Clockin Time" > base."Scheduled Start Time" + interval '15 mins' THEN 1 ELSE 0 END) AS "Late Count",
  SUM(CASE WHEN base."Actual Clockout Time" < base."Scheduled End Time" - interval '15 mins' THEN 1 ELSE 0 END) AS "Early Clockout Count",
  SUM(CASE 
    WHEN base."Actual Work Duration" > base."Scheduled Hours excl Break" + (1/6)
      AND base."Actual Clockout Time" > base."Scheduled End Time" + interval '10 mins'
    THEN ceiling(base."Actual Work Duration" - base."Scheduled Hours excl Break" - (1/6)) ELSE 0 END) AS "Overtime Hours",
  SUM(CASE 
    WHEN base."Actual Work Duration" < base."Scheduled Hours excl Break" - (1/6)
    THEN ceiling(base."Scheduled Hours excl Break" - base."Actual Work Duration" - (1/6)) ELSE 0 END) AS "Undertime Hours"
FROM base
group by 1,2,3,4,5
order by 1
```

---

## Talabat Attendance Master Export-copy_1743831301_Attendance Tracking.sql

**Tables referenced:** LATERAL, base, fci_edit, first_clock_in, last_clock_out, lco_edit, shift_attendance, time_events_clockin, time_events_clockout, user_details

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: Talabat Attendance Master Export-copy_1743831301
-- Dashboard: Attendance Tracking
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:24
-- ============================================================

SELECT
		"QueryTable 1"."Shift ID" AS "Shift ID",
		"QueryTable 1"."Shift Name" AS "Shift Name",
		"QueryTable 1"."Leave Tags" AS "Leave Tags",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Talabat ID" AS "Talabat ID",
		"QueryTable 1"."User Type" AS "User Type",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."Picker Type" AS "Picker Type",
		"QueryTable 1"."Agency" AS "Agency",
		"QueryTable 1"."Country" AS "Country",
		"QueryTable 1"."Chain" AS "Chain",
		"QueryTable 1"."Shift Branch ID" AS "Shift Branch ID",
		"QueryTable 1"."Shift Branch Name" AS "Shift Branch Name",
		"QueryTable 1"."Shift Location" AS "Shift Location",
		"QueryTable 1"."Clockin Location" AS "Clockin Location",
		"QueryTable 1"."Clockout Location" AS "Clockout Location",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
		"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
		"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
		"QueryTable 1"."Scheduled Hours incl Break" AS "Scheduled Hours incl Break",
		"QueryTable 1"."Scheduled Hours excl Break" AS "Scheduled Hours excl Break",
		"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
		"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
		"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
		"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
		"QueryTable 1"."Late Mins" AS "Late Mins",
		"QueryTable 1"."Late Hours" AS "Late Hours",
		"QueryTable 1"."Early Clockout Hours" AS "Early Clockout Hours",
		"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
		"QueryTable 1"."Leave Count" AS "Leave Count",
		"QueryTable 1"."Present Count" AS "Present Count",
		"QueryTable 1"."Absent Count" AS "Absent Count",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Modified Status" AS "Modified Status",
		"QueryTable 1"."Selfie Status" AS "Selfie Status",
		"QueryTable 1"."Selfie Image Link" AS "Selfie Image Link",
		"QueryTable 1"."Overtime Hours" AS "Overtime Hours",
		"QueryTable 1"."Overtime Count" AS "Overtime Count",
		"QueryTable 1"."Undertime Hours" AS "Undertime Hours",
		"QueryTable 1"."Undertime Count" AS "Undertime Count",
		"QueryTable 1"."Late Count" AS "Late Count",
		"QueryTable 1"."Early Clockout Count" AS "Early Clockout Count",
		"QueryTable 1"."First CI Edited At" AS "First CI Edited At",
		"QueryTable 1"."First CI Edited By" AS "First CI Edited By",
		"QueryTable 1"."Original First CI" AS "Original First CI",
		"QueryTable 1"."Last CO Edited At" AS "Last CO Edited At",
		"QueryTable 1"."Last CO Edited By" AS "Last CO Edited By",
		"QueryTable 1"."Original Last CO" AS "Original Last CO",
		"QueryTable 1"."CI-CO Same Location?" AS "CI-CO Same Location?"
FROM( SELECT
		"QueryTable 1"."Shift ID" AS "Shift ID",
		"QueryTable 1"."Shift Name" AS "Shift Name",
		"QueryTable 1"."Leave Tags" AS "Leave Tags",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Talabat ID" AS "Talabat ID",
		"QueryTable 1"."User Type" AS "User Type",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."Picker Type" AS "Picker Type",
		"QueryTable 1"."Agency" AS "Agency",
		"QueryTable 1"."Country" AS "Country",
		"QueryTable 1"."Chain" AS "Chain",
		"QueryTable 1"."Shift Branch ID" AS "Shift Branch ID",
		"QueryTable 1"."Shift Branch Name" AS "Shift Branch Name",
		"QueryTable 1"."Shift Location" AS "Shift Location",
		"QueryTable 1"."Clockin Location" AS "Clockin Location",
		"QueryTable 1"."Clockout Location" AS "Clockout Location",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
		"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
		"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
		"QueryTable 1"."Scheduled Hours incl Break" AS "Scheduled Hours incl Break",
		"QueryTable 1"."Scheduled Hours excl Break" AS "Scheduled Hours excl Break",
		"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
		"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
		"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
		"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
		"QueryTable 1"."Late Mins" AS "Late Mins",
		"QueryTable 1"."Late Hours" AS "Late Hours",
		"QueryTable 1"."Early Clockout Hours" AS "Early Clockout Hours",
		"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
		"QueryTable 1"."Leave Count" AS "Leave Count",
		"QueryTable 1"."Present Count" AS "Present Count",
		"QueryTable 1"."Absent Count" AS "Absent Count",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Modified Status" AS "Modified Status",
		"QueryTable 1"."Selfie Status" AS "Selfie Status",
		"QueryTable 1"."Selfie Image Link" AS "Selfie Image Link",
		"QueryTable 1"."Overtime Hours" AS "Overtime Hours",
		"QueryTable 1"."Overtime Count" AS "Overtime Count",
		"QueryTable 1"."Undertime Hours" AS "Undertime Hours",
		"QueryTable 1"."Undertime Count" AS "Undertime Count",
		"QueryTable 1"."Late Count" AS "Late Count",
		"QueryTable 1"."Early Clockout Count" AS "Early Clockout Count",
		"QueryTable 1"."First CI Edited At" AS "First CI Edited At",
		"QueryTable 1"."First CI Edited By" AS "First CI Edited By",
		"QueryTable 1"."Original First CI" AS "Original First CI",
		"QueryTable 1"."Last CO Edited At" AS "Last CO Edited At",
		"QueryTable 1"."Last CO Edited By" AS "Last CO Edited By",
		"QueryTable 1"."Original Last CO" AS "Original Last CO",
		"QueryTable 1"."CI-CO Same Location?" AS "CI-CO Same Location?"
FROM(WITH base AS
  (SELECT "Shift ID",
   "Shift Name",
   InitCap(CASE
                                                       WHEN "Status" = 'On Leave'
                                                            THEN substring("Shift ID", 11 + length("Shift Location"), length("Shift ID") - length("UUID") - length("Shift Location")-11)
                                                       ELSE NULL
                                                   END) AS "Leave Tags",
          "UUID",
          "Employee Name",
          "Employee ID" AS "Talabat ID",
          "Designation" AS "User Type",
          "Department",
          CASE
              WHEN "Job Type" ILIKE '%3PL' THEN '3PL'
              ELSE 'Talabat'
          END AS "Picker Type",
          CASE
              WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
              WHEN "Department" = 'Almasia' THEN 'Almasia'
                 WHEN "Department" = 'Dynamic' THEN 'Dynamic'
                    WHEN "Department" = 'Mazoon' THEN 'Mazoon'
                       WHEN "Department" = 'Pillars' THEN 'Pillars'
                          WHEN "Department" = 'TFIL' THEN 'TFIL'
              ELSE 'Others'
          END AS "Agency",
          "Division" AS "Country",
          "Sub Division" AS "Chain",
          branch.branch_id AS "Shift Branch ID",
          branch.branch_name AS "Shift Branch Name",
          "Shift Location",
          "Clockin Geofence" AS "Clockin Location",
          "Clockout Geofence" AS "Clockout Location",
          "Status",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Scheduled Start Time" + interval '3 hours'
              ELSE "Scheduled Start Time" + interval '4 hours'
          END AS "Scheduled Start Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Scheduled End Time" + interval '3 hours'
              ELSE "Scheduled End Time" + interval '4 hours'
          END AS "Scheduled End Time",
          "Scheduled Break Hours",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600
              ELSE 0
          END AS "Scheduled Hours incl Break",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600 - "Scheduled Break Hours"
              ELSE 0
          END AS "Scheduled Hours excl Break",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Actual Clockin Time" + interval '3 hours'
              ELSE "Actual Clockin Time" + interval '4 hours'
          END AS "Actual Clockin Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Actual Clockout Time" + interval '3 hours'
              ELSE "Actual Clockout Time" + interval '4 hours'
          END AS "Actual Clockout Time",
          "Actual Break Hours",
          "Actual Work Duration",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ((extract(epoch
                                                                                                          FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                           FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/60
              ELSE 0
          END AS "Late Mins",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                  FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                                   FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/3600)
              ELSE 0
          END AS "Late Hours",
          CASE
              WHEN "Actual Clockout Time" IS NOT NULL
                   AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                 FROM "Scheduled End Time" - interval '15 mins'))::numeric - (extract(epoch
                                                                                                                                                                                      FROM "Actual Clockout Time"))::numeric)/3600)
              ELSE 0
          END AS "Early Clockout Hours",
          "Scheduled Count",
          "Leave Count",
          "Present Count",
          "Absent Count"
   FROM shift_attendance sa
   LEFT JOIN LATERAL
     (SELECT 
    (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
    regexp_replace(sa."Shift Location", '^\d+\s*-\s*(.*)', '\1') AS branch_name
      WHERE sa."Shift Location" ~ '^\d+' ) branch ON TRUE
   WHERE organization = 'talabat-cartwheel'
     AND "Scheduled Start Time" + interval '3 hours' BETWEEN '2025-04-30'::TIMESTAMP AND '2025-05-06'::TIMESTAMP + INTERVAL '1 hour'
     AND sa."Shift Location" ~ '^\d+'
    ),
     first_clock_in AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.selfie,
   					  tec.details
   FROM time_events_clockin tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND ci_time + interval '3 hours' BETWEEN '2025-04-30'::TIMESTAMP AND '2025-05-06'::TIMESTAMP + INTERVAL '1 hour'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.ci_time),
     fci_edit AS
  (SELECT fci.shift_id,
          fci.uuid,
          to_timestamp((fci.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             fci.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((fci.details->>'originalDeviceTime')::bigint/1000) AS original_ci_time
   FROM first_clock_in fci
   WHERE fci.details->>'isEdited' = 'true'),
     last_clock_out AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.details
   FROM time_events_clockout tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND co_time + interval '3 hours' BETWEEN '2025-04-30'::TIMESTAMP AND '2025-05-06'::TIMESTAMP + INTERVAL '1 day'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.co_time DESC),
     lco_edit AS
  (SELECT lco.shift_id,
          lco.uuid,
          to_timestamp((lco.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             lco.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((lco.details->>'originalDeviceTime')::bigint/1000) AS original_co_time
   FROM last_clock_out lco
   WHERE lco.details->>'isEdited' = 'true')
SELECT base.*, Coalesce("Shift Name", "Leave Tags") as "Shift",
       CASE
           WHEN "Status" IN ('On Leave',
                             'Absent') THEN "Status"
           WHEN "Late Mins" > 0 THEN 'Present - Late'
           ELSE 'Present - On Time'
       END AS "Modified Status",
       CASE
           WHEN (fci.selfie ILIKE '%Photofailed%' or fci.selfie is null) THEN 'No Selfie Image'
           ELSE 'Selfie Available'
       END AS "Selfie Status",
	   fci.selfie as "Selfie Image Link",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN ceiling("Actual Work Duration" - "Scheduled Hours excl Break" - (1/6))
           ELSE 0
       END AS "Overtime Hours",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN 1
           ELSE 0
       END AS "Overtime Count",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN ceiling("Scheduled Hours excl Break" - "Actual Work Duration" - (1/6))
           ELSE 0
       END AS "Undertime Hours",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN 1
           ELSE 0
       END AS "Undertime Count",
       CASE
           WHEN "Late Hours" > 0 THEN 1
           ELSE 0
       END AS "Late Count",
       CASE
           WHEN "Early Clockout Hours" > 0 THEN 1
           ELSE 0
       END AS "Early Clockout Count",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN fci_edit.edited_at + interval '3 hours'
           ELSE fci_edit.edited_at + interval '4 hours'
       END AS "First CI Edited At",
       fci_edit.edited_by AS "First CI Edited By",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN fci_edit.original_ci_time + interval '3 hours'
           ELSE fci_edit.original_ci_time + interval '4 hours'
       END AS "Original First CI",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN lco_edit.edited_at + interval '3 hours'
           ELSE lco_edit.edited_at + interval '4 hours'
       END AS "Last CO Edited At",
       lco_edit.edited_by AS "Last CO Edited By",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN lco_edit.original_co_time + interval '3 hours'
           ELSE lco_edit.original_co_time + interval '4 hours'
       END AS "Original Last CO",
	   case when base."Clockin Location" !=  base."Clockout Location" then 'Different' else 'Same' end as "CI-CO Same Location?"
FROM base
LEFT OUTER JOIN first_clock_in fci ON base."Shift ID" = fci.shift_id
AND base."UUID" = fci.uuid
LEFT OUTER JOIN fci_edit ON base."Shift ID" = fci_edit.shift_id
AND base."UUID" = fci_edit.uuid
LEFT OUTER JOIN lco_edit ON base."Shift ID" = lco_edit.shift_id
AND base."UUID" = lco_edit.uuid
ORDER BY 10,
         11,
         12,
         19,
         9,
         4)"QueryTable 1")"QueryTable 1"
```

---

## Talabat Attendance Master Export_Master Export.sql

**Tables referenced:** base, first_clock_in, last_clock_out, sa, shift_attendance, time_events_clockin, time_events_clockout, user_details

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: Talabat Attendance Master Export
-- Dashboard: Master Export
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:52:55
-- ============================================================

SELECT
	"QueryTable 1"."Shift ID" AS "Shift ID",
	"QueryTable 1"."Shift Name" AS "Shift Name",
	"QueryTable 1"."Leave Tags" AS "Leave Tags",
	"QueryTable 1"."UUID" AS "UUID",
	"QueryTable 1"."Employee Name" AS "Employee Name",
	"QueryTable 1"."Talabat ID" AS "Talabat ID",
	"QueryTable 1"."User Type" AS "User Type",
	"QueryTable 1"."Department" AS "Department",
	"QueryTable 1"."Picker Type" AS "Picker Type",
	"QueryTable 1"."Agency" AS "Agency",
	"QueryTable 1"."Country" AS "Country",
	"QueryTable 1"."Chain" AS "Chain",
	"QueryTable 1"."Shift Branch ID" AS "Shift Branch ID",
	"QueryTable 1"."Shift Branch Name" AS "Shift Branch Name",
	"QueryTable 1"."Shift Location" AS "Shift Location",
	"QueryTable 1"."Clockin Location" AS "Clockin Location",
	"QueryTable 1"."Clockout Location" AS "Clockout Location",
	"QueryTable 1"."Status" AS "Status",
	"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
	"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
	"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
	"QueryTable 1"."Scheduled Hours incl Break" AS "Scheduled Hours incl Break",
	"QueryTable 1"."Scheduled Hours excl Break" AS "Scheduled Hours excl Break",
	"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
	"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
	"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
	"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
	"QueryTable 1"."Late Mins" AS "Late Mins",
	"QueryTable 1"."Late Hours" AS "Late Hours",
	"QueryTable 1"."Early Clockout Hours" AS "Early Clockout Hours",
	"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
	"QueryTable 1"."Leave Count" AS "Leave Count",
	"QueryTable 1"."Present Count" AS "Present Count",
	"QueryTable 1"."Absent Count" AS "Absent Count",
	"QueryTable 1"."Shift" AS "Shift",
	"QueryTable 1"."Modified Status" AS "Modified Status",
	"QueryTable 1"."Selfie Status" AS "Selfie Status",
	"QueryTable 1"."Selfie Image Link" AS "Selfie Image Link",
	"QueryTable 1"."Overtime Hours" AS "Overtime Hours",
	"QueryTable 1"."Overtime Count" AS "Overtime Count",
	"QueryTable 1"."Undertime Hours" AS "Undertime Hours",
	"QueryTable 1"."Undertime Count" AS "Undertime Count",
	"QueryTable 1"."Late Count" AS "Late Count",
	"QueryTable 1"."Early Clockout Count" AS "Early Clockout Count",
	"QueryTable 1"."First CI Edited At" AS "First CI Edited At",
	"QueryTable 1"."First CI Edited By" AS "First CI Edited By",
	"QueryTable 1"."Original First CI" AS "Original First CI",
	"QueryTable 1"."Last CO Edited At" AS "Last CO Edited At",
	"QueryTable 1"."Last CO Edited By" AS "Last CO Edited By",
	"QueryTable 1"."Original Last CO" AS "Original Last CO",
	"QueryTable 1"."CI-CO Same Location?" AS "CI-CO Same Location?"
FROM(
WITH base AS (
    SELECT 
        sa."Shift ID",
        sa."Shift Name",
        InitCap(CASE WHEN sa."Status" = 'On Leave'
            THEN substring(sa."Shift ID", 11 + length(sa."Shift Location"), 
                 length(sa."Shift ID") - length(sa."UUID") - length(sa."Shift Location")-11)
            ELSE NULL END) AS "Leave Tags",
        sa."UUID",
        sa."Employee Name",
        sa."Employee ID" AS "Talabat ID",
        sa."Designation" AS "User Type",
        sa."Department",
        CASE WHEN sa."Job Type" ILIKE '%3PL' THEN '3PL' ELSE 'Talabat' END AS "Picker Type",
        CASE 
            WHEN sa."Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
            WHEN sa."Job Type" ILIKE '%- 3PL' THEN rtrim(sa."Job Type", '- 3PL')
            ELSE 'Others'
        END AS "Agency",
        sa."Division" AS "Country",
        sa."Sub Division" AS "Chain",
        -- OPTIMIZED: Inline branch extraction instead of LATERAL join
        (regexp_match(sa."Shift Location", '^(\d+)'))[1] AS "Shift Branch ID",
        regexp_replace(sa."Shift Location", '^\d+\s*-\s*', '') AS "Shift Branch Name",
        sa."Shift Location",
        sa."Clockin Geofence" AS "Clockin Location",
        sa."Clockout Geofence" AS "Clockout Location",
        sa."Status",
        CASE WHEN sa."Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
            THEN sa."Scheduled Start Time" + interval '3 hours' 
            ELSE sa."Scheduled Start Time" + interval '4 hours' END AS "Scheduled Start Time",
        CASE WHEN sa."Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
            THEN sa."Scheduled End Time" + interval '3 hours' 
            ELSE sa."Scheduled End Time" + interval '4 hours' END AS "Scheduled End Time",
        sa."Scheduled Break Hours",
        CASE WHEN sa."Status" != 'On Leave' 
            THEN (extract(epoch FROM sa."Scheduled End Time") - extract(epoch FROM sa."Scheduled Start Time"))/3600 
            ELSE 0 END AS "Scheduled Hours incl Break",
        CASE WHEN sa."Status" != 'On Leave' 
            THEN (extract(epoch FROM sa."Scheduled End Time") - extract(epoch FROM sa."Scheduled Start Time"))/3600 - sa."Scheduled Break Hours"
            ELSE 0 END AS "Scheduled Hours excl Break",
        CASE WHEN sa."Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
            THEN sa."Actual Clockin Time" + interval '3 hours' 
            ELSE sa."Actual Clockin Time" + interval '4 hours' END AS "Actual Clockin Time",
        CASE WHEN sa."Division" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
            THEN sa."Actual Clockout Time" + interval '3 hours' 
            ELSE sa."Actual Clockout Time" + interval '4 hours' END AS "Actual Clockout Time",
        sa."Actual Break Hours",
        sa."Actual Work Duration",
        CASE WHEN sa."Actual Clockin Time" IS NOT NULL AND sa."Actual Clockin Time" > sa."Scheduled Start Time" + interval '15 mins'
            THEN (extract(epoch FROM sa."Actual Clockin Time") - extract(epoch FROM sa."Scheduled Start Time" + interval '15 mins'))/60
            ELSE 0 END AS "Late Mins",
        CASE WHEN sa."Actual Clockin Time" IS NOT NULL AND sa."Actual Clockin Time" > sa."Scheduled Start Time" + interval '15 mins'
            THEN ceiling((extract(epoch FROM sa."Actual Clockin Time") - extract(epoch FROM sa."Scheduled Start Time" + interval '15 mins'))/3600)
            ELSE 0 END AS "Late Hours",
        CASE WHEN sa."Actual Clockout Time" IS NOT NULL AND sa."Actual Clockout Time" < sa."Scheduled End Time" - interval '15 mins'
            THEN ceiling((extract(epoch FROM sa."Scheduled End Time" - interval '15 mins') - extract(epoch FROM sa."Actual Clockout Time"))/3600)
            ELSE 0 END AS "Early Clockout Hours",
        sa."Scheduled Count",
        sa."Leave Count",
        sa."Present Count",
        sa."Absent Count"
    FROM shift_attendance sa
    WHERE sa.organization = 'talabat-cartwheel'
      AND sa."Scheduled Start Time" + interval '3 hours' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
      AND sa."Shift Location" ~ '^\d+'
),
-- OPTIMIZED: Combined first_clock_in + fci_edit into single CTE
first_clock_in AS (
    SELECT DISTINCT ON (tec.shift_id, tec.uuid) 
        tec.shift_id,
        tec.uuid,
        tec.selfie,
        CASE WHEN tec.details->>'isEdited' = 'true' 
            THEN to_timestamp((tec.details->>'editedAt')::bigint/1000) END AS edited_at,
        tec.details->>'editedByUsername' AS edited_by,
        CASE WHEN tec.details->>'isEdited' = 'true' 
            THEN to_timestamp((tec.details->>'originalDeviceTime')::bigint/1000) END AS original_ci_time
    FROM time_events_clockin tec
    JOIN user_details ud ON tec.uuid = ud.uuid
    WHERE ud.organization = 'talabat-cartwheel'
      AND tec.ci_time + interval '3 hours' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + INTERVAL '1 hour'
    ORDER BY tec.shift_id, tec.uuid, tec.ci_time
),
-- OPTIMIZED: Combined last_clock_out + lco_edit into single CTE
last_clock_out AS (
    SELECT DISTINCT ON (tec.shift_id, tec.uuid) 
        tec.shift_id,
        tec.uuid,
        CASE WHEN tec.details->>'isEdited' = 'true' 
            THEN to_timestamp((tec.details->>'editedAt')::bigint/1000) END AS edited_at,
        tec.details->>'editedByUsername' AS edited_by,
        CASE WHEN tec.details->>'isEdited' = 'true' 
            THEN to_timestamp((tec.details->>'originalDeviceTime')::bigint/1000) END AS original_co_time
    FROM time_events_clockout tec
    JOIN user_details ud ON tec.uuid = ud.uuid
    WHERE ud.organization = 'talabat-cartwheel'
      AND tec.co_time + interval '3 hours' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + INTERVAL '1 day'
    ORDER BY tec.shift_id, tec.uuid, tec.co_time DESC
)
SELECT 
    base."Shift ID",
    base."Shift Name",
    base."Leave Tags",
    base."UUID",
    base."Employee Name",
    base."Talabat ID",
    base."User Type",
    base."Department",
    base."Picker Type",
    base."Agency",
    base."Country",
    base."Chain",
    base."Shift Branch ID",
    base."Shift Branch Name",
    base."Shift Location",
    base."Clockin Location",
    base."Clockout Location",
    base."Status",
    base."Scheduled Start Time",
    base."Scheduled End Time",
    base."Scheduled Break Hours",
    base."Scheduled Hours incl Break",
    base."Scheduled Hours excl Break",
    base."Actual Clockin Time",
    base."Actual Clockout Time",
    base."Actual Break Hours",
    base."Actual Work Duration",
    base."Late Mins",
    base."Late Hours",
    base."Early Clockout Hours",
    base."Scheduled Count",
    base."Leave Count",
    base."Present Count",
    base."Absent Count",
    Coalesce(base."Shift Name", base."Leave Tags") as "Shift",
    CASE
        WHEN base."Status" IN ('On Leave', 'Absent') THEN base."Status"
        WHEN base."Late Mins" > 0 THEN 'Present - Late'
        ELSE 'Present - On Time'
    END AS "Modified Status",
    CASE
        WHEN (fci.selfie ILIKE '%Photofailed%' OR fci.selfie IS NULL) THEN 'No Selfie Image'
        ELSE 'Selfie Available'
    END AS "Selfie Status",
    fci.selfie AS "Selfie Image Link",
    CASE
        WHEN base."Actual Work Duration" > 0
            AND base."Actual Work Duration" > base."Scheduled Hours excl Break" + (1/6)
            AND base."Actual Clockout Time" > base."Scheduled End Time" + interval '10 mins' 
        THEN ceiling(base."Actual Work Duration" - base."Scheduled Hours excl Break" - (1/6))
        ELSE 0
    END AS "Overtime Hours",
    CASE
        WHEN base."Actual Work Duration" > 0
            AND base."Actual Work Duration" > base."Scheduled Hours excl Break" + (1/6)
            AND base."Actual Clockout Time" > base."Scheduled End Time" + interval '10 mins' THEN 1
        ELSE 0
    END AS "Overtime Count",
    CASE
        WHEN base."Actual Work Duration" > 0
            AND base."Actual Work Duration" < base."Scheduled Hours excl Break" - (1/6) 
        THEN ceiling(base."Scheduled Hours excl Break" - base."Actual Work Duration" - (1/6))
        ELSE 0
    END AS "Undertime Hours",
    CASE
        WHEN base."Actual Work Duration" > 0
            AND base."Actual Work Duration" < base."Scheduled Hours excl Break" - (1/6) THEN 1
        ELSE 0
    END AS "Undertime Count",
    CASE WHEN base."Late Hours" > 0 THEN 1 ELSE 0 END AS "Late Count",
    CASE WHEN base."Early Clockout Hours" > 0 THEN 1 ELSE 0 END AS "Early Clockout Count",
    fci.edited_at + CASE WHEN base."Country" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
        THEN interval '3 hours' ELSE interval '4 hours' END AS "First CI Edited At",
    fci.edited_by AS "First CI Edited By",
    fci.original_ci_time + CASE WHEN base."Country" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
        THEN interval '3 hours' ELSE interval '4 hours' END AS "Original First CI",
    lco.edited_at + CASE WHEN base."Country" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
        THEN interval '3 hours' ELSE interval '4 hours' END AS "Last CO Edited At",
    lco.edited_by AS "Last CO Edited By",
    lco.original_co_time + CASE WHEN base."Country" IN ('Qatar','Kuwait','Egypt','Bahrain','Oman','Jordan') 
        THEN interval '3 hours' ELSE interval '4 hours' END AS "Original Last CO",
    CASE WHEN base."Clockin Location" != base."Clockout Location" THEN 'Different' ELSE 'Same' END AS "CI-CO Same Location?"
FROM base
LEFT JOIN first_clock_in fci ON base."Shift ID" = fci.shift_id AND base."UUID" = fci.uuid
LEFT JOIN last_clock_out lco ON base."Shift ID" = lco.shift_id AND base."UUID" = lco.uuid
ORDER BY base."Country", base."Chain", base."Department", base."Scheduled Start Time", base."Agency", base."UUID"
)"QueryTable 1"
```

---

## Talabat Attendance Report_Attendance Report.sql

**Tables referenced:** LATERAL, base, day_wise, shift_attendance, user_details

**Original Query:**

```sql
-- Data Source: Talabat Attendance Report
-- Dashboard: Attendance Report
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:55:48
-- ============================================================

 SELECT
		"QueryTable 1"."Month" AS "Month",
		"QueryTable 1"."Country" AS "Country",
		"QueryTable 1"."Chain" AS "Chain",
		"QueryTable 1"."Branch ID" AS "Branch ID",
		"QueryTable 1"."Branch Name" AS "Branch Name",
		"QueryTable 1"."Agency" AS "Agency",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Talabat ID" AS "Talabat ID",
		"QueryTable 1"."User Type" AS "User Type",
		"QueryTable 1"."Picker Type" AS "Picker Type",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Scheduled Days" AS "Scheduled Days",
		"QueryTable 1"."Absent Days" AS "Absent Days",
		"QueryTable 1"."Total Scheduled Hours" AS "Total Scheduled Hours",
		"QueryTable 1"."Total Hours Worked" AS "Total Hours Worked",
		"QueryTable 1"."Total OT Hours" AS "Total OT Hours",
		"QueryTable 1"."Total UT Hours" AS "Total UT Hours",
		"QueryTable 1"."Total Late or Early CO Hours" AS "Total Late or Early CO Hours",
		"QueryTable 1"."01" AS "01",
		"QueryTable 1"."02" AS "02",
		"QueryTable 1"."03" AS "03",
		"QueryTable 1"."04" AS "04",
		"QueryTable 1"."05" AS "05",
		"QueryTable 1"."06" AS "06",
		"QueryTable 1"."07" AS "07",
		"QueryTable 1"."08" AS "08",
		"QueryTable 1"."09" AS "09",
		"QueryTable 1"."10" AS "10",
		"QueryTable 1"."11" AS "11",
		"QueryTable 1"."12" AS "12",
		"QueryTable 1"."13" AS "13",
		"QueryTable 1"."14" AS "14",
		"QueryTable 1"."15" AS "15",
		"QueryTable 1"."16" AS "16",
		"QueryTable 1"."17" AS "17",
		"QueryTable 1"."18" AS "18",
		"QueryTable 1"."19" AS "19",
		"QueryTable 1"."20" AS "20",
		"QueryTable 1"."21" AS "21",
		"QueryTable 1"."22" AS "22",
		"QueryTable 1"."23" AS "23",
		"QueryTable 1"."24" AS "24",
		"QueryTable 1"."25" AS "25",
		"QueryTable 1"."26" AS "26",
		"QueryTable 1"."27" AS "27",
		"QueryTable 1"."28" AS "28",
		"QueryTable 1"."29" AS "29",
		"QueryTable 1"."30" AS "30",
		"QueryTable 1"."31" AS "31"
FROM(WITH base AS
  (SELECT "Shift ID",
          "UUID",
          "Employee Name",
          "Employee ID" AS "Talabat ID",
          "Designation" AS "User Type",
          "Department",
          CASE
              WHEN "Job Type" ILIKE '%3PL' THEN '3PL'
              ELSE 'Talabat'
          END AS "Picker Type",
          CASE
              WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
              WHEN "Job Type" ILIKE '%- 3PL' THEN rtrim("Job Type", '- 3PL')
              ELSE 'Others'
          END AS "Agency",
          "Division" AS "Country",
          branch.chain_name AS "Chain",
          "Status",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait') THEN "Scheduled Start Time" + interval '3 hours'
              ELSE "Scheduled Start Time" + interval '4 hours'
          END AS "Scheduled Start Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait') THEN "Scheduled End Time" + interval '3 hours'
              ELSE "Scheduled End Time" + interval '4 hours'
          END AS "Scheduled End Time",
          "Scheduled Break Hours",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600
              ELSE 0
          END AS "Scheduled Hours incl Break",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600 - "Scheduled Break Hours"
              ELSE 0
          END AS "Scheduled Hours excl Break",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait') THEN "Actual Clockin Time" + interval '3 hours'
              ELSE "Actual Clockin Time" + interval '4 hours'
          END AS "Actual Clockin Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait') THEN "Actual Clockout Time" + interval '3 hours'
              ELSE "Actual Clockout Time" + interval '4 hours'
          END AS "Actual Clockout Time",
          "Actual Break Hours",
          "Actual Work Duration",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ((extract(epoch
                                                                                                          FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                           FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/60
              ELSE 0
          END AS "Late Mins",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                  FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                                   FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/3600)
              ELSE 0
          END AS "Late Hours",
          CASE
              WHEN "Actual Clockout Time" IS NOT NULL
                   AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                 FROM "Scheduled End Time" - interval '15 mins'))::numeric - (extract(epoch
                                                                                                                                                                                      FROM "Actual Clockout Time"))::numeric)/3600)
              ELSE 0
          END AS "Early Clockout Hours"
   FROM shift_attendance sa
   LEFT JOIN LATERAL
     (SELECT (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
             regexp_replace(sa."Shift Location", '^\d+\s*-\s*([^,]+).*', '\1') AS chain_name,
             regexp_replace(sa."Shift Location", '^\d+\s*-\s*[^,]+,\s*(.*)', '\1') AS branch_name
      WHERE sa."Shift Location" ~ '^\d+' ) branch ON TRUE
   WHERE organization = 'talabat-cartwheel'
     AND "Scheduled Start Time" + interval '3 hours' BETWEEN '2025-05-01'::TIMESTAMP AND '2025-05-31'::TIMESTAMP + INTERVAL '1 hour'
     AND sa."Shift Location" ~ '^\d+'
     AND sa."Division" in ('UAE','Jordan','Kuwait','HQ','Qatar','Bahrain','Oman','Egypt')),
     day_wise AS
  (SELECT "UUID",
          "Employee Name",
          "Talabat ID",
          "User Type",
          "Department",
          "Picker Type",
          "Agency",
          "Country",
          "Chain",
          to_char("Scheduled Start Time", 'YYYY-MM') AS "Month",
          to_char("Scheduled Start Time", 'DD') AS "Day",
   sum("Scheduled Hours excl Break") as "Scheduled Hours",
          sum("Actual Work Duration") AS "Actual Work Hours",
          sum(CASE
                  WHEN "Actual Work Duration" > 0
                       AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                       AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN ceiling("Actual Work Duration" - "Scheduled Hours excl Break" - (1/6))
                  ELSE 0
              END) AS "Overtime Hours",
          sum(CASE
                  WHEN "Actual Work Duration" > 0
                       AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                       AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN 1
                  ELSE 0
              END) AS "Overtime Count",
          sum(CASE
                  WHEN "Actual Work Duration" > 0
                       AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN ceiling("Scheduled Hours excl Break" - "Actual Work Duration" - (1/6))
                  ELSE 0
              END) AS "Undertime Hours",
          sum(CASE
                  WHEN "Actual Work Duration" > 0
                       AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN 1
                  ELSE 0
              END) AS "Undertime Count",
          count(distinct(CASE
                             WHEN "Status" != 'On Leave' THEN to_char("Scheduled Start Time", 'DD')
                             ELSE NULL
                         END)) AS "Scheduled Count",
          count(distinct(CASE
                             WHEN "Status" = 'Absent' THEN to_char("Scheduled Start Time", 'DD')
                             ELSE NULL
                         END)) AS "Absent Count",
          sum("Late Hours" + "Early Clockout Hours") AS "Late or Early CO Hours"
   FROM base
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
            11)
SELECT "Month",
       "Country",
       "Chain",
	   (regexp_matches(ud.job_location, '^(\d+)', 'g'))[1] AS "Branch ID",
	   TRIM(regexp_replace(ud.job_location, '^\d+\s*-\s*', '')) as "Branch Name",
       "Agency",
       "Employee Name",
       "Talabat ID",
       "User Type",
       "Picker Type",
       "Department",
       "UUID",
       sum("Scheduled Count") AS "Scheduled Days",
       sum("Absent Count") AS "Absent Days",
	   sum("Scheduled Hours") as "Total Scheduled Hours",
       sum("Actual Work Hours") AS "Total Hours Worked",
       sum("Overtime Hours") AS "Total OT Hours",
       sum("Undertime Hours") AS "Total UT Hours",
       sum("Late or Early CO Hours") AS "Total Late or Early CO Hours",
       sum(case when "Day" = '01' then "Actual Work Hours" else 0 end) as "01",
sum(case when "Day" = '02' then "Actual Work Hours" else 0 end) as "02",
sum(case when "Day" = '03' then "Actual Work Hours" else 0 end) as "03",
sum(case when "Day" = '04' then "Actual Work Hours" else 0 end) as "04",
sum(case when "Day" = '05' then "Actual Work Hours" else 0 end) as "05",
sum(case when "Day" = '06' then "Actual Work Hours" else 0 end) as "06",
sum(case when "Day" = '07' then "Actual Work Hours" else 0 end) as "07",
sum(case when "Day" = '08' then "Actual Work Hours" else 0 end) as "08",
sum(case when "Day" = '09' then "Actual Work Hours" else 0 end) as "09",
sum(case when "Day" = '10' then "Actual Work Hours" else 0 end) as "10",
sum(case when "Day" = '11' then "Actual Work Hours" else 0 end) as "11",
sum(case when "Day" = '12' then "Actual Work Hours" else 0 end) as "12",
sum(case when "Day" = '13' then "Actual Work Hours" else 0 end) as "13",
sum(case when "Day" = '14' then "Actual Work Hours" else 0 end) as "14",
sum(case when "Day" = '15' then "Actual Work Hours" else 0 end) as "15",
sum(case when "Day" = '16' then "Actual Work Hours" else 0 end) as "16",
sum(case when "Day" = '17' then "Actual Work Hours" else 0 end) as "17",
sum(case when "Day" = '18' then "Actual Work Hours" else 0 end) as "18",
sum(case when "Day" = '19' then "Actual Work Hours" else 0 end) as "19",
sum(case when "Day" = '20' then "Actual Work Hours" else 0 end) as "20",
sum(case when "Day" = '21' then "Actual Work Hours" else 0 end) as "21",
sum(case when "Day" = '22' then "Actual Work Hours" else 0 end) as "22",
sum(case when "Day" = '23' then "Actual Work Hours" else 0 end) as "23",
sum(case when "Day" = '24' then "Actual Work Hours" else 0 end) as "24",
sum(case when "Day" = '25' then "Actual Work Hours" else 0 end) as "25",
sum(case when "Day" = '26' then "Actual Work Hours" else 0 end) as "26",
sum(case when "Day" = '27' then "Actual Work Hours" else 0 end) as "27",
sum(case when "Day" = '28' then "Actual Work Hours" else 0 end) as "28",
sum(case when "Day" = '29' then "Actual Work Hours" else 0 end) as "29",
sum(case when "Day" = '30' then "Actual Work Hours" else 0 end) as "30",
sum(case when "Day" = '31' then "Actual Work Hours" else 0 end) as "31"
FROM day_wise
join user_details ud on day_wise."UUID" = ud.uuid
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10, 11, 12
ORDER BY 1,
         2,
         3,
         4,
         5, 6)"QueryTable 1"
```

---

## Talabat Hourly Attendance_Hourly Report.sql

**Tables referenced:** attendance_counts, attended_intervals, base, combined_intervals, hour, location_map, scheduled_intervals, shift_attendance

**Original Query:**

```sql
-- Data Source: Talabat Hourly Attendance
-- Dashboard: Hourly Report
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:55:11
-- ============================================================

WITH base AS
  (SELECT "Shift ID",
          "UUID",
          "Employee Name",
          "Employee ID" AS "Talabat ID",
          "Designation" AS "User Type",
          "Department",
          CASE
              WHEN "Job Type" ILIKE '%3PL' THEN '3PL'
              ELSE 'Talabat'
          END AS "Picker Type",
          CASE
              WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
              WHEN "Job Type" ILIKE '%- 3PL' THEN rtrim("Job Type", '- 3PL')
              ELSE 'Others'
          END AS "Agency",
          "Division" AS "Country",
          "Sub Division" AS "Chain",
          (regexp_matches("Shift Location", '^(\d+)', 'g'))[1] AS "Shift Location ID",
          "Shift Location",
          (regexp_matches("Clockin Geofence", '^(\d+)', 'g'))[1] AS "Clockin Location ID",
          "Clockin Geofence" AS "Clockin Location",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Bahrain',
								 'Jordan',
								 'Egypt') THEN "Scheduled Start Time" + interval '3 hours'
              ELSE "Scheduled Start Time" + interval '4 hours'
          END AS "Scheduled Start Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Bahrain',
								 'Jordan',
								 'Egypt') THEN "Scheduled End Time" + interval '3 hours'
              ELSE "Scheduled End Time" + interval '4 hours'
          END AS "Scheduled End Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Bahrain',
								 'Jordan',
								 'Egypt') THEN "Actual Clockin Time" + interval '3 hours'
              ELSE "Actual Clockin Time" + interval '4 hours'
          END AS "Actual Clockin Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Bahrain',
								 'Jordan',
								 'Egypt') THEN "Actual Clockout Time" + interval '3 hours'
              ELSE "Actual Clockout Time" + interval '4 hours'
          END AS "Actual Clockout Time"
   FROM shift_attendance sa
   WHERE sa.organization = 'talabat-cartwheel'
     AND sa."Shift Location" ~ '^\d+'
     AND sa."Status" != 'On Leave'
     AND date_trunc('Day', "Scheduled Start Time" + interval '3 hours')::date = @{{:Date Range.START}}::date),
     location_map AS
  (SELECT DISTINCT ON ("Location ID") "Location ID",
                      "Location Name",
                      "Country",
                      "Chain"
   FROM
     (SELECT "Shift Location ID" AS "Location ID",
             "Shift Location" AS "Location Name",
             "Country",
             "Chain",
             1 AS priority
      FROM base
      GROUP BY 1,
               2,
               3,
               4
      UNION ALL SELECT "Clockin Location ID" AS "Location ID",
                       "Clockin Location" AS "Location Name",
                       "Country",
                       "Chain",
                       2 AS priority
      FROM base
      GROUP BY 1,
               2,
               3,
               4) combined
   ORDER BY "Location ID",
            priority ),
     scheduled_intervals AS
  (SELECT "UUID",
          "Country",
          "Chain",
          "Shift Location ID",
          "Picker Type",
          generate_series("Scheduled Start Time", LEAST("Scheduled End Time", NOW() AT TIME ZONE 'Asia/Riyadh') - interval '1 hour', interval '1 hour') AS hour
   FROM base),
     attended_intervals AS
  (SELECT "UUID",
          "Country",
          "Chain",
          coalesce("Clockin Location ID", "Shift Location ID") AS "Clockin Location ID",
          "Picker Type",
          generate_series("Actual Clockin Time", COALESCE("Actual Clockout Time", NOW() AT TIME ZONE 'Asia/Riyadh') - interval '1 hour', interval '1 hour') AS hour
   FROM base
   WHERE "Actual Clockin Time" IS NOT NULL),
     combined_intervals AS
  (SELECT COALESCE(si."Country", ai."Country") AS "Country",
          COALESCE(si."Chain", ai."Chain") AS "Chain",
          COALESCE(si."Shift Location ID", ai."Clockin Location ID") AS "Shift Location ID",
          COALESCE(si."Picker Type", ai."Picker Type") AS "Picker Type",
          COALESCE(si.hour, ai.hour) AS hour,
          COUNT(DISTINCT si."UUID") AS users_scheduled,
          COUNT(DISTINCT ai."UUID") AS users_attended
   FROM scheduled_intervals si
   FULL OUTER JOIN attended_intervals ai ON si."Shift Location ID" = ai."Clockin Location ID"
   AND si.hour = ai.hour
   AND si."Country" = ai."Country"
   AND si."Chain" = ai."Chain"
   AND si."Picker Type" = ai."Picker Type"
   GROUP BY 1,
            2,
            3,
            4,
            5),
     attendance_counts AS
  (SELECT "Country",
          "Chain",
          "Shift Location ID" AS "Branch ID",
          hour::date AS "Date",
          EXTRACT(HOUR
                  FROM hour) AS "Hour",
          sum(CASE
                  WHEN "Picker Type" = '3PL' THEN users_scheduled
                  ELSE 0
              END) AS "Scheduled 3PL",
          sum(CASE
                  WHEN "Picker Type" = '3PL' THEN users_attended
                  ELSE 0
              END) AS "Attended 3PL",
          sum(CASE
                  WHEN "Picker Type" = 'Talabat' THEN users_scheduled
                  ELSE 0
              END) AS "Scheduled Talabat",
          sum(CASE
                  WHEN "Picker Type" = 'Talabat' THEN users_attended
                  ELSE 0
              END) AS "Attended Talabat"
   FROM combined_intervals
   GROUP BY 1,
            2,
            3,
            4,
            5)
SELECT lm."Country",
       lm."Chain",
       atc."Branch ID",
       lm."Location Name" AS "Branch Name",
       "Date",
       to_char("Date", 'Dy') AS "DoW",
       "Hour",
       "Scheduled Talabat"::numeric AS "Scheduled Talabat",
       "Attended Talabat"::numeric AS "Attended Talabat",
       "Scheduled 3PL"::numeric AS "Scheduled 3PL",
       "Attended 3PL"::numeric AS "Attended 3PL",
       ("Scheduled Talabat"+"Scheduled 3PL")::numeric AS "Scheduled Total",
       ("Attended Talabat" + "Attended 3PL")::numeric AS "Attended Total",
       CASE
           WHEN "Scheduled Talabat" = 0 THEN NULL
           WHEN "Attended Talabat" >= "Scheduled Talabat" THEN 1.0
           ELSE 0.0
       END AS "Talabat Fulfilled ",
       CASE
           WHEN "Scheduled 3PL" = 0 THEN NULL
           WHEN "Attended 3PL" >= "Scheduled 3PL" THEN 1.0
           ELSE 0.0
       END AS "3PL Fulfilled",
       CASE
           WHEN "Scheduled 3PL" + "Scheduled Talabat" = 0 THEN NULL
           WHEN "Attended 3PL" + "Attended Talabat" >= "Scheduled 3PL" + "Scheduled Talabat" THEN 1.0
           ELSE 0.0
       END AS "Total Fulfilled",
       CASE
           WHEN "Date" + interval '1 hour'*"Hour" <= CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Riyadh'
                AND "Scheduled Talabat" > 0 THEN "Attended Talabat"/"Scheduled Talabat"
           ELSE NULL
       END AS "Talabat Attendance %",
       CASE
           WHEN "Date" + interval '1 hour'*"Hour" <= CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Riyadh'
                AND "Scheduled 3PL" > 0 THEN "Attended 3PL"/"Scheduled 3PL"
           ELSE NULL
       END AS "3PL Attendance %",
       CASE
           WHEN "Date" + interval '1 hour'*"Hour" <= CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Riyadh'
                AND "Scheduled Talabat"+"Scheduled 3PL" > 0 THEN ("Attended Talabat"+"Attended 3PL")/("Scheduled Talabat" + "Scheduled 3PL")
           ELSE NULL
       END AS "Total Attendance %",
	   to_char(@{{:Date Range.START}}::date, 'DD-Mon, YYYY') as "Selected Date"
FROM attendance_counts atc
LEFT JOIN location_map lm ON atc."Branch ID" = lm."Location ID"
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
         13,
		 14
HAVING "Date" IS NOT NULL
ORDER BY 4,
         7
```

---

## Talabat Mimar Roster Dashboard_Mimar - Roster Dashboard.sql

**Tables referenced:** LATERAL, base, fci_edit, first_clock_in, last_clock_out, lco_edit, shift_attendance, time_events_clockin, time_events_clockout, user_details

**Columns needing snake_case conversion:**

- `editedAt` -> `edited_at` (alias: `edited_at AS "editedAt"`)

- `editedByUsername` -> `edited_by_username` (alias: `edited_by_username AS "editedByUsername"`)

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)

- `originalDeviceTime` -> `original_device_time` (alias: `original_device_time AS "originalDeviceTime"`)


**Original Query:**

```sql
-- Data Source: Talabat Mimar Roster Dashboard
-- Dashboard: Mimar - Roster Dashboard
-- Category: Talabat Attendance
-- Extracted: 2026-01-29 16:53:26
-- ============================================================

 SELECT
		"QueryTable 1"."Shift ID" AS "Shift ID",
		"QueryTable 1"."Shift Name" AS "Shift Name",
		"QueryTable 1"."Leave Tags" AS "Leave Tags",
		"QueryTable 1"."UUID" AS "UUID",
		"QueryTable 1"."Employee Name" AS "Employee Name",
		"QueryTable 1"."Talabat ID" AS "Talabat ID",
		"QueryTable 1"."User Type" AS "User Type",
		"QueryTable 1"."Department" AS "Department",
		"QueryTable 1"."Picker Type" AS "Picker Type",
		"QueryTable 1"."Agency" AS "Agency",
		"QueryTable 1"."Country" AS "Country",
		"QueryTable 1"."Chain" AS "Chain",
		"QueryTable 1"."Shift Branch ID" AS "Shift Branch ID",
		"QueryTable 1"."Shift Branch Name" AS "Shift Branch Name",
		"QueryTable 1"."Shift Location" AS "Shift Location",
		"QueryTable 1"."Clockin Location" AS "Clockin Location",
		"QueryTable 1"."Clockout Location" AS "Clockout Location",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Scheduled Start Time" AS "Scheduled Start Time",
		"QueryTable 1"."Scheduled End Time" AS "Scheduled End Time",
		"QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
		"QueryTable 1"."Scheduled Hours incl Break" AS "Scheduled Hours incl Break",
		"QueryTable 1"."Scheduled Hours excl Break" AS "Scheduled Hours excl Break",
		"QueryTable 1"."Actual Clockin Time" AS "Actual Clockin Time",
		"QueryTable 1"."Actual Clockout Time" AS "Actual Clockout Time",
		"QueryTable 1"."Actual Break Hours" AS "Actual Break Hours",
		"QueryTable 1"."Actual Work Duration" AS "Actual Work Duration",
		"QueryTable 1"."Late Mins" AS "Late Mins",
		"QueryTable 1"."Late Hours" AS "Late Hours",
		"QueryTable 1"."Early Clockout Hours" AS "Early Clockout Hours",
		"QueryTable 1"."Scheduled Count" AS "Scheduled Count",
		"QueryTable 1"."Leave Count" AS "Leave Count",
		"QueryTable 1"."Present Count" AS "Present Count",
		"QueryTable 1"."Absent Count" AS "Absent Count",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Modified Status" AS "Modified Status",
		"QueryTable 1"."Selfie Status" AS "Selfie Status",
		"QueryTable 1"."Selfie Image Link" AS "Selfie Image Link",
		"QueryTable 1"."Overtime Hours" AS "Overtime Hours",
		"QueryTable 1"."Overtime Count" AS "Overtime Count",
		"QueryTable 1"."Undertime Hours" AS "Undertime Hours",
		"QueryTable 1"."Undertime Count" AS "Undertime Count",
		"QueryTable 1"."Late Count" AS "Late Count",
		"QueryTable 1"."Early Clockout Count" AS "Early Clockout Count",
		"QueryTable 1"."First CI Edited At" AS "First CI Edited At",
		"QueryTable 1"."First CI Edited By" AS "First CI Edited By",
		"QueryTable 1"."Original First CI" AS "Original First CI",
		"QueryTable 1"."Last CO Edited At" AS "Last CO Edited At",
		"QueryTable 1"."Last CO Edited By" AS "Last CO Edited By",
		"QueryTable 1"."Original Last CO" AS "Original Last CO",
		"QueryTable 1"."CI-CO Same Location?" AS "CI-CO Same Location?"
FROM(WITH base AS
  (SELECT "Shift ID",
   "Shift Name",
   InitCap(CASE
                                                       WHEN "Status" = 'On Leave'
                                                            THEN substring("Shift ID", 11 + length("Shift Location"), length("Shift ID") - length("UUID") - length("Shift Location")-11)
                                                       ELSE NULL
                                                   END) AS "Leave Tags",
          "UUID",
          "Employee Name",
          "Employee ID" AS "Talabat ID",
          "Designation" AS "User Type",
          "Department",
          CASE
              WHEN "Job Type" ILIKE '%3PL' THEN '3PL'
              ELSE 'Talabat'
          END AS "Picker Type",
          CASE
              WHEN "Job Type" NOT ILIKE '%3PL' THEN 'Talabat'
              WHEN "Job Type" ILIKE '%- 3PL' THEN rtrim("Job Type", '- 3PL')
              ELSE 'Others'
          END AS "Agency",
          "Division" AS "Country",
          "Sub Division" AS "Chain",
          branch.branch_id AS "Shift Branch ID",
          branch.branch_name AS "Shift Branch Name",
          "Shift Location",
          "Clockin Geofence" AS "Clockin Location",
          "Clockout Geofence" AS "Clockout Location",
          "Status",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Scheduled Start Time" + interval '3 hours'
              ELSE "Scheduled Start Time" + interval '4 hours'
          END AS "Scheduled Start Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Scheduled End Time" + interval '3 hours'
              ELSE "Scheduled End Time" + interval '4 hours'
          END AS "Scheduled End Time",
          "Scheduled Break Hours",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600
              ELSE 0
          END AS "Scheduled Hours incl Break",
          CASE
              WHEN "Status" != 'On Leave' THEN ((extract(epoch
                                                         FROM "Scheduled End Time"))::numeric - (extract(epoch
                                                                                                         FROM "Scheduled Start Time"))::numeric)/3600 - "Scheduled Break Hours"
              ELSE 0
          END AS "Scheduled Hours excl Break",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Actual Clockin Time" + interval '3 hours'
              ELSE "Actual Clockin Time" + interval '4 hours'
          END AS "Actual Clockin Time",
          CASE
              WHEN "Division" IN ('Qatar',
                                  'Kuwait',
                                  'Egypt',
                                  'Bahrain',
                                  'Oman',
                                  'Jordan') THEN "Actual Clockout Time" + interval '3 hours'
              ELSE "Actual Clockout Time" + interval '4 hours'
          END AS "Actual Clockout Time",
          "Actual Break Hours",
          "Actual Work Duration",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ((extract(epoch
                                                                                                          FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                           FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/60
              ELSE 0
          END AS "Late Mins",
          CASE
              WHEN "Actual Clockin Time" IS NOT NULL
                   AND "Actual Clockin Time" > "Scheduled Start Time" + interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                  FROM "Actual Clockin Time"))::numeric - (extract(epoch
                                                                                                                                                                   FROM "Scheduled Start Time" + interval '15 mins'))::numeric)/3600)
              ELSE 0
          END AS "Late Hours",
          CASE
              WHEN "Actual Clockout Time" IS NOT NULL
                   AND "Actual Clockout Time" < "Scheduled End Time" - interval '15 mins' THEN ceiling(((extract(epoch
                                                                                                                 FROM "Scheduled End Time" - interval '15 mins'))::numeric - (extract(epoch
                                                                                                                                                                                      FROM "Actual Clockout Time"))::numeric)/3600)
              ELSE 0
          END AS "Early Clockout Hours",
          "Scheduled Count",
          "Leave Count",
          "Present Count",
          "Absent Count"
   FROM shift_attendance sa
   LEFT JOIN LATERAL
     (SELECT 
    (regexp_matches(sa."Shift Location", '^(\d+)', 'g'))[1] AS branch_id,
    regexp_replace(sa."Shift Location", '^\d+\s*-\s*(.*)', '\1') AS branch_name
      WHERE sa."Shift Location" ~ '^\d+' ) branch ON TRUE
   WHERE organization = 'talabat-cartwheel'
     AND "Scheduled Start Time" + interval '3 hours' BETWEEN '2025/11/17'::TIMESTAMP AND '2025/11/23'::TIMESTAMP + INTERVAL '1 hour'
     AND sa."Shift Location" ~ '^\d+'
    ),
     first_clock_in AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.selfie,
   					  tec.details
   FROM time_events_clockin tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND ci_time + interval '3 hours' BETWEEN '2025/11/17'::TIMESTAMP AND '2025/11/23'::TIMESTAMP + INTERVAL '1 hour'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.ci_time),
     fci_edit AS
  (SELECT fci.shift_id,
          fci.uuid,
          to_timestamp((fci.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             fci.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((fci.details->>'originalDeviceTime')::bigint/1000) AS original_ci_time
   FROM first_clock_in fci
   WHERE fci.details->>'isEdited' = 'true'),
     last_clock_out AS
  (SELECT DISTINCT ON (tec.shift_id,
                       tec.uuid) tec.shift_id,
                      tec.uuid,
                      tec.details
   FROM time_events_clockout tec
   JOIN user_details ud ON tec.uuid = ud.uuid
   WHERE ud.organization = 'talabat-cartwheel'
     AND co_time + interval '3 hours' BETWEEN '2025/11/17'::TIMESTAMP AND '2025/11/23'::TIMESTAMP + INTERVAL '1 day'
   ORDER BY tec.shift_id,
            tec.uuid,
            tec.co_time DESC),
     lco_edit AS
  (SELECT lco.shift_id,
          lco.uuid,
          to_timestamp((lco.details->>'editedAt')::bigint/1000) AS edited_at,
                                                                             lco.details->>'editedByUsername' AS edited_by,
                                                                                           to_timestamp((lco.details->>'originalDeviceTime')::bigint/1000) AS original_co_time
   FROM last_clock_out lco
   WHERE lco.details->>'isEdited' = 'true')
SELECT base.*, Coalesce("Shift Name", "Leave Tags") as "Shift",
       CASE
           WHEN "Status" IN ('On Leave',
                             'Absent') THEN "Status"
           WHEN "Late Mins" > 0 THEN 'Present - Late'
           ELSE 'Present - On Time'
       END AS "Modified Status",
       CASE
           WHEN (fci.selfie ILIKE '%Photofailed%' or fci.selfie is null) THEN 'No Selfie Image'
           ELSE 'Selfie Available'
       END AS "Selfie Status",
	   fci.selfie as "Selfie Image Link",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN ceiling("Actual Work Duration" - "Scheduled Hours excl Break" - (1/6))
           ELSE 0
       END AS "Overtime Hours",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" > "Scheduled Hours excl Break" + (1/6)
                AND "Actual Clockout Time" > "Scheduled End Time" + interval '10 mins' THEN 1
           ELSE 0
       END AS "Overtime Count",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN ceiling("Scheduled Hours excl Break" - "Actual Work Duration" - (1/6))
           ELSE 0
       END AS "Undertime Hours",
       CASE
           WHEN "Actual Work Duration" > 0
                AND "Actual Work Duration" < "Scheduled Hours excl Break" - (1/6) THEN 1
           ELSE 0
       END AS "Undertime Count",
       CASE
           WHEN "Late Hours" > 0 THEN 1
           ELSE 0
       END AS "Late Count",
       CASE
           WHEN "Early Clockout Hours" > 0 THEN 1
           ELSE 0
       END AS "Early Clockout Count",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN fci_edit.edited_at + interval '3 hours'
           ELSE fci_edit.edited_at + interval '4 hours'
       END AS "First CI Edited At",
       fci_edit.edited_by AS "First CI Edited By",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN fci_edit.original_ci_time + interval '3 hours'
           ELSE fci_edit.original_ci_time + interval '4 hours'
       END AS "Original First CI",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN lco_edit.edited_at + interval '3 hours'
           ELSE lco_edit.edited_at + interval '4 hours'
       END AS "Last CO Edited At",
       lco_edit.edited_by AS "Last CO Edited By",
       CASE
           WHEN "Country" IN ('Qatar',
                               'Kuwait',
                               'Egypt',
                               'Bahrain',
                               'Oman',
                               'Jordan') THEN lco_edit.original_co_time + interval '3 hours'
           ELSE lco_edit.original_co_time + interval '4 hours'
       END AS "Original Last CO",
	   case when base."Clockin Location" !=  base."Clockout Location" then 'Different' else 'Same' end as "CI-CO Same Location?"
FROM base
LEFT OUTER JOIN first_clock_in fci ON base."Shift ID" = fci.shift_id
AND base."UUID" = fci.uuid
LEFT OUTER JOIN fci_edit ON base."Shift ID" = fci_edit.shift_id
AND base."UUID" = fci_edit.uuid
LEFT OUTER JOIN lco_edit ON base."Shift ID" = lco_edit.shift_id
AND base."UUID" = lco_edit.uuid
WHERE base."Department" ilike '%Mimar%'
ORDER BY 10,
         11,
         12,
         19,
         9,
         4)"QueryTable 1"
```

---
