# PopEyes

> Auto-generated on 2026-03-04 08:13

**Total queries:** 3

---

## PopEyes Attendance Monthly Summary_Attendance Summary.sql

**Tables referenced:** base, shift_attendance, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: PopEyes Attendance Monthly Summary
-- Dashboard: Attendance Summary
-- Category: PopEyes
-- Extracted: 2026-01-29 16:58:11
-- ============================================================

WITH user_acl AS
  (SELECT uuid,
                   organization
   FROM user_details
   WHERE organization = 'popeyes-fw'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
  and phone_number not ilike '+9111%'),
  base AS
  (SELECT to_char("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore', 'Mon-YYYY') AS "Month",
          to_char("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore', 'DD') AS "Date",
          sa."Employee Name",
          sa."Employee ID",
   sa."Job Type",
   sa."Home Location",
   sa."Shift Location",
          max(CASE
                  WHEN sa."Status" ILIKE 'Present%' THEN "Shift Location"
                  WHEN sa."Status" = 'Absent' THEN 'ABS'
                  WHEN sa."Status" = 'On Leave'
                       AND substring("Shift ID", 12, 1) = '-' THEN 'Leave: '||replace(InitCap(substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)), '-', ' ')
                  WHEN "Status" = 'On Leave'
                       AND substring("Shift ID", 12, 1) != '-' THEN 'Leave: '||replace(InitCap(substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)), '-', ' ')
                  ELSE NULL
              END) AS "Status"
   FROM shift_attendance sa
   JOIN user_details ud ON sa."UUID" = ud.uuid
    JOIN user_acl ON sa."UUID" = user_acl.uuid
   WHERE sa.organization = 'popeyes-fw'
     AND sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
     AND sa."Shift Location" in (@{{:Location}})
     AND sa."Job Type" in (@{{:Job Type}})
   GROUP BY 1,
            2,
            3,
            4, 5, 6, 7
   ORDER BY 1,
            2,
            3)
SELECT "Month",
       "Employee Name",
       "Employee ID",
	   "Job Type",
	   "Home Location",
       max(CASE
               WHEN "Date" = '01' THEN "Status"
               ELSE NULL
           END) AS "01",
       max(CASE
               WHEN "Date" = '02' THEN "Status"
               ELSE NULL
           END) AS "02",
       max(CASE
               WHEN "Date" = '03' THEN "Status"
               ELSE NULL
           END) AS "03",
       max(CASE
               WHEN "Date" = '04' THEN "Status"
               ELSE NULL
           END) AS "04",
       max(CASE
               WHEN "Date" = '05' THEN "Status"
               ELSE NULL
           END) AS "05",
       max(CASE
               WHEN "Date" = '06' THEN "Status"
               ELSE NULL
           END) AS "06",
       max(CASE
               WHEN "Date" = '07' THEN "Status"
               ELSE NULL
           END) AS "07",
       max(CASE
               WHEN "Date" = '08' THEN "Status"
               ELSE NULL
           END) AS "08",
       max(CASE
               WHEN "Date" = '09' THEN "Status"
               ELSE NULL
           END) AS "09",
       max(CASE
               WHEN "Date" = '10' THEN "Status"
               ELSE NULL
           END) AS "10",
       max(CASE
               WHEN "Date" = '11' THEN "Status"
               ELSE NULL
           END) AS "11",
       max(CASE
               WHEN "Date" = '12' THEN "Status"
               ELSE NULL
           END) AS "12",
       max(CASE
               WHEN "Date" = '13' THEN "Status"
               ELSE NULL
           END) AS "13",
       max(CASE
               WHEN "Date" = '14' THEN "Status"
               ELSE NULL
           END) AS "14",
       max(CASE
               WHEN "Date" = '15' THEN "Status"
               ELSE NULL
           END) AS "15",
       max(CASE
               WHEN "Date" = '16' THEN "Status"
               ELSE NULL
           END) AS "16",
       max(CASE
               WHEN "Date" = '17' THEN "Status"
               ELSE NULL
           END) AS "17",
       max(CASE
               WHEN "Date" = '18' THEN "Status"
               ELSE NULL
           END) AS "18",
       max(CASE
               WHEN "Date" = '19' THEN "Status"
               ELSE NULL
           END) AS "19",
       max(CASE
               WHEN "Date" = '20' THEN "Status"
               ELSE NULL
           END) AS "20",
       max(CASE
               WHEN "Date" = '21' THEN "Status"
               ELSE NULL
           END) AS "21",
       max(CASE
               WHEN "Date" = '22' THEN "Status"
               ELSE NULL
           END) AS "22",
       max(CASE
               WHEN "Date" = '23' THEN "Status"
               ELSE NULL
           END) AS "23",
       max(CASE
               WHEN "Date" = '24' THEN "Status"
               ELSE NULL
           END) AS "24",
       max(CASE
               WHEN "Date" = '25' THEN "Status"
               ELSE NULL
           END) AS "25",
       max(CASE
               WHEN "Date" = '26' THEN "Status"
               ELSE NULL
           END) AS "26",
       max(CASE
               WHEN "Date" = '27' THEN "Status"
               ELSE NULL
           END) AS "27",
       max(CASE
               WHEN "Date" = '28' THEN "Status"
               ELSE NULL
           END) AS "28",
       max(CASE
               WHEN "Date" = '29' THEN "Status"
               ELSE NULL
           END) AS "29",
       max(CASE
               WHEN "Date" = '30' THEN "Status"
               ELSE NULL
           END) AS "30",
       max(CASE
               WHEN "Date" = '31' THEN "Status"
               ELSE NULL
           END) AS "31"
FROM base
GROUP BY 1,
         2,
         3, 4, 5
ORDER BY 1,
         2
```

---

## PopEyes Attendance Report_Attendance Report.sql

**Tables referenced:** base, base_sum, edited, shift_attendance, time_events_clockin, time_events_clockout, user_Details, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `isEdited` -> `is_edited` (alias: `is_edited AS "isEdited"`)


**Original Query:**

```sql
-- Data Source: PopEyes Attendance Report
-- Dashboard: Attendance Report
-- Category: PopEyes
-- Extracted: 2026-01-29 16:58:05
-- ============================================================

WITH user_acl AS
  (SELECT uuid,
                   organization
   FROM user_details
   WHERE organization = 'popeyes-fw'
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
  and phone_number not ilike '+9111%'),
  edited as (select teci.shift_id, teci.uuid as user_id, case when teci.details->>'isEdited' = 'true' or teco.details->>'isEdited' = 'true' then 'Yes' else 'No' end as is_edited
			 from time_events_clockin teci 
			 join time_events_clockout teco on teci.shift_id = teco.shift_id and teci.event_id = teco.ci_event_id
			 join user_Details ud on teci.uuid = ud.uuid
			 where ud.organization = 'popeyes-fw'
			 and teci.ci_time AT TIME ZONE 'Asia/Singapore' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP+ INTERVAL '1 day'),
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
          sa."Department",
          sa."Designation",
          COALESCE(NULLIF(regexp_replace(sa."Job Type", '[^0-9]', '', 'g'), ''), '44')::int AS "Hours Limit",
          extract('week'
                  FROM "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') AS "Week No",
          sa."Status",
          InitCap(CASE
                      WHEN "Status" = 'On Leave'
                           AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                      WHEN "Status" = 'On Leave'
                           AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                      ELSE NULL
                  END) AS "Leave Type",
          ("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')::date AS "Date",
          to_char("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore', 'Dy') AS "Day",
          CASE
              WHEN sa."Status" NOT IN ('On Leave') THEN "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
              ELSE NULL
          END AS "Scheduled In",
          CASE
              WHEN sa."Status" NOT IN ('On Leave') THEN "Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
              ELSE NULL
          END AS "Scheduled Out",
          CASE
              WHEN sa."Status" NOT IN ('On Leave',
                                       'Absent') THEN "Actual Clockin Time" AT TIME ZONE 'Asia/Singapore'
              ELSE NULL
          END AS "Time In",
          CASE
              WHEN sa."Status" NOT IN ('On Leave',
                                       'Absent') THEN "Actual Clockout Time" AT TIME ZONE 'Asia/Singapore'
              ELSE NULL
          END AS "Time Out",
          CASE
              WHEN sa."Status" IN ('On Leave',
                                   'Absent') THEN NULL
              ELSE greatest(sa."Actual Clockin Time" AT TIME ZONE 'Asia/Singapore', sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')
          END AS "Adjusted Time In",
          CASE
              WHEN sa."Status" NOT IN ('On Leave',
                                       'Absent') THEN sa."Actual Break Hours"
              ELSE NULL
          END AS "Actual Break Hours",
          CASE
              WHEN sa."Status" NOT IN ('On Leave') THEN extract(epoch
                                                                FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Scheduled Start Time" AT TIME ZONE 'UTC' - interval '1 hour'*sa."Scheduled Break Hours"))/3600
              ELSE NULL
          END AS "Scheduled Hours",
          CASE
              WHEN sa."Status" NOT IN ('On Leave') THEN sa."Scheduled Break Hours"
              ELSE NULL
          END AS "Scheduled Break Hours",
          CASE
              WHEN sa."Status" NOT IN ('On Leave',
                                       'Absent') THEN extract(epoch
                                                              FROM (sa."Actual Clockout Time" - greatest(sa."Actual Clockin Time", sa."Scheduled Start Time" AT TIME ZONE 'UTC')))/3600
              ELSE NULL
          END AS "Normal Hours",
          CASE
              WHEN sa."Status" IN ('Absent') THEN NULL
              WHEN sa."Status" IN ('On Leave')
                   AND ((CASE
                             WHEN "Status" = 'On Leave'
                                  AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                             WHEN "Status" = 'On Leave'
                                  AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                             ELSE NULL
                         END) ILIKE '%NoPay%'
                        OR (CASE
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                                ELSE NULL
                            END) ILIKE '%Unpaid%'
                        OR (CASE
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                                ELSE NULL
                            END) ILIKE '%Off-Day%'
					   OR (CASE
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) = '-' THEN substring("Shift ID", 13, length("Shift ID") - length("UUID")-13)
                                WHEN "Status" = 'On Leave'
                                     AND substring("Shift ID", 12, 1) != '-' THEN substring("Shift ID", 14, length("Shift ID") - length("UUID")-14)
                                ELSE NULL
                            END) ILIKE '%Rest%') THEN NULL
              WHEN sa."Status" IN ('On Leave') THEN 7.33
              ELSE extract(epoch
                           FROM (sa."Actual Clockout Time" - greatest(sa."Actual Clockin Time", sa."Scheduled Start Time" AT TIME ZONE 'UTC')))/3600 - greatest(sa."Actual Break Hours", sa."Scheduled Break Hours")
          END AS "Actual Hours",
          CASE
              WHEN sa."Status" IN ('On Leave',
                                   'Absent') THEN NULL
              ELSE CASE
                       WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC') THEN CEIL(EXTRACT(EPOCH FROM (sa."Actual Clockin Time" - sa."Scheduled Start Time" AT TIME ZONE 'UTC')) / 900.0) * 15/60
                       ELSE NULL
                   END
          END AS "Late In Hours",
          CASE
              WHEN sa."Status" IN ('On Leave',
                                   'Absent') THEN NULL
              ELSE CASE
                       WHEN sa."Actual Clockout Time" < (sa."Scheduled End Time" AT TIME ZONE 'UTC') THEN CEIL(EXTRACT(EPOCH FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Actual Clockout Time")) / 900.0) * 15/60
                       ELSE NULL
                   END
          END AS "Early Out Hours"
   FROM shift_attendance sa
   JOIN user_details ud ON sa."UUID" = ud.uuid
   JOIN user_acl ON sa."UUID" = user_acl.uuid
   WHERE sa.organization = 'popeyes-fw'
     AND sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP+ INTERVAL '1 day'
  and sa."Job Type" in (@{{:Job Type}})
   and sa."Shift Location" in (@{{:Location}})),
     base_sum AS
  (SELECT *,
          sum("Actual Hours") OVER (PARTITION BY "UUID",
                                                 "Week No"
                                    ORDER BY "Date") AS total_week_hours_to_date
   FROM base)
SELECT "UUID",
       "Shift ID",
       "Date",
       "Day",
       "Employee Name",
       "Employee ID",
       "Division",
       "Sub Division",
       "Job Type",
       "Designation",
       "Home Location",
       "Shift Location",
       "Department",
       "Status",
       replace("Leave Type", '-', ' ') as "Leave Type",
       "Scheduled In",
       "Scheduled Out",
       "Time In",
       "Time Out",
       "Scheduled Hours",
       "Scheduled Break Hours",
       "Normal Hours",
       "Late In Hours",
       "Early Out Hours",
       CASE
           WHEN ("Job Type" ILIKE 'FT%'
                 OR "Job Type" ILIKE 'Full%')
                AND total_week_hours_to_date <= "Hours Limit" THEN "Actual Hours"
           WHEN ("Job Type" ILIKE 'FT%'
                 OR "Job Type" ILIKE 'Full%')
                AND total_week_hours_to_date > "Hours Limit" THEN greatest("Hours Limit" - (total_week_hours_to_date - "Actual Hours"), 0)
           ELSE "Actual Hours"
       END AS "Actual Hours",
       CASE
           WHEN ("Job Type" ILIKE 'FT%'
                 OR "Job Type" ILIKE 'Full%')
                AND total_week_hours_to_date - "Actual Hours" > "Hours Limit"
                AND "Actual Hours" > 0 THEN FLOOR("Actual Hours" * 2) / 2
           WHEN ("Job Type" ILIKE 'FT%'
                 OR "Job Type" ILIKE 'Full%')
                AND total_week_hours_to_date > "Hours Limit"
                AND "Actual Hours" > 0 THEN FLOOR((total_week_hours_to_date - "Hours Limit") * 2) / 2
           ELSE NULL
       END AS "Overtime Hours",
	   edited.is_edited as "Is Edited?"
FROM base_sum
left outer join edited on base_sum."Shift ID" = edited.shift_id and base_sum."UUID" = edited.user_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 ,16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27
ORDER BY 5,
         3
```

---

## PopEyes Staff Tenure_Staff Tenure.sql

**Tables referenced:** to_date, user_details

**Columns needing snake_case conversion:**

- `otherDetails` -> `other_details` (alias: `other_details AS "otherDetails"`)


**Original Query:**

```sql
-- Data Source: PopEyes Staff Tenure
-- Dashboard: Staff Tenure
-- Category: PopEyes
-- Extracted: 2026-01-29 16:55:24
-- ============================================================

SELECT first_name||' '||last_name AS "Name",
       identifier AS "Identifier",
       department AS "Department",
       designation AS "Designation",
       division AS "Division",
       sub_division AS "Sub Division",
       job_location AS "Home Location",
       job_type AS "Job Type",
       phone_number AS "Phone Number",
       to_date(PROFILE->'otherDetails'->>'DOJ', 'YYYY-MM-DD') AS "DoJ",
         floor( ( (EXTRACT(EPOCH FROM (to_Date((CURRENT_Date AT TIME ZONE 'Asia/Singapore')::text, 'YYYY-MM-DD')))
          - EXTRACT(EPOCH FROM to_date(PROFILE->'otherDetails'->>'DOJ', 'YYYY-MM-DD')))
          ::int ) / 31557600 )::int || 'y ' ||
  floor( ( ((EXTRACT(EPOCH FROM (to_Date((CURRENT_Date AT TIME ZONE 'Asia/Singapore')::text, 'YYYY-MM-DD')))
          - EXTRACT(EPOCH FROM to_date(PROFILE->'otherDetails'->>'DOJ', 'YYYY-MM-DD')))
          ::int) % 31557600) / 2629800 )::int || 'm ' ||
  floor( ( (((EXTRACT(EPOCH FROM (to_Date((CURRENT_Date AT TIME ZONE 'Asia/Singapore')::text, 'YYYY-MM-DD')))
          - EXTRACT(EPOCH FROM to_date(PROFILE->'otherDetails'->>'DOJ', 'YYYY-MM-DD')))
          ::int) % 31557600) % 2629800) / 86400 )::int || 'd' as "Tenure"
FROM user_details
WHERE organization ILIKE 'Pop%'
  AND is_active = 'true'
  AND PROFILE->'otherDetails'->>'DOJ' IS NOT NULL
ORDER BY 5,
         6,
         7,
         3,
         4,
         1
```

---
