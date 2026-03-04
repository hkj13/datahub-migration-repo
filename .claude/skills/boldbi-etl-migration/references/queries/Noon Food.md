# Noon Food

> Auto-generated on 2026-03-04 08:13

**Total queries:** 3

---

## Course Report Noon_Learning Journey Dashboard.sql

**Tables referenced:** data_team.noon_ljr, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Course Report Noon
-- Dashboard: Learning Journey Dashboard
-- Category: Noon Food
-- Extracted: 2026-01-29 16:53:28
-- ============================================================

WITH user_acl AS
  (SELECT ud.organization,
          ud.uuid,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type
   FROM user_details ud
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
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
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10)
			select ljr.*
			from data_team.noon_ljr ljr
			JOIN user_acl on ljr.identifier = user_acl.emp_id
			where ljr.ljr_shared_at_local between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## LJR Attempts Noon_Learning Journey Dashboard.sql

**Tables referenced:** analytics.nuggets_user_share_requests, attempt_summary, latest_share_ids, learning_journey_shares, organizations, public.learning_journey, public.learning_journey_courses, quiz.quiz_responses, quiz_attempts, td, user_details

**Original Query:**

```sql
-- Data Source: LJR Attempts Noon
-- Dashboard: Learning Journey Dashboard
-- Category: Noon Food
-- Extracted: 2026-01-29 16:54:02
-- ============================================================

WITH td AS (
    SELECT 
        id AS organization,
        tzoffset, 
        interval '1 min' * tzoffset AS diff
    FROM organizations
    WHERE id = @{{:Course Report Noon.OrganizationParameter}}
),
latest_share_ids AS (
    SELECT DISTINCT ON (nugget_id, user_id)
        nugget_id,
        share_id,
        user_id,
        nusr.created_at AS sent_at
    FROM analytics.nuggets_user_share_requests nusr
    JOIN user_details ud ON nusr.user_id = ud.uuid
    WHERE nusr.created_at BETWEEN @{{:Course Report Noon.Date Range.START}}::TIMESTAMP 
                              AND @{{:Course Report Noon.Date Range.END}}::TIMESTAMP + interval '1 day'
    ORDER BY 1, 3, nusr.created_at DESC
),
learning_journey_shares AS (
    SELECT 
        lsi.user_id,
        lj.id AS learning_journey_id,
        lj.name AS learning_journey_name,
        ljc.course_id,
        lsi.share_id,
        lsi.sent_at
    FROM latest_share_ids lsi
    JOIN public.learning_journey_courses ljc 
        ON lsi.nugget_id = ljc.learning_journey_id
    JOIN public.learning_journey lj 
        ON ljc.learning_journey_id = lj.id
    WHERE lj.organization = @{{:Course Report Noon.OrganizationParameter}}
      AND lj.name IN ('New DA Onboarding', 'Retraining Module for Existing DAs')
),
quiz_attempts AS (
    SELECT 
        qr.user_id,
        lj_sh.learning_journey_name,
        qr.course_id,
        qr.share_id,
        qr.attempt,
        min(qr.created_at) AS first_attempt_at,
        max(qr.created_at) AS last_attempt_at
    FROM quiz.quiz_responses qr
    JOIN learning_journey_shares lj_sh 
        ON qr.user_id = lj_sh.user_id
        AND qr.course_id = lj_sh.course_id
        AND qr.share_id = lj_sh.share_id
    GROUP BY 1, 2, 3, 4, 5
),
attempt_summary AS (
    SELECT
        qa.user_id,
        qa.learning_journey_name,
        COUNT(DISTINCT qa.attempt) AS total_attempts,
        MIN(qa.first_attempt_at) AS first_attempt_at,
        MAX(qa.last_attempt_at) AS last_attempt_at
    FROM quiz_attempts qa
    GROUP BY 1, 2
)
SELECT
    ua.organization,
    ua.first_name as emp_name,
    ua.identifier as emp_id,
    ua.division,
    ua.sub_division,
    ua.job_location AS location,
    ua.department,
    ua.designation,
    ua.job_type,
    asy.learning_journey_name,
    asy.total_attempts,
    asy.first_attempt_at + td.diff AS first_attempt_local,
    asy.last_attempt_at + td.diff AS last_attempt_local
FROM attempt_summary asy
JOIN user_details ua ON ua.uuid = asy.user_id
LEFT JOIN td ON ua.organization = td.organization
ORDER BY ua.division, ua.sub_division, ua.job_location, ua.first_name
```

---

## Noon Food Onboarding Course Report_Onboarding Course Report - Noon Food.sql

**Tables referenced:** LATERAL, analytics.nuggets_user_progress, analytics_requests, ar.updated_at, course_info, courses, event_types, jsonb_object_keys, new_user_data, report_part_1, report_part_2, report_part_3, sessions_list, user_details

**Columns needing snake_case conversion:**

- `courseStatus` -> `course_status` (alias: `course_status AS "courseStatus"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `totalCardsConsumed` -> `total_cards_consumed` (alias: `total_cards_consumed AS "totalCardsConsumed"`)


**Original Query:**

```sql
-- Data Source: Noon Food Onboarding Course Report
-- Dashboard: Onboarding Course Report - Noon Food
-- Category: Noon Food
-- Extracted: 2026-01-29 16:54:05
-- ============================================================

 SELECT
		"QueryTable 1"."Restaurant ID" AS "Restaurant ID",
		"QueryTable 1"."Course Status" AS "Course Status",
		"QueryTable 1"."Restaurant name" AS "Restaurant name",
		"QueryTable 1"."Outlet code" AS "Outlet code",
		"QueryTable 1"."Phone Number" AS "Phone Number",
		"QueryTable 1"."Country" AS "Country",
		"QueryTable 1"."City" AS "City",
		"QueryTable 1"."Email" AS "Email",
		"QueryTable 1"."Total time spent on course (mins)" AS "Total time spent on course (mins)",
		"QueryTable 1"."Completion %" AS "Completion %",
		"QueryTable 1"."Regd on" AS "Regd on",
		"QueryTable 1"."Logged in on" AS "Logged in on",
		"QueryTable 1"."Course started on" AS "Course started on",
		"QueryTable 1"."Course completed on" AS "Course completed on",
		"QueryTable 1"."No of times the course was started" AS "No of times the course was started",
		"QueryTable 1"."KNOW_user_ID" AS "KNOW_user_ID",
		"QueryTable 1"."KNOW course ID" AS "KNOW course ID"
FROM(WITH course_info AS
  (SELECT courses.id AS nugget_id,
          courses.name AS course_name,
          courses.total_cards,
          jsonb_object_keys(answers) AS quiz_card_id
   FROM courses
   WHERE courses.id IN ('xk64PxGF9Xb5odABtwGmZW')),
     new_user_data AS
  (SELECT user_details.identifier AS Resto_ID,
          user_details.first_name AS resto_name,
          user_details.last_name AS outlet_code,
          user_Details.division AS country,
          user_details.sub_division AS City,
          user_details.uuid,
          user_details.phone_number,
          user_details.email,
          json_object_agg(et.event_type, (extract(epoch
                                                  FROM ar.updated_at)*1000)::bigint) AS analytics
   FROM analytics_requests ar
   JOIN event_types et ON et.id = ar.event_id
   JOIN user_details ON ar.user_id = user_details.uuid
   WHERE nugget_id IN ('-Ni9cTL1T-QT3jTXIKMr')
     AND user_details.phone_number IS NOT NULL
     AND (user_details.email IS NULL
          OR user_details.email NOT ILIKE '%knownuggets.com')
     AND to_timestamp(user_details.created_at/1000) > CURRENT_TIMESTAMP - interval '90 days'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     sessions_list AS
  (SELECT nugget_id,
          user_id,
          session_timestamp,
          updated_at,
          plv8_get_course_status_from_analytics(analytics, nugget_id, created_at) AS course_timeline,
          CASE
              WHEN sessions -> session_timestamp ->> 'courseStatus' = 'completed' THEN 3
              WHEN sessions -> session_timestamp ->> 'courseStatus' = 'inProgress' THEN 2
              WHEN sessions -> session_timestamp ->> 'courseStatus' IS NULL THEN NULL
              ELSE 1
          END AS session_status,
          (sessions -> session_timestamp ->> 'totalCardsConsumed')::integer AS total_cards_consumed,
          (sessions -> session_timestamp ->> 'end')::bigint - (sessions -> session_timestamp ->> 'start')::bigint AS session_duration
   FROM
     (SELECT nugget_id,
             user_id,
             status,
             updated_at,
             analytics,
             created_at,
             sessions,
             st.session_timestamp
      FROM
        (SELECT nup.*
         FROM analytics.nuggets_user_progress nup
         JOIN new_user_data nud ON nud.uuid = nup.user_id
         WHERE nugget_id IN ('xk64PxGF9Xb5odABtwGmZW') ) base
      LEFT JOIN LATERAL
        (SELECT *
         FROM jsonb_object_keys(base.sessions) session_timestamp) st ON TRUE) with_session_key
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     report_part_1 AS
  (SELECT new_user_data.Resto_ID,
          new_user_data.resto_name,
          new_user_data.outlet_code,
          new_user_data.country,
          new_user_data.City,
          new_user_data.uuid AS user_id,
          new_user_data.phone_number,
          new_user_data.email,
          least(min((analytics ->> 'sent')::bigint), min((course_timeline ->> 'sent')::bigint)) AS registered_at,
          least(min((analytics ->> 'received')::bigint), min((course_timeline ->> 'received')::bigint)) AS logged_in_at
   FROM new_user_data
   FULL OUTER JOIN sessions_list ON new_user_data.uuid = sessions_list.user_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     report_part_2 AS
  (SELECT nugget_id,
          user_id,
          CASE
              WHEN course_timeline ->> 'consumed' IS NOT NULL THEN 'Completed'
              WHEN course_timeline ->> 'started' IS NOT NULL THEN 'In Progress'
              WHEN course_timeline ->> 'received' IS NOT NULL THEN 'Logged in but not started'
              WHEN course_timeline ->> 'sent' IS NOT NULL THEN 'Not logged in yet'
              ELSE NULL
          END AS status,
          min((course_timeline ->> 'started')::bigint) AS course_started_at,
          max(total_cards_consumed) AS total_no_of_cards_completed,
          sum(session_duration/60000) AS total_time_spent_on_course_in_mins,
          count(session_timestamp) AS no_of_times_course_was_started
   FROM sessions_list
   WHERE (session_status > 1
          OR course_timeline ->> 'started' IS NOT NULL)
   GROUP BY 1,
            2,
            3),
     report_part_3 AS
  (SELECT nugget_id,
          user_id,
          (course_timeline ->> 'consumed')::bigint AS course_completed_at
   FROM sessions_list
   WHERE (session_status = 3
          OR course_timeline ->> 'consumed' IS NOT NULL))
SELECT report_part_1.Resto_ID AS "Restaurant ID",
       CASE
           WHEN report_part_2.status IS NOT NULL THEN report_part_2.status
           WHEN report_part_1.logged_in_at IS NOT NULL THEN 'Logged in but not started'
           WHEN report_part_1.registered_at IS NOT NULL THEN 'Not logged in yet'
       END AS "Course Status",
       report_part_1.resto_name AS "Restaurant name",
       report_part_1.outlet_code AS "Outlet code",
       report_part_1.phone_number AS "Phone Number",
       report_part_1.country AS "Country",
       report_part_1.city AS "City",
       report_part_1.email AS "Email",
       report_part_2.total_time_spent_on_course_in_mins AS "Total time spent on course (mins)",
       (CASE
            WHEN report_part_2.total_no_of_cards_completed IS NULL THEN NULL
            ELSE least(report_part_2.total_no_of_cards_completed, course_info.total_cards)
        END)::numeric/course_info.total_cards "Completion %",
       (to_timestamp(report_part_1.registered_at/1000) AT TIME ZONE 'Asia/Dubai')::date AS "Regd on",
       (to_timestamp(report_part_1.logged_in_at/1000) AT TIME ZONE 'Asia/Dubai')::date AS "Logged in on",
       (to_timestamp(report_part_2.course_started_at/1000) AT TIME ZONE 'Asia/Dubai')::date AS "Course started on",
       (to_timestamp(report_part_3.course_completed_at/1000) AT TIME ZONE 'Asia/Dubai')::date AS "Course completed on",
       report_part_2.no_of_times_course_was_started AS "No of times the course was started",
       report_part_1.user_id AS "KNOW_user_ID",
       course_info.nugget_id AS "KNOW course ID"
FROM report_part_1
LEFT OUTER JOIN report_part_2 ON report_part_1.user_id = report_part_2.user_id
LEFT OUTER JOIN report_part_3 ON report_part_1.user_id = report_part_3.user_id
LEFT OUTER JOIN course_info ON report_part_2.nugget_id = course_info.nugget_id
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
         14,
         15,
         16,
         17
ORDER BY 2,
         14 DESC,
         8,
         5,
         6,
         1)"QueryTable 1"
```

---
