# Abenson

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Abenson tasks_Tasks.sql

**Tables referenced:** acl, analytics_requests, assignees, checkpoint_master_sheet_table, locations, role_holders, t, tasks, user_details, user_groups

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
-- Data Source: Abenson tasks
-- Dashboard: Tasks
-- Category: Abenson
-- Extracted: 2026-01-29 16:55:20
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'abenson-sunflower'
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
   notes as "Details",
          /*coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",*/
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							/*CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           /*CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",*/
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
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image"/*,
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality"*/
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   /*left outer JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid*/
   WHERE t.is_deleted = 'false'
     --AND cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'abenson-sunflower'
  and to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' >= '2025-01-01'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' > '2025-01-08'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
   ud.division as "State",
   ud.sub_division as "City",
                      ud.job_location as store,
   ud.designation,
   ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
       assignees.assignee AS "Assignee",
	   assignees."State",
	   assignees."City",
	   assignees.store as "Location",
	   	   assignees.department AS "Assignee Department",
		   assignees.designation as "Assignee Designation"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
where assignees.store in (select store from acl) or author = @{{:UuidParameter}}
--and "Planned Start" >= '2025-01-01'
order by 12 desc
```

---

## Routine Compliance Abenson_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, form_submissions, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance Abenson
-- Dashboard: Routine Compliance
-- Category: Abenson
-- Extracted: 2026-01-29 16:53:08
-- ============================================================

SELECT
  "QueryTable 1"."Organization" AS "Organization",
  "QueryTable 1"."Date" AS "Date",
  "QueryTable 1"."Routine KNID" AS "Routine KNID",
  "QueryTable 1"."Routine Name" AS "Routine Name",
  "QueryTable 1"."Location" AS "Location",
  "QueryTable 1"."Final Division" AS "Division",
  "QueryTable 1"."Final Sub Division" AS "Sub Division",
  "QueryTable 1"."Reminded At" AS "Reminded At",
  "QueryTable 1"."Responded At" AS "Responded At",
  "QueryTable 1"."Compliance" AS "Compliance",
  "QueryTable 1"."Submission KNID" AS "Submission KNID",
  "QueryTable 1"."Routine #" AS "Routine #",
  "QueryTable 1"."Date Mod" AS "Date Mod"
FROM (
  WITH location_acl AS (
    SELECT DISTINCT job_location, division, sub_division
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
            WHERE ug2.user_id = @{{:UuidParameter}} AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ),
  td AS (
    SELECT id AS organization, interval '1 min' * tzoffset AS diff
    FROM organizations
    WHERE id = 'abenson-sunflower'
  )
  SELECT
    fc.*,
    TO_CHAR(fc."Date", 'YYYY-MM-DD') AS "Date Mod",
CASE
 WHEN fc."Location" ILIKE '16078%' THEN 'AVI'
WHEN fc."Location" ILIKE '17208%' THEN 'AVI'
WHEN fc."Location" ILIKE '17108%' THEN 'AVI'
WHEN fc."Location" ILIKE '16028%' THEN 'AVI'
WHEN fc."Location" ILIKE '17098%' THEN 'AVI'
WHEN fc."Location" ILIKE '10058%' THEN 'AVI'
WHEN fc."Location" ILIKE '17068%' THEN 'AVI'
WHEN fc."Location" ILIKE '17178%' THEN 'AVI'
WHEN fc."Location" ILIKE '10018%' THEN 'AVI'
WHEN fc."Location" ILIKE '17218%' THEN 'AVI'
WHEN fc."Location" ILIKE '10038%' THEN 'AVI'
WHEN fc."Location" ILIKE '17018%' THEN 'AVI'
WHEN fc."Location" ILIKE '10028%' THEN 'AVI'
WHEN fc."Location" ILIKE '10078%' THEN 'AVI'
WHEN fc."Location" ILIKE '508-AC NORTH EDSA%' THEN 'AC'
WHEN fc."Location" ILIKE '568-AC TUTUBAN%' THEN 'AC'
WHEN fc."Location" ILIKE '558-AC TRINOMA%' THEN 'AC'
WHEN fc."Location" ILIKE '31038%' THEN 'MP'
WHEN fc."Location" ILIKE '7004%' THEN 'EWI'
WHEN fc."Location" ILIKE '7008%' THEN 'EWI'
WHEN fc."Location" ILIKE '7015%' THEN 'EWI'
WHEN fc."Location" ILIKE '7021%' THEN 'EWI'
WHEN fc."Location" ILIKE '7035%' THEN 'EWI'
WHEN fc."Location" ILIKE '17008%' THEN 'AVI'
WHEN fc."Location" ILIKE '11058%' THEN 'AVI'
WHEN fc."Location" ILIKE '17128%' THEN 'AVI'
WHEN fc."Location" ILIKE '11118%' THEN 'AVI'
WHEN fc."Location" ILIKE '11018%' THEN 'AVI'
WHEN fc."Location" ILIKE '11088%' THEN 'AVI'
WHEN fc."Location" ILIKE '11168%' THEN 'AVI'
WHEN fc."Location" ILIKE '11098%' THEN 'AVI'
WHEN fc."Location" ILIKE '11138%' THEN 'AVI'
WHEN fc."Location" ILIKE '17118%' THEN 'AVI'
WHEN fc."Location" ILIKE '11158%' THEN 'AVI'
WHEN fc."Location" ILIKE '11068%' THEN 'AVI'
WHEN fc."Location" ILIKE '17138%' THEN 'AVI'
WHEN fc."Location" ILIKE '11008%' THEN 'AVI'
WHEN fc."Location" ILIKE '10088%' THEN 'AVI'
WHEN fc."Location" ILIKE '581-AC SHERIDAN%' THEN 'AC'
WHEN fc."Location" ILIKE '510-AC STA LUCIA%' THEN 'AC'
WHEN fc."Location" ILIKE '30268%' THEN 'AVI'
WHEN fc."Location" ILIKE '7010%' THEN 'EWI'
WHEN fc."Location" ILIKE '7026%' THEN 'EWI'
WHEN fc."Location" ILIKE '17158%' THEN 'AVI'
WHEN fc."Location" ILIKE '11108%' THEN 'AVI'
WHEN fc."Location" ILIKE '11038%' THEN 'AVI'
WHEN fc."Location" ILIKE '15008%' THEN 'AVI'
WHEN fc."Location" ILIKE '15018%' THEN 'AVI'
WHEN fc."Location" ILIKE '15028%' THEN 'AVI'
WHEN fc."Location" ILIKE '17198%' THEN 'AVI'
WHEN fc."Location" ILIKE '17028%' THEN 'AVI'
WHEN fc."Location" ILIKE '17088%' THEN 'AVI'
WHEN fc."Location" ILIKE '17058%' THEN 'AVI'
WHEN fc."Location" ILIKE '12038%' THEN 'AVI'
WHEN fc."Location" ILIKE '12068%' THEN 'AVI'
WHEN fc."Location" ILIKE '538-AC GATEWAY%' THEN 'AC'
WHEN fc."Location" ILIKE '528-AC ALIMALL%' THEN 'AC'
WHEN fc."Location" ILIKE '518-AC MARKET MARKET%' THEN 'AC'
WHEN fc."Location" ILIKE '36008%' THEN 'AVI'
WHEN fc."Location" ILIKE '30078%' THEN 'AVI'
WHEN fc."Location" ILIKE '7009%' THEN 'EWI'
WHEN fc."Location" ILIKE '7054%' THEN 'EWI'
WHEN fc."Location" ILIKE '221-FILINVEST%' THEN 'AVI'
WHEN fc."Location" ILIKE '16038%' THEN 'AVI'
WHEN fc."Location" ILIKE '16058%' THEN 'AVI'
WHEN fc."Location" ILIKE '222-LAS PINAS%' THEN 'AVI'
WHEN fc."Location" ILIKE '228-SUCAT%' THEN 'AVI'
WHEN fc."Location" ILIKE '223-JAKA%' THEN 'AVI'
WHEN fc."Location" ILIKE '220-AB ALABANG%' THEN 'AVI'
WHEN fc."Location" ILIKE '12008%' THEN 'AVI'
WHEN fc."Location" ILIKE '23678%' THEN 'AVI'
WHEN fc."Location" ILIKE '12058%' THEN 'AVI'
WHEN fc."Location" ILIKE '16068%' THEN 'AVI'
WHEN fc."Location" ILIKE '12088%' THEN 'AVI'
WHEN fc."Location" ILIKE '23628%' THEN 'AVI'
WHEN fc."Location" ILIKE '224-ATC%' THEN 'AVI'
WHEN fc."Location" ILIKE '23798%' THEN 'AVI'
WHEN fc."Location" ILIKE '598-AC ALABANG ATC%' THEN 'AC'
WHEN fc."Location" ILIKE '588-AC FILINVEST%' THEN 'AC'
WHEN fc."Location" ILIKE '578-AC GLORIETTA 1%' THEN 'AC'
WHEN fc."Location" ILIKE '230-MP SUCAT%' THEN 'MP'
WHEN fc."Location" ILIKE '8803%' THEN 'AVI'
WHEN fc."Location" ILIKE '229-ABH SUCAT%' THEN 'AVI'
WHEN fc."Location" ILIKE '30068%' THEN 'AVI'
WHEN fc."Location" ILIKE '7002%' THEN 'EWI'
WHEN fc."Location" ILIKE '7041%' THEN 'EWI'
WHEN fc."Location" ILIKE '7056-EW BICUTAN%' THEN 'EWI'
WHEN fc."Location" ILIKE '20078%' THEN 'AVI'
WHEN fc."Location" ILIKE '20018%' THEN 'AVI'
WHEN fc."Location" ILIKE '20008%' THEN 'AVI'
WHEN fc."Location" ILIKE '20068%' THEN 'AVI'
WHEN fc."Location" ILIKE '20088%' THEN 'AVI'
WHEN fc."Location" ILIKE '20098%' THEN 'AVI'
WHEN fc."Location" ILIKE '20038%' THEN 'AVI'
WHEN fc."Location" ILIKE '20028%' THEN 'AVI'
WHEN fc."Location" ILIKE '31018%' THEN 'MP'
WHEN fc."Location" ILIKE '30289%' THEN 'AVI'
WHEN fc."Location" ILIKE '30098%' THEN 'AVI'
WHEN fc."Location" ILIKE '30038%' THEN 'AVI'
WHEN fc."Location" ILIKE '30028%' THEN 'AVI'
WHEN fc."Location" ILIKE '22058%' THEN 'AVI'
WHEN fc."Location" ILIKE '22018%' THEN 'AVI'
WHEN fc."Location" ILIKE '22008%' THEN 'AVI'
WHEN fc."Location" ILIKE '22068%' THEN 'AVI'
WHEN fc."Location" ILIKE '22098%' THEN 'AVI'
WHEN fc."Location" ILIKE '27008%' THEN 'AVI'
WHEN fc."Location" ILIKE '22038%' THEN 'AVI'
WHEN fc."Location" ILIKE '31008%' THEN 'MP'
WHEN fc."Location" ILIKE '7012%' THEN 'EWI'
WHEN fc."Location" ILIKE '7051%' THEN 'EWI'
WHEN fc."Location" ILIKE '21038%' THEN 'AVI'
WHEN fc."Location" ILIKE '22088%' THEN 'AVI'
WHEN fc."Location" ILIKE '21058%' THEN 'AVI'
WHEN fc."Location" ILIKE '21018%' THEN 'AVI'
WHEN fc."Location" ILIKE '21068%' THEN 'AVI'
WHEN fc."Location" ILIKE '22078%' THEN 'AVI'
WHEN fc."Location" ILIKE '23008%' THEN 'AVI'
WHEN fc."Location" ILIKE '21078%' THEN 'AVI'
WHEN fc."Location" ILIKE '23018%' THEN 'AVI'
WHEN fc."Location" ILIKE '30188%' THEN 'AVI'
WHEN fc."Location" ILIKE '30058%' THEN 'AVI'
WHEN fc."Location" ILIKE '25018%' THEN 'AVI'
WHEN fc."Location" ILIKE '25068%' THEN 'AVI'
WHEN fc."Location" ILIKE '25088%' THEN 'AVI'
WHEN fc."Location" ILIKE '25378%' THEN 'AVI'
WHEN fc."Location" ILIKE '7052%' THEN 'EWI'
WHEN fc."Location" ILIKE '211-GEN TRIAS%' THEN 'AVI'
WHEN fc."Location" ILIKE '201-W DASMARINAS%' THEN 'AVI'
WHEN fc."Location" ILIKE '217-PG BACOOR%' THEN 'AVI'
WHEN fc."Location" ILIKE '23658%' THEN 'AVI'
 WHEN fc."Location" ILIKE '30068%' THEN 'AVI'
WHEN fc."Location" ILIKE '23608%' THEN 'AVI'
WHEN fc."Location" ILIKE '23748%' THEN 'AVI'
WHEN fc."Location" ILIKE '209-W CARMONA%' THEN 'AVI'
WHEN fc."Location" ILIKE '23618%' THEN 'AVI'
WHEN fc."Location" ILIKE '23738%' THEN 'AVI'
WHEN fc."Location" ILIKE '23708%' THEN 'AVI'
WHEN fc."Location" ILIKE '227-PG TANZA%' THEN 'AVI'
WHEN fc."Location" ILIKE '204-LOTUS%' THEN 'AVI'
WHEN fc."Location" ILIKE '23718%' THEN 'AVI'
WHEN fc."Location" ILIKE '202-IMUS 1%' THEN 'AVI'
WHEN fc."Location" ILIKE '233-ABH DASMA%' THEN 'AVI'
WHEN fc."Location" ILIKE '7013%' THEN 'EWI'
WHEN fc."Location" ILIKE '7052%' THEN 'EWI'
WHEN fc."Location" ILIKE '23208%' THEN 'AVI'
WHEN fc."Location" ILIKE '206-W STA ROSA%' THEN 'AVI'
WHEN fc."Location" ILIKE '23228%' THEN 'AVI'
WHEN fc."Location" ILIKE '23818%' THEN 'AVI'
WHEN fc."Location" ILIKE '203-MAKILING%' THEN 'AVI'
WHEN fc."Location" ILIKE '23298%' THEN 'AVI'
WHEN fc."Location" ILIKE '23728%' THEN 'AVI'
WHEN fc."Location" ILIKE '23238%' THEN 'AVI'
WHEN fc."Location" ILIKE '23758%' THEN 'AVI'
WHEN fc."Location" ILIKE '23218%' THEN 'AVI'
WHEN fc."Location" ILIKE '23268%' THEN 'AVI'
WHEN fc."Location" ILIKE '208-BINAN%' THEN 'AVI'
WHEN fc."Location" ILIKE '231-MP MAKILING%' THEN 'MP'
WHEN fc."Location" ILIKE '212-ABH MAKILING%' THEN 'AVI'
WHEN fc."Location" ILIKE '30178%' THEN 'AVI'
WHEN fc."Location" ILIKE '7034%' THEN 'EWI'
WHEN fc."Location" ILIKE '23838%' THEN 'AVI'
WHEN fc."Location" ILIKE '23808%' THEN 'AVI'
WHEN fc."Location" ILIKE '23828%' THEN 'AVI'
WHEN fc."Location" ILIKE '213-LUCENA%' THEN 'AVI'
WHEN fc."Location" ILIKE '23898%' THEN 'AVI'
WHEN fc."Location" ILIKE '18098%' THEN 'AVI'
WHEN fc."Location" ILIKE '225-W TANAUAN%' THEN 'AVI'
WHEN fc."Location" ILIKE '23888%' THEN 'AVI'
WHEN fc."Location" ILIKE '23878%' THEN 'AVI'
WHEN fc."Location" ILIKE '210-ULTIMART SAN PABLO%' THEN 'AVI'
WHEN fc."Location" ILIKE '23908%' THEN 'AVI'
WHEN fc."Location" ILIKE '23868%' THEN 'AVI'
WHEN fc."Location" ILIKE '23258%' THEN 'AVI'
WHEN fc."Location" ILIKE '232-MP TANAUAN%' THEN 'MP'
WHEN fc."Location" ILIKE '226-ABH TANAUAN%' THEN 'AVI'
WHEN fc."Location" ILIKE '7020%' THEN 'EWI'
WHEN fc."Location" ILIKE '7039%' THEN 'EWI'
WHEN fc."Location" ILIKE '611-LCC POLANGUI 2%' THEN 'AVI'
WHEN fc."Location" ILIKE '605-PG NAGA%' THEN 'AVI'
WHEN fc."Location" ILIKE '603-LCC NAGA%' THEN 'AVI'
WHEN fc."Location" ILIKE '602-PACIFIC LEGASPI%' THEN 'AVI'
WHEN fc."Location" ILIKE '601-LCC LEGASPI%' THEN 'AVI'
WHEN fc."Location" ILIKE '612-LCC CBD NAGA%' THEN 'AVI'
WHEN fc."Location" ILIKE '606-AYALA LEGASPI%' THEN 'AVI'
WHEN fc."Location" ILIKE '604-LCC IRIGA%' THEN 'AVI'
WHEN fc."Location" ILIKE '301-ICM BOHOL%' THEN 'AVI'
WHEN fc."Location" ILIKE '302-ALTURAS BOHOL%' THEN 'AVI'
WHEN fc."Location" ILIKE '303-TALIBON BOHOL%' THEN 'AVI'
WHEN fc."Location" ILIKE '18038%' THEN 'AVI'
WHEN fc."Location" ILIKE '18078%' THEN 'AVI'
WHEN fc."Location" ILIKE '18118%' THEN 'AVI'
WHEN fc."Location" ILIKE '18128%' THEN 'AVI'
WHEN fc."Location" ILIKE '18138%' THEN 'AVI'
WHEN fc."Location" ILIKE '18018%' THEN 'AVI'
WHEN fc."Location" ILIKE '18068%' THEN 'AVI'
WHEN fc."Location" ILIKE '18208%' THEN 'AVI'
WHEN fc."Location" ILIKE '18218%' THEN 'AVI'
WHEN fc."Location" ILIKE '18238%' THEN 'AVI'
WHEN fc."Location" ILIKE '18178%' THEN 'AVI'
WHEN fc."Location" ILIKE '7602%' THEN 'EWI'
WHEN fc."Location" ILIKE '7610%' THEN 'EWI'
WHEN fc."Location" ILIKE '852-AYALA ABREEZA%' THEN 'AVI'
WHEN fc."Location" ILIKE '855-NCCC BUHANGIN%' THEN 'AVI'
WHEN fc."Location" ILIKE '18108%' THEN 'AVI'
WHEN fc."Location" ILIKE '18198%' THEN 'AVI'
WHEN fc."Location" ILIKE '98008%' THEN 'AVI'
WHEN fc."Location" ILIKE '7053%' THEN 'EWI'
WHEN fc."Location" ILIKE '98028%' THEN 'AVI'
WHEN fc."Location" ILIKE '30068%' THEN 'AVI'
WHEN fc."Location" ILIKE '18258%' THEN 'AVI'
WHEN fc."Location" ILIKE '18248%' THEN 'AVI'
WHEN fc."Location" ILIKE '23028%' THEN 'AVI'
WHEN fc."Location" ILIKE '7055%' THEN 'EWI'
WHEN fc."Location" ILIKE '98038%' THEN 'AVI'
ELSE 'Unknown - Update the Master'
END AS "Final Division",
  
  CASE
  WHEN fc."Location" ILIKE '16078%' THEN 'MM1'
WHEN fc."Location" ILIKE '17208%' THEN 'MM1'
WHEN fc."Location" ILIKE '17108%' THEN 'MM1'
WHEN fc."Location" ILIKE '16028%' THEN 'MM1'
WHEN fc."Location" ILIKE '17098%' THEN 'MM1'
WHEN fc."Location" ILIKE '10058%' THEN 'MM1'
WHEN fc."Location" ILIKE '17068%' THEN 'MM1'
WHEN fc."Location" ILIKE '17178%' THEN 'MM1'
WHEN fc."Location" ILIKE '10018%' THEN 'MM1'
WHEN fc."Location" ILIKE '17218%' THEN 'MM1'
WHEN fc."Location" ILIKE '10038%' THEN 'MM1'
WHEN fc."Location" ILIKE '17018%' THEN 'MM1'
WHEN fc."Location" ILIKE '10028%' THEN 'MM1'
WHEN fc."Location" ILIKE '10078%' THEN 'MM1'
WHEN fc."Location" ILIKE '508-AC NORTH EDSA%' THEN 'MM1'
WHEN fc."Location" ILIKE '568-AC TUTUBAN%' THEN 'MM1'
WHEN fc."Location" ILIKE '558-AC TRINOMA%' THEN 'MM1'
WHEN fc."Location" ILIKE '31038%' THEN 'MM1'
WHEN fc."Location" ILIKE '7004%' THEN 'MM1'
WHEN fc."Location" ILIKE '7008%' THEN 'MM1'
WHEN fc."Location" ILIKE '7015%' THEN 'MM1'
WHEN fc."Location" ILIKE '7021%' THEN 'MM1'
WHEN fc."Location" ILIKE '7035%' THEN 'MM1'
WHEN fc."Location" ILIKE '17008%' THEN 'MM2'
WHEN fc."Location" ILIKE '11058%' THEN 'MM2'
WHEN fc."Location" ILIKE '17128%' THEN 'MM2'
WHEN fc."Location" ILIKE '11118%' THEN 'MM2'
WHEN fc."Location" ILIKE '11018%' THEN 'MM2'
WHEN fc."Location" ILIKE '11088%' THEN 'MM2'
WHEN fc."Location" ILIKE '11168%' THEN 'MM2'
WHEN fc."Location" ILIKE '11098%' THEN 'MM2'
WHEN fc."Location" ILIKE '11138%' THEN 'MM2'
WHEN fc."Location" ILIKE '17118%' THEN 'MM2'
WHEN fc."Location" ILIKE '11158%' THEN 'MM2'
WHEN fc."Location" ILIKE '11068%' THEN 'MM2'
WHEN fc."Location" ILIKE '17138%' THEN 'MM2'
WHEN fc."Location" ILIKE '11008%' THEN 'MM2'
WHEN fc."Location" ILIKE '10088%' THEN 'MM2'
WHEN fc."Location" ILIKE '581-AC SHERIDAN%' THEN 'MM2'
WHEN fc."Location" ILIKE '510-AC STA LUCIA%' THEN 'MM2'
WHEN fc."Location" ILIKE '30268%' THEN 'MM2'
WHEN fc."Location" ILIKE '7010%' THEN 'MM2'
WHEN fc."Location" ILIKE '7026%' THEN 'MM2'
WHEN fc."Location" ILIKE '17158%' THEN 'MM3'
WHEN fc."Location" ILIKE '11108%' THEN 'MM3'
WHEN fc."Location" ILIKE '11038%' THEN 'MM3'
WHEN fc."Location" ILIKE '15008%' THEN 'MM3'
WHEN fc."Location" ILIKE '15018%' THEN 'MM3'
WHEN fc."Location" ILIKE '15028%' THEN 'MM3'
WHEN fc."Location" ILIKE '17198%' THEN 'MM3'
WHEN fc."Location" ILIKE '17028%' THEN 'MM3'
WHEN fc."Location" ILIKE '17088%' THEN 'MM3'
WHEN fc."Location" ILIKE '17058%' THEN 'MM3'
WHEN fc."Location" ILIKE '12038%' THEN 'MM3'
WHEN fc."Location" ILIKE '12068%' THEN 'MM3'
WHEN fc."Location" ILIKE '538-AC GATEWAY%' THEN 'MM3'
WHEN fc."Location" ILIKE '528-AC ALIMALL%' THEN 'MM3'
WHEN fc."Location" ILIKE '518-AC MARKET MARKET%' THEN 'MM3'
WHEN fc."Location" ILIKE '36008%' THEN 'MM3'
WHEN fc."Location" ILIKE '30078%' THEN 'MM3'
WHEN fc."Location" ILIKE '7009%' THEN 'MM3'
WHEN fc."Location" ILIKE '7054%' THEN 'MM3'
WHEN fc."Location" ILIKE '221-FILINVEST%' THEN 'MM4'
WHEN fc."Location" ILIKE '16038-ERMITA 2%' THEN 'MM4'
WHEN fc."Location" ILIKE '16058-W MALL%' THEN 'MM4'
WHEN fc."Location" ILIKE '222-LAS PINAS%' THEN 'MM4'
WHEN fc."Location" ILIKE '228-SUCAT%' THEN 'MM4'
WHEN fc."Location" ILIKE '223-JAKA%' THEN 'MM4'
WHEN fc."Location" ILIKE '220-AB ALABANG%' THEN 'MM4'
WHEN fc."Location" ILIKE '12008-MAKATI%' THEN 'MM4'
WHEN fc."Location" ILIKE '23678-FTI TAGUIG%' THEN 'MM4'
WHEN fc."Location" ILIKE '12058-GLORIETTA 1%' THEN 'MM4'
WHEN fc."Location" ILIKE '16068-CIRCUIT MALL%' THEN 'MM4'
WHEN fc."Location" ILIKE '12088-ONE AYALA%' THEN 'MM4'
WHEN fc."Location" ILIKE '23628-BICUTAN%' THEN 'MM4'
WHEN fc."Location" ILIKE '224-ATC%' THEN 'MM4'
WHEN fc."Location" ILIKE '23798-W MUNTINLUPA%' THEN 'MM4'
WHEN fc."Location" ILIKE '598-AC ALABANG ATC%' THEN 'MM4'
WHEN fc."Location" ILIKE '588-AC FILINVEST%' THEN 'MM4'
WHEN fc."Location" ILIKE '578-AC GLORIETTA 1%' THEN 'MM4'
WHEN fc."Location" ILIKE '230-MP SUCAT%' THEN 'MM4'
WHEN fc."Location" ILIKE '8803-ABH WMALL%' THEN 'MM4'
WHEN fc."Location" ILIKE '229-ABH SUCAT%' THEN 'MM4'
WHEN fc."Location" ILIKE '30068- ABH MAKATI%' THEN 'MM4'
WHEN fc."Location" ILIKE '7002-EW GLORIETTA%' THEN 'MM4'
WHEN fc."Location" ILIKE '7041-EW MALL OF ASIA 2%' THEN 'MM4'
WHEN fc."Location" ILIKE '7056-EW BICUTAN%' THEN 'MM4'
WHEN fc."Location" ILIKE '30068%' THEN 'MM4'
WHEN fc."Location" ILIKE '20078%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20018%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20008%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20068%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20088%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20098%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20038%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '20028%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '31018%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '30289%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '30098%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '30038%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '30028%' THEN 'NORTH1'
WHEN fc."Location" ILIKE '22058%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '22018%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '22008%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '22068%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '22098%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '27008%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '22038%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '31008%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '7012%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '7051%' THEN 'NORTH2'
  WHEN fc."Location" ILIKE '23028%' THEN 'NORTH2'
WHEN fc."Location" ILIKE '21038%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '22088%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '21058%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '21018%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '21068%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '22078%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '23008%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '21078%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '23018%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '30188%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '30058%' THEN 'NORTH3'
WHEN fc."Location" ILIKE '25018%' THEN 'NORTH4'
WHEN fc."Location" ILIKE '25068%' THEN 'NORTH4'
WHEN fc."Location" ILIKE '25088%' THEN 'NORTH4'
WHEN fc."Location" ILIKE '25378%' THEN 'NORTH4'
WHEN fc."Location" ILIKE '7053%' THEN 'NORTH 4'
  WHEN fc."Location" ILIKE '7055%' THEN 'NORTH 4'
WHEN fc."Location" ILIKE '211-GEN TRIAS%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '201-W DASMARINAS%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '217-PG BACOOR%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23658%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23608%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23748%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '209-W CARMONA%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23618%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23738%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23708%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '227-PG TANZA%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '204-LOTUS%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23718%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '202-IMUS 1%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '233-ABH DASMA%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '7013%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '7052%' THEN 'SOUTH1'
WHEN fc."Location" ILIKE '23208%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '206-W STA ROSA%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23228%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23818%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '203-MAKILING%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23298%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23728%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23238%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23758%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23218%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23268%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '208-BINAN%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '231-MP MAKILING%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '212-ABH MAKILING%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '30178%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '7034%' THEN 'SOUTH2'
WHEN fc."Location" ILIKE '23838%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23808%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23828%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '213-LUCENA%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23898%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '18098%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '225-W TANAUAN%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23888%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23878%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '210-ULTIMART SAN PABLO%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23908%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23868%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '23258%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '232-MP TANAUAN%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '226-ABH TANAUAN%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '7020%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '7039%' THEN 'SOUTH3'
WHEN fc."Location" ILIKE '611-LCC POLANGUI 2%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '605-PG NAGA%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '603-LCC NAGA%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '602-PACIFIC LEGASPI%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '601-LCC LEGASPI%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '612-LCC CBD NAGA%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '606-AYALA LEGASPI%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '604-LCC IRIGA%' THEN 'SOUTH4'
WHEN fc."Location" ILIKE '301-ICM BOHOL%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '302-ALTURAS BOHOL%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '303-TALIBON BOHOL%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18038%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18078%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18118%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18128%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18138%' THEN 'VISMIN1'
 WHEN fc."Location" ILIKE '18178%' THEN 'VISMIN1'
WHEN fc."Location" ILIKE '18018%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '18068%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '18208%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '18218%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '18238%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '7602%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '7610%' THEN 'VISMIN2'
WHEN fc."Location" ILIKE '852-AYALA ABREEZA%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '855-NCCC BUHANGIN%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '18108%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '18198%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '98008%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '98028%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '18258%' THEN 'VISMIN3'
  WHEN fc."Location" ILIKE '98038%' THEN 'VISMIN3'
WHEN fc."Location" ILIKE '18248%' THEN 'VISMIN1'
ELSE 'Unknown - Update the Master'
END AS "Final Sub Division"
  FROM form_compliance_v2 fc
  JOIN location_acl ON fc."Location" = location_acl.job_location
  LEFT JOIN form_submissions fs ON fs.response_id = fc."Submission KNID"
  LEFT JOIN user_details ud ON fs.user_id = ud.uuid
  WHERE fc."Organization" = @{{:OrganizationParameter}}
    AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  AND COALESCE(ud.division, location_acl.division) NOT IN  ('AHQ','KNOW')
AND COALESCE(ud.sub_division, location_acl.sub_division) != 'AHQ'
AND fc."Location" != 'AHQ'
) "QueryTable 1"
```

---
