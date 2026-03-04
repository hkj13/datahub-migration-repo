# Mr Bean

> Auto-generated on 2026-03-04 08:13

**Total queries:** 5

---

## Audit Details-copy_1746441555_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Audit Details-copy_1746441555
-- Dashboard: Audits
-- Category: Mr Bean
-- Extracted: 2026-01-29 16:56:22
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
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
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_submitted_at,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_submitted_at)
                          ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = @{{:OrganizationParameter}}
  and audit_submitted_at between @{{:Audit Summary.Date Range.START}}::timestamp and @{{:Audit Summary.Date Range.END}}::timestamp + interval '1 day'
 )
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
	   theme as "Theme",
       checkpoint_knid as "Checkpoint KNID",
	   checkpoint as "Checkpoint",
	   result as "Result",
	   status as "Checkpoint Status",
	   auditor_observations as "Auditor Notes",
	   result_score as "Actual Score",
	   max_score as "Max Score",
	   criticality as "Criticality",
       total_follow_up_tasks AS "Total Follow Ups",
       total_closed_follow_up_tasks AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM base
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
ORDER BY 1,
         2,
         4
```

---

## Audit Summary-copy_1746441555_Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Audit Summary-copy_1746441555
-- Dashboard: Audits
-- Category: Mr Bean
-- Extracted: 2026-01-29 16:56:23
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
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
               AND ug1.is_active = TRUE))),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = @{{:OrganizationParameter}}),
     base AS
  (SELECT organization_id,
          CASE
              WHEN result_score = '' THEN NULL
              ELSE result_score::numeric
          END AS result_score,
          CASE
              WHEN max_score = '' THEN NULL
              ELSE max_score::numeric
          END AS max_score,
          store_id,
          audit_main_theme,
          theme,
          audit_submitted_at,
          audit_submission_number,
          audit_submission_knid,
          auditor_name,
          checkpoint_knid,
          CHECKPOINT,
          RESULT,
          criticality,
          is_critical_question_failed,
          auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          CASE
              WHEN result_score = '' THEN 'Not checked'
              WHEN result_score::numeric < max_score::numeric THEN 'Failed'
              ELSE 'Passed'
          END AS status,
                              row_number() OVER (PARTITION BY store_id,
                                       audit_main_theme,
                                       theme, checkpoint_knid,
                                       extract('Year'
                  FROM audit_submitted_at)
                          ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   join location_acl on cms.store_id = location_acl.job_location
   WHERE organization_id = @{{:OrganizationParameter}}
  and audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day' )
SELECT organization_id AS "Org",
       store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       sum(result_score) as "Actual Score",
	   sum(max_score) as "Max Score",
	   sum(result_score)/sum(max_score) AS "Audit Score",
       count(CASE
                 WHEN is_critical_question_failed = 'true' THEN checkpoint_knid
                 ELSE NULL
             END) AS "Critical Failed Count",
       sum(total_follow_up_tasks) AS "Total Follow Ups",
       sum(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
       "Audit No in Year"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 14
ORDER BY 1,
         2,
         4
```

---

## Mr Bean Daily Compliance Emailer_Mr Bean Ops Routine Compliance.sql

**Tables referenced:** am_map, form_reminders, form_submissions, fr, fs_appr, fs_init, lfr, lm, location_form_reminders, location_map, nuggets, user_details

**Original Query:**

```sql
-- Data Source: Mr Bean Daily Compliance Emailer
-- Dashboard: Mr Bean Ops Routine Compliance
-- Category: Mr Bean
-- Extracted: 2026-01-29 16:58:19
-- ============================================================

WITH location_map AS
  (SELECT sub_division AS area,
          job_location AS LOCATION
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Store account'
   GROUP BY 1,
            2),
     am_map AS
  (SELECT DISTINCT ON (sub_division) sub_division AS area,
                      first_name||' '||last_name AS am
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Area Manager'
   GROUP BY 1,
            2
   ORDER BY sub_division),
     lm AS
  (SELECT lm.location,
          lm.area,
          amm.am
   FROM location_map lm
   LEFT OUTER JOIN am_map amm ON lm.area = amm.area
   GROUP BY 1,
            2,
            3),
     fr AS
  (SELECT fr.organization,
          fr.id,
          fr.form_id,
          fr.schedule_id,
          fr.tz_offset/60 AS tz_offset_min
   FROM form_reminders fr
   WHERE (to_timestamp(fr.sent_at/1000) + interval '1 min'*fr.tz_offset/60)::date = (current_timestamp)::date
     AND fr.organization = 'mrbean-fireworks'),
     lfr AS
  (SELECT fr.organization,
          lfr.location_id,
          fr.form_id,
          lfr.form_response_id AS lfr_form_response_id,
          to_timestamp(lfr.reminded_at/1000) + interval '1 min'*fr.tz_offset_min AS reminded_at,
                                                        to_timestamp(lfr.reminder_window_end/1000) + interval '1 min'*fr.tz_offset_min AS reminder_window_end,
                                                                                                              lfr.reminder_id,
                                                                                                              fr.tz_offset_min
   FROM location_form_reminders lfr
   JOIN fr ON fr.id = lfr.reminder_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     fs_init AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.submit_date + interval '1 min'*lfr.tz_offset_min AS responded_at,
                                                fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN lfr ON fs.location = lfr.location_id
   AND fs.form_id = lfr.form_id
   AND fs.submit_date + interval '1 min'*lfr.tz_offset_min BETWEEN lfr.reminded_at AND lfr.reminder_window_end
   ORDER BY fs.response_id,
            fs.id),
     fs_appr AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN fr ON fs.form_id = fr.form_id
   WHERE in_progress = 'false'
   ORDER BY fs.response_id,
            fs.id DESC)
SELECT lfr.organization AS "Organization",
       lfr.reminded_at::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lm.area||' ('||lm.am||')' AS "Area",
       lfr.location_id AS "Location",
       lfr.reminded_at AS "Reminded At",
       fs_init.responded_at AS "Responded At",
       CASE
           WHEN fs_init.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "Compliance",
       CASE
           WHEN fs_appr.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "AM Compliance",
       fs_init.form_response_id AS "Submission KNID",
       row_number() OVER (PARTITION BY (lfr.reminded_at)::date,
                                       lfr.form_id,
                                       lfr.location_id
                          ORDER BY (lfr.reminded_at)) AS "Routine #"
FROM lfr
LEFT OUTER JOIN lm ON lfr.location_id = lm.location
LEFT OUTER JOIN fs_init ON fs_init.location = lfr.location_id
AND fs_init.form_id = lfr.form_id
LEFT OUTER JOIN fs_appr ON fs_appr.form_response_id = fs_init.form_response_id
JOIN nuggets n ON lfr.form_id = n.id
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
         11
HAVING lm.area||' ('||lm.am||')' IS NOT NULL
AND lm.area||' ('||lm.am||')' NOT ILIKE 'KNOW%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'HQ%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'Outlet%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'All%'
ORDER BY 1,
         2,
         5,
         6,
         7,
         4
```

---

## Mr Bean One Time Compliance_Mr Bean One Time Report.sql

**Tables referenced:** am_map, form_reminders, form_submissions, fr, fs_appr, fs_init, lfr, lm, location_map, nuggets, user_details, user_form_reminders

**Original Query:**

```sql
-- Data Source: Mr Bean One Time Compliance
-- Dashboard: Mr Bean One Time Report
-- Category: Mr Bean
-- Extracted: 2026-01-29 16:58:20
-- ============================================================

WITH location_map AS
  (SELECT sub_division AS area,
          job_location AS LOCATION
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Store account'
   GROUP BY 1,
            2),
     am_map AS
  (SELECT DISTINCT ON (sub_division) sub_division AS area,
                      first_name||' '||last_name AS am
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Area Manager'
   GROUP BY 1,
            2
   ORDER BY sub_division),
     lm AS
  (SELECT lm.location,
          lm.area,
          amm.am
   FROM location_map lm
   LEFT OUTER JOIN am_map amm ON lm.area = amm.area
   GROUP BY 1,
            2,
            3),
     fr AS
  (SELECT fr.organization,
          fr.id,
          fr.form_id,
          fr.schedule_id,
          fr.tz_offset/60 AS tz_offset_min
   FROM form_reminders fr
   WHERE to_timestamp(fr.sent_at/1000) + interval '1 min'*fr.tz_offset/60 BETWEEN @{{:Date.START}}::TIMESTAMP + interval '1 min'*fr.tz_offset/60 AND @{{:Date.END}}::TIMESTAMP + interval '1 min'*fr.tz_offset/60
     AND fr.organization = 'mrbean-fireworks'),
     lfr AS
  (SELECT fr.organization,
          lfr.location_id,
          fr.form_id,
          lfr.form_response_id AS lfr_form_response_id,
          to_timestamp(lfr.reminded_at/1000) + interval '1 min'*fr.tz_offset_min AS reminded_at,
                                                        to_timestamp(lfr.reminder_window_end/1000) + interval '1 min'*fr.tz_offset_min AS reminder_window_end,
                                                                                                              lfr.reminder_id,
                                                                                                              fr.tz_offset_min
   FROM user_form_reminders lfr
   JOIN fr ON fr.id = lfr.reminder_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     fs_init AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.submit_date + interval '1 min'*lfr.tz_offset_min AS responded_at,
                                                fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN lfr ON fs.location = lfr.location_id
   AND fs.form_id = lfr.form_id
   AND fs.submit_date + interval '1 min'*lfr.tz_offset_min BETWEEN lfr.reminded_at AND lfr.reminder_window_end
   ORDER BY fs.response_id,
            fs.id),
     fs_appr AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN fr ON fs.form_id = fr.form_id
   WHERE in_progress = 'false'
   ORDER BY fs.response_id,
            fs.id DESC)
SELECT lfr.organization AS "Organization",
       lfr.reminded_at::date AS "Date",
       lfr.form_id AS "Routine KNID",
       CASE WHEN n.title ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(n.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') ELSE n.title END AS "Routine Name",
       lm.area||' ('||lm.am||')' AS "Area",
       lfr.location_id AS "Location",
       lfr.reminded_at AS "Reminded At",
       fs_init.responded_at AS "Responded At",
       CASE
           WHEN fs_init.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "Compliance",
       CASE
           WHEN fs_appr.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "AM Compliance",
       fs_init.form_response_id AS "Submission KNID",
       row_number() OVER (PARTITION BY (lfr.reminded_at)::date,
                                       lfr.form_id,
                                       lfr.location_id
                          ORDER BY (lfr.reminded_at)) AS "Routine #"
FROM lfr
LEFT OUTER JOIN lm ON lfr.location_id = lm.location
LEFT OUTER JOIN fs_init ON fs_init.location = lfr.location_id
AND fs_init.form_id = lfr.form_id
LEFT OUTER JOIN fs_appr ON fs_appr.form_response_id = fs_init.form_response_id
JOIN nuggets n ON lfr.form_id = n.id
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
         11
HAVING lm.area||' ('||lm.am||')' IS NOT NULL
AND lm.area||' ('||lm.am||')' NOT ILIKE 'KNOW%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'HQ%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'Outlet%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'All%'
ORDER BY 1,
         2,
         5,
         6,
         7,
         4
```

---

## Mr Bean Routine Compliance_Routine Compliance.sql

**Tables referenced:** am_map, form_reminders, form_submissions, fr, fs_appr, fs_init, lfr, lm, location_form_reminders, location_map, nuggets, user_details

**Original Query:**

```sql
-- Data Source: Mr Bean Routine Compliance
-- Dashboard: Routine Compliance
-- Category: Mr Bean
-- Extracted: 2026-01-29 16:58:20
-- ============================================================

WITH location_map AS
  (SELECT sub_division AS area,
          job_location AS LOCATION
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Store account'
   GROUP BY 1,
            2),
     am_map AS
  (SELECT DISTINCT ON (sub_division) sub_division AS area,
                      first_name||' '||last_name AS am
   FROM user_details
   WHERE organization = 'mrbean-fireworks'
     AND is_active = 'true'
     AND designation ILIKE 'Area Manager'
   GROUP BY 1,
            2
   ORDER BY sub_division),
     lm AS
  (SELECT lm.location,
          lm.area,
          amm.am
   FROM location_map lm
   LEFT OUTER JOIN am_map amm ON lm.area = amm.area
   GROUP BY 1,
            2,
            3),
     fr AS
  (SELECT fr.organization,
          fr.id,
          fr.form_id,
          fr.schedule_id,
          fr.tz_offset/60 AS tz_offset_min
   FROM form_reminders fr
   WHERE to_timestamp(fr.sent_at/1000) + interval '1 min'*fr.tz_offset/60 BETWEEN @{{:Date.START}}::TIMESTAMP + interval '1 min'*fr.tz_offset/60 AND @{{:Date.END}}::TIMESTAMP + interval '1 min'*fr.tz_offset/60
     AND fr.organization = 'mrbean-fireworks'),
     lfr AS
  (SELECT fr.organization,
          lfr.location_id,
          fr.form_id,
          lfr.form_response_id AS lfr_form_response_id,
          to_timestamp(lfr.reminded_at/1000) + interval '1 min'*fr.tz_offset_min AS reminded_at,
                                                        to_timestamp(lfr.reminder_window_end/1000) + interval '1 min'*fr.tz_offset_min AS reminder_window_end,
                                                                                                              lfr.reminder_id,
                                                                                                              fr.tz_offset_min
   FROM location_form_reminders lfr
   JOIN fr ON fr.id = lfr.reminder_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     fs_init AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.submit_date + interval '1 min'*lfr.tz_offset_min AS responded_at,
                                                fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN lfr ON fs.location = lfr.location_id
   AND fs.form_id = lfr.form_id
   AND fs.submit_date + interval '1 min'*lfr.tz_offset_min BETWEEN lfr.reminded_at AND lfr.reminder_window_end
   ORDER BY fs.response_id,
            fs.id),
     fs_appr AS
  (SELECT DISTINCT ON (fs.response_id) fs.location,
                      fs.form_id,
                      fs.sno,
                      fs.response_id AS form_response_id
   FROM form_submissions fs
   JOIN fr ON fs.form_id = fr.form_id
   WHERE in_progress = 'false'
   ORDER BY fs.response_id,
            fs.id DESC)
SELECT lfr.organization AS "Organization",
       lfr.reminded_at::date AS "Date",
       lfr.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lm.area||' ('||lm.am||')' AS "Area",
       lfr.location_id AS "Location",
       lfr.reminded_at AS "Reminded At",
       fs_init.responded_at AS "Responded At",
       CASE
           WHEN fs_init.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "Compliance",
       CASE
           WHEN fs_appr.form_response_id IS NOT NULL THEN 1
           ELSE 0
       END AS "AM Compliance",
       fs_init.form_response_id AS "Submission KNID",
       row_number() OVER (PARTITION BY (lfr.reminded_at)::date,
                                       lfr.form_id,
                                       lfr.location_id
                          ORDER BY (lfr.reminded_at)) AS "Routine #"
FROM lfr
LEFT OUTER JOIN lm ON lfr.location_id = lm.location
LEFT OUTER JOIN fs_init ON fs_init.location = lfr.location_id
AND fs_init.form_id = lfr.form_id
LEFT OUTER JOIN fs_appr ON fs_appr.form_response_id = fs_init.form_response_id
JOIN nuggets n ON lfr.form_id = n.id
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
         11
HAVING lm.area||' ('||lm.am||')' IS NOT NULL
AND lm.area||' ('||lm.am||')' NOT ILIKE 'KNOW%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'HQ%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'Outlet%'
AND lm.area||' ('||lm.am||')' NOT ILIKE 'All%'
ORDER BY 1,
         2,
         5,
         6,
         7,
         4
```

---
