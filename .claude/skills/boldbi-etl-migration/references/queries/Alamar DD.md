# Alamar DD

> Auto-generated on 2026-03-04 08:13

**Total queries:** 4

---

## Alamar DD LP Audit Summary_LP Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, forms, location_acl, nuggets, organizations, stores, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar DD LP Audit Summary
-- Dashboard: LP Audits
-- Category: Alamar DD
-- Extracted: 2026-01-29 16:58:02
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Alamar-DD-antenna' 
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Alamar-DD-antenna'),
   stores AS
  (SELECT identifier AS store_id,
          CASE
              WHEN division ILIKE 'KSA%' THEN 'KSA'
              WHEN division ILIKE 'PK %' THEN 'Pakistan'
              ELSE division
          END AS country,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'Alamar-DD-antenna'),
	 forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'Alamar-DD-antenna'
   AND cms.audit_type = 'Loss Prevention'
      join td on td.organization = cms.organization_id
   WHERE cms.audit_submitted_at + td.diff BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   GROUP BY 1,
            2),
	 
    
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
  join forms on cms.audit_submission_knid = forms.response_id
  join location_acl on cms.store_id = location_acl.job_location)
SELECT country as "Country",
region as "Region",
city as "City",
       base.store_id AS "Location",
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
FROM base
LEFT OUTER JOIN stores ON stores.store_id = base.store_id
group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 16
ORDER BY 1,
         2,
         4
```

---

## Alamar DD LP Audits Details_LP Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, forms, location_acl, nuggets, organizations, stores, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar DD LP Audits Details
-- Dashboard: LP Audits
-- Category: Alamar DD
-- Extracted: 2026-01-29 16:58:01
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Alamar-DD-antenna'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Alamar-DD-antenna'),
     stores AS
  (SELECT identifier AS store_id,
          CASE
              WHEN division ILIKE 'KSA%' THEN 'KSA'
              WHEN division ILIKE 'PK %' THEN 'Pakistan'
              ELSE division
          END AS country,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'Alamar-DD-antenna'),
     forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'Alamar-DD-antenna'
   AND cms.audit_type = 'Loss Prevention'
   JOIN td ON td.organization = cms.organization_id
   WHERE cms.audit_submitted_at + td.diff BETWEEN@{{:Alamar DD LP Audit Summary.Date Range.START}}::timestamp AND @{{:Alamar DD LP Audit Summary.Date Range.END}}::timestamp
   GROUP BY 1,
            2),
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
          audit_submitted_at + td.diff AS audit_submitted_at,
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
                                          theme,
                                          checkpoint_knid,
                                          extract('Year'
                                                  FROM audit_submitted_at)
                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   JOIN forms ON cms.audit_submission_knid = forms.response_id
  join location_acl on cms.store_id = location_acl.job_location)
SELECT country AS "Country",
       region AS "Region",
       city AS "City",
       base.store_id AS "Location",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audit Date",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       auditor_name AS "Auditor",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               status AS "Checkpoint Status",
                               auditor_observations AS "Auditor Notes",
                               result_score AS "Actual Score",
                               max_score AS "Max Score",
                               criticality AS "Criticality",
                               total_follow_up_tasks AS "Total Follow Ups",
                               total_closed_follow_up_tasks AS "Total Closed Follow Ups",
                               "Audit No in Year"
FROM base
LEFT OUTER JOIN stores ON base.store_id = stores.store_id
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
         17,
         18,
         19,
         20,
         21
ORDER BY 1,
         2,
         4,
         5,
         6 DESC
```

---

## Alamar DD Loss Prevention Follow Ups_LP Audit Follow Ups.sql

**Tables referenced:** analytics_requests, checkpoint_master_sheet_table, cms, cms_theme_score, cmscp, forms, fu, location_acl, nuggets, organizations, question_definitions, stores, t, task_assignees, tasks, td, tfq, user_Details, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionGroupId` -> `question_group_id` (alias: `question_group_id AS "questionGroupId"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Alamar DD Loss Prevention Follow Ups
-- Dashboard: LP Audit Follow Ups
-- Category: Alamar DD
-- Extracted: 2026-01-29 16:58:03
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'Alamar-DD-antenna'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   stores AS
  (SELECT identifier AS store_id,
          CASE
              WHEN division ILIKE 'KSA%' THEN 'KSA'
              WHEN division ILIKE 'PK %' THEN 'Pakistan'
              ELSE division
          END AS country,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'Alamar-DD-antenna'),
forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'Alamar-DD-antenna'
   AND cms.audit_type = 'Loss Prevention'
   WHERE cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   and cms.store_id in (select job_location from location_acl)
   GROUP BY 1,
            2),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Alamar-DD-antenna'
   GROUP BY 1,
            2),
     t AS
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
          case WHEN t.details->'auditDetails'->>'name' ~ '\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$' THEN regexp_replace(t.details->'auditDetails'->>'name', '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') ELSE t.details->'auditDetails'->>'name' END AS "Trigger Form",
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
                                                                                                                              WHEN t.status ILIKE 'notStarted' THEN 1
                                                                                                                              ELSE 0
                                                                                                                          END AS "Not Started Count",
                                                                                                                          CASE
                                                                                                                              WHEN (t.status ILIKE 'started'
                                                                                                                                    OR t.status ILIKE 'reopened') THEN 1
                                                                                                                              ELSE 0
                                                                                                                          END AS "In Progress Count",
                                                                                                                          CASE
                                                                                                                              WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                              ELSE 0
                                                                                                                          END AS "Completed Count",
                                                                                                                          CASE
                                                                                                                              WHEN t.status ILIKE 'completed'
                                                                                                                                   AND completed_at <= deadline THEN 1
                                                                                                                              ELSE 0
                                                                                                                          END AS "On Time Completed Count",
                                                                                                                          CASE
                                                                                                                              WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                              ELSE 0
                                                                                                                          END AS "Reopened Count",
                                                                                                                          t.details->>'comment' AS "Completion Comment",
                                                                                                                                      t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                  t.details->'auditDetails'->>'questionGroupId' AS theme_knid,
                                                                                                                                                                                                              t.details->'auditDetails'->>'questionId' AS checkpoint_knid
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN td ON t.organization = td.organization
   JOIN forms ON t.details->'auditDetails'->>'responseId' = forms.response_id
   WHERE t.is_deleted = 'false' ),   
   task_assignees AS
  (SELECT t."Task KNID",
          string_Agg(ud.first_name||' '||ud.last_name, ', ') AS assignee_list
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   join user_Details ud on ar.user_id = ud.uuid 
   WHERE ar.event_id = 1
   GROUP BY 1),
     tfq AS
  (SELECT qd.nugget_id AS form_knid,
          qd.question_id AS theme_knid,
          qd.question AS theme,
          q.key AS checkpoint_knid,
          q.value->>'question' AS CHECKPOINT
   FROM question_definitions qd,
        LATERAL jsonb_each(qd.definition->'questions') AS q
   WHERE qd.question_id IN
       (SELECT theme_knid
        FROM t)
   GROUP BY 1,
            2,
            3,
            4,
            5),
     cms AS
  (SELECT cms.store_id,
          cms.audit_submission_knid
   FROM checkpoint_master_sheet_table cms
   JOIN forms ON cms.audit_submission_knid = forms.response_id
   where cms.store_id in (select job_location from location_acl)
   GROUP BY 1,
            2),
     fu AS
  (SELECT cms.store_id AS "Location",
          "Trigger Form",
          "Trigger Form Submission No",
          tfq.theme AS "Theme",
          tfq.checkpoint AS "Checkpoint",
          "Status",
          "Assigned At",
          "Deadline",
          "Started At",
          "Completed At",
          "Reopened At",
          "Assigned By",
   ta.assignee_list as "Assignees",
          "Started By",
          "Completed By",
          "Completion Comment",
          "Completion Image",
          "Reopened By",
          "Overdue Count",
          "Not Started Count",
          "In Progress Count",
          "Completed Count",
          "Reopened Count",
          t."Task KNID",
          "Org",
          "Task ID",
          "Task",
          "Trigger Form KNID",
          "Trigger Form Submission KNID",
          tfq.theme_knid AS "Theme KNID",
          tfq.checkpoint_knid AS "Checkpoint KNID"
   FROM t
   LEFT OUTER JOIN tfq ON t."Trigger Form KNID" = tfq.form_knid
   AND t.theme_knid = tfq.theme_knid
   AND t.checkpoint_knid = tfq.checkpoint_knid
   JOIN cms ON t."Trigger Form Submission KNID" = cms.audit_submission_knid
   left outer join task_assignees ta on t."Task KNID" = ta."Task KNID"
   ORDER BY 10 DESC, 9 DESC, 1,
                             2,
                             3,
                             4,
                             5,
                             7,
                             8),
     cmscp AS
  (SELECT audit_submission_knid,
          checkpoint_knid,
          RESULT,
          auditor_observations
   FROM checkpoint_master_sheet_table cms
   JOIN forms ON cms.audit_submission_knid = forms.response_id
   WHERE total_follow_up_tasks > 0
     AND organization_id = 'Alamar-DD-antenna'
     AND auditor_observations IS NOT NULL),
     cms_theme_score AS
  (SELECT audit_submission_knid,
          theme,
          sum(CASE
                  WHEN result_score = '' THEN NULL
                  ELSE result_score::numeric
              END)/sum(CASE
                           WHEN max_score = '' THEN NULL
                           ELSE max_score::numeric
                       END) AS theme_score
   FROM checkpoint_master_sheet_table cms
   JOIN forms ON cms.audit_submission_knid = forms.response_id
   WHERE organization_id = 'Alamar-DD-antenna'
   GROUP BY 1,
            2)
SELECT 
s.country as "Country",
s.region as "Region",
s.city as "City",
fu."Location",
       fu."Trigger Form",
       fu."Trigger Form Submission No",
       fu."Theme",
       cmsts.theme_score AS "Theme Score",
       fu."Checkpoint",
       cmscp.result AS "Result",
       cmscp.auditor_observations AS "Observation",
       fu."Status",
       fu."Assigned At",
       fu."Deadline",
       fu."Started At",
       fu."Completed At",
       fu."Reopened At",
       fu."Assigned By",
	   fu."Assignees",
       fu."Started By",
       fu."Completed By",
       fu."Completion Comment",
       fu."Completion Image",
       fu."Reopened By",
       fu."Overdue Count",
       fu."Not Started Count",
       fu."In Progress Count",
       fu."Completed Count",
       fu."Reopened Count",
       fu."Task KNID",
       fu."Org",
       fu."Task",
       fu."Trigger Form KNID",
       fu."Trigger Form Submission KNID",
       fu."Theme KNID",
       fu."Checkpoint KNID"
FROM fu
LEFT OUTER JOIN cmscp ON fu."Trigger Form Submission KNID" = cmscp.audit_submission_knid
AND fu."Checkpoint KNID" = cmscp.checkpoint_knid
LEFT OUTER JOIN cms_theme_score cmsts ON fu."Trigger Form Submission KNID" = cmsts.audit_submission_knid
AND fu."Theme" = cmsts.Theme
LEFT OUTER JOIN stores s on fu."Location" = s.store_id
ORDER BY 13 DESC,
         12 DESC,
         1,
         2,
         3,
         4,
         5,
         7,
         9
```

---

## Alamar DD Visits Tracker_DM Visits Tracker.sql

**Tables referenced:** acl, audit_location_questions, audit_locations, cal, dm, dm_groups, form_responses, form_submissions, generate_series, location_acl, nuggets, question_definitions, rm, rm_groups, store_map, stores, submissions, user_details, user_groups, visits

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `isAudit` -> `is_audit` (alias: `is_audit AS "isAudit"`)


**Original Query:**

```sql
-- Data Source: Alamar DD Visits Tracker
-- Dashboard: DM Visits Tracker
-- Category: Alamar DD
-- Extracted: 2026-01-29 16:59:55
-- ============================================================

WITH 
location_acl as (SELECT DISTINCT job_location
FROM user_details
WHERE organization = @{{:OrganizationParameter}}
				 and designation ilike 'Store%'
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
cal AS
  (SELECT MONTH
   FROM generate_series('2023-07-01', CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Cairo', '1 month') AS m(MONTH)),
     store_map AS
  (WITH stores AS
     (SELECT *
      FROM user_details
      WHERE job_type ILIKE 'Store%'
        AND organization ILIKE 'Alamar-DD-antenna'),
        dm AS
     (SELECT *
      FROM user_details
      WHERE designation IN ('DM',
                            'District Manager')
        AND organization ILIKE 'Alamar-DD-antenna'),
        rm AS
     (SELECT *
      FROM user_details
      WHERE designation IN ('RM',
                            'Regional Manager')
        AND organization ILIKE 'Alamar-DD-antenna'),
        dm_groups AS
     (SELECT dm.*,
             group_id
      FROM user_groups ug
      JOIN dm ON ug.user_id = dm.uuid
      AND ug.has_access = 'true'),
        rm_groups AS
     (SELECT rm.*,
             group_id
      FROM user_groups ug
      JOIN rm ON ug.user_id = rm.uuid
      AND ug.has_access = 'true'),
        acl AS
     (SELECT stores.identifier AS store_id,
             stores.first_name||' - '||stores.last_name AS store_name,
             CASE
                 WHEN stores.division ILIKE 'KSA%' THEN 'KSA'
                 WHEN stores.division ILIKE 'PK %' THEN 'Pakistan'
                 ELSE stores.division
             END AS country,
             stores.division AS region,
             stores.sub_division AS city,
             max(dm_groups.uuid) AS dm_knid,
             max(rm_groups.uuid) AS rm_knid
      FROM stores
      LEFT OUTER JOIN user_groups ug ON stores.uuid = ug.user_id
      AND ug.is_active = 'true'
      LEFT OUTER JOIN dm_groups ON ug.group_id = dm_groups.group_id
      LEFT OUTER JOIN rm_groups ON ug.group_id = rm_groups.group_id
      GROUP BY 1,
               2,
               3,
               4,
               5) SELECT acl.*,
                         dm.first_name||' '||dm.last_name AS dm,
                         rm.first_name||' '||rm.last_name AS rm
   FROM acl
   LEFT OUTER JOIN user_details dm ON acl.dm_knid = dm.uuid
   LEFT OUTER JOIN user_details rm ON acl.rm_knid = rm.uuid
   ORDER BY 2,
            3,
            4,
            1),
     stores AS
  (SELECT identifier AS store_id,
          last_name AS store_name,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE designation ILIKE 'Store%'
     AND organization ILIKE 'Alamar-DD%'),
     audit_location_questions AS
  (SELECT nugget_id,
          question_id
   FROM
     (SELECT DISTINCT ON (nugget_id) nugget_id,
                         jsonb_object_keys(definition -> 'questions') question_id,
                         definition -> 'questions' questions
      FROM question_definitions qd
      WHERE question_type = 'nested'
        AND sqno = '1'
      ORDER BY nugget_id,
               created_at DESC) q
   WHERE questions -> question_id ->> 'question_type' = 'location' ),
     audit_locations AS
  (SELECT nugget_id AS form_id,
          fs.response_id,
          fr.response ->> 'name' AS audit_location
   FROM audit_location_questions alq
   JOIN form_submissions fs ON alq.nugget_id = fs.form_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND alq.question_id = fr.question_id
   WHERE fs.organization = 'Alamar-DD-antenna'),
     submissions AS
  (SELECT CASE
              WHEN n.details->>'isAudit' = 'true' THEN left(al.audit_location, 6)
              ELSE lefT(fs.location, 6)
          END AS store_id,
          CASE
              WHEN n.title ILIKE 'Food Safety%' THEN 'Food Safety'
              WHEN n.title ILIKE 'General%' THEN 'Gen'
              WHEN n.title ILIKE 'Opening%' THEN 'Opening'
              WHEN n.title ILIKE 'Closing%' THEN 'Closing'
              WHEN n.title ILIKE 'Maint%' THEN 'Maintenance'
              WHEN n.title ILIKE 'Rush%' THEN 'Rush'
              WHEN n.title ILIKE 'Training%' THEN 'Training'
              WHEN n.title ILIKE 'ROR%' THEN 'ROR'
              ELSE n.title
          END AS form,
          fs.sno,
          ud.first_name||' '||ud.last_name AS submitted_by,
          (fs.submit_date AT TIME ZONE 'Africa/Cairo')::date AS submit_date,
          (fr.response ->> 'auditStatus') AS audit_status,
          (fr.response ->> 'auditScore')::numeric AS actual_score,
          (fr.response ->> 'auditMaxScore')::numeric AS max_score,
          fs.user_id,
          fs.form_id,
          fs.response_id
   FROM form_submissions fs
   LEFT OUTER JOIN form_responses fr ON fr.form_submit_id = fs.id
   AND fr.question_id = 'formAuditResults'
   LEFT OUTER JOIN audit_locations al ON fs.response_id = al.response_id
   JOIN nuggets n ON fs.form_id = n.id
   JOIN user_details ud ON fs.user_id = ud.uuid
   WHERE fs.organization = 'Alamar-DD-antenna'
     AND ud.phone_number NOT ILIKE '+9111%' --and fs.submit_date AT TIME ZONE 'Africa/Cairo' between date_trunc('Month', CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Cairo') and date_trunc('Month', CURRENT_TIMESTAMP AT TIME ZONE 'Africa/Cairo') + interval '1 month'

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
            11),
     visits AS
  (SELECT 'Food Safety' AS form
   UNION SELECT 'Gen'
   UNION SELECT 'Opening'
   UNION SELECT 'Closing'
   UNION SELECT 'Rush'
   UNION SELECT 'Training'
   UNION SELECT 'Maintenance'
   UNION SELECT 'ROR')
SELECT store_map.country,
       store_map.region,
       store_map.city,
       store_map.store_id,
       store_map.store_name,
       store_map.dm,
       visits.form,
       cal.month,
       submissions.sno,
       submissions.submitted_by,
       submissions.submit_date,
       submissions.audit_status,
       submissions.actual_score,
       submissions.max_score,
       submissions.user_id,
       submissions.form_id,
       submissions.response_id
FROM store_map
CROSS JOIN visits
CROSS JOIN cal
LEFT OUTER JOIN submissions ON submissions.store_id = store_map.store_id
AND submissions.form = visits.form
AND date_trunc('Month', submissions.submit_date) = cal.month
join location_acl on left(location_acl.job_location, 6) = store_map.store_id
```

---
