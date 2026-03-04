# Delivery Hero

> Auto-generated on 2026-03-04 08:13

**Total queries:** 19

---

## CC Compliance_CC Dashboard.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: CC Compliance
-- Dashboard: CC Dashboard
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:17
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod",
		"QueryTable 1"."Country" AS "Country"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   AND job_location NOT ILIKE '%HO'
AND job_location NOT ILIKE 'MY Fresh DC'
   --and is_active = 'true'
   --and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",max(ud.division) as "Country"
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
Join user_details ud on fc."Location" = ud.job_location
where fc."Organization" =@{{:OrganizationParameter}}
AND fc."Reminded At" at time zone 'Asia/Kuala_Lumpur' BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	 and "Location" NOT IN ('HQ','KNOW')
	 and fc."Routine Name" IN ('Daily Cleaning Checklist v2','Weekly Cleaning Checklist v2','Monthly Cleaning Checklist')
	 group by 1,2,3,4,5,6,7,8,9,10,11
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## DH Audit Tasks_DH Audits.sql

**Tables referenced:** MAP, acl, analytics_requests, assignees, checkpoint_master_sheet_table, locations, org, role_holders, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: DH Audit Tasks
-- Dashboard: DH Audits
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:46
-- ============================================================

WITH org as (select organization from user_details where uuid = @{{:DH Audits.UuidParameter}}),
			 acl AS
  (SELECT DISTINCT store_id, organization
   FROM
     (SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
	  join org on l.organization = org.organization
      WHERE rh.role_holder_id = @{{:DH Audits.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
	  join org on l.organization = org.organization
      WHERE ug.user_id = @{{:DH Audits.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id, user_details.organization
      FROM user_details
	  join org on user_Details.organization = org.organization
        AND user_Details.is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:DH Audits.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:DH Audits.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.organization, acl.store_id) acl.organization, acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.organization, acl.store_id, ud.created_at),
						  t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   CASE 
    WHEN t.status ILIKE 'completed' THEN 0
    ELSE DATE_PART('day', CURRENT_TIMESTAMP - to_timestamp(t.created_at/1000) AT TIME ZONE 'Europe/Berlin')
END AS "Aging",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Europe/Berlin' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000)
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000)
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) 
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at as "Audited At",
   replace(cms.CHECKPOINT, left(cms.checkpoint, position(':' in cms.checkpoint)+1), '') as "Checkpoint",
   left(cms.checkpoint, position(':' in cms.checkpoint)-1) as "Criticality",
   map.Country as "Country",
   map.City as "City",
    CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   JOIN MAP ON cms.store_id = map.store_id and t.organization = map.organization
   WHERE t.is_deleted = 'false'
     AND cms.audit_submitted_at BETWEEN @{{:DH Audits.Date Range.START}}::timestamp AND @{{:DH Audits.Date Range.END}}::timestamp + interval '1 day'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40,41,42),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
	   assignees.assignee AS "Assigneee",
       assignees.department AS "Assignee Department",
	   CASE 
    WHEN t."Status" ILIKE 'completed' THEN DATE_PART('day', "Completed At" - "Assigned At")
    ELSE NULL
END AS "TAT (Days)"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
```

---

## DH Audit Tasks_superadmin_DH Audits Superadmin.sql

**Tables referenced:** MAP, acl, analytics_requests, assignees, checkpoint_master_sheet_table, locations, t, tasks, user_details

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: DH Audit Tasks_superadmin
-- Dashboard: DH Audits Superadmin
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:58
-- ============================================================

WITH acl AS
  (SELECT DISTINCT l.location_name AS store_id, l.organization
      FROM locations l 
      WHERE organization in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
        AND is_active = 'true'),
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.store_id, ud.created_at),
						  t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   CASE 
    WHEN t.status ILIKE 'completed' THEN 0
    ELSE DATE_PART('day', CURRENT_TIMESTAMP - to_timestamp(t.created_at/1000) AT TIME ZONE 'Europe/Berlin')
END AS "Aging",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) 
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) 
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) 
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at as "Audited At",
   replace(cms.CHECKPOINT, left(cms.checkpoint, position(':' in cms.checkpoint)+1), '') as "Checkpoint",
   left(cms.checkpoint, position(':' in cms.checkpoint)-1) as "Criticality",
   map.Country as "Country",
   map.City as "City",
    CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   JOIN MAP ON cms.store_id = map.store_id
   WHERE t.is_deleted = 'false'
     AND cms.audit_submitted_at BETWEEN @{{:DH Audits_superadmin.Date Range.START}}::timestamp AND @{{:DH Audits_superadmin.Date Range.END}}::timestamp + interval '1 day'
     AND t.organization in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40,41,42),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
	   assignees.assignee AS "Assigneee",
       assignees.department AS "Assignee Department",
	   CASE 
    WHEN t."Status" ILIKE 'completed' THEN DATE_PART('day', "Completed At" - "Assigned At")
    ELSE NULL
END AS "TAT (Days)"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
```

---

## DH Audits Summary_DH Audits.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, locations, map, org, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: DH Audits Summary
-- Dashboard: DH Audits
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:47
-- ============================================================

WITH org as (select organization from user_details where uuid = @{{:DH Audits.UuidParameter}}),
			 acl AS
  (SELECT DISTINCT store_id, organization
   FROM
     (SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
	  join org on l.organization = org.organization
      WHERE rh.role_holder_id = @{{:DH Audits.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
	  join org on l.organization = org.organization
      WHERE ug.user_id = @{{:DH Audits.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id, user_details.organization
      FROM user_details
	  join org on user_Details.organization = org.organization
        AND user_Details.is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:DH Audits.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:DH Audits.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.organization, acl.store_id) acl.organization, acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.organization, acl.store_id, ud.created_at)
		select map.country AS "Country",
		map.city as "City", 
       map.store_id AS "Store",
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
	   to_char(@{{:DH Audits.Date Range.START}}::timestamp, 'DD-Mon-YYYY') as "Start Date",
	   to_char(@{{:DH Audits.Date Range.END}}::timestamp, 'DD-Mon-YYYY') as "End Date",       
                               sum(CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END)/sum(                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END) AS "Audit Score"
FROM map left outer join checkpoint_master_sheet_table cms on cms.store_id = map.store_id and cms.organization_id = map.organization
WHERE audit_submitted_at between @{{:DH Audits.Date Range.START}}::timestamp and @{{:DH Audits.Date Range.END}}::timestamp + interval '1 day'
  group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
  order by 1, 2, 3, 4, 5, 6
```

---

## DH Audits Summary_superadmin_DH Audits Superadmin.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, locations, map, user_details

**Original Query:**

```sql
-- Data Source: DH Audits Summary_superadmin
-- Dashboard: DH Audits Superadmin
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:57
-- ============================================================

WITH acl AS
  (SELECT DISTINCT l.location_name AS store_id, l.organization
      FROM locations l 
      WHERE organization in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
        AND is_active = 'true'),
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.store_id, ud.created_at)
		select map.country AS "Country",
		map.city as "City", 
       map.store_id AS "Store",
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
	   to_char(@{{:DH Audits_superadmin.Date Range.START}}::timestamp, 'DD-Mon-YYYY') as "Start Date",
	   to_char(@{{:DH Audits_superadmin.Date Range.END}}::timestamp, 'DD-Mon-YYYY') as "End Date",       
                               sum(CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END)/sum(                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END) AS "Audit Score"
FROM map left outer join checkpoint_master_sheet_table cms on cms.store_id = map.store_id
WHERE organization_id in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
  and audit_submitted_at between @{{:DH Audits_superadmin.Date Range.START}}::timestamp and @{{:DH Audits_superadmin.Date Range.END}}::timestamp + interval '1 day'
  group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
  order by 1, 2, 3, 4, 5, 6
```

---

## DH Audits_DH Audits.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, locations, map, org, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: DH Audits
-- Dashboard: DH Audits
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:48
-- ============================================================

WITH org as (select organization from user_details where uuid = @{{:UuidParameter}}),
			 acl AS
  (SELECT DISTINCT store_id, organization
   FROM
     (SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
	  join org on l.organization = org.organization
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
	  join org on l.organization = org.organization
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id, user_details.organization
      FROM user_details
	  join org on user_Details.organization = org.organization
        AND user_Details.is_active = 'true'    
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
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.organization, acl.store_id) acl.organization, acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.organization, acl.store_id, ud.created_at)
		select map.country AS "Country",
		map.city as "City", 
       map.store_id AS "Store",
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       replace(CHECKPOINT, left(checkpoint, position(':' in checkpoint)+1), '') AS "Checkpoint",
                     RESULT AS "Result",
                              left(checkpoint, position(':' in checkpoint)-1) AS "Criticality",
                               CASE
                                   WHEN result = 'NA' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result = 'NA' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN total_follow_up_tasks IS NULL
                                        OR total_follow_up_tasks = 0 THEN 'No Follow Up'
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 'Closed'
                                   ELSE 'Open'
                               END AS "Status",
							   CASE
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1.0
                                   ELSE 0.0
                               END AS "Closed Count",
							   CASE
                                  WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1.0
                                   ELSE 0.0
                               END AS "Open Count"
FROM map left outer join checkpoint_master_sheet_table cms on cms.store_id = map.store_id and map.organization = cms.organization_id
WHERE audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  order by 1, 2, 3, 4, 5, 6, 10, 12
```

---

## DH Audits_superadmin_DH Audits Superadmin.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, locations, map, user_details

**Original Query:**

```sql
-- Data Source: DH Audits_superadmin
-- Dashboard: DH Audits Superadmin
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:57
-- ============================================================

WITH acl AS
  (SELECT DISTINCT l.location_name AS store_id, l.organization
      FROM locations l 
      WHERE organization in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
        AND is_active = 'true'),
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.store_id, ud.created_at)
		select map.country AS "Country",
		map.city as "City", 
       map.store_id AS "Store",
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       replace(CHECKPOINT, left(checkpoint, position(':' in checkpoint)+1), '') AS "Checkpoint",
                     RESULT AS "Result",
                              left(checkpoint, position(':' in checkpoint)-1) AS "Criticality",
                               CASE
                                   WHEN result = 'NA' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result = 'NA' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN total_follow_up_tasks IS NULL
                                        OR total_follow_up_tasks = 0 THEN 'No Follow Up'
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 'Closed'
                                   ELSE 'Open'
                               END AS "Status",
							   CASE
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1.0
                                   ELSE 0.0
                               END AS "Closed Count",
							   CASE
                                  WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1.0
                                   ELSE 0.0
                               END AS "Open Count"
FROM map left outer join checkpoint_master_sheet_table cms on cms.store_id = map.store_id
WHERE organization_id in ('foodpanda-antenna', 'foodora-antenna', 'yemeksepeti-antenna')
  and audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  order by 1, 2, 3, 4, 5, 6, 10, 12
```

---

## DH Product Inspection Compliance_Product Inspection.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, po_compliance, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, raw_pos, td, user_details, weekly_pos

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: DH Product Inspection Compliance
-- Dashboard: Product Inspection
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:52:21
-- ============================================================

WITH td AS (
    SELECT id AS organization,
           tzoffset,
           interval '1 min' * tzoffset AS diff
    FROM organizations
    WHERE id = 'foodpanda-antenna'
    GROUP BY 1, 2
),
forms AS (
    SELECT id AS form_knid,
           title AS form_name
    FROM nuggets n
    WHERE title ILIKE '%Incoming Product Quality & Food Safety Inspection%'
      AND organization = 'foodpanda-antenna'
      AND is_deleted = false
    GROUP BY 1, 2
),
qd_non_table_non_logic AS (
    SELECT nugget_id AS form_knid,
           CASE WHEN qd.section_id = 'section' THEN 1
                ELSE replace(section_id, 'section-', '')::integer
           END AS section_no,
           CASE WHEN qd.question_type = 'section' THEN 0
                ELSE sqno::integer*10000
           END AS q_no,
           section_id,
           question_id AS parent_qid,
           question_type AS parent_q_type,
           question AS parent_question,
           question_id AS qid,
           question_type AS q_type,
           question
    FROM forms
    JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
    WHERE question_type NOT IN ('table')
),
qdntwl_prework AS (
    SELECT *,
           jsonb_array_elements(definition -> 'logic') -> 'questions' q
    FROM forms
    JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
    WHERE qd.definition -> 'logic' IS NOT NULL
),
qd_non_table_with_logic AS (
    SELECT nugget_id AS form_knid,
           CASE WHEN qd.section_id = 'section' THEN 1
                ELSE replace(section_id, 'section-', '')::integer
           END AS section_no,
           sqno::integer*10000 + (def.value->>'order')::integer AS q_no,
           section_id,
           question_id AS parent_qid,
           question_type AS parent_q_type,
           question AS parent_question,
           def.key AS qid,
           def.value->>'question_type' AS q_type,
           def.value->>'question' AS question
    FROM qdntwl_prework qd
    CROSS JOIN jsonb_each(qd.q) def
    WHERE definition ->>'logic' IS NOT NULL
),
qd_table AS (
    SELECT nugget_id AS form_knid,
           CASE WHEN qd.section_id = 'section' THEN 1
                ELSE replace(section_id, 'section-', '')::integer
           END AS section_no,
           sqno::integer*10000 + (def.value->>'order')::integer AS q_no,
           section_id,
           question_id AS parent_qid,
           question_type AS parent_q_type,
           question AS parent_question,
           def.key AS qid,
           def.value->>'question_type' AS q_type,
           def.value->>'question' AS question
    FROM forms
    JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
    CROSS JOIN jsonb_each(definition -> 'questions') def
    WHERE qd.question_type = 'table'
),
final_definition AS (
    SELECT * FROM qd_non_table_non_logic
    UNION ALL
    SELECT * FROM qd_non_table_with_logic
    UNION ALL
    SELECT * FROM qd_table
    ORDER BY 1,2,3,5 DESC,7 DESC
),
_fs AS (
    SELECT DISTINCT ON (response_id) form_submissions.*,
           form_name
    FROM forms
    JOIN form_submissions ON forms.form_knid = form_submissions.form_id
    ORDER BY response_id, id DESC
),
fs AS (
    SELECT *
    FROM _fs
    WHERE submit_date BETWEEN @{{:DH Product Inspection.Date Range.START}}::timestamp
                          AND @{{:DH Product Inspection.Date Range.END}}::timestamp + interval '1 day'
),
fr AS (
    SELECT fs.organization,
           form_submit_id,
           form_id,
           form_name,
           sno,
           submit_date + td.diff AS submit_date,
           user_id,
           response_id,
           question_id AS parent_qid,
           question_id AS qid,
           question_type,
           response,
           1 AS rn,
           location
    FROM form_responses fr
    JOIN fs ON fs.id = fr.form_submit_id
    JOIN td ON fs.organization = td.organization
    WHERE question_type NOT IN ('table','nested')

    UNION ALL

    SELECT organization,
           form_submit_id,
           form_id,
           form_name,
           sno,
           submit_date,
           user_id,
           response_id,
           question_id AS parent_qid,
           res.key AS qid,
           question_type,
           res.value AS response,
           rn,
           location
    FROM (
        SELECT fs.organization,
               form_submit_id,
               form_id,
               form_name,
               sno,
               submit_date + td.diff AS submit_date,
               user_id,
               response_id,
               question_id,
               question_type,
               base.value,
               base.ordinality AS rn,
               location
        FROM form_responses fr
        JOIN fs ON fs.id = fr.form_submit_id
        JOIN td ON fs.organization = td.organization,
             jsonb_array_elements(response) WITH ORDINALITY AS base
        WHERE question_type = 'table'
    ) base1
    CROSS JOIN jsonb_each(base1.value) res
),
RAW AS (
    SELECT fr.sno,
           fd.section_no,
           fd.q_no,
           fd.parent_question,
           fd.question,
           q_type,
           CASE
               WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
               WHEN fd.q_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') THEN fr.response -> 'selected'->>0
               WHEN fd.q_type IN ('checkboxes') THEN array_to_string(
                   ARRAY(
                       SELECT jsonb_array_elements_text(fr.response->'selected')
                       UNION
                       SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText' ELSE NULL END
                   ), ', '
               )
               WHEN fd.q_type IN ('date', 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
               WHEN fd.q_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula') THEN fr.response->>0
               WHEN fd.q_type IN ('user') THEN fr.response::text
               WHEN fd.q_type IN ('upload_mixed','upload_image','upload_video','upload_file') THEN (fr.response)->0->>'response'
               WHEN fd.q_type IN ('signature','location','division','sub_division') THEN fr.response ->> 'name'
               ELSE NULL
           END AS response,
           fr.submit_date AS submit_date,
           ud.division AS region,
           form_name
    FROM final_definition fd
    JOIN fr ON fr.qid = fd.qid AND fr.form_id = fd.form_knid
    JOIN td ON fr.organization = td.organization
    JOIN user_details ud ON fr.user_id = ud.uuid
),

-- Extract Store Name and each PO as separate row
raw_pos AS (
     SELECT
        po.region,
        po.submit_date,
        po.form_name,
        sn.store_name,
        po.response AS po_number
    FROM raw po
    JOIN (
        SELECT
            sno,
            MAX(response) AS store_name
        FROM raw
        WHERE question ILIKE '%Store Name%'
        GROUP BY sno
    ) sn
      ON po.sno = sn.sno
    WHERE po.question ILIKE '%PO Number%'
),

-- Count distinct POs per store per week
weekly_pos AS (
    SELECT
        region,
        form_name,
        store_name,
        date_trunc('week', submit_date) AS week_start,
        COUNT(DISTINCT po_number) AS po_count
    FROM raw_pos
    GROUP BY region, form_name, store_name, date_trunc('week', submit_date)
),

-- Compute compliance and deviation against 5 POs/week
po_compliance AS (
    SELECT
        region,
        form_name,
        store_name AS "Store Name",
        week_start,
        po_count,

        /* Region-wise expected PO count */
        CASE
            WHEN region = 'Bangladesh'  THEN 5
            WHEN region = 'Hong Kong'   THEN 15
            WHEN region = 'Malaysia'    THEN 15
            WHEN region = 'Pakistan'    THEN 15
            WHEN region = 'Philippines' THEN 4
            WHEN region = 'Singapore'   THEN 15
            ELSE 0
        END AS expected_pos,

        /* Compliance check */
        CASE
            WHEN po_count >=
                CASE
                    WHEN region = 'Bangladesh'  THEN 5
                    WHEN region = 'Hong Kong'   THEN 15
                    WHEN region = 'Malaysia'    THEN 15
                    WHEN region = 'Pakistan'    THEN 15
                    WHEN region = 'Philippines' THEN 4
                    WHEN region = 'Singapore'   THEN 15
                    ELSE 0
                END
            THEN 'Compliant'
            ELSE 'Non-Compliant'
        END AS compliance_status,

        /* Deviation */
        GREATEST(
            CASE
                WHEN region = 'Bangladesh'  THEN 5
                WHEN region = 'Hong Kong'   THEN 15
                WHEN region = 'Malaysia'    THEN 15
                WHEN region = 'Pakistan'    THEN 15
                WHEN region = 'Philippines' THEN 4
                WHEN region = 'Singapore'   THEN 15
                ELSE 0
            END - po_count,
            0
        ) AS deviation
    FROM weekly_pos
)

SELECT *,SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) AS compliant_count
FROM po_compliance
group by 1,2,3,4,5,6,7,8
ORDER BY region, "Store Name", week_start
```

---

## DH Product Inspection_Product Inspection.sql

**Tables referenced:** data_team.dh_product_inspection

**Original Query:**

```sql
-- Data Source: DH Product Inspection
-- Dashboard: Product Inspection
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:52:36
-- ============================================================

select *
from data_team.dh_product_inspection
where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
```

---

## DH Temp_Temp Log.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: DH Temp
-- Dashboard: Temp Log
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:52:24
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location,division,sub_division
   FROM user_details
   WHERE organization = 'foodpanda-antenna'
     AND is_active = 'true'
     --AND job_location NOT ILIKE 'Head Office%'
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
               AND ug1.is_active = TRUE))),td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'foodpanda-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE ( title ilike '%Temperature Log - SEA%' or title ilike '%Temperature Log - PK & BD%')
     AND organization = 'foodpanda-antenna'
    and is_deleted = false
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
  form_name,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
  form_name,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
  form_name,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          location
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn,
                location
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             location
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
   /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd 
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
         fr.form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
   location_acl.division,
      location_acl.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   Join location_acl on fr.location = location_acl. job_location
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
   14,15,16
   ORDER BY 1,
            2,
            3)
SELECT
    form_name,
    sno,
    submit_date,
    location,
	division,
	sub_division,
    equipment_type,
    MAX(equipment_no) AS equipment_no,
    MAX(reading) AS reading,
    MAX(reading_status) AS reading_status
FROM (
    SELECT 
        form_name,
        sno,
        submit_date,
        location,
  division,
	sub_division,
        CASE 
            WHEN raw.parent_question LIKE '%Chiller Temperature - Fruit and vegetable%' THEN 'Chiller - Fruit and vegetable'
            WHEN raw.parent_question LIKE '%Chiller Temperature - General Chilled Items%' THEN 'Chiller - General Chilled Items'
            WHEN raw.parent_question LIKE '%Freezer Temperature%' THEN 'Freezer'
        END AS equipment_type,
        CASE 
            WHEN raw.question LIKE '%Equipment Number%' THEN response
        END AS equipment_no,
        CASE 
            WHEN raw.question LIKE '%Temperature Reading%' THEN response::numeric
        END AS reading,
        CASE
            WHEN raw.question LIKE '%Temperature Reading%' 
                 AND raw.parent_question LIKE '%Chiller Temperature - Fruit and vegetable%' 
                 AND CAST(response AS FLOAT) BETWEEN 0 AND 8 THEN 'In Range'
            WHEN raw.question LIKE '%Temperature Reading%' 
                 AND LOWER(parent_question) LIKE '%freezer%' 
                 AND CAST(response AS FLOAT) BETWEEN -23 AND -18 THEN 'In Range'
            WHEN raw.question LIKE '%Temperature Reading%' 
                 AND raw.parent_question LIKE '%Chiller Temperature - General Chilled Items%' 
                 AND CAST(response AS FLOAT) BETWEEN 0 AND 5 THEN 'In Range'
            WHEN raw.question LIKE '%Temperature Reading%' THEN 'Out of Range'
        END AS reading_status
    FROM raw
    WHERE raw.parent_question LIKE '%Chiller Temperature - Fruit and vegetable%'
       OR raw.parent_question LIKE '%Freezer Temperature%'
       OR raw.parent_question LIKE '%Chiller Temperature - General Chilled Items%'
) t
GROUP BY form_name, sno, submit_date, location, equipment_type,division,sub_division
ORDER BY submit_date DESC
```

---

## FD Daily CC_CC Dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: FD Daily CC
-- Dashboard: CC Dashboard
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:16
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:CC Compliance.OrganizationParameter}}
   AND job_location NOT ILIKE '%HO'
AND job_location NOT ILIKE 'MY Fresh DC'
   --and is_active = 'true'
   --and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:CC Compliance.UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:CC Compliance.UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'foodpanda-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title IN ('Daily Cleaning Checklist v2')
     AND organization = 'foodpanda-antenna'
     AND is_deleted = FALSE
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date between @{{:CC Compliance.Date Range.START}}::timestamp and @{{:CC Compliance.Date Range.END}}::timestamp + interval '1 day' ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          LOCATION
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn,
                LOCATION
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            16
   ORDER BY 1,
            2,
            3)
			SELECT
    sno,
    submit_date,
    location as "Location",
    "Country",
    CASE WHEN daily_resp ILIKE '%Floor - sweep%' THEN 'Yes' ELSE 'No' END AS floor_sweep,
    CASE WHEN daily_resp ILIKE '%Wall - remove dust%' THEN 'Yes' ELSE 'No' END AS wall_remove_dust,
    CASE WHEN daily_resp ILIKE '%Shelves - remove dust%' THEN 'Yes' ELSE 'No' END AS shelves_remove_dust,
    CASE WHEN daily_resp ILIKE '%Toilet - ensure in clean condition%' THEN 'Yes' ELSE 'No' END AS toilet_clean,
    CASE WHEN daily_resp ILIKE '%Pantry - including hand sink, microwave & water filter%' THEN 'Yes' ELSE 'No' END AS pantry_clean,
    CASE WHEN daily_resp ILIKE '%Cleaning Towels - rinse with appropriate chemical & air dry%' THEN 'Yes' ELSE 'No' END AS cleaning_towels,
    CASE WHEN daily_resp ILIKE '%Garbage Bin - ensure rubbish is clear before store closing%' THEN 'Yes' ELSE 'No' END AS garbage_bin_clear,
    CASE WHEN daily_resp ILIKE '%Packing Area - wipe with appropriate chemical%' THEN 'Yes' ELSE 'No' END AS packing_area_clean,
    CASE WHEN daily_resp ILIKE '%Surrounding (front entrance) - swipe%' THEN 'Yes' ELSE 'No' END AS surrounding_swipe,
    CASE WHEN daily_resp ILIKE '%Loading Area - swipe%' THEN 'Yes' ELSE 'No' END AS loading_area_swipe,
    CASE WHEN daily_resp ILIKE '%NC Area - ensure returned products to be clear within the set timeframe%' THEN 'Yes' ELSE 'No' END AS nc_area_clear,
    CASE WHEN daily_resp ILIKE '%Door Handle - wipe with appropriate chemical%' THEN 'Yes' ELSE 'No' END AS door_handle_clean

FROM (
    SELECT
        sno,
        submit_date,
        location,
        max(ud.division) as "Country",
        MAX(CASE WHEN question = 'Are these area/ equipment had cleaned?' THEN response END) AS daily_resp
    FROM raw
  JOIN location_acl on raw.location = location_acl.job_location
  Join user_details ud on raw.location = ud.job_location
    GROUP BY 1,2,3
) t
```

---

## FD Monthly CC_CC Dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: FD Monthly CC
-- Dashboard: CC Dashboard
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:15
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:CC Compliance.OrganizationParameter}}
   AND job_location NOT ILIKE '%HO'
AND job_location NOT ILIKE 'MY Fresh DC'
   --and is_active = 'true'
   --and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:CC Compliance.UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:CC Compliance.UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'foodpanda-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title IN ('Monthly Cleaning Checklist')
     AND organization = 'foodpanda-antenna'
     AND is_deleted = FALSE
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date between @{{:CC Compliance.Date Range.START}}::timestamp and @{{:CC Compliance.Date Range.END}}::timestamp + interval '1 day' ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          LOCATION
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn,
                LOCATION
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            16
   ORDER BY 1,
            2,
            3)
			 SELECT
        sno,
        submit_date,
        location,
        max(ud.division) as "Country",
        MAX(CASE WHEN question = 'Are all the freezers deep cleaned?' THEN response END) AS "Freezers Deep Cleaned ?"
    FROM raw
  JOIN location_acl on raw.location = location_acl.job_location
  Join user_details ud on raw.location = ud.job_location
    GROUP BY 1,2,3
```

---

## FD Weekly CC_CC Dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: FD Weekly CC
-- Dashboard: CC Dashboard
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:15
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:CC Compliance.OrganizationParameter}}
   AND job_location NOT ILIKE '%HO'
AND job_location NOT ILIKE 'MY Fresh DC'
   --and is_active = 'true'
   --and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:CC Compliance.UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:CC Compliance.UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'foodpanda-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title IN ('Weekly Cleaning Checklist v2')
     AND organization = 'foodpanda-antenna'
     AND is_deleted = FALSE
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer*10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table')),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer*10000+(def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table')),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date between @{{:CC Compliance.Date Range.START}}::timestamp and @{{:CC Compliance.Date Range.END}}::timestamp + interval '1 day' ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          LOCATION
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn,
                LOCATION
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            16
   ORDER BY 1,
            2,
            3)
			SELECT
    sno,
    submit_date,
    location as "Location",
    "Country",
    CASE WHEN daily_resp ILIKE '%Floor%' THEN 'Yes' ELSE 'No' END AS "Floor Deep Clean",
    CASE WHEN daily_resp ILIKE '%Shelves%' THEN 'Yes' ELSE 'No' END AS "Shelves Deep Clean",
    CASE WHEN daily_resp ILIKE '%Chiller%' THEN 'Yes' ELSE 'No' END AS "Chiller Deep Clean",
    CASE WHEN daily_resp ILIKE '%Store Room%' THEN 'Yes' ELSE 'No' END AS "Store Room"

FROM (
    SELECT
        sno,
        submit_date,
        location,
        max(ud.division) as "Country",
        MAX(CASE WHEN question = 'Are these area/ equipment had cleaned?' THEN response END) AS daily_resp
    FROM raw
  JOIN location_acl on raw.location = location_acl.job_location
  Join user_details ud on raw.location = ud.job_location
    GROUP BY 1,2,3
) t
```

---

## FoodPanda Routine_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: FoodPanda Routine
-- Dashboard: Routine Compliance
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:52:20
-- ============================================================

SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod",
		"QueryTable 1"."Country" AS "Country"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   AND job_location NOT ILIKE '%HO'
AND job_location NOT ILIKE 'MY Fresh DC'
   --and is_active = 'true'
   --and job_location not in ('KNOW', 'All', 'HO')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid =@{{:UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",max(ud.division) as "Country"
from form_compliance_v2 fc
join location_acl on LOWER(fc."Location") = LOWER(location_acl.job_location)
Join user_details ud on LOWER(fc."Location") = LOWER(ud.job_location)
where fc."Organization" =@{{:OrganizationParameter}}
AND fc."Reminded At" AT TIME ZONE 'Asia/Kuala_Lumpur' 
BETWEEN @{{:Date Range.START}}::timestamp 
AND @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
	 and "Location" NOT IN ('HQ','KNOW')
	 group by 1,2,3,4,5,6,7,8,9,10,11
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## Foodora - Forms_Foodora - Forms.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Foodora - Forms
-- Dashboard: Foodora - Forms
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:30
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'foodora-antenna'
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'foodora-antenna'),
			   forms as (select * from nuggets where organization = 'foodora-antenna'
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
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
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
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---

## Foodpanda Antenna - Forms_Foodpanda - Forms.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Foodpanda Antenna - Forms
-- Dashboard: Foodpanda - Forms
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:32
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'foodpanda-antenna'
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'foodpanda-antenna'),
			   forms as (select * from nuggets where organization = 'foodpanda-antenna'
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
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
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
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---

## PQFS Dashboard_PQFS Dashboard.sql

**Tables referenced:** _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, locations, nuggets, org, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, role_holders, submit_date, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sSp` -> `s_sp` (alias: `s_sp AS "sSp"`)


**Original Query:**

```sql
-- Data Source: PQFS Dashboard
-- Dashboard: PQFS Dashboard
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:54:18
-- ============================================================

WITH org as (select organization from user_details where uuid = @{{:UuidParameter}}),
			 acl AS
  (SELECT DISTINCT store_id, organization
   FROM
     (SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
	  join org on l.organization = org.organization
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id, l.organization
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
	  join org on l.organization = org.organization
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id, user_details.organization
      FROM user_details
	  join org on user_Details.organization = org.organization
        AND user_Details.is_active = 'true'    
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
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.organization, acl.store_id) acl.organization, acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id and ud.organization = acl.organization
						  where ud.is_active = 'true'
						  order by acl.organization, acl.store_id, ud.created_at),
						  td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'foodpanda-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Product Quality & Food Safety%')
     AND organization = 'foodpanda-antenna'
     AND is_deleted = FALSE
   GROUP BY 1,
            2),
     qd_non_table_non_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          CASE
              WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer * 10000
          END AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          question_id AS qid,
          question_type AS q_type,
          question AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   WHERE question_type NOT IN ('table') ),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL ),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer * 10000 + (def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL ),
     qd_table AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::integer * 10000 + (def.value->>'order')::integer AS q_no,
          section_id,
          question_id AS parent_qid,
          question_type AS parent_q_type,
          question AS parent_question,
          def.key AS qid,
          def.value->>'question_type' AS q_type,
                      def.value->>'question' AS question
   FROM forms
   JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE qd.question_type IN ('table') ),
     final_definition AS
  (SELECT *
   FROM qd_non_table_non_logic
   UNION SELECT *
   FROM qd_non_table_with_logic
   UNION SELECT *
   FROM qd_table
   ORDER BY 1,
            2,
            3,
            5 DESC, 7 DESC),
     _fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,extract(epoch from submit_date)*1000::bigint as submit_epoch
  from form_submissions
   where form_id IN (select form_knid from forms)
   --JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT _fs.*,forms.form_name
   FROM _fs
   JOIN forms on _fs.form_id = forms.form_knid
   WHERE submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day' ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          submit_epoch,
          user_id,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          question_type,
          response,
          1 AS rn,
          LOCATION
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT organization,
                form_submit_id,
                form_id,
                form_name,
                sno,
                submit_date,
                submit_epoch,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn,
                LOCATION
   FROM
     (SELECT fs.organization,
             form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date + td.diff AS submit_date,
	         submit_epoch,
             user_id,
             response_id,
             question_id,
             question_type,
             base.value,
             base.ordinality AS rn,
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table' ) base1
   CROSS JOIN jsonb_each(base1.value) res),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit') THEN fr.response -> 'selected' ->> 0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response ->> 0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location',
                                 'division',
                                 'sub_division') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date::DATE AS submit_date,
          fr.location,
          fr.user_id,
   		  ud.identifier,
          ud.division,
          ud.sub_division,
         fr.submit_epoch
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   LEFT JOIN user_details ud ON fr.user_id = ud.uuid
   JOIN acl on fr.location = acl.store_id
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
   19
   ORDER BY 1,
            2,
            3
            )

SELECT raw.*,
            MAX(CASE
               WHEN raw.question ilike '%Product Type%'
                    AND qid in ('-OVCKwXxWo-OCFXE4N9r', '-OVCMK5pRPQeU1dxEk3s') THEN fr.response -> 'selected' ->> 0
               ELSE NULL
           END) AS "Fresh fruit or vegetable dropdown",
           MAX(CASE
               WHEN raw.question ilike '%Product Type%'
                    AND qid = chr(45)||'OVCKwXyAIlwhvX'||chr(45)||chr(45)||'sSp' THEN fr.response -> 'selected' ->> 0
               ELSE NULL
           END) AS "Is there any NC identified dropdown?",
    COUNT(DISTINCT raw.response_id) AS actual_skus,
    (20 * ( @{{:Date Range.END}}::date - @{{:Date Range.START}}::date + 1 )) AS baseline_skus,
    ROUND(
    (COUNT(*) OVER (PARTITION BY raw.location)::numeric * 100)
    /
    NULLIF( (20 * ( @{{:Date Range.END}}::date - @{{:Date Range.START}}::date + 1 )), 0)
  , 2) AS baseline_pct,
    COUNT(DISTINCT raw.response_id) AS total_skus
            from raw
            JOIN fr ON raw.response_id = fr.response_id and raw.rn = fr.rn
			WHERE question NOT ILIKE '%Storage%'
AND q_type NOT IN ('section', 'title_description','qr_code','signature','single_text_field')
            group by 1,
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
			19
```

---

## Temperature Logs - Foodora_Foodora - Temperature Logs.sql

**Tables referenced:** QR, form_responses, form_submissions, jsonb_each, nuggets, organizations, parsed_readings, question_definitions, s.submit_date_local, submissions, table_column_mapping, table_columns, table_responses, td, temp_forms, user_details

**Original Query:**

```sql
-- Data Source: Temperature Logs - Foodora
-- Dashboard: Foodora - Temperature Logs
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:01
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) AS tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id = 'foodora-antenna'
    LIMIT 1
),
-- Get all temperature log forms dynamically by name
temp_forms AS (
    SELECT n.id AS form_id, n.title AS form_name
    FROM nuggets n
    WHERE n.organization = 'foodora-antenna'
    AND (
        n.title ILIKE '%Temperature Log%'
        OR n.title ILIKE '%Freezer Temperature%'
        OR n.title ILIKE '%Chiller Temperature%'
        OR n.title ILIKE '%Teploty mrazniček%'
        OR n.title ILIKE '%Teploty chladniček%'
    )
),
-- Get table question definitions with column mappings
table_columns AS (
    SELECT 
        qd.nugget_id AS form_id,
        qd.question_id AS table_qid,
        qd.question AS table_name,
        col.key AS col_id,
        col.value->>'question' AS col_question,
        col.value->>'question_type' AS col_type
    FROM question_definitions qd
    CROSS JOIN jsonb_each(qd.definition->'questions') AS col
    WHERE qd.nugget_id IN (SELECT form_id FROM temp_forms)
    AND qd.question_type = 'table'
),
-- Identify QR code equipment columns and temperature columns per table
table_column_mapping AS (
    SELECT 
        tc.form_id,
        tc.table_qid,
        tc.table_name,
        MAX(CASE WHEN tc.col_type = 'qr_code' THEN tc.col_id END) AS equipment_col_id,
        MAX(CASE WHEN tc.col_type = 'single_text_field' 
            AND (tc.col_question ILIKE '%Temperature%' OR tc.col_question ILIKE '%teploty%' OR tc.col_question ILIKE '%Odečet%')
            THEN tc.col_id END) AS temperature_col_id,
        MAX(CASE WHEN tc.col_type = 'upload_file' THEN tc.col_id END) AS photo_col_id
    FROM table_columns tc
    GROUP BY tc.form_id, tc.table_qid, tc.table_name
),
-- Get latest submission per response_id
submissions AS (
    SELECT DISTINCT ON (fs.response_id)
        fs.id AS submission_id,
        fs.response_id,
        fs.sno,
        fs.submit_date + td.diff AS submit_date_local,
        fs.submit_date AS submit_date_utc,
        fs.user_id,
        fs.location,
        fs.organization,
        fs.form_id
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id IN (SELECT form_id FROM temp_forms)
    AND fs.submit_date BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
    ORDER BY fs.response_id, fs.id DESC
),
-- Extract table responses and flatten rows
table_responses AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS table_qid,
        jsonb_array_elements(fr.response) AS row_data
    FROM form_responses fr
    WHERE fr.form_submit_id IN (SELECT submission_id FROM submissions)
    AND fr.question_type = 'table'
),
-- Parse temperature readings with equipment from QR code only
parsed_readings AS (
    SELECT 
        tr.submission_id,
        tcm.form_id,
        tcm.table_name,
        CASE 
            WHEN tcm.table_name ILIKE '%Freezer%' OR tcm.table_name ILIKE '%Fagyasztó%' OR tcm.table_name ILIKE '%mrazničky%'
            THEN 'Freezer'
            WHEN tcm.table_name ILIKE '%Fruit%' OR tcm.table_name ILIKE '%vegetable%' OR tcm.table_name ILIKE '%Ovoce%' OR tcm.table_name ILIKE '%zöldség%' OR tcm.table_name ILIKE '%zelenina%'
            THEN 'Chiller - Fruit/Vegetable'
            WHEN tcm.table_name ILIKE '%Egg%' OR tcm.table_name ILIKE '%Vejce%'
            THEN 'Chiller - Eggs'
            ELSE 'Chiller - General'
        END AS equipment_type,
        -- Equipment Number from QR code column only
        tr.row_data->>tcm.equipment_col_id AS equipment_number,
        -- Temperature reading
        NULLIF(TRIM(tr.row_data->>tcm.temperature_col_id), '')::NUMERIC AS temperature_reading,
        -- Photo URL
        CASE 
            WHEN tr.row_data->tcm.photo_col_id IS NOT NULL 
            THEN (tr.row_data->tcm.photo_col_id->0->>'response')
            ELSE NULL 
        END AS photo_url
    FROM table_responses tr
    JOIN table_column_mapping tcm ON tr.table_qid = tcm.table_qid
    WHERE tcm.equipment_col_id IS NOT NULL
)
-- Final output with all metadata
SELECT 
    -- Submission metadata
    s.response_id,
    s.sno AS submission_number,
    s.submit_date_local,
    s.submit_date_utc,
    DATE(s.submit_date_local) AS reading_date,
    TO_CHAR(s.submit_date_local, 'HH24:MI') AS reading_time,
    TO_CHAR(s.submit_date_local, 'Day') AS day_of_week,
    EXTRACT(HOUR FROM s.submit_date_local)::INTEGER AS hour_of_day,
    
    -- Location info (for Store filter)
    s.location AS store_name,
    SPLIT_PART(s.location, ' - ', 1) AS store_code,
    
    -- User/Division info (for Region filter)
    COALESCE(ud.division, 'Unknown') AS region,
    ud.sub_division,
    CONCAT(ud.first_name, ' ', ud.last_name) AS submitted_by,
    
    -- Form info
    tf.form_name,
    
    -- Temperature data
    pr.equipment_type,
    pr.equipment_number,
    pr.temperature_reading,
    pr.photo_url,
    
    -- Temperature range flags (configurable thresholds)
    -- Thresholds: Freezer ≤-18°C, General 0-5°C, Eggs 5-18°C, Fruit/Veg 0-10°C
    CASE 
        WHEN pr.equipment_type = 'Freezer' THEN
            CASE WHEN pr.temperature_reading > -18 THEN 'Too Warm' ELSE 'In Range' END
        WHEN pr.equipment_type = 'Chiller - Eggs' THEN
            CASE 
                WHEN pr.temperature_reading < 5 THEN 'Too Cold'
                WHEN pr.temperature_reading > 18 THEN 'Too Warm'
                ELSE 'In Range'
            END
        WHEN pr.equipment_type = 'Chiller - Fruit/Vegetable' THEN
            CASE 
                WHEN pr.temperature_reading < 0 THEN 'Too Cold'
                WHEN pr.temperature_reading > 10 THEN 'Too Warm'
                ELSE 'In Range'
            END
        ELSE -- Chiller - General (Standard chilled items)
            CASE 
                WHEN pr.temperature_reading < 0 THEN 'Too Cold'
                WHEN pr.temperature_reading > 5 THEN 'Too Warm'
                ELSE 'In Range'
            END
    END AS temperature_status,
    
    -- Deviation flag (1 = out of range, 0 = in range) - USE FOR KPI CARDS
    CASE 
        WHEN pr.equipment_type = 'Freezer' THEN
            CASE WHEN pr.temperature_reading > -18 THEN 1 ELSE 0 END
        WHEN pr.equipment_type = 'Chiller - Eggs' THEN
            CASE WHEN pr.temperature_reading < 5 OR pr.temperature_reading > 18 THEN 1 ELSE 0 END
        WHEN pr.equipment_type = 'Chiller - Fruit/Vegetable' THEN
            CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 10 THEN 1 ELSE 0 END
        ELSE -- Chiller - General
            CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 5 THEN 1 ELSE 0 END
    END AS is_deviation,
    
    -- Deviation status (Yes/No) for display
    CASE 
        WHEN pr.equipment_type = 'Freezer' THEN
            CASE WHEN pr.temperature_reading > -18 THEN 'Yes' ELSE 'No' END
        WHEN pr.equipment_type = 'Chiller - Eggs' THEN
            CASE WHEN pr.temperature_reading < 5 OR pr.temperature_reading > 18 THEN 'Yes' ELSE 'No' END
        WHEN pr.equipment_type = 'Chiller - Fruit/Vegetable' THEN
            CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 10 THEN 'Yes' ELSE 'No' END
        ELSE -- Chiller - General
            CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 5 THEN 'Yes' ELSE 'No' END
    END AS deviation_status,
    
    -- Threshold values (for chart reference lines)
    CASE 
        WHEN pr.equipment_type = 'Freezer' THEN -18
        WHEN pr.equipment_type = 'Chiller - Eggs' THEN 18
        WHEN pr.equipment_type = 'Chiller - Fruit/Vegetable' THEN 10
        ELSE 5
    END AS upper_threshold,
    CASE 
        WHEN pr.equipment_type = 'Freezer' THEN NULL  -- No lower limit for freezer
        WHEN pr.equipment_type = 'Chiller - Eggs' THEN 5
        ELSE 0
    END AS lower_threshold,
    
    -- Calculated fields for grouping/aggregation
    TO_CHAR(s.submit_date_local, 'YYYY-MM') AS reading_month,
    TO_CHAR(s.submit_date_local, 'YYYY-"W"WW') AS reading_week,
    EXTRACT(YEAR FROM s.submit_date_local)::INTEGER AS reading_year,
    
    -- Pre-calculated deviation percentage (use SUM for KPI card)
    ROUND(
        100.0 * SUM(
            CASE 
                WHEN pr.equipment_type = 'Freezer' THEN
                    CASE WHEN pr.temperature_reading > -18 THEN 1 ELSE 0 END
                WHEN pr.equipment_type = 'Chiller - Eggs' THEN
                    CASE WHEN pr.temperature_reading < 5 OR pr.temperature_reading > 18 THEN 1 ELSE 0 END
                WHEN pr.equipment_type = 'Chiller - Fruit/Vegetable' THEN
                    CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 10 THEN 1 ELSE 0 END
                ELSE
                    CASE WHEN pr.temperature_reading < 0 OR pr.temperature_reading > 5 THEN 1 ELSE 0 END
            END
        ) OVER () / COUNT(*) OVER ()
    , 2) AS deviation_percentage
    
FROM submissions s
JOIN parsed_readings pr ON pr.submission_id = s.submission_id
JOIN temp_forms tf ON s.form_id = tf.form_id
LEFT JOIN user_details ud ON s.user_id = ud.uuid
WHERE pr.equipment_number IS NOT NULL
AND pr.temperature_reading IS NOT NULL
ORDER BY s.submit_date_local DESC, pr.equipment_number
```

---

## Yemeksepeti - Forms_Yemeksepeti - Forms.sql

**Tables referenced:** form_responses, form_submissions, forms, fr, fr_location, fs, location_acl, nuggets, organizations, question_definitions, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Yemeksepeti - Forms
-- Dashboard: Yemeksepeti - Forms
-- Category: Delivery Hero
-- Extracted: 2026-01-29 16:53:29
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'yemeksepeti-antenna'
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'yemeksepeti-antenna'),
			   forms as (select * from nuggets where organization = 'yemeksepeti-antenna'
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
   LEFT OUTER JOIN fr_location ON fs.response_id = fr_location.response_id)
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
	 to_char(fr.submit_date + td.diff, 'YYYY-MM-DD') as "Date"
FROM location_acl la
LEFT OUTER JOIN fr ON fr.location = la.job_location
LEFT OUTER JOIN forms ON fr.form_id = forms.id
LEFT OUTER JOIN td ON fr.organization = td.organization
LEFT OUTER JOIN user_details ud ON fr.user_id = ud.uuid
ORDER BY 1,
         6,
         5
```

---
