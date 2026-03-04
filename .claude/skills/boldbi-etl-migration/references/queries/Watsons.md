# Watsons

> Auto-generated on 2026-03-04 08:13

**Total queries:** 4

---

## PH Tasks_Tasks.sql

**Tables referenced:** ROLES, accessible_tasks, analytics_requests, audit_tasks, form_submissions, form_tasks, lm, locations, lr, organizations, question_definitions, role_holders, t, tasks, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionGroupId` -> `question_group_id` (alias: `question_group_id AS "questionGroupId"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: PH Tasks
-- Dashboard: Tasks
-- Category: Watsons
-- Extracted: 2026-01-29 16:52:28
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
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
            10),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     form_tasks AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          t.details->'formDetails'->>'name' AS "Trigger Form",
                                     t.details->'formDetails'->>'formId' AS "Trigger Form KNID",
                                                                t.details->'formDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                                           t.details->'formDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                                                      initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                      to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                      initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                      initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                      initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                      to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                                                      to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                                                      END AS "Started At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Completed At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed'
                                                                                                                               OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Reopened At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'completed'
                                                                                                                               AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Overdue Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'notStarted'
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Not Started Count",
                                                                                                                      CASE
                                                                                                                          WHEN (t.status ILIKE 'started'
                                                                                                                                OR t.status ILIKE 'reopened')
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "In Progress Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Completed Count",
                                                                                                                         CASE
                                                                                                                          WHEN t.status ILIKE 'completed' AND completed_at <= deadline THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "On Time Completed Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Reopened Count",
   																													  t.details->>'comment' as "Completion Comment",
   																													  t.details->'resolvedPayload'->'images'->0->>'url' as "Completion Image",
                                                                                                                      split_part(t.details->'formDetails'->>'path', '/', 1) AS trigger_question_knid,
          qd.question AS "Form Question",
          fs.location AS "Location"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   LEFT JOIN question_definitions qd ON split_part(t.details->'formDetails'->>'path', '/', 1) = qd.question_id
   LEFT JOIN form_submissions fs ON t.details->'formDetails'->>'responseId' = fs.response_id
   WHERE t.is_deleted = 'false'
     AND to_timestamp((t.details->>'plannedStartDate')::bigint/1000) + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = @{{:OrganizationParameter}}),
	 audit_tasks AS
  (SELECT t.id AS "Task KNID",
          t.organization AS "Org",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          t.details->'auditDetails'->>'name' AS "Trigger Form",
                                     t.details->'auditDetails'->>'formId' AS "Trigger Form KNID",
                                                                t.details->'auditDetails'->>'responseId' AS "Trigger Form Submission KNID",
                                                                                           t.details->'auditDetails'->>'sno' AS "Trigger Form Submission No",
                                                                                                                      initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                      to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                      initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                      initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                      initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                      to_timestamp(t.created_at/1000) + td.diff AS "Assigned At",
                                                                                                                      to_timestamp(t.deadline/1000) + td.diff AS "Deadline",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) + td.diff
                                                                                                                      END AS "Started At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Completed At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed'
                                                                                                                               OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) + td.diff
                                                                                                                          ELSE NULL
                                                                                                                      END AS "Reopened At",
                                                                                                                      CASE
                                                                                                                          WHEN t.status NOT ILIKE 'completed'
                                                                                                                               AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Overdue Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'notStarted'
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Not Started Count",
                                                                                                                      CASE
                                                                                                                          WHEN (t.status ILIKE 'started'
                                                                                                                                OR t.status ILIKE 'reopened')
                                                                                                                               THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "In Progress Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Completed Count",
                                                                                                                         CASE
                                                                                                                          WHEN t.status ILIKE 'completed' AND completed_at <= deadline THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "On Time Completed Count",
                                                                                                                      CASE
                                                                                                                          WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                          ELSE 0
                                                                                                                      END AS "Reopened Count",
   																													  t.details->>'comment' as "Completion Comment",
   																													  t.details->'resolvedPayload'->'images'->0->>'url' as "Completion Image",
                                                                                                                      t.details->'auditDetails'->>'questionGroupId' AS theme_knid,
          qd.question AS "Form Question",
          fs.location AS "Location"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   LEFT JOIN question_definitions qd ON t.details->'auditDetails'->>'questionId' = qd.question_id
   LEFT JOIN form_submissions fs ON t.details->'auditDetails'->>'responseId' = fs.response_id
   WHERE t.is_deleted = 'false'
     AND to_timestamp((t.details->>'plannedStartDate')::bigint/1000) + td.diff BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = @{{:OrganizationParameter}}),
	t AS (
  SELECT DISTINCT ON ("Task KNID") *
  FROM (
      SELECT * FROM form_tasks
      UNION ALL
      SELECT * FROM audit_tasks
  ) x
  ORDER BY
      "Task KNID",
      "Trigger Form" DESC NULLS LAST,
      "Form Question" DESC NULLS LAST
),
	 
    accessible_tasks AS
  (SELECT
      t."Task KNID",
      string_agg(DISTINCT ua.emp_name, ', ') AS assignee_list,
      MAX(ua.division)      AS division,
      MAX(ua.sub_division)  AS sub_division,
      MAX(ua.department)   AS department,
      MAX(ua.job_location) AS job_location
  FROM t
  JOIN analytics_requests ar
    ON t."Task KNID" = ar.nugget_id
  JOIN user_acl ua
    ON ar.user_id = ua.uuid
  WHERE ar.event_id = 1
  GROUP BY 1),
    lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Operations Manager','Regional Operations Manager','Operations Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'watsons-ph-leo'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'Area Operations Manager' THEN holder
              END) AS "AOM",
        MAX(CASE
                  WHEN ROLE = 'Regional Operations Manager' THEN holder
              END) AS "ROM",
   MAX(CASE
                  WHEN ROLE = 'Operations Head' THEN holder
              END) AS "TOH"
   FROM lr
   GROUP BY store_id,
            store_name)
SELECT t.*,
       at.assignee_list AS "Assignee(s)",
	   at.division,
	   at.sub_division,
	   at.department,
	   at.job_location,
	   lm."AOM",
	   lm."ROM",
	   lm."TOH"
FROM t
JOIN accessible_tasks AT ON t."Task KNID" = at."Task KNID"
LEFT JOIN lm ON AT.job_location = lm.store_id
ORDER BY 2,
         14,
         15
```

---

## Routine Compliance  Watsons Ph_Routine Compliance.sql

**Tables referenced:** ROLES, form_compliance_v2, form_submissions, lm, location_acl, locations, lr, organizations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance  Watsons Ph
-- Dashboard: Routine Compliance
-- Category: Watsons
-- Extracted: 2026-01-29 16:52:42
-- ============================================================

SELECT
  "QueryTable 1"."Organization" AS "Organization",
  "QueryTable 1"."Date" AS "Date",
  "QueryTable 1"."Routine KNID" AS "Routine KNID",
  "QueryTable 1"."Routine Name" AS "Routine Name",
  "QueryTable 1"."Location" AS "Location",
  "QueryTable 1"."division" AS "Division",
  "QueryTable 1"."sub_division" AS "Sub Division",
  "QueryTable 1"."department" AS "Department",
  "QueryTable 1"."Reminded At" AS "Reminded At",
  "QueryTable 1"."Responded At" AS "Responded At",
  "QueryTable 1"."Compliance" AS "Compliance",
  "QueryTable 1"."Submission KNID" AS "Submission KNID",
  "QueryTable 1"."Routine #" AS "Routine #",
  "QueryTable 1"."Date Mod" AS "Date Mod",
    "QueryTable 1"."AOM" AS "AOM",
	 "QueryTable 1"."ROM" AS "ROM",
	 "QueryTable 1"."TOH" AS "TOH"
FROM (
  WITH location_acl AS (
    SELECT DISTINCT ON (job_location)
           job_location,
           division,
           sub_division,
           department
    FROM user_details
    WHERE organization = @{{:OrganizationParameter}}
      AND is_active = TRUE
      AND job_location NOT IN ('KNOW', 'All', 'HO')
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
          SELECT user_id
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
    ORDER BY job_location
  ),
  td AS (
    SELECT id AS organization, interval '1 min' * tzoffset AS diff
    FROM organizations
    WHERE id = 'watsons-ph-leo'
  ),
   lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Operations Manager','Regional Operations Manager','Operations Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'watsons-ph-leo'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'Area Operations Manager' THEN holder
              END) AS "AOM",
        MAX(CASE
                  WHEN ROLE = 'Regional Operations Manager' THEN holder
              END) AS "ROM",
   MAX(CASE
                  WHEN ROLE = 'Operations Head' THEN holder
              END) AS "TOH"
   FROM lr
   GROUP BY store_id,
            store_name)
  SELECT
    fc.*,
    TO_CHAR(fc."Date", 'YYYY-MM-DD') AS "Date Mod",
    location_acl.division,
    location_acl.sub_division,
    location_acl.department,
    lm."AOM",
   lm."ROM",
  lm."TOH"
  FROM form_compliance_v2 fc
  JOIN location_acl
    ON fc."Location" = location_acl.job_location
  LEFT JOIN form_submissions fs
    ON fs.response_id = fc."Submission KNID"
  LEFT JOIN user_details ud
    ON fs.user_id = ud.uuid
  LEFT JOIN lm on lm. store_id = fc."Location"
  WHERE fc."Organization" = @{{:OrganizationParameter}}
    AND fc."Reminded At"
        BETWEEN @{{:Date Range.START}}::timestamp
            AND @{{:Date Range.END}}::timestamp + interval '1 day'
) "QueryTable 1"
```

---

## Watsons PH Forms_Forms.sql

**Tables referenced:** ROLES, form_responses, form_submissions, forms, fr, fr_location, fs, lm, location_acl, locations, lr, nuggets, organizations, question_definitions, role_holders, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Watsons PH Forms
-- Dashboard: Forms
-- Category: Watsons
-- Extracted: 2026-01-29 16:52:42
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'watsons-ph-leo'
   and is_active = 'true'
   and job_location not in ('KNOW', 'All')
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
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'watsons-ph-leo'),
			   forms as (select * from nuggets where organization = 'watsons-ph-leo'
						 and (is_deleted = 'false' or is_deleted is null)
						 and classification_type = 'form'
						and title not ilike 'Issue Creation%'
						and title not ilike 'Issue Closure%'
						and id not ilike 'compliment%'
						and id not ilike 'leave%'),
						fs AS
  (SELECT DISTINCT ON (response_id) fs2.*
   FROM form_submissions fs2
   JOIN forms ON forms.id = fs2.form_id
   JOIN td ON fs2.organization = td.organization
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   ORDER BY response_id,
            fs2.id),
     fr_location AS
  (SELECT DISTINCT ON (fs.response_id) fs.response_id,
                      fr.response->>'name' AS fr_location
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fr.question_id = qd.question_id
   AND fs.form_id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY fs.response_id,
            fs.id,
            qd.section_id,
            qd.sqno),
     fr AS
  (SELECT fs.response_Id,
          fs.form_id,
          fs.id,
          fs.sno,
          fs.submit_date,
          fs.organization,
          fs.user_id,
          CASE
              WHEN fr_location.fr_location IS NULL THEN fs.location
              ELSE fr_location.fr_location
          END AS LOCATION
   FROM fs
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id),
    lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Area Operations Manager','Regional Operations Manager','Operations Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'watsons-ph-leo'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'Area Operations Manager' THEN holder
              END) AS "AOM",
        MAX(CASE
                  WHEN ROLE = 'Regional Operations Manager' THEN holder
              END) AS "ROM",
   MAX(CASE
                  WHEN ROLE = 'Operations Head' THEN holder
              END) AS "TOH"
   FROM lr
   GROUP BY store_id,
            store_name)
SELECT forms.title AS "Form Title",
       forms.id AS "Form KNID",
       fr.response_id AS "Response KNID",
       fr.sno AS "Submission No",
       fr.submit_date + td.diff AS "Submitted At",
       fr.location AS "Form Location",
       ud.identifier AS "Submitter ID",
       ud.uuid AS "Submitter KNID",
       ud.first_name||' '||ud.last_name AS "Submitter Name",
       ud.division AS "Submitter Division",
       ud.sub_division AS "Submitter Sub Division",
       ud.job_location AS "Submitter Location",
       ud.department AS "Submitter Department",
       ud.designation AS "Submitter Designation",
       ud.job_type AS "Submitter Job Type",
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date",
	 lm."ROM",
	 lm."AOM",
	 	 lm."TOH"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
LEFT JOIN lm on ud.job_location = lm.store_id
ORDER BY 1,
         6,
         5
```

---

## Watsons PH Shifts and Attendance_Weekly Published Shifts.sql

**Tables referenced:** base, shift_attendance, user_details, user_week, users, weeks

**Original Query:**

```sql
-- Data Source: Watsons PH Shifts and Attendance
-- Dashboard: Weekly Published Shifts
-- Category: Watsons
-- Extracted: 2026-01-29 16:52:27
-- ============================================================

WITH base AS (
    SELECT 
        sa."UUID",
        date_trunc('week', sa."Scheduled Start Time")::date AS week_start,
        COUNT(*) AS shift_count
    FROM shift_attendance sa
    WHERE sa.organization = 'watsons-ph-leo'
      AND sa."Scheduled Start Time" >= current_date
    GROUP BY 1,2
),
weeks AS (
    SELECT generate_series(
        date_trunc('week', current_date),
        date_trunc('week', current_date + interval '4 weeks'),
        interval '1 week'
    )::date AS week_start
),
users AS (
    SELECT 
        ud.uuid,
        ud.first_name || ' ' || ud.last_name AS user_name,
        ud.designation,
        ud.job_location
    FROM user_details ud
    WHERE ud.organization = 'watsons-ph-leo'
      AND ud.is_active = true
  and ud.designation NOT IN ('Store Account')
),
user_week AS (
    SELECT u.*, w.week_start
    FROM users u
    CROSS JOIN weeks w
)

SELECT 
    uw.uuid,
    uw.user_name,
    uw.designation,
    uw.job_location,
    uw.week_start,
    COALESCE(b.shift_count,0) AS shifts_in_week,
    CASE 
        WHEN b.shift_count > 0 THEN 'Shift Planned'
        ELSE 'Missing Shift'
    END AS weekly_status
FROM user_week uw
LEFT JOIN base b 
       ON uw.uuid = b."UUID"
      AND uw.week_start = b.week_start
ORDER BY uw.user_name, uw.week_start
```

---
