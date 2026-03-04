# Da Paolo

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Da Paolo Certifications Expiry Alert_Da Paolo Certifications Expiry Alert.sql

**Tables referenced:** user_details

**Original Query:**

```sql
-- Data Source: Da Paolo Certifications Expiry Alert
-- Dashboard: Da Paolo Certifications Expiry Alert
-- Category: Da Paolo
-- Extracted: 2026-01-29 16:55:29
-- ============================================================

SELECT emp_name AS "Employee Name",
       identifier AS "Employee ID",
       division AS "Division",
       sub_division AS "Sub Division",
       job_location AS "Location",
       designation AS "Designation",
       department AS "Department",
       job_type AS "Job Type",
       certification_details ->> 'name' AS "Certification",
                                 to_date(certification_details ->> 'value', 'YYYY-MM-DD') as "Expiry"
FROM
  (SELECT first_name||' '||last_name AS emp_name,
          identifier,
          division,
          sub_division,
          job_location,
          job_type,
          designation,
          department,
          jsonb_array_elements(PROFILE -> 'certifications') AS certification_details
   FROM user_details
   WHERE is_active = 'true'
     AND organization ILIKE 'Da-paolo%'
     AND PROFILE -> 'certifications' IS NOT NULL
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            user_details.profile) base
WHERE certification_details ->> 'type' = 'certifications'
  AND certification_details ->> 'value'IS NOT NULL
  AND to_date(certification_details ->> 'value', 'YYYY-MM-DD') <= date_trunc('Day', current_timestamp + interval '2 months')
ORDER BY 1,
         2,
         10
```

---

## Da Paolo Shift Report_Da Paolo Attendance Report.sql

**Tables referenced:** base, base_sum, sa, shift_attendance, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherDetails` -> `other_details` (alias: `other_details AS "otherDetails"`)


**Original Query:**

```sql
-- Data Source: Da Paolo Shift Report
-- Dashboard: Da Paolo Attendance Report
-- Category: Da Paolo
-- Extracted: 2026-01-29 16:52:22
-- ============================================================

SELECT
    "QueryTable 1"."UUID" AS "UUID",
    "QueryTable 1"."Shift ID" AS "Shift ID",
    "QueryTable 1"."Scheduled Start for Date Filter" AS "Scheduled Start for Date Filter",
    "QueryTable 1"."Employee Name" AS "Employee Name",
    "QueryTable 1"."Employee ID" AS "Employee ID",
    "QueryTable 1"."NRIC" AS "NRIC",
    "QueryTable 1"."Division" AS "Division",
    "QueryTable 1"."Sub Division" AS "Sub Division",
    "QueryTable 1"."Job Type" AS "Job Type",
    "QueryTable 1"."Designation" AS "Designation",
    "QueryTable 1"."Home Location" AS "Home Location",
    "QueryTable 1"."Shift Location" AS "Shift Location",
    "QueryTable 1"."Role" AS "Role",
    "QueryTable 1"."Local / Foreign" AS "Local / Foreign",
    "QueryTable 1"."Special Rates" AS "Special Rates",
    "QueryTable 1"."Status" AS "Status",
    "QueryTable 1"."Leave Tags" AS "Leave Tags",
    "QueryTable 1"."Scheduled In" AS "Scheduled In",
    "QueryTable 1"."Scheduled Out" AS "Scheduled Out",
    "QueryTable 1"."Time In" AS "Time In",
    "QueryTable 1"."Time Out" AS "Time Out",
    "QueryTable 1"."Unpaid Break" AS "Unpaid Break",
    "QueryTable 1"."Scheduled Hours" AS "Scheduled Hours",
    "QueryTable 1"."Scheduled Break Hours" AS "Scheduled Break Hours",
    "QueryTable 1"."Total Paid Hours" AS "Total Paid Hours",
    "QueryTable 1"."Difference" AS "Difference",
    "QueryTable 1"."Basic Hours" AS "Basic Hours",
    "QueryTable 1"."Weekend Hours" AS "Weekend Hours",
    "QueryTable 1"."Event Hours" AS "Event Hours",
    "QueryTable 1"."Overtime Hours" AS "Overtime Hours",
    "QueryTable 1"."Late In Hours" AS "Late In Hours",
    "QueryTable 1"."Excess Break Hours" AS "Excess Break Hours",
    "QueryTable 1"."Early Out Hours" AS "Early Out Hours",
    "QueryTable 1"."Late Out Hours" AS "Late Out Hours",
    "QueryTable 1"."Late Shifts" AS "Late Shifts",
    "QueryTable 1"."Absent Shifts" AS "Absent Shifts",
    "QueryTable 1"."Early Out Shifts" AS "Early Out Shifts",
    "QueryTable 1"."Night Shift Allowance" AS "Night Shift Allowance"
FROM(WITH user_acl AS
  (SELECT uuid,
                   organization
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
  and phone_number not ilike '+9111%'),
  base AS
  (SELECT sa."Shift ID",
       sa."UUID",
       sa."Employee Name",
       sa."Division",
       sa."Sub Division",
       sa."Employee ID",
       sa."Job Type",
       ud.job_location AS "Home Location",
       sa."Shift Location",
       sa."Department" AS "Role",
       sa."Designation",
       ud.profile ->'otherDetails'->'ID'->>'type' AS "Local / Foreign",
       ud.profile -> 'otherDetails' -> 'ID' ->> 'number' AS "NRIC",
       extract('week' FROM "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') AS "Week No",
       CASE
           WHEN to_char("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore', 'Dy') IN ('Sat', 'Sun') THEN 'Weekend'
           ELSE NULL
       END AS "Special Rates",
       sa."Status",
       InitCap(CASE
           WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
           WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
           ELSE NULL
       END) AS "Leave Tags",
       "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' AS "Scheduled Start for Date Filter",
       CASE
           WHEN sa."Status" NOT IN ('On Leave') THEN "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
           ELSE NULL
       END AS "Scheduled In",
       CASE
           WHEN sa."Status" NOT IN ('On Leave') THEN "Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
           ELSE NULL
       END AS "Scheduled Out",
       CASE
           WHEN sa."Status" NOT IN ('On Leave', 'Absent') THEN "Actual Clockin Time" AT TIME ZONE 'Asia/Singapore'
           ELSE NULL
       END AS "Time In",
       CASE
           WHEN sa."Status" NOT IN ('On Leave', 'Absent') THEN "Actual Clockout Time" AT TIME ZONE 'Asia/Singapore'
           ELSE NULL
       END AS "Time Out",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins') THEN sa."Actual Clockin Time" AT TIME ZONE 'Asia/Singapore'
               ELSE sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
           END
       END AS "Adjusted Time In",
       CASE
           WHEN sa."Status" NOT IN ('On Leave', 'Absent') THEN sa."Actual Break Hours"
           ELSE NULL
       END AS "Unpaid Break",
       CASE
           WHEN sa."Status" NOT IN ('On Leave') THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Scheduled Start Time" AT TIME ZONE 'UTC' - interval '1 hour'*sa."Scheduled Break Hours"))/3600
           ELSE NULL
       END AS "Scheduled Hours",
       CASE
           WHEN sa."Status" NOT IN ('On Leave') THEN sa."Scheduled Break Hours"
           ELSE NULL
       END AS "Scheduled Break Hours",
       CASE
           WHEN sa."Status" IN ('Absent') THEN NULL
           WHEN sa."Status" IN ('On Leave')
                AND ((CASE
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                    ELSE NULL
                END) ILIKE 'NoPay%'
                OR (CASE
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                    ELSE NULL
                END) ILIKE 'Unpaid%'
                OR (CASE
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                    WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                    ELSE NULL
                END) ILIKE 'Off-Day') THEN NULL
           WHEN sa."Status" IN ('On Leave') THEN 8
           ELSE CASE
               WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins') THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Actual Clockin Time"))/3600 - sa."Actual Break Hours"
               ELSE extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Scheduled Start Time" AT TIME ZONE 'UTC'))/3600 - sa."Actual Break Hours"
           END
       END AS "Total Paid Hours",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins') THEN extract(epoch FROM (sa."Actual Clockin Time" - sa."Scheduled Start Time" AT TIME ZONE 'UTC'))/3600
               ELSE NULL
           END
       END AS "Late In Hours",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Break Hours"*60 > sa."Scheduled Break Hours"*60 + 5 THEN sa."Actual Break Hours" - sa."Scheduled Break Hours"
               ELSE NULL
           END
       END AS "Excess Break Hours",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockout Time" < (sa."Scheduled End Time" AT TIME ZONE 'UTC' - interval '5 mins') THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Actual Clockout Time"))/3600
               ELSE NULL
           END
       END AS "Early Out Hours",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockout Time" > (sa."Scheduled End Time" AT TIME ZONE 'UTC' + interval '10 mins') THEN extract(epoch FROM (sa."Actual Clockout Time" - sa."Scheduled End Time" AT TIME ZONE 'UTC'))/3600
               ELSE NULL
           END
       END AS "Late Out Hours",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins') THEN 1
               ELSE NULL
           END
       END AS "Late Shifts",
       CASE
           WHEN sa."Status" IN ('Absent') THEN 1
           ELSE NULL
       END AS "Absent Shifts",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN sa."Actual Clockout Time" < (sa."Scheduled End Time" AT TIME ZONE 'UTC' - interval '5 mins') THEN 1
               ELSE NULL
           END
       END AS "Early Out Shifts",
       CASE
           WHEN sa."Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE CASE
               WHEN extract('day' FROM sa."Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') > extract('day' FROM sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')
                    AND extract('hour' FROM sa."Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') >= 4 THEN 1
               ELSE NULL
           END
       END AS "Night Shift Allowance"
FROM shift_attendance sa
JOIN user_details ud ON sa."UUID" = ud.uuid
WHERE sa.organization = @{{:OrganizationParameter}}
  AND sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' between date_trunc('week', @{{:Date Range.START}}::timestamp) and @{{:Date Range.END}}::timestamp + interval '1 day') ,
     base_sum AS
  (SELECT *,
          sum("Total Paid Hours") OVER (PARTITION BY "UUID",
                                                     "Week No"
                                        ORDER BY "Scheduled Start for Date Filter") AS total_week_hours_to_date
   FROM base)
SELECT "UUID",
       "Shift ID",
       "Scheduled Start for Date Filter",
       "Employee Name",
       "Employee ID",
       "NRIC",
       "Division",
       "Sub Division",
       "Job Type",
       "Designation",
       "Home Location",
       "Shift Location",
       "Role",
       "Local / Foreign",
       "Special Rates",
       "Status",
       "Leave Tags",
       "Scheduled In",
       "Scheduled Out",
       "Time In",
       "Time Out",
       "Unpaid Break",
       "Scheduled Hours",
       "Scheduled Break Hours",
       "Total Paid Hours",
       CASE
           WHEN "Status" IN ('On Leave', 'Absent') THEN NULL
           ELSE "Total Paid Hours" - "Scheduled Hours"
       END AS "Difference",
       CASE
           WHEN "Special Rates" IS NULL AND total_week_hours_to_date <= 44 THEN "Total Paid Hours"
           WHEN "Special Rates" IS NULL AND total_week_hours_to_date > 44 THEN greatest(44 - (total_week_hours_to_date - "Total Paid Hours"), 0)
           ELSE NULL
       END AS "Basic Hours",
       CASE
           WHEN "Special Rates" = 'Weekend' AND total_week_hours_to_date <= 44 THEN "Total Paid Hours"
           WHEN "Special Rates" = 'Weekend' AND total_week_hours_to_date > 44 THEN greatest(44 - (total_week_hours_to_date - "Total Paid Hours"), 0)
           ELSE NULL
       END AS "Weekend Hours",
       CASE
           WHEN "Special Rates" = 'Event' AND total_week_hours_to_date <= 44 THEN "Total Paid Hours"
           WHEN "Special Rates" = 'Event' AND total_week_hours_to_date > 44 THEN greatest(44 - (total_week_hours_to_date - "Total Paid Hours"), 0)
           ELSE NULL
       END AS "Event Hours",
       CASE
           WHEN total_week_hours_to_date - "Total Paid Hours" > 44 and "Total Paid Hours" > 0 THEN "Total Paid Hours"
           WHEN total_week_hours_to_date > 44 and "Total Paid Hours" > 0 THEN total_week_hours_to_date - 44
           ELSE NULL
       END AS "Overtime Hours",
       "Late In Hours",
       "Excess Break Hours",
       "Early Out Hours",
       "Late Out Hours",
       "Late Shifts",
       "Absent Shifts",
       "Early Out Shifts",
       "Night Shift Allowance"
FROM base_sum
join user_acl on base_sum."UUID" = user_acl.uuid
WHERE "Scheduled Start for Date Filter" >= @{{:Date Range.START}}::timestamp
ORDER BY 5, 3)"QueryTable 1"
```

---
