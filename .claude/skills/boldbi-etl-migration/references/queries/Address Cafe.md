# Address Cafe

> Auto-generated on 2026-03-04 08:13

**Total queries:** 3

---

## Address Cafe DM Tasks Status_DM Task Status.sql

**Tables referenced:** acl, analytics_requests, audit_location_questions, audit_locations, dm, dm_groups, form_responses, form_submissions, location_acl, question_definitions, rm, rm_groups, store_map, stores, submissions, t, tasks, to_timestamp, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)


**Original Query:**

```sql
-- Data Source: Address Cafe DM Tasks Status
-- Dashboard: DM Task Status
-- Category: Address Cafe
-- Extracted: 2026-01-29 16:55:21
-- ============================================================

 SELECT
		"QueryTable 1"."region" AS "region",
		"QueryTable 1"."city" AS "city",
		"QueryTable 1"."dm_name" AS "dm_name",
		"QueryTable 1"."manager_designation" AS "manager_designation",
		"QueryTable 1"."store_id" AS "store_id",
		"QueryTable 1"."checklist" AS "checklist",
		"QueryTable 1"."month" AS "month",
		"QueryTable 1"."task_start" AS "task_start",
		"QueryTable 1"."due_date" AS "due_date",
		"QueryTable 1"."task_status" AS "task_status",
		"QueryTable 1"."comp_task_count" AS "comp_task_count",
		"QueryTable 1"."task_done_by" AS "task_done_by",
		"QueryTable 1"."task_done_on" AS "task_done_on",
		"QueryTable 1"."avg_actual_score" AS "avg_actual_score",
		"QueryTable 1"."max_score" AS "max_score",
		"QueryTable 1"."avg_score_pct" AS "avg_score_pct",
		"QueryTable 1"."task_knid" AS "task_knid",
		"QueryTable 1"."checklist_knid" AS "checklist_knid",
		"QueryTable 1"."manager_knid" AS "manager_knid",
		"QueryTable 1"."doer_knid" AS "doer_knid",
		"QueryTable 1"."submission_knid" AS "submission_knid",
		"QueryTable 1"."submit_date" AS "submit_date",
		"QueryTable 1"."started_at" AS "started_at"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'addresscafe-cartwheel'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = '3BhZAw1uBa6VbqLZzQiBsp')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = '3BhZAw1uBa6VbqLZzQiBsp'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     stores AS
  (SELECT *
   FROM user_details
   WHERE designation = 'Store'
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
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
          stores.last_name AS store_name,
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
            4),
     store_map AS
  (SELECT acl.*,
          dm.first_name||' '||dm.last_name AS dm_name,
          dm.identifier AS dm_identifier,
          rm.first_name||' '||rm.last_name AS rm_name,
          rm.identifier AS rm_identifier
   FROM acl
   LEFT OUTER JOIN user_details dm ON acl.dm_knid = dm.uuid
   LEFT OUTER JOIN user_details rm ON acl.rm_knid = rm.uuid
   ORDER BY 2,
            3,
            4,
            1),
     t AS
  (SELECT *,
          substring(title, position('@' IN title)+2, 4) AS store_id,
          upper(CASE
                    WHEN title ILIKE 'Food Safety%' THEN 'Food Safety'
                    WHEN title ILIKE 'Opening%' THEN 'Opening'
                    WHEN title ILIKE 'Closing%' THEN 'Closing'
                    WHEN title ILIKE 'Manager Obs%' THEN 'MOC'
                    WHEN title ILIKE 'Rush%' THEN 'Rush'
                    WHEN title ILIKE 'Game Day%' THEN 'Game Day'
				    WHEN title ILIKE 'Cafe Audit%' then 'Cafe Audit'
				    WHEN title ILIKE 'Coffee DT%' then 'Coffee DT'
				
                    ELSE substring(title, 1, position('@' IN title)-2)
                END) AS checklist
   FROM tasks
   WHERE organization = 'addresscafe-cartwheel'
     AND is_Deleted != 'true'
     AND ext_id ILIKE '%-DM-202%'
   AND to_timestamp(planned_start_date/1000) at time zone 'Asia/Riyadh' between (@{{:Date Range.START}}::timestamp at time zone 'Asia/Riyadh') and (@{{:Date Range.END}}::timestamp at time zone 'Asia/Riyadh' + interval '1 day'  - interval '1 second')),
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
   WHERE fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t) ),
     submissions AS
  (SELECT fs.user_id,
          parent_nugget_id,
          fs.form_id,
          fs.sno,
          fs.response_id,
          left(al.audit_location, 4) AS store_id,
         
          (fr.response ->> 'auditStatus') AS status,
          (fr.response ->> 'auditScore')::numeric AS actual_score,
          (fr.response ->> 'auditMaxScore')::numeric AS max_score,
   fs.submit_date,
         fs.started_at
   FROM form_submissions fs
   JOIN form_responses fr ON fr.form_submit_id = fs.id
   JOIN audit_locations al ON fs.response_id = al.response_id
   WHERE fr.question_id = 'formAuditResults'
     AND fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t)
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,fs.submit_date,fs.started_at,fr.response)
SELECT store_map.region AS region,
       store_map.city AS city,
       CAST(store_map.dm_name AS VARCHAR) AS dm_name,
       'DM' AS manager_designation,
       t.store_id,
       t.checklist,
       to_char(date_trunc('Month', to_timestamp(planned_start_date/1000) at time zone 'Asia/Riyadh'), 'YYYY-MM') AS MONTH,
       CASE
           WHEN extract('day'
                        FROM to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh')>27 THEN to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'+ interval '1 day'
           ELSE to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'
       END AS task_start,
       to_timestamp(deadline/1000) AT TIME ZONE 'Asia/Riyadh' AS due_date,
                                                min(CASE
                                                        WHEN submissions.submit_date IS NOT NULL THEN 'Completed'
                                                        ELSE 'Incomplete'
                                                    END) AS task_status,
                                                max(CASE
                                                        WHEN submissions.submit_date IS NOT NULL THEN 1
                                                        ELSE 0
                                                    END) AS comp_task_count,
                                                submitter.first_name||' '||submitter.last_name AS task_done_by,
												
                                                min(submissions.submit_date) AS task_done_on,
                                                avg(submissions.actual_score) AS avg_actual_score,
                                                avg(submissions.max_score) AS max_score,
                                                avg(CASE
                                                        WHEN submissions.max_score != 0 THEN submissions.actual_score*100/submissions.max_score
                                                        ELSE NULL
                                                    END) AS avg_score_pct,
                                                t.id AS task_knid,
                                                t.details->0->'value'->>'formId' AS checklist_knid,
                                                                        ar.user_id AS manager_knid,
                                                                        submitter.uuid AS doer_knid,
                                                                        submissions.response_id AS submission_knid,
																		submissions.submit_date,
	 submissions.started_at
FROM t
LEFT OUTER JOIN analytics_requests ar ON t.id = ar.nugget_id
LEFT OUTER JOIN submissions ON submissions.parent_nugget_id = t.id
LEFT OUTER JOIN user_details submitter ON submissions.user_id = submitter.uuid
LEFT OUTER JOIN store_map ON t.store_id = store_map.store_id
 JOIN location_acl ON left(location_acl.job_location, 4) = store_map.store_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         12,
         17,
         18,
         19,
         20,
         21,submissions.submit_date,
	 submissions.started_at
ORDER BY 8 DESC,
         1,
         2,
         3,
         5)"QueryTable 1"
```

---

## Address Cafe QA Tasks Status_QA Task Status.sql

**Tables referenced:** acl, analytics_requests, audit_location_questions, audit_locations, dm, dm_groups, form_responses, form_submissions, location_acl, question_definitions, rm, rm_groups, store_map, stores, submissions, t, tasks, to_timestamp, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)


**Original Query:**

```sql
-- Data Source: Address Cafe QA Tasks Status
-- Dashboard: QA Task Status
-- Category: Address Cafe
-- Extracted: 2026-01-29 16:56:09
-- ============================================================

 SELECT
		"QueryTable 1"."region" AS "region",
		"QueryTable 1"."city" AS "city",
		"QueryTable 1"."Auditor" AS "Auditor",
		"QueryTable 1"."store_id" AS "store_id",
		"QueryTable 1"."checklist" AS "checklist",
		"QueryTable 1"."month" AS "month",
		"QueryTable 1"."task_start" AS "task_start",
		"QueryTable 1"."due_date" AS "due_date",
		"QueryTable 1"."task_status" AS "task_status",
		"QueryTable 1"."comp_task_count" AS "comp_task_count",
		"QueryTable 1"."task_done_by" AS "task_done_by",
		"QueryTable 1"."task_done_on" AS "task_done_on",
		"QueryTable 1"."avg_actual_score" AS "avg_actual_score",
		"QueryTable 1"."max_score" AS "max_score",
		"QueryTable 1"."avg_score_pct" AS "avg_score_pct",
		"QueryTable 1"."task_knid" AS "task_knid",
		"QueryTable 1"."checklist_knid" AS "checklist_knid",
		"QueryTable 1"."manager_knid" AS "manager_knid",
		"QueryTable 1"."doer_knid" AS "doer_knid",
		"QueryTable 1"."submission_knid" AS "submission_knid"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'addresscafe-cartwheel'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = '3BhZAw1uBa6VbqLZzQiBsp')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = '3BhZAw1uBa6VbqLZzQiBsp'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     stores AS
  (SELECT *
   FROM user_details
   WHERE designation = 'Store'
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     /*dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
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
   AND ug.has_access = 'true'),*/
     acl AS
  (SELECT stores.identifier AS store_id,
          stores.last_name AS store_name,
          stores.division AS region,
          stores.sub_division AS city/*,
          max(dm_groups.uuid) AS dm_knid,
          max(rm_groups.uuid) AS rm_knid*/
   FROM stores
   /*LEFT OUTER JOIN user_groups ug ON stores.uuid = ug.user_id
   AND ug.is_active = 'true'
   LEFT OUTER JOIN dm_groups ON ug.group_id = dm_groups.group_id
   LEFT OUTER JOIN rm_groups ON ug.group_id = rm_groups.group_id*/
   GROUP BY 1,
            2,
            3,
            4),
     store_map AS
  (SELECT acl.*/*,
          dm.first_name||' '||dm.last_name AS dm_name,
          dm.identifier AS dm_identifier,
          rm.first_name||' '||rm.last_name AS rm_name,
          rm.identifier AS rm_identifier*/
   FROM acl
   /*LEFT OUTER JOIN user_details dm ON acl.dm_knid = dm.uuid
   LEFT OUTER JOIN user_details rm ON acl.rm_knid = rm.uuid
   ORDER BY 2,
            3,
            4,
            1*/),
     t AS
  (SELECT *,
          substring(title, position('_' IN title)+1, 4) AS store_id,
          'Quality Audit' AS checklist
   FROM tasks
   WHERE organization = 'addresscafe-cartwheel'
     AND is_Deleted != 'true'
     AND title ILIKE 'Quality Audit_%'
   AND to_timestamp(planned_start_date/1000) at time zone 'Asia/Riyadh' between ('2025-05-01'::timestamp at time zone 'Asia/Riyadh') and ('2025-05-31'::timestamp at time zone 'Asia/Riyadh' + interval '1 day'  - interval '1 second')),
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
   WHERE fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t) ),
     submissions AS
  (SELECT fs.user_id,
          parent_nugget_id,
          fs.form_id,
          fs.sno,
          fs.response_id,
          left(al.audit_location, 4) AS store_id,
          (fs.submit_date AT TIME ZONE 'Asia/Riyadh')::date AS submit_date,
          (fr.response ->> 'auditStatus') AS status,
          (fr.response ->> 'auditScore')::numeric AS actual_score,
          (fr.response ->> 'auditMaxScore')::numeric AS max_score
   FROM form_submissions fs
   JOIN form_responses fr ON fr.form_submit_id = fs.id
   JOIN audit_locations al ON fs.response_id = al.response_id
   WHERE fr.question_id = 'formAuditResults'
     AND fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t)
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
SELECT store_map.region AS region,
       store_map.city AS city,
       /*CAST(store_map.dm_name AS VARCHAR) AS dm_name,
       'DM' AS manager_designation,*/
	   qa.first_name||' '||qa.last_name as "Auditor",
       t.store_id,
       t.checklist,
       to_char(date_trunc('Month', to_timestamp(planned_start_date/1000) at time zone 'Asia/Riyadh'), 'YYYY-MM') AS MONTH,
       CASE
           WHEN extract('day'
                        FROM to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh')>27 THEN to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'+ interval '1 day'
           ELSE to_timestamp(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'
       END AS task_start,
       to_timestamp(deadline/1000) AT TIME ZONE 'Asia/Riyadh' AS due_date,
                                                min(CASE
                                                        WHEN submissions.submit_date IS NOT NULL THEN 'Completed'
                                                        ELSE 'Incomplete'
                                                    END) AS task_status,
                                                max(CASE
                                                        WHEN submissions.submit_date IS NOT NULL THEN 1
                                                        ELSE 0
                                                    END) AS comp_task_count,
                                                submitter.first_name||' '||submitter.last_name AS task_done_by,
                                                min(submissions.submit_date) AS task_done_on,
                                                avg(submissions.actual_score) AS avg_actual_score,
                                                avg(submissions.max_score) AS max_score,
                                                avg(CASE
                                                        WHEN submissions.max_score != 0 THEN submissions.actual_score*100/submissions.max_score
                                                        ELSE NULL
                                                    END) AS avg_score_pct,
                                                t.id AS task_knid,
                                                t.details->0->'value'->>'formId' AS checklist_knid,
                                                                        ar.user_id AS manager_knid,
                                                                        submitter.uuid AS doer_knid,
                                                                        submissions.response_id AS submission_knid
FROM t
LEFT OUTER JOIN analytics_requests ar ON t.id = ar.nugget_id and event_id =  1
LEFT OUTER JOIN submissions ON submissions.parent_nugget_id = t.id
LEFT OUTER JOIN user_details submitter ON submissions.user_id = submitter.uuid
left outer join user_details qa on qa.uuid = ar.user_id
LEFT OUTER JOIN store_map ON t.store_id = store_map.store_id
JOIN location_acl ON left(location_acl.job_location, 4) = store_map.store_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         11,
         16,
         17,
         18,
		 19,
         20
ORDER BY 7 DESC,
         1,
         2,
         4,
         3)"QueryTable 1"
```

---

## Address Cafe RM Tasks Status_RM Task Status.sql

**Tables referenced:** TO_TIMESTAMP, acl, analytics_requests, assignees, audit_location_questions, audit_locations, dm, dm_groups, form_responses, form_submissions, location_acl, question_definitions, rm, rm_groups, store_map, stores, submissions, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)


**Original Query:**

```sql
-- Data Source: Address Cafe RM Tasks Status
-- Dashboard: RM Task Status
-- Category: Address Cafe
-- Extracted: 2026-01-29 16:55:21
-- ============================================================

 SELECT
		"QueryTable 1"."RM" AS "RM",
		"QueryTable 1"."DM" AS "DM",
		"QueryTable 1"."manager_designation" AS "manager_designation",
		"QueryTable 1"."checklist" AS "checklist",
		"QueryTable 1"."store_id" AS "store_id",
		"QueryTable 1"."month" AS "month",
		"QueryTable 1"."task_start" AS "task_start",
		"QueryTable 1"."due_date" AS "due_date",
		"QueryTable 1"."task_status" AS "task_status",
		"QueryTable 1"."comp_task_count" AS "comp_task_count",
		"QueryTable 1"."task_done_by" AS "task_done_by",
		"QueryTable 1"."submit_date" AS "submit_date",
		"QueryTable 1"."started_at" AS "started_at",
		"QueryTable 1"."task_done_on" AS "task_done_on",
		"QueryTable 1"."avg_actual_score" AS "avg_actual_score",
		"QueryTable 1"."max_score" AS "max_score",
		"QueryTable 1"."avg_score_pct" AS "avg_score_pct",
		"QueryTable 1"."task_knid" AS "task_knid",
		"QueryTable 1"."checklist_knid" AS "checklist_knid",
		"QueryTable 1"."manager_knid" AS "manager_knid",
		"QueryTable 1"."doer_knid" AS "doer_knid",
		"QueryTable 1"."submission_knid" AS "submission_knid"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'addresscafe-cartwheel'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = '3BhZAw1uBa6VbqLZzQiBsp')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = '3BhZAw1uBa6VbqLZzQiBsp'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     stores AS
  (SELECT *
   FROM user_details
   WHERE designation = 'Store'
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization = 'addresscafe-cartwheel'
     AND is_active = 'true'),
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
          stores.last_name AS store_name,
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
            4),
     store_map AS
  (SELECT acl.*,
          dm.first_name||' '||dm.last_name AS dm_name,
          dm.identifier AS dm_identifier,
          rm.first_name||' '||rm.last_name AS rm_name,
          rm.identifier AS rm_identifier
   FROM acl
   LEFT OUTER JOIN user_details dm ON acl.dm_knid = dm.uuid
   LEFT OUTER JOIN user_details rm ON acl.rm_knid = rm.uuid
   ORDER BY 2,
            3,
            4,
            1),
     t AS
  (SELECT *,
          substring(title, position('@' IN title)+2, 4) AS store_id,
          upper(CASE
                    WHEN title ILIKE 'Food Safety%' THEN 'Food Safety'
                    WHEN title ILIKE 'Opening%' THEN 'Opening'
                    WHEN title ILIKE 'Closing%' THEN 'Closing'
                    WHEN title ILIKE 'Manager Obs%' THEN 'MOC'
                    WHEN title ILIKE 'Rush%' THEN 'Rush'
                    WHEN title ILIKE 'Game Day%' THEN 'Game Day'
				    WHEN title ILIKE 'Cafe Audit%' then 'Cafe Audit'
				    WHEN title ILIKE 'Coffee DT%' then 'Coffee DT'
				WHEN title ILIKE 'OER%' then 'OER'
				
                    ELSE substring(title, 1, position('@' IN title)-2)
                END) AS checklist
   FROM tasks
   WHERE organization = 'addresscafe-cartwheel'
     AND is_Deleted != 'true'
     AND ext_id LIKE 'RM%' 
  AND to_timestamp(planned_start_date/1000) at time zone 'Asia/Riyadh' between (@{{:Date Range.START}}::timestamp at time zone 'Asia/Riyadh') and (@{{:Date Range.END}}::timestamp at time zone 'Asia/Riyadh' + interval '1 day'  - interval '1 second')),
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
   WHERE fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t) ),
     submissions AS
  (SELECT fs.user_id,
          parent_nugget_id,
          fs.form_id,
          fs.sno,
          fs.response_id,
          left(al.audit_location, 4) AS store_id,
         
          fs.submit_date,
         fs.started_at,
          (fr.response ->> 'auditStatus') AS status,
          (fr.response ->> 'auditScore')::numeric AS actual_score,
          (fr.response ->> 'auditMaxScore')::numeric AS max_score
   FROM form_submissions fs
   JOIN form_responses fr ON fr.form_submit_id = fs.id
   JOIN audit_locations al ON fs.response_id = al.response_id
   WHERE fr.question_id = 'formAuditResults'
     AND fs.organization = 'addresscafe-cartwheel'
     AND fs.parent_nugget_id IN
       (SELECT id
        FROM t)
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            9,
            10,fr.response,fs.submit_date,fs.started_at),
			 assignees AS (
    SELECT DISTINCT ON (t.id)
        t.id AS task_knid,
        ud.first_name,
        ud.uuid AS user_id
    FROM t 
    JOIN analytics_requests ar ON t.id = ar.nugget_id
    JOIN user_details ud ON ar.user_id = ud.uuid
    ORDER BY t.id, ar.updated_at DESC
)
SELECT 
    
    
    assignees.first_name AS "RM",
    split_part(t.title, ' ', 2) AS "DM", 
    
    'RM' AS manager_designation,  
    'OER' AS checklist,
    submissions.store_id,
    TO_CHAR(DATE_TRUNC('Month', TO_TIMESTAMP(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'), 'YYYY-MM') AS MONTH,
    CASE
        WHEN EXTRACT('day' FROM TO_TIMESTAMP(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh') > 27 
        THEN TO_TIMESTAMP(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh' + INTERVAL '1 day'
        ELSE TO_TIMESTAMP(planned_start_date/1000) AT TIME ZONE 'Asia/Riyadh'
    END AS task_start,
    TO_TIMESTAMP(deadline/1000) AT TIME ZONE 'Asia/Riyadh' AS due_date,
    MIN(
        CASE
            WHEN submissions.submit_date IS NOT NULL THEN 'Completed'
            ELSE 'Incomplete'
        END
    ) AS task_status,
    MAX(
        CASE
            WHEN submissions.submit_date IS NOT NULL THEN 1
            ELSE 0
        END
    ) AS comp_task_count,
    submitter.first_name || ' ' || submitter.last_name AS task_done_by,
	 AVG(submissions.submit_date - TO_TIMESTAMP(submissions.started_at)) AS avg_completion_time,
	 submissions.submit_date,
	 submissions.started_at,
    MIN(submissions.submit_date) AS task_done_on,
    AVG(submissions.actual_score) AS avg_actual_score,
    AVG(submissions.max_score) AS max_score,
    AVG(
        CASE
            WHEN submissions.max_score != 0 THEN submissions.actual_score * 100 / submissions.max_score
            ELSE NULL
        END
    ) AS avg_score_pct,
    t.id AS task_knid,
    t.details->0->'value'->>'formId' AS checklist_knid,
    assignees.user_id AS manager_knid,  
    submitter.uuid AS doer_knid,
    submissions.response_id AS submission_knid
FROM t
LEFT OUTER JOIN submissions ON submissions.parent_nugget_id = t.id
LEFT OUTER JOIN user_details submitter ON submissions.user_id = submitter.uuid
LEFT OUTER JOIN assignees ON assignees.task_knid = t.id


WHERE assignees.user_id IN (
    SELECT rm_knid
    FROM store_map
    JOIN location_acl ON LEFT(location_acl.job_location, 4) = store_map.store_id
)
GROUP BY 
    assignees.first_name, 
	submitter.first_name,
	submitter.last_name,
	submitter.uuid,
	submissions.response_id,
    split_part(t.title, ' ', 2),
    submissions.store_id,
    MONTH,
    task_start,
    due_date,
    t.id,
    checklist_knid,
    assignees.user_id,
	submissions.submit_date,
	 submissions.started_at
ORDER BY task_start DESC, assignees.first_name, task_knid)"QueryTable 1"
```

---
