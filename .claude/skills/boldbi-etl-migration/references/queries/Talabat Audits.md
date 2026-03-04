# Talabat Audits

> Auto-generated on 2026-03-04 08:13

**Total queries:** 13

---

## Store Audits - NC Summary_Store Audits - NC Dashboard.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, cms, final_data, form_submissions, fs, locations, map, role_holders, submit_date, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Store Audits - NC Summary
-- Dashboard: Store Audits - NC Dashboard
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:56:30
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:Talabat Audit Tasks NC.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:Talabat Audit Tasks NC.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'talabat-stores-antenna'
        AND is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:Talabat Audit Tasks NC.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id =@{{:Talabat Audit Tasks NC.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city,
						  ud.department
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id
						  where ud.is_active = 'true'
						  and ud.job_type = 'Store'
						  order by acl.store_id, ud.created_at), cms as (
		select store_id, 
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               criticality AS "Criticality",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL THEN 1
                                   ELSE 0
                               END AS "Checked Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score THEN 1
                                   ELSE 0
                               END AS "Failed Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score
                                        AND criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Failed Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
							THEN 1
                                   ELSE 0
                               END AS "Followup Points Count",
                               CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1
                                   ELSE 0
                               END AS "Closed Count",
							 CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1
                                   ELSE 0
                               END AS "Open Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) and criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Open Count"
FROM checkpoint_master_sheet_table cms
WHERE organization_id = 'talabat-stores-antenna'
  AND store_id NOT ILIKE '%HO'
						  and audit_submitted_at between @{{:Talabat Audit Tasks NC.Date Range.START}}::timestamp and @{{:Talabat Audit Tasks NC.Date Range.END}}::timestamp + interval '1 day'),
						  fs as (select distinct on (response_id) response_id, form_id, extract(epoch from submit_date)*1000::bigint as submit_epoch, user_id as submitter_knid from form_submissions fs
								 join cms on cms."Audit Report KNID" = fs.response_id
								 order by fs.response_id, id desc),
final_data AS (
  SELECT 
    map.country AS "Country",
    map.city AS "City", 
    map.store_id AS "Store",
  map.department AS "Department",
    cms."Audit Type",
    cms."Audit",
    cms."Audited At",
    cms."Auditor",
    cms."Theme",
    cms."Checkpoint KNID",
    cms."Checkpoint",
    cms."Audit Report No",
    cms."Audit Report KNID",
    fs.form_id,
    fs.submit_epoch,
    fs.submitter_knid,
    cms."Actual Score",
    cms."Max Score",
    cms."Checked Count",
    cms."Failed Count",
    cms."Critical Failed Count",
    cms."Followup Points Count",
    cms."Closed Count",
    cms."Open Count",
    cms."Critical Open Count",
    CASE 
      WHEN cms."Failed Count" > 0 THEN 1 
      ELSE 0 
    END AS checkpoint_failed
  FROM map
  LEFT JOIN cms ON map.store_id = cms.store_id
  LEFT JOIN fs ON cms."Audit Report KNID" = fs.response_id
)

SELECT *,
  (
    SELECT COUNT(DISTINCT fd2."Store")
    FROM final_data fd2
    WHERE fd2."Checkpoint KNID" = fd."Checkpoint KNID"
      AND fd2.checkpoint_failed = 1
  ) AS "Stores Failed This Checkpoint"
FROM final_data fd
ORDER BY "Country", "City", "Store", "Audited At", "Audit Report No", "Checkpoint"
```

---

## Talabat Audit Tasks NC_Store Audits - NC Dashboard.sql

**Tables referenced:** MAP, acl, analytics_requests, assignees, checkpoint_master_sheet_table, locations, role_holders, t, tasks, user_details, user_groups

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
-- Data Source: Talabat Audit Tasks NC
-- Dashboard: Store Audits - NC Dashboard
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:56:30
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'talabat-stores-antenna'
        AND is_active = 'true'
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
     MAP AS
  (SELECT DISTINCT ON (acl.store_id) acl.store_id as "Store",
                      ud.division as "Country",
                      ud.sub_division as "City"
   FROM acl
   LEFT OUTER JOIN user_details ud ON ud.job_location = acl.store_id
   WHERE ud.is_active = 'true'
     AND ud.job_type = 'Store'
   ORDER BY acl.store_id,
            ud.created_at), t AS
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
    ELSE DATE_PART('day', CURRENT_TIMESTAMP - to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Dubai')
END AS "Aging",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Dubai' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Dubai' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Dubai' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Dubai'
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
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality",
   map."Country",
   map."City",
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
   JOIN MAP ON cms.store_id = map."Store"
   WHERE t.is_deleted = 'false'
     AND cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'talabat-stores-antenna'
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

## Talabat Issues_Maintenance Issues.sql

**Tables referenced:** alamar_dominos_maintenance_requests_table, issue_list, issues, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Talabat Issues
-- Dashboard: Maintenance Issues
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:55:48
-- ============================================================

WITH user_acl AS (
  SELECT uuid, organization
  FROM user_details
  WHERE organization = @{{:OrganizationParameter}}
    AND is_active = 'true'
    AND (
      (SELECT is_super_admin
       FROM user_details
       WHERE uuid = @{{:UuidParameter}})
      OR uuid IN (
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
    AND phone_number NOT ILIKE '+9111%'
),

issue_list AS (
  SELECT 
    issues.sno AS "Ticket No",
    reporter.division AS "Country",
    --reporter.region AS "Region",
    reporter.sub_division AS "City",
    issues.location AS "Location",
    issues.severity AS "Severity",
    reporter.first_name || ' ' || reporter.last_name AS "Requester",
    reporter.identifier AS "Requested ID",
    reporter.uuid AS "Requester UUID",
    REPLACE(issues.category_name, ' Maintenance', '') AS "Request Type",
    CASE
      WHEN issues.status = 'open' THEN 'Pending'
      ELSE 'Store Acknowledged'
    END AS "Current Status",
    TO_TIMESTAMP(issues.created_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Requested At",
    TO_TIMESTAMP(issues.closed_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Responded At",
    TO_TIMESTAMP(issues.closed_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai' AS "Acknowledged At",
    issues.id AS issue_knid,
    issues.category_id AS issue_category_knid
  FROM issues
  LEFT JOIN user_details reporter ON issues.author = reporter.uuid
  LEFT JOIN user_details resolver ON issues.closed_by = resolver.uuid
  WHERE issues.organization = 'talabat-stores-antenna'
    AND TO_TIMESTAMP(issues.created_at::bigint / 1000) AT TIME ZONE 'Asia/Dubai'
        BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + INTERVAL '1 day'
    AND issues.is_deleted != 'true'
)

-- Uncomment and fix below parts if needed:
--, issues_q AS (...)
--, issues_expanded AS (...)
--, cost_q AS (...)
--, costs AS (...)
--, completed_q AS (...)
--, completed_status AS (...)

SELECT requests.*
FROM user_acl
JOIN (
  -- select *, null as "Location", null as "Severity", NULL AS "issue_knid" from alamar_dominos_maintenance_requests_table requests
  -- union
  SELECT 
    "Ticket No",
    "Country",
    --"Region",
    "City",
    "Requester",
    "Requested ID",
    "Requester UUID",
    "Request Type",
    "Current Status",
    "Requested At",
    "Responded At",
    "Acknowledged At",
    "Location",
    "Severity",
    issue_knid
  FROM issue_list
  WHERE "Country" NOT ILIKE 'KNOW'
) requests ON user_acl.uuid = requests."Requester UUID"
```

---

## Talabat Meat Audit 1_Meat Audits.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_notes_q, add_sku_notes_r, add_sku_param_q, add_sku_param_r, audit_param_r, details, forms, fq, fr, fs, lq, metadata, param_r, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, ratings, talabat.sku_master, visible

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupID` -> `group_id` (alias: `group_id AS "groupID"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat Meat Audit 1
-- Dashboard: Meat Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:51
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-Of1OhCblmoTYvLwm44C')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
      fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
WHERE DATE(TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}})),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  WHERE DATE(TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}})),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add( fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),      add_sku_barcode_q AS   (
   SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_param_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionType IN ('dropdown',
                             'multiple_choice')
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table'),
     add_sku_notes_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Inspector Notes'
     AND questionType = 'long_text_field'
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table' ),
     add_sku_param_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_param_q.param,
          json_value(fr.response['selected'], '$.0') AS response
   FROM add_sku_param_q
   JOIN fr ON add_sku_param_q.formId = fr.formId
   AND add_sku_param_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
     add_sku_notes_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_notes_q.param,
          json_extract_scalar(fr.response) AS response
   FROM add_sku_notes_q
   JOIN fr ON add_sku_notes_q.formId = fr.formId
   AND add_sku_notes_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
			audit_param_r AS (
  SELECT
    fr.formId,
    fr.responseId,
    CAST(NULL AS STRING) AS sku,
    fq.questionTitle AS param,
    COALESCE(
      json_value(fr.response['selected'], '$.0'),
      json_extract_scalar(fr.response)
    ) AS response
  FROM fr
  JOIN fq
    ON fr.questionId = fq.questionId
   AND fr.formId = fq.formId
  WHERE
    fq.questionTitle IN ('Cleanliness', 'Arrangement')
    OR fq.questionTitle LIKE 'Chiller Temperature%'
),
     param_r AS (
  SELECT * FROM add_sku_param_r
  UNION ALL
  SELECT * FROM add_sku_notes_r
  UNION ALL
  SELECT * FROM audit_param_r
),
   details AS (
  SELECT
    md.formId AS `Form KNID`,
    md.responseId AS `Audit Report KNID`,
    md.sno AS `Audit Report No`,
    md.submittedAt AS `Audited At`,
    md.store AS `Store`,

    
    COALESCE(asmd.sku, '__AUDIT_LEVEL__') AS `SKU`,

    param_r.param AS `Parameter`,
    param_r.response AS `Reading`,

    
    CASE
      
      WHEN REPLACE(param_r.param, '\t', ' ') LIKE 'Chiller Temperature%' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%within acceptable%' THEN 0
          WHEN lower(param_r.response) LIKE '%slight%'
            OR lower(param_r.response) LIKE '%monitor closely%' THEN 0.05
          WHEN lower(param_r.response) LIKE '%high%' THEN 0.10
          WHEN lower(param_r.response) LIKE '%below 0%'
            OR lower(param_r.response) LIKE '%frozen%' THEN 0.10
          ELSE 0
        END

      WHEN param_r.param = 'Cleanliness' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%clean%' THEN 0
          WHEN lower(param_r.response) LIKE '%unclean%'
            OR lower(param_r.response) LIKE '%off odor%' THEN 0.04
          ELSE 0
        END

      WHEN param_r.param = 'Arrangement' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%complied%' THEN 0
          WHEN lower(param_r.response) LIKE '%partially%' THEN 0.01
          WHEN lower(param_r.response) LIKE '%not complied%' THEN 0.05
          WHEN lower(param_r.response) LIKE '%cross contamination%' THEN 0.03
          ELSE 0
        END

      WHEN param_r.param = 'Appearance' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%bright%'
            OR lower(param_r.response) LIKE '%moist%' THEN 0
          WHEN lower(param_r.response) LIKE '%dry%'
            OR lower(param_r.response) LIKE '%slimy%' THEN 0.10
          ELSE 0
        END

      WHEN param_r.param = 'Color' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%red%'
            OR lower(param_r.response) LIKE '%pink%' THEN 0
          WHEN lower(param_r.response) LIKE '%brown%'
            OR lower(param_r.response) LIKE '%green%'
            OR lower(param_r.response) LIKE '%grey%' THEN 0.08
          WHEN lower(param_r.response) LIKE '%dark%'
            OR lower(param_r.response) LIKE '%blood%'
            OR lower(param_r.response) LIKE '%bruis%' THEN 0.12
          ELSE 0
        END

      WHEN param_r.param = 'Size/Shape (as per product specification)' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%compliant%' THEN 0
          WHEN lower(param_r.response) LIKE '%non-compliant%' THEN 0.03
          ELSE 0
        END

      WHEN param_r.param = 'Texture / Firmness' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%firm%'
            OR lower(param_r.response) LIKE '%tender%' THEN 0
          WHEN lower(param_r.response) LIKE '%mushy%' THEN 0.03
          ELSE 0
        END

      WHEN param_r.param = 'Drip / Exudate' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%minimal%' THEN 0
          WHEN lower(param_r.response) LIKE '%moderate%' THEN 0.015
          WHEN lower(param_r.response) LIKE '%excessive%' THEN 0.025
          ELSE 0
        END

      WHEN param_r.param = 'Foreign Matter' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%not present%' THEN 0
          WHEN lower(param_r.response) LIKE '%present%' THEN 0.05
          ELSE 0
        END

      WHEN param_r.param = 'Absorbent Pad Status' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%compliant%'
            OR lower(param_r.response) LIKE '%present%' THEN 0
          WHEN lower(param_r.response) LIKE '%non-compliant%'
            OR lower(param_r.response) LIKE '%not present%' THEN 0.05
          ELSE 0
        END

      WHEN param_r.param = 'Expiry / Production Date' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%within shelf%'
            OR lower(param_r.response) LIKE '%clearly mentioned%' THEN 0
          WHEN lower(param_r.response) LIKE '%missing%'
            OR lower(param_r.response) LIKE '%expired%'
            OR lower(param_r.response) LIKE '%incorrect%' THEN 0.05
          ELSE 0
        END

      WHEN param_r.param = 'Is the packaging intact and free from visible damage?' THEN
        CASE
          WHEN lower(coalesce(param_r.response,'')) LIKE '%yes%'
            OR lower(param_r.response) LIKE '%intact%' THEN 0
          WHEN lower(param_r.response) LIKE '%direct contact%' THEN 0.04
          WHEN lower(param_r.response) LIKE '%torn%'
            OR lower(param_r.response) LIKE '%punctured%'
            OR lower(param_r.response) LIKE '%broken%' THEN 0.06
          WHEN lower(param_r.response) LIKE '%moisture%'
            OR lower(param_r.response) LIKE '%leakage%'
            OR lower(param_r.response) LIKE '%bloating%' THEN 0.10
          ELSE 0
        END

      WHEN param_r.param = 'Inspector Notes' THEN NULL
      ELSE 0
    END AS `Given Score`,

    
    CASE
      WHEN param_r.param IN (
        'Color',
        'Size/Shape (as per product specification)',
        'Appearance',
        'Texture / Firmness'
      ) THEN 'Stable'
      WHEN param_r.param IN (
        'Drip / Exudate',
        'Foreign Matter',
        'Absorbent Pad Status',
        'Cleanliness',
        'Arrangement'
      ) THEN 'Unstable'
      WHEN param_r.param = 'Inspector Notes' THEN 'Overall'
      ELSE NULL
    END AS `Category`,

    
    CASE
      WHEN REPLACE(param_r.param, '\t', ' ') LIKE 'Chiller Temperature%' THEN 0.10
      WHEN param_r.param = 'Cleanliness' THEN 0.04
      WHEN param_r.param = 'Arrangement' THEN 0.03
      WHEN param_r.param = 'Appearance' THEN 0.10
      WHEN param_r.param = 'Color' THEN 0.12
      WHEN param_r.param = 'Size/Shape (as per product specification)' THEN 0.03
      WHEN param_r.param = 'Texture / Firmness' THEN 0.03
      WHEN param_r.param = 'Drip / Exudate' THEN 0.025
      WHEN param_r.param = 'Foreign Matter' THEN 0.05
      WHEN param_r.param = 'Absorbent Pad Status' THEN 0.05
      WHEN param_r.param = 'Expiry / Production Date' THEN 0.05
      WHEN param_r.param = 'Is the packaging intact and free from visible damage?' THEN 0.10
      ELSE 0
    END AS `Max Score`,

    
    CASE
      WHEN REPLACE(param_r.param, '\t', ' ') LIKE 'Chiller Temperature%' THEN 0.15
      WHEN param_r.param = 'Cleanliness' THEN 0.04
      WHEN param_r.param = 'Arrangement' THEN 0.06
      WHEN param_r.param = 'Appearance' THEN 0.10
      WHEN param_r.param = 'Color' THEN 0.20
      WHEN param_r.param = 'Size/Shape (as per product specification)' THEN 0.03
      WHEN param_r.param = 'Texture / Firmness' THEN 0.03
      WHEN param_r.param = 'Drip / Exudate' THEN 0.04
      WHEN param_r.param = 'Foreign Matter' THEN 0.05
      WHEN param_r.param = 'Absorbent Pad Status' THEN 0.05
      WHEN param_r.param = 'Expiry / Production Date' THEN 0.05
      WHEN param_r.param = 'Is the packaging intact and free from visible damage?' THEN 0.20
      ELSE 0
    END AS `Weightage`,

    md.submitted_epoch,
    md.initiator_uuid

  FROM metadata md
  LEFT JOIN add_sku asmd
    ON md.responseId = asmd.responseId
  LEFT JOIN param_r
    ON md.responseId = param_r.responseId
   AND (
        param_r.sku = asmd.sku
        OR param_r.sku IS NULL
       )

  GROUP BY
    1,2,3,4,5,6,7,8,9,10,11,12,13,14
),
     ratings AS
  (SELECT `Form KNID`,
          `Audit Report KNID`,
          `SKU`,
          SUM(COALESCE(`Given Score`, 0) * COALESCE(`Weightage`, 0) * 100) AS sku_score,
          max(CASE
                  WHEN `Parameter` = 'Inspector Notes' THEN `Reading`
                  ELSE NULL
              END) AS `Inspector Notes`
   FROM details
   GROUP BY 1,
            2,
            3)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       left(d.`Store`, 3) AS `Region`,
       d.`SKU` as `Barcode`,
	   t.product_desc as `SKU`,
	   t.supplier as `Supplier`,
       d.`Audit Report KNID`||' - '||d.`SKU` AS `Audit Combo`,
       r.sku_score `SKU Score`,
       CASE
           WHEN r.sku_score <=@{{:Acceptability Threshold}} THEN 'Acceptable'
           ELSE 'Not Acceptable'
       END AS `Acceptability`,
       r.`Inspector Notes`,
       d.`Category`,
       d.`Parameter`,
	   d.`Reading`,
       d.`Weightage`,
       `Given Score` AS `Actual Score`,
       `Max Score` AS `Max Score`,
       d.submitted_epoch,
       d.initiator_uuid
FROM details d
LEFT OUTER JOIN ratings r ON d.`Audit Report KNID` = r.`Audit Report KNID`
AND d.`SKU` = r.`SKU`
LEFT OUTER JOIN talabat.sku_master t on LTRIM(d.`SKU`, '0') = cast(t.barcode as string)
WHERE (d.`Parameter` NOT IN ('Inspector Notes')
       OR d.`Parameter` IS NULL)
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
         18, 19, 20, 21
ORDER BY 4 DESC,
         6,
         5,
         7
```

---

## Talabat Meat Audit Ops 1_Meat Audits.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_chiller_q, add_sku_chiller_r, add_sku_ops_issue_q, add_sku_ops_issue_r, add_sku_packaging_q, add_sku_packaging_r, details, forms, fq, fr, fs, lq, metadata, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, talabat.sku_master, visible

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat Meat Audit Ops 1
-- Dashboard: Meat Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:49
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-Of1OhCblmoTYvLwm44C')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
WHERE DATE(TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Talabat Meat Audit 1.Date Range.START}})
          AND DATE(@{{:Talabat Meat Audit 1.Date Range.END}})),
    fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  WHERE DATE(TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Talabat Meat Audit 1.Date Range.START}})
          AND DATE(@{{:Talabat Meat Audit 1.Date Range.END}})) ,
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add(fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),
     add_sku_barcode_q AS
  (SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_ops_issue_q AS
  ( SELECT fq.formId,
           fq.questionTitle AS param,
           fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Issue Category' ),
     add_sku_ops_issue_r AS
  ( SELECT fr.formId,
           fr.responseId,
           add_sku.sku,
           json_extract_scalar(response) as response
   FROM add_sku_ops_issue_q
   JOIN fr ON add_sku_ops_issue_q.formId = fr.formId
   AND add_sku_ops_issue_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.rowId = fr.rowIdX,
       UNNEST(JSON_EXTRACT_ARRAY(fr.response, '$.selected')) AS response
   GROUP BY 1,
            2,
            3,
            4),
			add_sku_chiller_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle like '%Chiller Temperature%'
),
add_sku_chiller_r AS (
 SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS chiller_response
  FROM add_sku_chiller_q
  JOIN fr ON add_sku_chiller_q.formId = fr.formId
          AND add_sku_chiller_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
add_sku_packaging_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle = 'Is the packaging intact and free from visible damage?'
),
add_sku_packaging_r AS (
   SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS packaging_response
  FROM add_sku_packaging_q
  JOIN fr ON add_sku_packaging_q.formId = fr.formId
          AND add_sku_packaging_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
     details AS (
  SELECT md.formId AS `Form KNID`,
         md.responseId AS `Audit Report KNID`,
         md.sno AS `Audit Report No`,
         md.submittedAt AS `Audited At`,
         md.store AS `Store`,
         asmd.sku AS `SKU`,
         asoir.response AS `Ops Issues`,
         asrip.chiller_response AS `Chiller Check`,
         aspack.packaging_response AS `Packaging Check`
  FROM metadata md
  LEFT OUTER JOIN add_sku asmd ON md.responseId = asmd.responseId
  LEFT JOIN add_sku_ops_issue_r asoir ON md.responseId = asoir.responseId
                                     AND asoir.sku = asmd.sku
  LEFT JOIN add_sku_chiller_r asrip ON md.responseId = asrip.responseId
                                     AND asrip.sku = asmd.sku
  LEFT JOIN add_sku_packaging_r aspack ON md.responseId = aspack.responseId
                                       AND aspack.sku = asmd.sku
)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       LEFT(d.`Store`, 3) AS `Region`,
       d.`SKU` AS `Barcode`,
       t.product_desc AS `SKU`,
       t.supplier AS `Supplier`,
       d.`Audit Report KNID` || ' - ' || d.`SKU` AS `Audit Combo`,
       d.`Ops Issues`,
       d.`Chiller Check`,
       d.`Packaging Check`
FROM details d
LEFT OUTER JOIN talabat.sku_master t
    ON LTRIM(d.`SKU`, '0') = CAST(t.barcode AS STRING)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ORDER BY 4 DESC, 6, 5, 7
```

---

## Talabat SKU Audit Store Ops_Store wise F and V Quality.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_ops_issue_q, add_sku_ops_issue_r, add_sku_packaging_q, add_sku_packaging_r, add_sku_ripeness_q, add_sku_ripeness_r, details, forms, fq, fr, fs, lq, metadata, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, talabat.sku_master, visible

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat SKU Audit Store Ops
-- Dashboard: Store wise F and V Quality
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:56
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-O6eonkCensW239HGPsI',
                '-O8GY_odFHRGxDfQdwdS',
			   '-OTavFZ5aMD5uQ_w_arU',
			   '-OY7myPjXJi1C2KlLlo5')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
     fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
   WHERE timestamp_add(fs.submittedAt, interval 4 hour) BETWEEN cast(@{{:Talabat Sku Audit Store.Date Range.START}} as timestamp) and cast(@{{:Talabat Sku Audit Store.Date Range.END}} as timestamp)),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  WHERE timestamp_add(fr.submittedAt, interval 4 hour) BETWEEN cast(@{{:Talabat Sku Audit Store.Date Range.START}} as timestamp) and cast(@{{:Talabat Sku Audit Store.Date Range.END}} as timestamp)),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add(fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),
     add_sku_barcode_q AS
  (SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_ops_issue_q AS
  ( SELECT fq.formId,
           fq.questionTitle AS param,
           fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Issue Category'
     AND fq.groupTitle = 'Is there an issue related to the operations/ stores?' ),
     add_sku_ops_issue_r AS
  ( SELECT fr.formId,
           fr.responseId,
           add_sku.sku,
           json_extract_scalar(response) as response
   FROM add_sku_ops_issue_q
   JOIN fr ON add_sku_ops_issue_q.formId = fr.formId
   AND add_sku_ops_issue_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.rowId = fr.rowIdX,
       UNNEST(JSON_EXTRACT_ARRAY(fr.response, '$.selected')) AS response
   GROUP BY 1,
            2,
            3,
            4),
			add_sku_ripeness_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle = 'Is the ripeness of the fruits/vegetables appropriate for their intended use?'
),
add_sku_ripeness_r AS (
 SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS ripeness_response
  FROM add_sku_ripeness_q
  JOIN fr ON add_sku_ripeness_q.formId = fr.formId
          AND add_sku_ripeness_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
add_sku_packaging_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle = 'Is the packaging intact and free from visible damage?'
),
add_sku_packaging_r AS (
   SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS packaging_response
  FROM add_sku_packaging_q
  JOIN fr ON add_sku_packaging_q.formId = fr.formId
          AND add_sku_packaging_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
     details AS (
  SELECT md.formId AS `Form KNID`,
         md.responseId AS `Audit Report KNID`,
         md.sno AS `Audit Report No`,
         md.submittedAt AS `Audited At`,
         md.store AS `Store`,
         asmd.sku AS `SKU`,
         asoir.response AS `Ops Issues`,
         asrip.ripeness_response AS `Ripeness Check`,
         aspack.packaging_response AS `Packaging Check`
  FROM metadata md
  LEFT OUTER JOIN add_sku asmd ON md.responseId = asmd.responseId
  LEFT JOIN add_sku_ops_issue_r asoir ON md.responseId = asoir.responseId
                                     AND asoir.sku = asmd.sku
  LEFT JOIN add_sku_ripeness_r asrip ON md.responseId = asrip.responseId
                                     AND asrip.sku = asmd.sku
  LEFT JOIN add_sku_packaging_r aspack ON md.responseId = aspack.responseId
                                       AND aspack.sku = asmd.sku
)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       LEFT(d.`Store`, 3) AS `Region`,
       d.`SKU` AS `Barcode`,
       t.product_desc AS `SKU`,
       t.supplier AS `Supplier`,
       d.`Audit Report KNID` || ' - ' || d.`SKU` AS `Audit Combo`,
       d.`Ops Issues`,
       d.`Ripeness Check`,
       d.`Packaging Check`
FROM details d
LEFT OUTER JOIN talabat.sku_master t
    ON LTRIM(d.`SKU`, '0') = CAST(t.barcode AS STRING)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ORDER BY 4 DESC, 6, 5, 7
```

---

## Talabat SKU Audits Dashboard_SKU Audits.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_notes_q, add_sku_notes_r, add_sku_param_q, add_sku_param_r, details, forms, fq, fr, fs, lq, metadata, param_r, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, ratings, talabat.sku_master

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupID` -> `group_id` (alias: `group_id AS "groupID"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat SKU Audits Dashboard
-- Dashboard: SKU Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:51
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-O6eonkCensW239HGPsI', '-O8GY_odFHRGxDfQdwdS','-OTavFZ5aMD5uQ_w_arU','-OY7myPjXJi1C2KlLlo5')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
     fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
WHERE DATE(TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}})),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  WHERE DATE(TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}})),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add( fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),      add_sku_barcode_q AS   (
   SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_param_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionType IN ('dropdown',
                             'multiple_choice')
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table'),
     add_sku_notes_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Inspector Notes'
     AND questionType = 'long_text_field'
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table' ),
     add_sku_param_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_param_q.param,
          json_value(fr.response['selected'], '$.0') AS response
   FROM add_sku_param_q
   JOIN fr ON add_sku_param_q.formId = fr.formId
   AND add_sku_param_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
     add_sku_notes_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_notes_q.param,
          json_extract_scalar(fr.response) AS response
   FROM add_sku_notes_q
   JOIN fr ON add_sku_notes_q.formId = fr.formId
   AND add_sku_notes_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
     param_r AS
  (SELECT *
   FROM add_sku_param_r
   UNION ALL SELECT *
   FROM add_sku_notes_r),
     details AS
  (SELECT md.formId `Form KNID`,
          md.responseId AS `Audit Report KNID`,
          md.sno AS `Audit Report No`,
          md.submittedAt AS `Audited At`,
          md.store AS `Store`,
          asmd.sku AS `SKU`,
          param_r.param AS `Parameter`,
          param_r.response AS `Reading`,
          CASE
   WHEN param_r.param NOT IN ('Inspector Notes') AND (param_r.response IS NULL OR TRIM(param_r.response) = '') THEN 0
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('No discoloration',
                                            'No visible Deviation',
                                            'No visible Deformity',
                                            'No visible Blemishes',
                                            'No Bruising',
                                            'No pest Damage',
                                            'Not Found') THEN 0
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Slight Discoloration',
                                            'Minor (1% to 5%) deviation',
                                            'Minor Deformity',
                                            'Small Blemishes or scars',
										    'Small',
                                            'Small area of Damage',
                                            'Small Area') THEN 1
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Not extensive discoloration',
                                            'Moderate (6% to 10%) deviation',
                                            'Significant Deformity',
                                            'Larger Blemishes or scars',
											'Large or Extensive',
                                            'More significant damage',
                                            'Larger Area'
                                           ) THEN 2
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Extensive discoloration',
                                            'Severe (more than 10%) Deviation',
                                            'Extreme Deformity',
                                            'Extensive Blemishes or scars',
										   'Extensive',
                                            'Extensive Damage',
                                            'Extensive Area') THEN 3
              ELSE NULL
          END AS `Given Score`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect') THEN 'Stable'
              WHEN param_r.param IN ('Bruising Crushing',
                                     'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 'Unstable'
              WHEN param_r.param IN ('Inspector Notes') THEN 'Overall'
              ELSE NULL
          END AS `Category`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect',
									 'Bruising Crushing',
                                     'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 3
              ELSE NULL
          END AS `Max Score`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect') THEN 0.1
              WHEN param_r.param IN ('Bruising Crushing',
									 'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 0.2
              ELSE NULL
          END AS `Weightage`,
          md.submitted_epoch,
          md.initiator_uuid
   FROM metadata md
   LEFT OUTER JOIN add_sku asmd ON md.responseId = asmd.responseId
   LEFT OUTER JOIN param_r ON md.responseId = param_r.responseId
   AND param_r.sku = asmd.sku
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
            14),
     ratings AS
  (SELECT `Form KNID`,
          `Audit Report KNID`,
          `SKU`,
          SUM(COALESCE(`Given Score`, 0) * COALESCE(`Weightage`, 0) * 100) AS sku_score,
          max(CASE
                  WHEN `Parameter` = 'Inspector Notes' THEN `Reading`
                  ELSE NULL
              END) AS `Inspector Notes`
   FROM details
   GROUP BY 1,
            2,
            3)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       left(d.`Store`, 3) AS `Region`,
       d.`SKU` as `Barcode`,
	   t.product_desc as `SKU`,
	   t.supplier as `Supplier`,
       d.`Audit Report KNID`||' - '||d.`SKU` AS `Audit Combo`,
       r.sku_score `SKU Score`,
       CASE
           WHEN r.sku_score <=@{{:Acceptability Threshold}} THEN 'Acceptable'
           ELSE 'Not Acceptable'
       END AS `Acceptability`,
       r.`Inspector Notes`,
       d.`Category`,
       d.`Parameter`,
	   d.`Reading`,
       d.`Weightage`,
       `Given Score` AS `Actual Score`,
       `Max Score` AS `Max Score`,
       d.submitted_epoch,
       d.initiator_uuid
FROM details d
LEFT OUTER JOIN ratings r ON d.`Audit Report KNID` = r.`Audit Report KNID`
AND d.`SKU` = r.`SKU`
LEFT OUTER JOIN talabat.sku_master t on LTRIM(d.`SKU`, '0') = cast(t.barcode as string)
WHERE (d.`Parameter` NOT IN ('Inspector Notes')
       OR d.`Parameter` IS NULL)
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
         18, 19, 20, 21
ORDER BY 4 DESC,
         6,
         5,
         7
```

---

## Talabat SKU Audits Ops Issues for Dashboard_SKU Audits.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_ops_issue_q, add_sku_ops_issue_r, add_sku_packaging_q, add_sku_packaging_r, add_sku_ripeness_q, add_sku_ripeness_r, details, forms, fq, fr, fs, lq, metadata, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, talabat.sku_master, visible

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat SKU Audits Ops Issues for Dashboard
-- Dashboard: SKU Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:50
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-O6eonkCensW239HGPsI',
                '-O8GY_odFHRGxDfQdwdS',
			   '-OTavFZ5aMD5uQ_w_arU',
			   '-OY7myPjXJi1C2KlLlo5')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
     fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
   WHERE timestamp_add(fs.submittedAt, interval 4 hour) BETWEEN cast(@{{:Talabat SKU Audits Dashboard.Date Range.START}} as timestamp) and cast(@{{:Talabat SKU Audits Dashboard.Date Range.END}} as timestamp)),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  WHERE timestamp_add(fr.submittedAt, interval 4 hour) BETWEEN cast(@{{:Talabat SKU Audits Dashboard.Date Range.START}} as timestamp) and cast(@{{:Talabat SKU Audits Dashboard.Date Range.END}} as timestamp)),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add(fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),
     add_sku_barcode_q AS
  (SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_ops_issue_q AS
  ( SELECT fq.formId,
           fq.questionTitle AS param,
           fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Issue Category'
     AND fq.groupTitle = 'Is there an issue related to the operations/ stores?' ),
     add_sku_ops_issue_r AS
  ( SELECT fr.formId,
           fr.responseId,
           add_sku.sku,
           json_extract_scalar(response) as response
   FROM add_sku_ops_issue_q
   JOIN fr ON add_sku_ops_issue_q.formId = fr.formId
   AND add_sku_ops_issue_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.rowId = fr.rowIdX,
       UNNEST(JSON_EXTRACT_ARRAY(fr.response, '$.selected')) AS response
   GROUP BY 1,
            2,
            3,
            4),
			add_sku_ripeness_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle = 'Is the ripeness of the fruits/vegetables appropriate for their intended use?'
),
add_sku_ripeness_r AS (
 SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS ripeness_response
  FROM add_sku_ripeness_q
  JOIN fr ON add_sku_ripeness_q.formId = fr.formId
          AND add_sku_ripeness_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
add_sku_packaging_q AS (
  SELECT fq.formId,
         fq.questionTitle AS param,
         fq.questionId AS qid
  FROM fq
  WHERE fq.questionTitle = 'Is the packaging intact and free from visible damage?'
),
add_sku_packaging_r AS (
   SELECT fr.formId,
         fr.responseId,
         add_sku.sku,
         json_extract_scalar(fr.response, '$.selected[0]') AS packaging_response
  FROM add_sku_packaging_q
  JOIN fr ON add_sku_packaging_q.formId = fr.formId
          AND add_sku_packaging_q.qid = fr.questionId
  JOIN add_sku ON add_sku.formId = fr.formId
               AND add_sku.responseId = fr.responseId
               AND add_sku.rowId = fr.rowIdX
),
     details AS (
  SELECT md.formId AS `Form KNID`,
         md.responseId AS `Audit Report KNID`,
         md.sno AS `Audit Report No`,
         md.submittedAt AS `Audited At`,
         md.store AS `Store`,
         asmd.sku AS `SKU`,
         asoir.response AS `Ops Issues`,
         asrip.ripeness_response AS `Ripeness Check`,
         aspack.packaging_response AS `Packaging Check`
  FROM metadata md
  LEFT OUTER JOIN add_sku asmd ON md.responseId = asmd.responseId
  LEFT JOIN add_sku_ops_issue_r asoir ON md.responseId = asoir.responseId
                                     AND asoir.sku = asmd.sku
  LEFT JOIN add_sku_ripeness_r asrip ON md.responseId = asrip.responseId
                                     AND asrip.sku = asmd.sku
  LEFT JOIN add_sku_packaging_r aspack ON md.responseId = aspack.responseId
                                       AND aspack.sku = asmd.sku
)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       LEFT(d.`Store`, 3) AS `Region`,
       d.`SKU` AS `Barcode`,
       t.product_desc AS `SKU`,
       t.supplier AS `Supplier`,
       d.`Audit Report KNID` || ' - ' || d.`SKU` AS `Audit Combo`,
       d.`Ops Issues`,
       d.`Ripeness Check`,
       d.`Packaging Check`
FROM details d
LEFT OUTER JOIN talabat.sku_master t
    ON LTRIM(d.`SKU`, '0') = CAST(t.barcode AS STRING)
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ORDER BY 4 DESC, 6, 5, 7
```

---

## Talabat Sku Audit Store_Store wise F and V Quality.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_notes_q, add_sku_notes_r, add_sku_param_q, add_sku_param_r, details, forms, fq, fr, fs, lq, metadata, param_r, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, ratings, talabat.sku_master

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupID` -> `group_id` (alias: `group_id AS "groupID"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat Sku Audit Store
-- Dashboard: Store wise F and V Quality
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:52:56
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-O6eonkCensW239HGPsI', '-O8GY_odFHRGxDfQdwdS','-OTavFZ5aMD5uQ_w_arU','-OY7myPjXJi1C2KlLlo5')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
     fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
WHERE DATE(TIMESTAMP_ADD(fs.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}})),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId
  where DATE(TIMESTAMP_ADD(fr.submittedAt, INTERVAL 4 HOUR)) 
      BETWEEN DATE(@{{:Date Range.START}})
          AND DATE(@{{:Date Range.END}}) ),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add( fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),      add_sku_barcode_q AS   (
   SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'SKU Details'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     add_sku_param_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionType IN ('dropdown',
                             'multiple_choice')
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table'),
     add_sku_notes_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Inspector Notes'
     AND questionType = 'long_text_field'
     AND fq.groupTitle = 'SKU Details'
     AND fq.groupType = 'table' ),
     add_sku_param_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_param_q.param,
          json_value(fr.response['selected'], '$.0') AS response
   FROM add_sku_param_q
   JOIN fr ON add_sku_param_q.formId = fr.formId
   AND add_sku_param_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
     add_sku_notes_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_notes_q.param,
          json_extract_scalar(fr.response) AS response
   FROM add_sku_notes_q
   JOIN fr ON add_sku_notes_q.formId = fr.formId
   AND add_sku_notes_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5),
     param_r AS
  (SELECT *
   FROM add_sku_param_r
   UNION ALL SELECT *
   FROM add_sku_notes_r),
     details AS
  (SELECT md.formId `Form KNID`,
          md.responseId AS `Audit Report KNID`,
          md.sno AS `Audit Report No`,
          md.submittedAt AS `Audited At`,
          md.store AS `Store`,
          asmd.sku AS `SKU`,
          param_r.param AS `Parameter`,
          param_r.response AS `Reading`,
          CASE
   WHEN param_r.param NOT IN ('Inspector Notes') AND (param_r.response IS NULL OR TRIM(param_r.response) = '') THEN 0
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('No discoloration',
                                            'No visible Deviation',
                                            'No visible Deformity',
                                            'No visible Blemishes',
                                            'No Bruising',
                                            'No pest Damage',
                                            'Not Found') THEN 0
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Slight Discoloration',
                                            'Minor (1% to 5%) deviation',
                                            'Minor Deformity',
                                            'Small Blemishes or scars',
										    'Small',
                                            'Small area of Damage',
                                            'Small Area') THEN 1
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Not extensive discoloration',
                                            'Moderate (6% to 10%) deviation',
                                            'Significant Deformity',
                                            'Larger Blemishes or scars',
											'Large or Extensive',
                                            'More significant damage',
                                            'Larger Area'
                                           ) THEN 2
              WHEN param_r.param NOT IN ('Inspector Notes')
                   AND param_r.response IN ('Extensive discoloration',
                                            'Severe (more than 10%) Deviation',
                                            'Extreme Deformity',
                                            'Extensive Blemishes or scars',
										   'Extensive',
                                            'Extensive Damage',
                                            'Extensive Area') THEN 3
              ELSE NULL
          END AS `Given Score`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect') THEN 'Stable'
              WHEN param_r.param IN ('Bruising Crushing',
                                     'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 'Unstable'
              WHEN param_r.param IN ('Inspector Notes') THEN 'Overall'
              ELSE NULL
          END AS `Category`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect',
									 'Bruising Crushing',
                                     'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 3
              ELSE NULL
          END AS `Max Score`,
          CASE
              WHEN param_r.param IN ('Colour',
                                     'Size',
                                     'Uniformity of Shape',
                                     'Skin Defect') THEN 0.1
              WHEN param_r.param IN ('Bruising Crushing',
									 'Pest Damage',
                                     'Mold or Decay or Sprouting') THEN 0.2
              ELSE NULL
          END AS `Weightage`,
          md.submitted_epoch,
          md.initiator_uuid
   FROM metadata md
   LEFT OUTER JOIN add_sku asmd ON md.responseId = asmd.responseId
   LEFT OUTER JOIN param_r ON md.responseId = param_r.responseId
   AND param_r.sku = asmd.sku
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
            14),
     ratings AS
  (SELECT `Form KNID`,
          `Audit Report KNID`,
          `SKU`,
           SUM(COALESCE(`Given Score`, 0) * COALESCE(`Weightage`, 0) * 100) AS sku_score,
          max(CASE
                  WHEN `Parameter` = 'Inspector Notes' THEN `Reading`
                  ELSE NULL
              END) AS `Inspector Notes`
   FROM details
   GROUP BY 1,
            2,
            3)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       left(d.`Store`, 3) AS `Region`,
       d.`SKU` as `Barcode`,
	   t.product_desc as `SKU`,
	   t.supplier as `Supplier`,
       d.`Audit Report KNID`||' - '||d.`SKU` AS `Audit Combo`,
       r.sku_score `SKU Score`,
       CASE
           WHEN r.sku_score <=@{{:Acceptability Threshold}} THEN 'Acceptable'
           ELSE 'Not Acceptable'
       END AS `Acceptability`,
       r.`Inspector Notes`,
       d.`Category`,
       d.`Parameter`,
	   d.`Reading`,
       d.`Weightage`,
       `Given Score` AS `Actual Score`,
       `Max Score` AS `Max Score`,
       d.submitted_epoch,
       d.initiator_uuid
FROM details d
LEFT OUTER JOIN ratings r ON d.`Audit Report KNID` = r.`Audit Report KNID`
AND d.`SKU` = r.`SKU`
LEFT OUTER JOIN talabat.sku_master t on LTRIM(d.`SKU`, '0') = cast(t.barcode as string)
WHERE (d.`Parameter` NOT IN ('Inspector Notes')
       OR d.`Parameter` IS NULL)
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
         18, 19, 20, 21
ORDER BY 4 DESC,
         6,
         5,
         7
```

---

## Talabat Stores Audit Tasks_Store Audits.sql

**Tables referenced:** MAP, acl, analytics_requests, assignees, checkpoint_master_sheet_table, locations, role_holders, t, tasks, user_details, user_groups

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
-- Data Source: Talabat Stores Audit Tasks
-- Dashboard: Store Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:54:25
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'talabat-stores-antenna'
        AND is_active = 'true'
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
     MAP AS
  (SELECT DISTINCT ON (acl.store_id) acl.store_id as "Store",
                      ud.division as "Country",
                      ud.sub_division as "City"
   FROM acl
   LEFT OUTER JOIN user_details ud ON ud.job_location = acl.store_id
   WHERE ud.is_active = 'true'
     AND ud.job_type = 'Store'
   ORDER BY acl.store_id,
            ud.created_at), t AS
  (SELECT distinct on(t.id)t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Dubai' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Dubai' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Dubai' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Dubai'
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
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality",
   map."Country",
   map."City"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   JOIN MAP ON cms.store_id = map."Store"
   WHERE t.is_deleted = 'false'
     AND cms.audit_submitted_at BETWEEN @{{:Talabat Stores Audits.Date Range.START}}::timestamp AND @{{:Talabat Stores Audits.Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'talabat-stores-antenna'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39),
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
       assignees.department AS "Assignee Department"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
```

---

## Talabat Stores Audits Summary_Store Audits.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, cms, form_submissions, fs, locations, map, role_holders, submit_date, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Talabat Stores Audits Summary
-- Dashboard: Store Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:53:14
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:Talabat Stores Audits.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:Talabat Stores Audits.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'talabat-stores-antenna'
        AND is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:Talabat Stores Audits.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:Talabat Stores Audits.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id
						  where ud.is_active = 'true'
						  and ud.job_type = 'Store'
						  order by acl.store_id, ud.created_at), cms as (
		select store_id, 
	   audit_type as "Audit Type",
       audit_main_theme AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               criticality AS "Criticality",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL THEN 1
                                   ELSE 0
                               END AS "Checked Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score THEN 1
                                   ELSE 0
                               END AS "Failed Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score
                                        AND criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Failed Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
							THEN 1
                                   ELSE 0
                               END AS "Followup Points Count",
                               CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1
                                   ELSE 0
                               END AS "Closed Count",
							 CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1
                                   ELSE 0
                               END AS "Open Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) and criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Open Count"
FROM checkpoint_master_sheet_table cms
WHERE organization_id = 'talabat-stores-antenna'
  AND store_id NOT ILIKE '%HO'
						  and audit_submitted_at between @{{:Talabat Stores Audits.Date Range.START}}::timestamp and @{{:Talabat Stores Audits.Date Range.END}}::timestamp + interval '1 day'),
						  fs as (select distinct on (response_id) response_id, form_id, extract(epoch from submit_date)*1000::bigint as submit_epoch, user_id as submitter_knid from form_submissions fs
								 join cms on cms."Audit Report KNID" = fs.response_id
								 order by fs.response_id, id desc)
  select map.country AS "Country",
		map.city as "City", 
       map.store_id AS "Store",
	   cms."Audit Type",
	   cms."Audit",
	   cms."Audited At",
	   cms."Auditor",
	   cms."Audit Report No",
	   cms."Audit Report KNID",
	   fs.form_id,
	   fs.submit_epoch,
	   fs.submitter_knid,
	   sum(cms."Actual Score")/sum(cms."Max Score") as "Audit Score",
	   sum(cms."Checked Count") as "Checked Count",
	   sum(cms."Failed Count") as "Failed Count",
	   sum(cms."Critical Failed Count") as "Critical Failed Count",
	   sum(cms."Followup Points Count") as "Followup Points Count",
	   sum(cms."Closed Count") as "Closed Count",
	   sum(cms."Open Count") as "Open Count",
	   sum(cms."Critical Open Count") as "Critical Open Count"
	   from map
	   left outer join cms on map.store_id = cms.store_id
	   left outer join fs on cms."Audit Report KNID" = fs.response_id
	   group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
	   order by 1, 2, 3, 4, 5, 6
```

---

## Talabat Stores Audits_Store Audits.sql

**Tables referenced:** acl, checkpoint_master_sheet_table, locations, map, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Talabat Stores Audits
-- Dashboard: Store Audits
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:57:07
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'talabat-stores-antenna'
        AND is_active = 'true'    
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
				  map as (select distinct on (acl.store_id) acl.store_id,
						  ud.division as country,
						  ud.sub_division as city
						  from acl
						  left outer join user_details ud on ud.job_location = acl.store_id
						  where ud.is_active = 'true'
						  and ud.job_type = 'Store'
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
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               criticality AS "Criticality",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL THEN 1.0
                                   ELSE 0.0
                               END AS "Checked Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score THEN 1.0
                                   ELSE 0.0
                               END AS "Failed Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score
                                        AND criticality = 'Critical' THEN 1.0
                                   ELSE 0.0
                               END AS "Critical Failed Count",
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
WHERE organization_id = 'talabat-stores-antenna'
  AND map.store_id NOT ILIKE '%HO'
  and audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  order by 1, 2, 3, 4, 5, 6, 10, 12
```

---

## Talabat Stores LMS_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: Talabat Stores LMS
-- Dashboard: Learn
-- Category: Talabat Audits
-- Extracted: 2026-01-29 16:55:16
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
          ud.job_type,
   ud.phone_number
   FROM user_details ud
   WHERE organization = 'talabat-stores-antenna'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
   and designation = 'Picker'
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
   WHERE id = 'talabat-stores-antenna'),
     latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      created_at AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   JOIN user_acl ud ON nusr.user_id = ud.uuid
   ORDER BY 1,
            3,
            created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at,
          1 AS seq
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nugget_id = c.id
   WHERE c.organization = 'talabat-stores-antenna'
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at,
                    (seq::int)+1 AS seq
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id),
     latest_received AS
  (SELECT ra.user_id,
          ra.nugget_id,
          ra.share_id,
          ra.created_at AS received_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_share_ids lsi ON ra.user_id = lsi.user_id
   AND ra.nugget_id = lsi.nugget_id
   AND ra.share_id = lsi.share_id
   WHERE ra.event_id NOT IN (1,
                             7)),
     latest_course_received AS
  (SELECT lr.user_id,
          lr.nugget_id AS course_id,
          lr.share_id,
          min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.courses c ON lr.nugget_id = c.id
   WHERE c.organization = 'talabat-stores-antenna'
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.user_id,
                    ljc.course_id,
                    lr.share_id,
                    min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id
   WHERE c.organization = 'talabat-stores-antenna'
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = 'talabat-stores-antenna'
   GROUP BY 1,
            2),
     cards_consumed AS
  (SELECT ra.user_id,
          lcs.seq,
          ra.course_id,
          ra.share_id,
          lc.card_id,
          ra.lang,
          min(ra.created_at) AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.course_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   JOIN cards lc ON lc.course_id = ra.course_id
   AND lc.card_id = ra.nugget_id
   WHERE ra.event_id = 3
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   ORDER BY 1,
            2,
            3,
            4,
            5),
     progress AS
  (SELECT cc.user_id,
          cc.course_id,
          cc.share_id,
          count(distinct(cc.card_id)) AS consumed_count
   FROM cards_consumed cc
   GROUP BY 1,
            2,
            3),
     final_quiz_cards AS
  (SELECT DISTINCT ON (c.id) c.id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount,
                      (lc.settings->>'passMark')::numeric AS pass_mark
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = 'talabat-stores-antenna'
     AND lc.type = 'quiz'
   ORDER BY c.id,
            l.seq DESC, lc.seq DESC),
     latest_attempt AS
  (SELECT qr.user_id,
          qr.course_id,
          qr.share_id,
          qr.card_id,
          qr.question_id,
          max(attempt) AS latestAttempt
   FROM quiz.quiz_responses qr
   JOIN latest_course_shares lcs ON qr.user_id = lcs.user_id
   AND qr.course_id = lcs.course_id
   AND qr.share_id = lcs.share_id
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.user_id,
          la.course_id,
          la.share_id,
          qc.quizcard_id,
          qc.pass_mark,
          qc.qcount,
          count(distinct(CASE
                             WHEN qr.is_correct = TRUE THEN qr.question_id
                             ELSE NULL
                         END))::numeric AS correct_count
   FROM latest_attempt la
   JOIN quiz.quiz_responses qr ON la.user_id = qr.user_id
   AND la.course_id = qr.course_id
   AND la.share_id = qr.share_id
   AND la.card_id = qr.card_id
   AND la.question_id = qr.question_id
   AND la.latestAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     quiz_status AS
  (SELECT fs.user_id,
          fs.course_id,
          fs.share_id,
          count(distinct(quizcard_id)) AS no_of_quizzes,
          count(distinct(CASE
                             WHEN correct_count >= pass_mark THEN quizcard_id
                             ELSE NULL
                         END)) AS passed_quizzes,
          sum(correct_count) *100 / sum(qcount) AS score_in_pct
   FROM final_scores fs
   GROUP BY 1,
            2,
            3)
SELECT c.name as "Course",
ud.division as "Country",
       ud.job_location AS "Store",
	    ud.designation "Role",
       ud.job_type as "Picker Type",
       ud.emp_name as "Picker Name",
       ud.emp_id as "Rooster ID",
	   ud.phone_number as "Phone Number",
       lcs.sent_at + td.diff as "Assigned At",
       max(cc.consumed_at + td.diff) AS "Completed At",
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN c.total_cards > 0
                AND p.consumed_count > 0
                AND p.consumed_count < c.total_cards THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS "Course Status",
      CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes = 0 THEN 'NA'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes >= s.no_of_quizzes THEN 'Pass'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes < s.no_of_quizzes THEN 'Fail'
           ELSE NULL
       END AS "Quiz Status",
       s.score_in_pct as "Score",
       lcs.course_id AS "Course KNID",
       ud.uuid AS "User KNID"
FROM user_acl ud
JOIN latest_course_shares lcs ON lcs.user_id = ud.uuid
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
AND lcs.share_id = lcr.share_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
AND lcs.share_id = p.share_id
LEFT OUTER JOIN cards_consumed cc ON lcs.user_id = cc.user_id
AND lcs.course_id = cc.course_id
AND lcs.share_id = cc.share_id
LEFT OUTER JOIN quiz_status s ON lcs.user_id = s.user_id
AND lcs.course_id = s.course_id
AND lcs.share_id = s.share_id
LEFT OUTER JOIN public.courses c ON lcs.course_id = c.id
LEFT OUTER JOIN td ON ud.organization = td.organization
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
		 9,
         11,
		 12,
         13,
         14,
		 15
ORDER BY 1, 2, 3, 4, 5, 10, 7, 9
```

---
