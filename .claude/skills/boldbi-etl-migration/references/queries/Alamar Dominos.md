# Alamar Dominos

> Auto-generated on 2026-03-04 08:13

**Total queries:** 34

---

## Alamar DM Tasks from Postgres_DM Task Status.sql

**Tables referenced:** Postgres, acl, dm, dm_groups, location_acl, rm, rm_groups, store_map, stores, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar DM Tasks from Postgres
-- Dashboard: DM Task Status
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:57:09
-- ============================================================

with location_acl as (SELECT DISTINCT job_location
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE))),
			stores AS
  (SELECT *
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'AlaPtr-antenna'),
     dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
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
   stores.last_name as store_name,
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
  group by 1, 2, 3, 4, 5),
   store_map as (SELECT acl.*,
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
         1)
SELECT distinct on ("dominos_task_status_table"."task_knid")
		"store_map"."country" AS "country",
		"store_map"."region" AS "region",
		"store_map"."city" AS "city",
		CAST("store_map"."dm_name" AS VARCHAR) AS "dm_name",
		CAST("store_map"."rm_name" AS VARCHAR) AS "rm_name",
		CAST("dominos_task_status_table"."manager_designation" AS VARCHAR) AS "manager_designation",
		CAST("dominos_task_status_table"."store_id" AS VARCHAR) AS "store_id",
		CAST("store_map"."store_name" AS VARCHAR) AS "store_name",
		CAST("dominos_task_status_table"."Checklist" AS VARCHAR) AS "checklist",
		CAST("dominos_task_status_table"."month" AS VARCHAR) AS "month",
		case when extract('day' from "dominos_task_status_table"."task_start")>27 then "dominos_task_status_table"."task_start" + interval '1 day' else "dominos_task_status_table"."task_start" end AS "task_start",
		"dominos_task_status_table"."due_date" AS "due_date",
		CAST("dominos_task_status_table"."task_status" AS VARCHAR) AS "task_status",
		CASE WHEN task_status='Completed' THEN 1 ELSE 0 END AS "comp_task_count",
		CAST("dominos_task_status_table"."task_done_by" AS VARCHAR) AS "task_done_by",
		"dominos_task_status_table"."task_done_on" AS "task_done_on",
		"dominos_task_status_table"."avg_actual_score" AS "avg_actual_score",
		"dominos_task_status_table"."max_score" AS "max_score",
		"dominos_task_status_table"."avg_score_pct" AS "avg_score_pct",
		"dominos_task_status_table"."task_knid" AS "task_knid",
		CAST("dominos_task_status_table"."checklist_knid" AS VARCHAR) AS "checklist_knid",
		CAST("dominos_task_status_table"."manager_knid" AS VARCHAR) AS "manager_knid",
		"dominos_task_status_table"."doer_knid" AS "doer_knid",
		"dominos_task_status_table"."submission_knid" AS "submission_knid"
FROM "public"."dominos_task_status_table" AS "dominos_task_status_table"
left outer join store_map on "dominos_task_status_table"."store_id" = store_map.store_id
join location_acl on location_acl.job_location = store_map.store_id
where "dominos_task_status_table"."task_id" ilike '%-DM-202%'
order by "dominos_task_status_table"."task_knid"
```

---

## Alamar Dom Logbook - Banking Log_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Banking Log
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:09
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvUu7re7uidrjOdPSQ_'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       max(case when dolb."Question" = 'Banking Status' then dolb."Response" else null end) as "Banking Status",
	   max(case when dolb."Question" = 'Days of banking hold' then dolb."Response"::numeric else null end) as "Days of Banking Hold",
	   max(case when dolb."Question" = 'Amount' then dolb."Response"::numeric else null end) as "Amount",
	   max(case when dolb."Question" = 'Reason' then dolb."Response" else null end) as "Reason"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
where dolb."Question" in ('Banking Status', 'Amount', 'Days of banking hold', 'Reason')
GROUP BY 1,
2,
3,
4,
5,
6,
7
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Cash Log_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Cash Log
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:11
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nw-1ocA75tkcXEvInfD'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Parent Question" as "Type",
	   max(case when dolb."Question" = 'Physical' then dolb."Response"::numeric else null end) as "Physical",
	   max(case when dolb."Question" = 'System' then dolb."Response"::numeric else null end) as "System"
FROM location_acl
JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
and dolb."Parent Question" in ('Cash in Safe', 'Expense Voucher', 'Till Money')
GROUP BY 1,
2,
3,
4,
5,
6,
7,
8
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Closing Assets_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Closing Assets
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:13
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nw-1ocA75tkcXEvInfD'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Section No",
       dolb."Question No",
       dolb."Parent Question",
       dolb."Question",
       dolb."Row No",
       dolb."Response"::numeric,
       dolb."Section Response"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
where dolb."Parent Question" in ('Car', 'Bike', 'Delivery Bag', 'Helmet', 'Table', 'Chair', 'PathOne Mobiles')
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Closing_Store Log Book.sql

**Tables referenced:** dolb, dominos_ops_logbook, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Closing
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:15
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nw-1ocA75tkcXEvInfD'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
   fd.q_type  as "Question Type",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15, 16)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Section No",
       dolb."Question No",
       dolb."Parent Question",
       dolb."Question",
       dolb."Row No",
       dolb."Response",
       dolb."Section Response",
	   dolb2."Response" as "Comments"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID" and dolb."Question Type" in ('multiple_choice', 'checkboxes')
left join dominos_ops_logbook dolb2 on dolb."Submission KNID" = dolb2."Submission KNID" and dolb."Question No"/10000 = dolb2."Question No"/10000 and dolb2."Question" = 'Comments'
			where dolb."Question No" != 0
			and right(dolb."Question No"::varchar, 1) = '0'
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Eqpt Temperature Log_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Eqpt Temperature Log
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:15
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvUuNKmTuxKupPhhK8e'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       max (case when dolb."Question" = 'Walk-In Cooler' then dolb."Response" else null end) as "Walk-In Cooler",
	   max (case when dolb."Question" = 'Makeline Cabinet' then dolb."Response" else null end) as "Makeline Cabinet",
	   max (case when dolb."Question" = 'Makeline Bin - Right' then dolb."Response" else null end) as "Makeline Bin - Right",
	   max (case when dolb."Question" = 'Makeline Bin - Centre' then dolb."Response" else null end) as "Makeline Bin - Centre",
	   max (case when dolb."Question" = 'Makeline Bin - Left' then dolb."Response" else null end) as "Makeline Bin - Left",
	   max (case when dolb."Question" = 'Beverage Cooler' then dolb."Response" else null end) as "Beverage Cooler"       
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
GROUP BY 1,2, 3, 4, 5, 6, 7

ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Food Costs_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Food Costs
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:11
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nvv0UcaVSUnrAJ-EoYu'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       case when dolb."Parent Question" = 'Last Day Food Cost' then 'Yday'
	   when dolb."Parent Question" = 'MTD Food Cost' then 'MTD'
	   else null end as "Category",
       max(case when dolb."Question" = 'Ideal' then dolb."Response"::numeric else null end) as "Ideal Cost",
	   max(case when dolb."Question" = 'Actual' then dolb."Response"::numeric else null end) as "Actual Cost"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
and dolb."Parent Question" in ('Last Day Food Cost', 'MTD Food Cost')
GROUP BY 1,
2,
3,
4,
5,
6,
7,
8
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - OOS Ingredients_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - OOS Ingredients
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:10
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvkceB5KojWhn_qnWOU'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
	   dolb."Parent Question",
	   dolb."Row No",
	   max(case when dolb."Question" ilike 'Name%' then dolb."Response" else null end) as "Ingredient",
	   max(case when dolb."Question" ilike 'Quantity%' then dolb."Response"::numeric else null end) as "Qty"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
where dolb."Parent Question" = 'List of Out of Stock Ingredients'
GROUP BY 1,
2,
3,
4,
5,
6,
7,
8,
9
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Opening Assets_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Opening Assets
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:13
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvvNBgKJI5nmfm9mdiX'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Section No",
       dolb."Question No",
       dolb."Parent Question",
       dolb."Question",
       dolb."Row No",
       dolb."Response"::numeric,
       dolb."Section Response"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
WHERE dolb."Parent Question" in ('Car', 'Bike', 'Delivery Bag', 'Helmet', 'Table', 'Chair', 'PathOne Mobiles')
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Opening_Store Log Book.sql

**Tables referenced:** dolb, dominos_ops_logbook, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Opening
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:16
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvvNBgKJI5nmfm9mdiX'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
   fd.q_type as "Question Type",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15, 16)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Section No",
       dolb."Question No",
       dolb."Parent Question",
       dolb."Question",
       dolb."Row No",
       dolb."Response",
       dolb."Section Response",
	   dolb2."Response" as "Comments"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID" and dolb."Question Type" in ('multiple_choice', 'checkboxes')
left join dominos_ops_logbook dolb2 on dolb."Submission KNID" = dolb2."Submission KNID" and dolb."Question No"/10000 = dolb2."Question No"/10000 and dolb2."Question" = 'Comments'
			where dolb."Question No" != 0
			and right(dolb."Question No"::varchar, 1) = '0'
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Performance Metrics_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Performance Metrics
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:09
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nvv0UcaVSUnrAJ-EoYu'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Parent Question" as "Metric",
       max(case when dolb."Question" = 'Yesterday' then dolb."Response"::numeric else null end) as "Yday",
	   max(case when dolb."Question" = 'MTD' then dolb."Response"::numeric else null end) as "MTD"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
and dolb."Parent Question" in ('Delivery - Bad Orders', 'Carry Out - Bad Orders', 'Delivery - Void Orders', 'Carry Out - Void Orders', 'Load Time', 'Out the Door', 'Single Run')
GROUP BY 1,
2,
3,
4,
5,
6,
7,
8
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Product Temperature Log_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Product Temperature Log
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:14
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-NvUvR_RGE2B4x8ou6Ul'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
	   dolb."Row No",
       max (case when dolb."Question" = 'Name of the Product' then dolb."Response" else null end) as "Product",
	   max (case when dolb."Question" = 'Temperature' then dolb."Response" else null end) as "Temperature"   
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
GROUP BY 1,2, 3, 4, 5, 6, 7, 8

ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dom Logbook - Sales_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dom Logbook - Sales
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:12
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-Nvv0UcaVSUnrAJ-EoYu'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
      WHERE (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Alamar Dominos Ops Log Book.Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Riyadh', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
	   max(case when dolb."Parent Question" = 'Daily Sales' and dolb."Question" = 'Yesterday - Actual' then dolb."Response"::numeric else null end) as "Yday Actual Sales",
	   max(case when dolb."Parent Question" = 'Daily Sales' and dolb."Question" = 'Yesterday - Target' then dolb."Response"::numeric else null end) as "Yday Target Sales",
	   max(case when dolb."Parent Question" = 'Daily Sales' and dolb."Question" = 'LW Same Day - Actual' then dolb."Response"::numeric else null end) as "LW Actual Sales",
	   max(case when dolb."Parent Question" = 'Daily Sales' and dolb."Question" = 'LY Same Day - Actual' then dolb."Response"::numeric else null end) as "LY Actual Sales",
	   max(case when dolb."Parent Question" = 'MTD Sales' and dolb."Question" = 'Actual' then dolb."Response"::numeric else null end) as "MTD Actual Sales",
	   max(case when dolb."Parent Question" = 'MTD Sales' and dolb."Question" = 'Target' then dolb."Response"::numeric else null end) as "MTD Target Sales",
	   max(case when dolb."Parent Question" = 'MTD Sales' and dolb."Question" = 'LY Same Day' then dolb."Response"::numeric else null end) as "MTD LY Sales",
	   max(case when dolb."Parent Question" = 'Daily Orders' and dolb."Question" = 'Yesterday - Actual' then dolb."Response"::numeric else null end) as "Yday Actual Orders",
	   max(case when dolb."Parent Question" = 'Daily Orders' and dolb."Question" = 'Yesterday - Target' then dolb."Response"::numeric else null end) as "Yday Target Orders",
	   max(case when dolb."Parent Question" = 'Daily Orders' and dolb."Question" = 'LW Same Day - Actual' then dolb."Response"::numeric else null end) as "LW Actual Orders",
	   max(case when dolb."Parent Question" = 'Daily Orders' and dolb."Question" = 'LY Same Day - Actual' then dolb."Response"::numeric else null end) as "LY Actual Orders",
	   max(case when dolb."Parent Question" = 'MTD Orders' and dolb."Question" = 'Actual' then dolb."Response"::numeric else null end) as "MTD Actual Orders",
	   max(case when dolb."Parent Question" = 'MTD Orders' and dolb."Question" = 'Target' then dolb."Response"::numeric else null end) as "MTD Target Orders",
	   max(case when dolb."Parent Question" = 'MTD Orders' and dolb."Question" = 'LY Same Day' then dolb."Response"::numeric else null end) as "MTD LY Orders",
	   max(case when dolb."Parent Question" = 'MTD ATP' and dolb."Question" = 'Actual' then dolb."Response"::numeric else null end) as "MTD Actual ATP",
	   max(case when dolb."Parent Question" = 'MTD ATP' and dolb."Question" = 'Target' then dolb."Response"::numeric else null end) as "MTD Target ATP",
	   max(case when dolb."Parent Question" = 'MTD ATP' and dolb."Question" = 'LY Same Day' then dolb."Response"::numeric else null end) as "MTD LY ATP"
	   FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
and dolb."Parent Question" in ('Daily Sales', 'Daily Orders', 'MTD Sales', 'MTD Orders', 'MTD ATP')
GROUP BY 1,
2,
3,
4,
5,
6,
7
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Dominos KSA Maintenance_KSA - Mnt Requests.sql

**Tables referenced:** division_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dominos KSA Maintenance
-- Dashboard: KSA - Mnt Requests
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:53
-- ============================================================

with division_acl as (SELECT DISTINCT division
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE)))
			SELECT
		"alamar_dominos_ksa_maintenance_requests_table"."sno" AS "Ticket No",
		"alamar_dominos_ksa_maintenance_requests_table"."country" AS "Country",
		"alamar_dominos_ksa_maintenance_requests_table"."region" AS "Region",
		"alamar_dominos_ksa_maintenance_requests_table"."city" AS "City",
		CAST("alamar_dominos_ksa_maintenance_requests_table"."requester" AS VARCHAR) AS "Requester",
		"alamar_dominos_ksa_maintenance_requests_table"."requester_id" AS "Requester ID",
		CAST("alamar_dominos_ksa_maintenance_requests_table"."issue" AS VARCHAR) AS "Issues",
		CAST((case when "alamar_dominos_ksa_maintenance_requests_table"."current_status" is null then 'Rework'
			  when "alamar_dominos_ksa_maintenance_requests_table"."current_status" = 'Action Completed' then 'Actioned'
			  when "alamar_dominos_ksa_maintenance_requests_table"."current_status" = 'Request Raised' then 'Pending'
			  else "alamar_dominos_ksa_maintenance_requests_table"."current_status" end) AS VARCHAR) AS "Current Status",
		"alamar_dominos_ksa_maintenance_requests_table"."cost" as "Cost",
		CAST("alamar_dominos_ksa_maintenance_requests_table"."all_tasks_completed" AS VARCHAR) AS "Were All Tasks Completed?",
		"alamar_dominos_ksa_maintenance_requests_table"."requested_at" AS "Requested At",
		"alamar_dominos_ksa_maintenance_requests_table"."mnt_responded_at" AS "Responded At",
		"alamar_dominos_ksa_maintenance_requests_table"."store_acknowledged_at" AS "Acknowledged At"
FROM "public"."alamar_dominos_ksa_maintenance_requests_table" AS "alamar_dominos_ksa_maintenance_requests_table"
join division_acl on division_acl.division = "alamar_dominos_ksa_maintenance_requests_table"."region"
where "alamar_dominos_ksa_maintenance_requests_table"."region" ilike 'KSA%'
```

---

## Alamar Dominos LP Audit Details_LP Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, forms, location_acl, nuggets, organizations, stores, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dominos LP Audit Details
-- Dashboard: LP Audits
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:58:04
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
   WHERE id = 'AlaPtr-antenna'),
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
     AND organization ILIKE 'AlaPtr-antenna'),
     forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'AlaPtr-antenna'
   AND cms.audit_type = 'Loss Prevention'
   JOIN td ON td.organization = cms.organization_id
   WHERE cms.audit_submitted_at + td.diff BETWEEN @{{:Alamar Dominos LP Audit Summary.Date Range.START}}::timestamp AND @{{:Alamar Dominos LP Audit Summary.Date Range.END}}::timestamp
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

## Alamar Dominos LP Audit Summary_LP Audits.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, forms, location_acl, nuggets, organizations, stores, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dominos LP Audit Summary
-- Dashboard: LP Audits
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:58:05
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
   WHERE id = 'AlaPtr-antenna'),
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
     AND organization ILIKE 'AlaPtr-antenna'),
	 forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'AlaPtr-antenna'
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

## Alamar Dominos Loss Prevention Follow Ups_LP Audit Follow Ups.sql

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
-- Data Source: Alamar Dominos Loss Prevention Follow Ups
-- Dashboard: LP Audit Follow Ups
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:58:03
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
     AND organization ILIKE 'AlaPtr-antenna'),
forms AS
  (SELECT n.id,
          cms.audit_submission_knid AS response_id
   FROM checkpoint_master_sheet_table cms
   JOIN nuggets n ON cms.audit_main_theme = n.title
   AND n.classification_type = 'form'
   AND n.organization = 'AlaPtr-antenna'
   AND cms.audit_type = 'Loss Prevention'
   WHERE cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   and cms.store_id in (select job_location from location_acl)
   GROUP BY 1,
            2),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'AlaPtr-antenna'
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
     AND organization_id = 'AlaPtr-antenna'
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
   WHERE organization_id = 'AlaPtr-antenna'
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

## Alamar Dominos Maintenance Requests_Maintenance Requests.sql

**Tables referenced:** alamar_dominos_maintenance_requests_table, completed_status, costs, form_responses, form_submissions, issue_list, issues, issues_Expanded, issues_q, jsonb_each, nuggets, question_definitions, user_acl, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dominos Maintenance Requests
-- Dashboard: Maintenance Requests
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:57:01
-- ============================================================

WITH user_acl AS
  (SELECT uuid,
                   organization
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
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
                  WHERE ug2.user_id =@{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))
  and phone_number not ilike '+9111%'),
issue_list AS
  (SELECT issues.sno AS "Ticket No",
          CASE
              WHEN reporter.division::text ~~* 'KSA%'::text THEN 'KSA'::character varying
              WHEN reporter.division::text ~~* 'PK%'::text THEN 'Pakistan'::character varying
              ELSE reporter.division
          END AS "Country",
          reporter.division AS "Region",
          reporter.sub_division AS "City",
   issues.location as "Location",
   issues.severity as "Severity",
          reporter.first_name||'  '||reporter.last_name AS "Requester",
          reporter.identifier AS "Requested ID",
          reporter.uuid AS "Requester UUID",
          replace(issues.category_name, ' Maintenance', '') AS "Request Type",
          CASE
              WHEN issues.status = 'open' THEN 'Pending'
              ELSE 'Store Acknowledged'
          END AS "Current Status",
          to_timestamp(issues.created_at::bigint/1000) AT TIME ZONE 'Asia/Riyadh' AS "Requested At",
                                                                    to_timestamp(issues.closed_at::bigint/1000) AT TIME ZONE 'Asia/Riyadh' AS "Responded At",
                                                                                                                             to_timestamp(issues.closed_at::bigint/1000) AT TIME ZONE 'Asia/Riyadh' AS "Acknowledged At",
                                                                                                                                                                                      issues.id AS issue_knid,
                                                                                                                                                                                      issues.category_id AS issue_category_knid
   FROM issues
   LEFT OUTER JOIN user_details reporter ON issues.author = reporter.uuid
   LEFT OUTER JOIN user_details resolver ON issues.closed_by = resolver.uuid
   WHERE issues.organization = 'AlaPtr-antenna'
     AND issues.is_deleted != 'true' ),
     issues_q AS
  (SELECT nugget_id,
          def.key AS qid
   FROM question_definitions qds
   JOIN nuggets n ON qds.nugget_id = n.id
    CROSS JOIN jsonb_each(definition) AS def
      WHERE n.title ILIKE 'Issue Creation Form%'
     AND n.organization = 'AlaPtr-antenna'
     AND def.value->>'question' ILIKE '%Issue%'
   GROUP BY 1,
            2),
     issues_expanded AS
  (SELECT issues.id AS issue_knid,
          jsonb_array_elements_text(fr.response->'selected') AS "Issues"
   FROM issues
   JOIN form_submissions fs ON issues.open_form_response_id = fs.response_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN issues_q ON fr.question_id = issues_q.qid),
     cost_q AS
  (SELECT nugget_id,
          def.key AS qid
   FROM question_definitions qds
   JOIN nuggets n ON qds.nugget_id = n.id
   CROSS JOIN jsonb_each(definition) AS def
   WHERE n.title ILIKE 'Issue Closure Form%'
     AND n.organization = 'AlaPtr-antenna'
     AND def.value->>'question' ILIKE 'Cost%'
   GROUP BY 1,
            2),
     costs AS
  (SELECT issues.id AS issue_knid,
          CASE
              WHEN fr.response->>0 ~ '^[-+]?\d+(\.\d+)?$' THEN (fr.response->>0)::numeric
              ELSE NULL
          END AS "Cost"
   FROM issues
   JOIN form_submissions fs ON issues.close_form_response_id = fs.response_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN issues_q ON fr.question_id = issues_q.qid),
     completed_q AS
  (SELECT nugget_id,
          def.key AS qid
   FROM question_definitions qds
   JOIN nuggets n ON qds.nugget_id = n.id
   CROSS JOIN jsonb_each(definition) AS def
   WHERE n.title ILIKE 'Issue Closure Form%'
     AND n.organization = 'AlaPtr-antenna'
     AND def.value->>'question' ILIKE '%completed?'
   GROUP BY 1,
            2),
     completed_status AS
  (SELECT issues.id AS issue_knid,
          fr.response->'selected'->>0 AS "Were All Tasks Completed"
   FROM issues
   JOIN form_submissions fs ON issues.close_form_response_id = fs.response_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   JOIN issues_q ON fr.question_id = issues_q.qid)
select requests.*
FROM user_acl
join (select *, null as "Location", null as "Severity",NULL AS "issue_knid" from alamar_dominos_maintenance_requests_table requests
	  union SELECT issue_list."Ticket No",
       issue_list."Country",
       issue_list."Region",
       issue_list."City",
	  
       issue_list."Requester",
       issue_list."Requested ID",
       issue_list."Requester UUID",
       issue_list."Request Type",
       issues_expanded."Issues",
       issue_list."Current Status",
       costs."Cost",
       completed_status."Were All Tasks Completed",
       issue_list."Requested At",
       issue_list."Responded At",
       issue_list."Acknowledged At",
	  issue_list."Location",
	  issue_list."Severity",
	  issue_list.issue_knid
FROM issue_list
LEFT OUTER JOIN issues_Expanded ON issue_list.issue_knid = issues_expanded.issue_knid
LEFT OUTER JOIN costs ON issue_list.issue_knid = costs.issue_knid
LEFT OUTER JOIN completed_status ON issue_list.issue_knid = completed_Status.issue_knid
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
	  18
         Having "Country" not ilike 'KNOW'
	AND "Request Type" NOT ILIKE '%IT%') requests on user_acl.uuid = requests."Requester UUID"
```

---

## Alamar Dominos Ops Log Book_Store Log Book.sql

**Tables referenced:** dolb, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar Dominos Ops Log Book
-- Dashboard: Store Log Book
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:16
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
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
               AND ug1.is_active = TRUE))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id in ('-Nw-1ocA75tkcXEvInfD',
                '-NvvNBgKJI5nmfm9mdiX',
                '-Nvv0UcaVSUnrAJ-EoYu',
                '-NvkceB5KojWhn_qnWOU',
                '-NvUvR_RGE2B4x8ou6Ul',
                '-NvUuNKmTuxKupPhhK8e',
                '-NvUu7re7uidrjOdPSQ_')), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT forms.organization,
                                                                  nugget_id AS form_knid,
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
                                                                  question AS parent_question,
                                                                  question_type AS parent_q_type,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT qd.organization,
                                                                                                                       nugget_id AS form_knid,
                                                                                                                       form_name,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question AS parent_question,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
                                                                                    qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT forms.organization,
                                                                                                        nugget_id AS form_knid,
                                                                                                        form_name,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question AS parent_question,
                                                                                                        question_type AS parent_q_type,
                                                                                                        def.key AS qid,
                                                                                                        def.value->>'question_type' AS q_type,
                                                                                                                    (def.value->>'question') AS question
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
                                                                                    fs AS
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   where (submit_date at time zone 'Asia/Riyadh')::date = (@{{:Date.START}})::date
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                LOCATION,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             LOCATION,
             sno,
             submit_Date AT TIME ZONE 'Asia/Riyadh' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                    dolb AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Store ID",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS "Response",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS "Section Response",
          user_id AS "User KNID",
          fd.form_knid AS "Form KNID",
          fr.response_id AS "Submission KNID"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fd.form_knid = fr.form_id
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
            15)
SELECT dolb."Organization",
       dolb."Form KNID",
       dolb."Form Name",
       dolb."Submission KNID",
       dolb."Submission No",
       dolb."Submitted At",
       dolb1."Response" AS "Store ID",
       dolb."Section No",
       dolb."Question No",
       dolb."Parent Question",
       dolb."Question",
       dolb."Row No",
       dolb."Response",
       dolb."Section Response"
FROM location_acl
LEFT JOIN dolb dolb1 ON location_acl.job_location = dolb1."Response"
AND dolb1."Question No" = 10000
LEFT JOIN dolb ON dolb."Submission KNID" = dolb1."Submission KNID"
ORDER BY 1,
         2,
         3,
         4,
         6,
         7,
         8,
         9
```

---

## Alamar Maintenance Tasks Status_KSA - Mnt Requests.sql

**Tables referenced:** analytics_requests, form_responses, form_submissions, location_acl, n, nuggets, question_definitions, stores, submissions, task_location_questions, task_locations, tasks, tasks_issues_progress, user_details, user_groups

**Columns needing snake_case conversion:**

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `isFormSubmitted` -> `is_form_submitted` (alias: `is_form_submitted AS "isFormSubmitted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `resolvedAt` -> `resolved_at` (alias: `resolved_at AS "resolvedAt"`)


**Original Query:**

```sql
-- Data Source: Alamar Maintenance Tasks Status
-- Dashboard: KSA - Mnt Requests
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:59
-- ============================================================

with location_acl as (SELECT DISTINCT job_location
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE))),
			stores AS
  (SELECT identifier AS store_id,
          last_name AS store_name,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE designation ILIKE 'Store%'
     AND organization ILIKE 'AlaPtr%' ),
     n AS
  ( SELECT *
   FROM nuggets
   WHERE classification_type = 'form'
     AND title ILIKE 'Maintenance Checklist%'
     AND (is_deleted != 'true'
          OR is_deleted = 'false') ),
     task_location_questions AS
  ( SELECT DISTINCT ON (nugget_id) nugget_id,
                       question_id
   FROM n
   JOIN question_definitions qd ON n.id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY nugget_id,
            sqno::numeric ),
     task_locations AS
  ( SELECT nugget_id AS form_id,
           fs.response_id,
           fr.response ->> 'name' AS task_location
   FROM task_location_questions tlq
   JOIN form_submissions fs ON tlq.nugget_id = fs.form_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND tlq.question_id = fr.question_id
   WHERE fs.organization = 'AlaPtr-antenna' ),
     submissions AS
  ( SELECT fs.user_id,
           fs.form_id,
           fs.sno,
           fs.response_id,
           al.task_location AS store_id,
           (fs.submit_date AT TIME ZONE 'Asia/Riyadh')::date AS submit_date
   FROM form_submissions fs
   JOIN form_responses fr ON fr.form_submit_id = fs.id
   JOIN task_locations al ON fs.response_id = al.response_id
   WHERE fs.organization = 'AlaPtr-antenna'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6 ),
     tasks AS
  ( SELECT DISTINCT on(task_knid) n1.id AS task_knid,
                    substring(n1.title, position('@' IN n1.title)+2, 5) AS store_id, --this includes tasks of the format xyz @ store_id
 t.details->0->'value'->>'name' AS checklist,
                         t.details->0->'value'->>'formId' AS form_knid,
                                                 (to_timestamp((n1.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Riyadh')::date AS planned_start,
                                                 (to_timestamp((n1.details->>'deadline')::bigint/1000) AT TIME ZONE 'Asia/Riyadh')::date AS deadline,
                                                 ar.user_id AS assignee,
                                                 CASE
                                                     WHEN n1.details->>'isFormSubmitted' = 'true' THEN 'Completed'
                                                     ELSE 'Incomplete'
                                                 END AS status,
                                                 CASE
                                                     WHEN n1.details->>'resolvedAt' IS NOT NULL THEN (to_timestamp((n1.details->>'resolvedAt')::bigint/1000))::date
                                                     ELSE NULL
                                                 END AS completed_on
   FROM tasks_issues_progress t
   JOIN nuggets n1 ON t.nugget_id = n1.id
   JOIN n ON t.details->0->'value'->>'formId' = n.id
   LEFT OUTER JOIN analytics_requests ar ON n1.id = ar.nugget_id
   WHERE t.details ->0->> 'type' = 'form_link'
     AND n1.organization = 'AlaPtr-antenna'
     AND ar.event_id = 1
     AND n1.is_deleted != 'true'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            ar.updated_at
   HAVING left(substring(n1.title, position('@' IN n1.title)+2, 5), 1) IN ('4',
                                                                           '5',
                                                                           '6')--this includes tasks which are just of the format xyz @ store id where store id begins with 4, 5, 6

   ORDER BY task_knid,
            ar.updated_at )
SELECT DISTINCT ON (task_knid) CASE
                                   WHEN stores.region ILIKE 'KSA%' THEN 'KSA'
                                   WHEN stores.region ILIKE 'PK %' THEN 'Pakistan'
                                   ELSE stores.region
                               END AS "Country",
                   stores.region AS "Region",
                   ud.designation AS "Assignee Designation",
                   ud.first_name||' '||ud.last_name AS "Assignee Name",
                   tasks.store_id AS "Store ID",
                   tasks.planned_start AS "Task Start",
                   tasks.deadline AS "Due Date",
                   min(CASE
                           WHEN submissions.submit_date IS NOT NULL THEN 'Completed'
                           ELSE 'Incomplete'
                       END) AS "Task Status",
                   submitter.first_name||' '||submitter.last_name AS "Task Done By",
                   min(submissions.submit_date) AS "Task Done On",
                   submissions.sno AS "Submission No",
                   tasks.task_knid AS "Task KNID",
                   tasks.form_knid AS "Checklist KNID",
                   tasks.assignee AS "Assignee KNID",
                   submitter.uuid AS "Doer KNID",
                   submissions.response_id AS "Submission KNID"
FROM tasks
LEFT OUTER JOIN submissions ON tasks.form_knid = submissions.form_id
AND tasks.store_id = submissions.store_id
AND submissions.submit_date BETWEEN tasks.planned_start AND tasks.deadline
LEFT OUTER JOIN stores ON tasks.store_id = stores.store_id
LEFT OUTER JOIN user_details ud ON tasks.assignee = ud.uuid
LEFT OUTER JOIN user_details submitter ON submissions.user_id = submitter.uuid
join location_acl on location_acl.job_location = tasks.store_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         9,
         11,
         12,
         13,
         14,
         15,
         16
ORDER BY 12,
         1,
         2,
         5,
         8,
         4,
         3
```

---

## Alamar Maintenance Tasks Status_Scheduled PM Tasks.sql

**Tables referenced:** analytics_requests, form_responses, form_submissions, location_acl, n, nuggets, question_definitions, stores, submissions, task_location_questions, task_locations, tasks, tasks_issues_progress, user_details, user_groups

**Columns needing snake_case conversion:**

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `isFormSubmitted` -> `is_form_submitted` (alias: `is_form_submitted AS "isFormSubmitted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `resolvedAt` -> `resolved_at` (alias: `resolved_at AS "resolvedAt"`)


**Original Query:**

```sql
-- Data Source: Alamar Maintenance Tasks Status
-- Dashboard: Scheduled PM Tasks
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:59:59
-- ============================================================

with location_acl as (SELECT DISTINCT job_location
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE))),
			stores AS
  (SELECT identifier AS store_id,
          last_name AS store_name,
          division AS region,
          sub_division AS city
   FROM user_details
   WHERE designation ILIKE 'Store%'
     AND organization ILIKE 'AlaPtr%' ),
     n AS
  ( SELECT *
   FROM nuggets
   WHERE classification_type = 'form'
     AND title ILIKE 'Maintenance Checklist%'
     AND (is_deleted != 'true'
          OR is_deleted = 'false') ),
     task_location_questions AS
  ( SELECT DISTINCT ON (nugget_id) nugget_id,
                       question_id
   FROM n
   JOIN question_definitions qd ON n.id = qd.nugget_id
   WHERE qd.question_type = 'location'
   ORDER BY nugget_id,
            sqno::numeric ),
     task_locations AS
  ( SELECT nugget_id AS form_id,
           fs.response_id,
           fr.response ->> 'name' AS task_location
   FROM task_location_questions tlq
   JOIN form_submissions fs ON tlq.nugget_id = fs.form_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND tlq.question_id = fr.question_id
   WHERE fs.organization = 'AlaPtr-antenna' ),
     submissions AS
  ( SELECT fs.user_id,
           fs.form_id,
           fs.sno,
           fs.response_id,
           al.task_location AS store_id,
           (fs.submit_date AT TIME ZONE 'Asia/Riyadh')::date AS submit_date
   FROM form_submissions fs
   JOIN form_responses fr ON fr.form_submit_id = fs.id
   JOIN task_locations al ON fs.response_id = al.response_id
   WHERE fs.organization = 'AlaPtr-antenna'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6 ),
     tasks AS
  ( SELECT DISTINCT on(task_knid) n1.id AS task_knid,
                    substring(n1.title, position('@' IN n1.title)+2, 5) AS store_id, --this includes tasks of the format xyz @ store_id
 t.details->0->'value'->>'name' AS checklist,
                         t.details->0->'value'->>'formId' AS form_knid,
                                                 (to_timestamp((n1.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Riyadh')::date AS planned_start,
                                                 (to_timestamp((n1.details->>'deadline')::bigint/1000) AT TIME ZONE 'Asia/Riyadh')::date AS deadline,
                                                 ar.user_id AS assignee,
                                                 CASE
                                                     WHEN n1.details->>'isFormSubmitted' = 'true' THEN 'Completed'
                                                     ELSE 'Incomplete'
                                                 END AS status,
                                                 CASE
                                                     WHEN n1.details->>'resolvedAt' IS NOT NULL THEN (to_timestamp((n1.details->>'resolvedAt')::bigint/1000))::date
                                                     ELSE NULL
                                                 END AS completed_on
   FROM tasks_issues_progress t
   JOIN nuggets n1 ON t.nugget_id = n1.id
   JOIN n ON t.details->0->'value'->>'formId' = n.id
   LEFT OUTER JOIN analytics_requests ar ON n1.id = ar.nugget_id
   WHERE t.details ->0->> 'type' = 'form_link'
     AND n1.organization = 'AlaPtr-antenna'
     AND ar.event_id = 1
     AND n1.is_deleted != 'true'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            ar.updated_at
   HAVING left(substring(n1.title, position('@' IN n1.title)+2, 5), 1) IN ('4',
                                                                           '5',
                                                                           '6')--this includes tasks which are just of the format xyz @ store id where store id begins with 4, 5, 6

   ORDER BY task_knid,
            ar.updated_at )
SELECT DISTINCT ON (task_knid) CASE
                                   WHEN stores.region ILIKE 'KSA%' THEN 'KSA'
                                   WHEN stores.region ILIKE 'PK %' THEN 'Pakistan'
                                   ELSE stores.region
                               END AS "Country",
                   stores.region AS "Region",
                   ud.designation AS "Assignee Designation",
                   ud.first_name||' '||ud.last_name AS "Assignee Name",
                   tasks.store_id AS "Store ID",
                   tasks.planned_start AS "Task Start",
                   tasks.deadline AS "Due Date",
                   min(CASE
                           WHEN submissions.submit_date IS NOT NULL THEN 'Completed'
                           ELSE 'Incomplete'
                       END) AS "Task Status",
                   submitter.first_name||' '||submitter.last_name AS "Task Done By",
                   min(submissions.submit_date) AS "Task Done On",
                   submissions.sno AS "Submission No",
                   tasks.task_knid AS "Task KNID",
                   tasks.form_knid AS "Checklist KNID",
                   tasks.assignee AS "Assignee KNID",
                   submitter.uuid AS "Doer KNID",
                   submissions.response_id AS "Submission KNID"
FROM tasks
LEFT OUTER JOIN submissions ON tasks.form_knid = submissions.form_id
AND tasks.store_id = submissions.store_id
AND submissions.submit_date BETWEEN tasks.planned_start AND tasks.deadline
LEFT OUTER JOIN stores ON tasks.store_id = stores.store_id
LEFT OUTER JOIN user_details ud ON tasks.assignee = ud.uuid
LEFT OUTER JOIN user_details submitter ON submissions.user_id = submitter.uuid
join location_acl on location_acl.job_location = tasks.store_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         9,
         11,
         12,
         13,
         14,
         15,
         16
ORDER BY 12,
         1,
         2,
         5,
         8,
         4,
         3
```

---

## Alamar RM Tasks from Postgres_RM Task Status.sql

**Tables referenced:** Postgres, acl, dm, dm_groups, location_acl, rm, rm_groups, store_map, stores, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Alamar RM Tasks from Postgres
-- Dashboard: RM Task Status
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:57:09
-- ============================================================

with location_acl as (SELECT DISTINCT job_location
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE))),
			stores AS
  (SELECT *
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'AlaPtr-antenna'),
     dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
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
   stores.last_name as store_name,
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
  group by 1, 2, 3, 4, 5),
   
   store_map as (SELECT acl.*,
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
         1)
SELECT distinct on ("dominos_task_status_table"."task_knid")
		"store_map"."country" AS "country",
		"store_map"."region" AS "region",
		"store_map"."city" AS "city",
		CAST("store_map"."dm_name" AS VARCHAR) AS "dm_name",
		CAST("store_map"."rm_name" AS VARCHAR) AS "rm_name",
		CAST("dominos_task_status_table"."manager_designation" AS VARCHAR) AS "manager_designation",
		CAST("dominos_task_status_table"."store_id" AS VARCHAR) AS "store_id",
		CAST("store_map"."store_name" AS VARCHAR) AS "store_name",
		CAST("dominos_task_status_table"."Checklist" AS VARCHAR) AS "checklist",
		CAST("dominos_task_status_table"."month" AS VARCHAR) AS "month",
		case when extract('day' from "dominos_task_status_table"."task_start")>27 then "dominos_task_status_table"."task_start" + interval '1 day' else "dominos_task_status_table"."task_start" end AS "task_start",
		"dominos_task_status_table"."due_date" AS "due_date",
		CAST("dominos_task_status_table"."task_status" AS VARCHAR) AS "task_status",
		CASE WHEN task_status='Completed' THEN 1 ELSE 0 END AS "comp_task_count",
		CAST("dominos_task_status_table"."task_done_by" AS VARCHAR) AS "task_done_by",
		"dominos_task_status_table"."task_done_on" AS "task_done_on",
		"dominos_task_status_table"."avg_actual_score" AS "avg_actual_score",
		"dominos_task_status_table"."max_score" AS "max_score",
		"dominos_task_status_table"."avg_score_pct" AS "avg_score_pct",
		"dominos_task_status_table"."task_knid" AS "task_knid",
		CAST("dominos_task_status_table"."checklist_knid" AS VARCHAR) AS "checklist_knid",
		CAST("dominos_task_status_table"."manager_knid" AS VARCHAR) AS "manager_knid",
		"dominos_task_status_table"."doer_knid" AS "doer_knid",
		"dominos_task_status_table"."submission_knid" AS "submission_knid"
FROM "public"."dominos_task_status_table" AS "dominos_task_status_table"
left outer join store_map on "dominos_task_status_table"."store_id" = store_map.store_id
join location_acl on location_acl.job_location = store_map.store_id
where "dominos_task_status_table"."task_id" ilike '%-RM-%'
order by "dominos_task_status_table"."task_knid"
```

---

## DM Tasks Top Missed Questions_DM Task Status.sql

**Tables referenced:** completed_submissions, cs.submit_date, dm_tasks, dominos_task_status_table, form_responses, form_submissions, location_acl, parent_questions, question_aggregated, question_definitions, question_definitions_full, question_detail, question_performance, ranked_questions, recent_submissions, responses_with_scores, stores, user_details, user_groups

**Columns needing snake_case conversion:**

- `parentQuestionId` -> `parent_question_id` (alias: `parent_question_id AS "parentQuestionId"`)


**Original Query:**

```sql
-- Data Source: DM Tasks Top Missed Questions
-- Dashboard: DM Task Status
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:52:39
-- ============================================================

-- ============================================================================
-- DM TASK STATUS - TOP MISSED QUESTIONS (UNPIVOTED DATA)
-- Use this data source for Top Missed Questions tables in DM Dashboard
-- ============================================================================
-- Audit Types: SPOT CHECK, OPENING, CLOSING, RUSH, GAME DAY, OER, 
--              FOOD SAFETY, OSA TRADITIONAL, OSA NON-TRADITIONAL, MOC
-- 
-- PERFORMANCE OPTIMIZATIONS:
-- - Last 30 days data only (adjustable)
-- - Pre-filter form submissions by date
-- - Only scoreable questions considered
-- - No Year-over-Year comparison
-- ============================================================================

WITH location_acl AS (
    SELECT DISTINCT job_location
    FROM user_details
    WHERE organization = @{{:OrganizationParameter}}
    AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
            SELECT DISTINCT user_id
            FROM user_groups ug1
            WHERE ug1.group_id IN (
                SELECT group_id FROM user_groups ug2
                WHERE ug2.user_id = @{{:UuidParameter}}
                AND ug2.has_access = TRUE
            )
            AND ug1.is_active = TRUE
        )
    )
),

stores AS (
    SELECT 
        identifier AS store_id,
        last_name AS store_name,
        CASE
            WHEN division ILIKE 'KSA%' THEN 'KSA'
            WHEN division ILIKE 'PK %' THEN 'Pakistan'
            ELSE division
        END AS country,
        division AS region,
        sub_division AS city
    FROM user_details
    WHERE job_type ILIKE 'Store%'
    AND organization ILIKE 'AlaPtr-antenna'
),


-- Pre-filter form submissions for last 30 days (better performance)
recent_submissions AS (
    SELECT id, response_id, form_id, submit_date
    FROM form_submissions
    WHERE submit_date >= CURRENT_DATE - INTERVAL '30 days'
),

-- Get completed DM tasks with normalized audit type (last 30 days)
dm_tasks AS (
    SELECT 
        t.submission_knid,
        t.store_id,
        t.due_date,
        t.checklist_knid,
        CASE 
            WHEN t."Checklist" ILIKE '%FOOD SAFETY%' THEN 'FOOD SAFETY'
            WHEN t."Checklist" ILIKE '%OER%' THEN 'OER'
            WHEN t."Checklist" ILIKE '%OPERATIONS%' AND t."Checklist" ILIKE '%NON-TRADITIONAL%' THEN 'OSA NON-TRADITIONAL'
            WHEN t."Checklist" ILIKE '%OPERATIONS%' AND t."Checklist" ILIKE '%TRADITIONAL%' THEN 'OSA TRADITIONAL'
            ELSE t."Checklist"
        END AS audit_type
    FROM dominos_task_status_table t
    WHERE t.task_status = 'Completed'
    AND t.submission_knid IS NOT NULL
    AND t.task_id ILIKE '%-DM-202%'
    AND t.due_date >= CURRENT_DATE - INTERVAL '30 days'
),

-- Link tasks to form submissions with ACL filter
completed_submissions AS (
    SELECT 
        dt.audit_type,
        dt.store_id,
        dt.due_date,
        fs.id AS submission_id,
        fs.form_id,
        fs.submit_date,
        s.country,
        s.region,
        s.city
    FROM dm_tasks dt
    INNER JOIN recent_submissions fs ON dt.submission_knid = fs.response_id
    INNER JOIN stores s ON dt.store_id = s.store_id
    INNER JOIN location_acl acl ON s.store_id = acl.job_location
),

-- Get question definitions with max scores and criteria grouping
question_definitions_full AS (
    SELECT 
        qd.nugget_id AS form_id,
        qd.question_id AS qid,
        qd.question,
        qd.question_type,
        qd.definition->>'parentQuestionId' AS parent_question_id,
        MAX(COALESCE(NULLIF(opt.value->>'score', '')::numeric, 0)) AS max_score
    FROM question_definitions qd,
    LATERAL jsonb_array_elements(qd.definition->'options') AS opt
    WHERE qd.nugget_id IN (SELECT DISTINCT form_id FROM completed_submissions)
    AND qd.question_type NOT IN ('section', 'table', 'nested', 'upload_image', 'upload_file', 'upload_video', 'upload_mixed', 'signature', 'location')
    AND qd.definition->'options' IS NOT NULL
    AND opt.value->>'score' IS NOT NULL  -- Only consider options with scores
    GROUP BY qd.nugget_id, qd.question_id, qd.question, qd.question_type, qd.definition->>'parentQuestionId'
    HAVING MAX(COALESCE(NULLIF(opt.value->>'score', '')::numeric, 0)) > 0
),

-- Get parent questions for criteria grouping
parent_questions AS (
    SELECT DISTINCT
        pq.nugget_id AS form_id,
        pq.question_id,
        pq.question AS criteria_name
    FROM question_definitions qd
    INNER JOIN question_definitions pq 
        ON pq.question_id = qd.definition->>'parentQuestionId'
        AND pq.nugget_id = qd.nugget_id
    WHERE qd.nugget_id IN (SELECT DISTINCT form_id FROM completed_submissions)
    AND qd.definition->>'parentQuestionId' IS NOT NULL
),

-- Map questions to criteria
question_detail AS (
    SELECT 
        qd.form_id,
        qd.qid,
        qd.question,
        qd.max_score,
        COALESCE(pq.criteria_name, 'General') AS criteria
    FROM question_definitions_full qd
    LEFT JOIN parent_questions pq 
        ON pq.question_id = qd.parent_question_id 
        AND pq.form_id = qd.form_id
),

-- Get responses with scores (only for scoreable questions)
responses_with_scores AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        COALESCE(NULLIF(fr.response->>'score', '')::numeric, 0) AS score_earned
    FROM form_responses fr
    WHERE fr.form_submit_id IN (SELECT submission_id FROM completed_submissions)
    AND fr.question_type NOT IN ('section', 'table', 'nested')
    AND fr.response->>'score' IS NOT NULL
    AND fr.response->>'score' != ''
),

-- Combine submission details with question performance
question_performance AS (
    SELECT 
        cs.audit_type,
        cs.country,
        cs.region,
        cs.city,
        cs.submission_id,
        cs.submit_date,
        EXTRACT(YEAR FROM cs.submit_date)::INTEGER AS audit_year,
        EXTRACT(QUARTER FROM cs.submit_date)::INTEGER AS audit_quarter,
        'Q' || EXTRACT(QUARTER FROM cs.submit_date) || ' ' || EXTRACT(YEAR FROM cs.submit_date) AS quarter_label,
        qd.qid,
        qd.question,
        qd.criteria,
        qd.max_score,
        rws.score_earned,
        qd.max_score - rws.score_earned AS points_lost,
        CASE WHEN rws.score_earned = 0 THEN 1 ELSE 0 END AS is_missed
    FROM completed_submissions cs
    INNER JOIN responses_with_scores rws ON rws.submission_id = cs.submission_id
    INNER JOIN question_detail qd ON qd.qid = rws.qid AND qd.form_id = cs.form_id
),

-- Aggregate and rank questions per checklist
question_aggregated AS (
    SELECT 
        audit_type,
        criteria,
        qid,
        LEFT(question, 100) AS question_text,
        max_score,
        COUNT(*) AS times_asked,
        ROUND(AVG(score_earned), 2) AS avg_score_earned,
        ROUND(AVG(points_lost), 2) AS avg_points_lost,
        SUM(is_missed) AS times_missed,
        ROUND(100.0 * SUM(is_missed) / COUNT(*), 2) AS missed_percentage
    FROM question_performance
    GROUP BY audit_type, criteria, qid, LEFT(question, 100), max_score
    HAVING COUNT(*) >= 5  -- Minimum sample size
),
-- Rank within each audit_type
ranked_questions AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY audit_type ORDER BY missed_percentage DESC) AS rank_in_checklist
    FROM question_aggregated
)

-- Output: Filter in BoldBI using [rank_in_checklist] <= 5
SELECT 
    audit_type,
    criteria,
    qid,
    question_text,
    max_score,
    times_asked,
    avg_score_earned,
    avg_points_lost,
    times_missed,
    missed_percentage,
    rank_in_checklist
FROM ranked_questions
WHERE rank_in_checklist <= 5
ORDER BY audit_type, rank_in_checklist
```

---

## Dough_Production_Dough Production Record.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Dough_Production
-- Dashboard: Dough Production Record
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:56:59
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
               AND ug1.is_active = TRUE))),td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'AlaPtr-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = '-OJrAawzpMkdV0ImEGug'
     AND organization = 'AlaPtr-antenna'
    and is_deleted = false
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
    fs as (
        select * from _fs
        where submit_date between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
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
          1 AS rn
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
                rn
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
             base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
   location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd 
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
/*location_response as (
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date
         -- lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   --join location_response lr
   --on lr.form_submit_id = fr.form_submit_id
   JOIN td ON fr.organization = td.organization
   join form_submissions fs on fs.form_id = fd.form_knid
   join location_acl on fs.location = location_acl.job_location
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
            13
   ORDER BY 1,
            2,
            3)
SELECT 
sno,
max(response) filter (where question = 'Market') as market,
max(response) filter (where question = 'Batch Number #') as batch_number,
max(response) filter (where question = 'Flour (kg) (As per the Mixer Size & formula in the Market)') as flour_kg,
max(response) filter (where question = 'Yeast (kg) (As per the formula in the Market)') as yeast_kg,
max(response) filter (where question = 'Slurry Water (kg) (Slurry water should 4 times of the weight of Yeast.)') as slurry_water,
max(response) filter (where question = 'Premix (kg) (As per the formula in the Market)') as premix_kg,
max(response) filter (where question = 'Oil (kg) (As per the formula in the Market)') as oil_kg
FROM raw
group by 1
```

---

## FSA Internal Audit - Unpivoted_FSA Internal Audit.sql

**Tables referenced:** CURRENT_DATE, form_responses, form_submissions, nuggets, organizations, parent_questions, quarter_range, question_definitions, question_definitions_full, question_detail, question_performance, responses_with_scores, s.submit_date, store_cities, submissions, td, user_details

**Columns needing snake_case conversion:**

- `parentQuestionId` -> `parent_question_id` (alias: `parent_question_id AS "parentQuestionId"`)


**Original Query:**

```sql
-- Data Source: FSA Internal Audit - Unpivoted
-- Dashboard: FSA Internal Audit
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:53:14
-- ============================================================

-- ============================================================================
-- FSA AUDIT - COMPREHENSIVE UNPIVOTED DATA
-- Use this ONE data source for:
--   1. Criteria Performance Chart (group by criteria)
--   2. Top Missed Questions Table (group by question)
-- ============================================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (SELECT organization FROM nuggets WHERE id = '-OFpARux3oJxjZP6FDWB')
),
quarter_range AS (
    SELECT 
        EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER AS current_year,
        EXTRACT(QUARTER FROM CURRENT_DATE)::INTEGER AS current_quarter,
        EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 year')::INTEGER AS prev_year
),
submissions AS (
    SELECT DISTINCT ON (fs.response_id)
        fs.id AS submission_id,
        fs.response_id,
        fs.submit_date + td.diff AS submit_date,
        fs.user_id,
        fs.location
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id = '-OFpARux3oJxjZP6FDWB'
    AND fs.user_id = '9yC6ibhL7hxjo3t1H4eUmM'
    ORDER BY fs.response_id, fs.id DESC
),
question_definitions_full AS (
    SELECT 
        qd.question_id AS qid,
        qd.question,
        qd.question_type,
        qd.definition->>'parentQuestionId' as parent_question_id,
        MAX(COALESCE((opt.value->>'score')::numeric, 0)) as max_score
    FROM question_definitions qd,
    LATERAL jsonb_array_elements(qd.definition->'options') AS opt
    WHERE qd.nugget_id = '-OFpARux3oJxjZP6FDWB'
    AND qd.question_type NOT IN ('section', 'table', 'nested')
    AND qd.definition->'options' IS NOT NULL
    GROUP BY qd.question_id, qd.question, qd.question_type, qd.definition->>'parentQuestionId'
),
parent_questions AS (
    SELECT DISTINCT
        pq.question_id,
        pq.question as group_name
    FROM question_definitions qd
    INNER JOIN question_definitions pq 
        ON pq.question_id = qd.definition->>'parentQuestionId'
    WHERE qd.nugget_id = '-OFpARux3oJxjZP6FDWB'
    AND qd.definition->>'parentQuestionId' IS NOT NULL
),
responses_with_scores AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        COALESCE((fr.response->>'score')::numeric, 0) AS score_earned
    FROM form_responses fr
    WHERE fr.form_submit_id IN (SELECT submission_id FROM submissions)
    AND fr.question_type NOT IN ('section', 'table', 'nested')
),
-- Get store city from user_details based on job_location
store_cities AS (
    SELECT DISTINCT ON (job_location)
        job_location,
        sub_division AS store_city
    FROM user_details
    WHERE job_type ILIKE '%Store%'
    AND organization = 'AlaPtr-antenna'
    ORDER BY job_location, identifier
),
-- Map questions to criteria using ACTUAL form groups (parent questions)
question_detail AS (
    SELECT 
        qd.qid,
        qd.question,
        qd.max_score,
        qd.parent_question_id,
        COALESCE(pq.group_name, 'Ungrouped') AS criteria,
        CASE COALESCE(pq.group_name, 'Ungrouped')
            WHEN 'Food Safety Risk Factors' THEN 1
            WHEN 'Cleanliness' THEN 2
            WHEN 'Maintenance and Facility' THEN 3
            WHEN 'Storage' THEN 4
            WHEN 'Knowledge and Compliance' THEN 5
            WHEN 'Critical Violations' THEN 6
            ELSE 7
        END AS criteria_sort_order
    FROM question_definitions_full qd
    LEFT JOIN parent_questions pq ON pq.question_id = qd.parent_question_id
    WHERE qd.max_score > 0  -- Only scoreable questions
),
-- Combine with submission details (FILTERED for year-over-year comparison)
question_performance AS (
    SELECT 
        s.response_id,
        s.submit_date,
        EXTRACT(YEAR FROM s.submit_date)::INTEGER AS audit_year,
        EXTRACT(QUARTER FROM s.submit_date)::INTEGER AS audit_quarter,
        'Q' || EXTRACT(QUARTER FROM s.submit_date) || ', ' || EXTRACT(YEAR FROM s.submit_date) AS quarter_label,
        sc.store_city,
        ud.sub_division AS auditor_region,
        qd.qid,
        qd.question,
        qd.criteria,
        qd.criteria_sort_order,
        qd.max_score,
        rws.score_earned,
        qd.max_score - rws.score_earned AS points_lost,
        CASE WHEN rws.score_earned = 0 THEN 1 ELSE 0 END AS is_missed
    FROM submissions s
    CROSS JOIN quarter_range qr
    INNER JOIN responses_with_scores rws ON rws.submission_id = s.submission_id
    INNER JOIN question_detail qd ON qd.qid = rws.qid
    LEFT JOIN user_details ud ON s.user_id = ud.uuid
    LEFT JOIN store_cities sc ON s.location = sc.job_location
    WHERE qd.criteria != 'Ungrouped'  -- Exclude questions without a group
    -- YEAR-OVER-YEAR FILTER: Same quarter, current year vs previous year
    AND EXTRACT(QUARTER FROM s.submit_date)::INTEGER = qr.current_quarter
    AND (EXTRACT(YEAR FROM s.submit_date)::INTEGER = qr.current_year 
         OR EXTRACT(YEAR FROM s.submit_date)::INTEGER = qr.prev_year)
)
-- Output question-level data (aggregate in BoldBI widgets as needed)
SELECT 
    criteria,
    criteria_sort_order,
    qid,
    LEFT(question, 100) AS question_text,
    max_score,
    score_earned,
    points_lost,
    is_missed,
    audit_year,
    audit_quarter,
    quarter_label,
    store_city,
    auditor_region,
    response_id
FROM question_performance
ORDER BY criteria_sort_order, qid, audit_year, audit_quarter
```

---

## FSA Internal Audit_FSA Internal Audit.sql

**Tables referenced:** all_questions, dominos_task_status_table, form_responses, form_submissions, locations, nuggets, organizations, qd_logic, qd_logic_base, qd_logic_expanded, qd_main, question_definitions, response, responses_parsed, responses_with_scores, s.submit_date, store_cities, submission_scores, submissions, t.due_date, task_counts_per_city, td, total_stores_per_city, uae_stores, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: FSA Internal Audit
-- Dashboard: FSA Internal Audit
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:53:12
-- ============================================================

WITH td AS (
    SELECT 
        COALESCE(o.tzoffset, 0) as tzoffset,
        interval '1 min' * COALESCE(o.tzoffset, 0) AS diff
    FROM organizations o
    WHERE o.id IN (
        SELECT organization FROM nuggets WHERE id = '-OFpARux3oJxjZP6FDWB'
    )
),
-- Get all questions with their scoring information
qd_main AS (
    SELECT 
        question_id AS qid,
        question,
        question_type,
        sqno::integer AS sort_order,
        definition
    FROM question_definitions
    WHERE nugget_id = '-OFpARux3oJxjZP6FDWB'
    AND question_type NOT IN ('table')
),
qd_logic_base AS (
    SELECT 
        nugget_id,
        sqno,
        definition
    FROM question_definitions
    WHERE nugget_id = '-OFpARux3oJxjZP6FDWB'
    AND definition -> 'logic' IS NOT NULL
),
qd_logic_expanded AS (
    SELECT 
        nugget_id,
        sqno,
        logic_element
    FROM qd_logic_base,
    LATERAL jsonb_array_elements(definition -> 'logic') AS logic_element
),
qd_logic AS (
    SELECT 
        qe.key AS qid,
        qe.value->>'question' AS question,
        qe.value->>'question_type' AS question_type,
        sqno::integer * 10000 + (qe.value->>'order')::integer AS sort_order,
        qe.value AS definition
    FROM qd_logic_expanded qle,
    LATERAL jsonb_each(qle.logic_element -> 'questions') AS qe
),
all_questions AS (
    SELECT * FROM qd_main
    UNION
    SELECT * FROM qd_logic
),
-- Extract scoring options
question_options AS (
    SELECT 
        aq.qid,
        aq.question,
        opt.value->>'value' AS option_value,
        COALESCE((opt.value->>'score')::numeric, 0) AS score
    FROM all_questions aq,
    LATERAL jsonb_array_elements(aq.definition->'options') AS opt
    WHERE aq.definition->'options' IS NOT NULL
),
-- Get submissions by the specific auditor
submissions AS (
    SELECT DISTINCT ON (fs.response_id)
        fs.id AS submission_id,
        fs.response_id,
        fs.sno,
        fs.submit_date + td.diff AS submit_date,
        fs.user_id,
        fs.location,
        fs.organization
    FROM form_submissions fs
    CROSS JOIN td
    WHERE fs.form_id = '-OFpARux3oJxjZP6FDWB'
    AND fs.user_id = '9yC6ibhL7hxjo3t1H4eUmM'  -- Filter for specific auditor
    ORDER BY fs.response_id, fs.id DESC
),
-- Get all responses with parsed values
responses_parsed AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        CASE
            WHEN fr.question_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') 
                THEN fr.response -> 'selected' ->> 0
            WHEN fr.question_type IN ('checkboxes') 
                THEN array_to_string(ARRAY(
                    SELECT jsonb_array_elements_text(fr.response->'selected')
                    UNION 
                    SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL 
                        THEN fr.response->>'otherText' END
                ), ', ')
            WHEN fr.question_type IN ('date', 'datetime') 
                THEN to_char(to_timestamp((fr.response::text::bigint)/1000), 'YYYY-MM-DD HH24:MI:SS')
            WHEN fr.question_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula') 
                THEN fr.response ->> 0
            WHEN fr.question_type IN ('upload_file', 'upload_image', 'upload_video', 'upload_mixed') 
                THEN COALESCE((fr.response)->0->>'response', fr.response::text)
            WHEN fr.question_type IN ('location', 'signature', 'division', 'sub_division') 
                THEN fr.response ->> 'name'
            WHEN fr.question_type = 'user'
                THEN fr.response::text
            ELSE fr.response::text
        END AS response_value
    FROM form_responses fr
    WHERE fr.form_submit_id IN (SELECT submission_id FROM submissions)
    AND fr.question_type NOT IN ('section', 'nested')
),
-- Extract scores directly from response JSON (scores are pre-calculated in mobile app)
responses_with_scores AS (
    SELECT 
        rp.submission_id,
        rp.qid,
        rp.response_value,
        COALESCE((fr.response->>'score')::numeric, 0) AS score_earned
    FROM responses_parsed rp
    INNER JOIN form_responses fr 
        ON fr.form_submit_id = rp.submission_id 
        AND fr.question_id = rp.qid
),
-- Calculate total scores per submission
submission_scores AS (
    SELECT 
        submission_id,
        SUM(score_earned) AS total_score
    FROM responses_with_scores
    GROUP BY submission_id
),
-- Get store city from user_details based on job_location matching the audited location
store_cities AS (
    SELECT DISTINCT ON (job_location)
        job_location,
        sub_division AS store_city,
        division AS store_division
    FROM user_details
    WHERE job_type ILIKE '%Store%'
    AND organization = 'AlaPtr-antenna'
    ORDER BY job_location, identifier
),
-- Count total stores per city (for pending calculation)
total_stores_per_city AS (
    SELECT 
        sub_division AS store_city,
        COUNT(DISTINCT identifier) AS total_store_count
    FROM user_details
    WHERE job_type ILIKE '%Store%'
    AND organization = 'AlaPtr-antenna'
    AND division ILIKE '%United Arab Emirates%'
    GROUP BY sub_division
),
-- Task counts per city from dominos_task_status_table (for pending calculation)
uae_stores AS (
    SELECT identifier as store_id, sub_division as city
    FROM user_details
    WHERE job_type ILIKE '%Store%'
    AND organization = 'AlaPtr-antenna'
    AND division ILIKE '%United Arab Emirates%'
),
task_counts_per_city AS (
    SELECT 
        us.city AS store_city,
        EXTRACT(QUARTER FROM t.due_date)::INTEGER AS task_quarter,
        EXTRACT(YEAR FROM t.due_date)::INTEGER AS task_year,
        COUNT(DISTINCT t.task_knid) AS tasks_assigned,
        COUNT(DISTINCT CASE WHEN t.task_status = 'Completed' THEN t.task_knid END) AS tasks_completed,
        COUNT(DISTINCT t.task_knid) - COUNT(DISTINCT CASE WHEN t.task_status = 'Completed' THEN t.task_knid END) AS tasks_pending
    FROM dominos_task_status_table t
    INNER JOIN uae_stores us ON t.store_id = us.store_id
    WHERE t."Checklist" ILIKE '%FOOD SAFETY%'
    GROUP BY us.city, EXTRACT(QUARTER FROM t.due_date), EXTRACT(YEAR FROM t.due_date)
)
-- Final query with all data
SELECT 
    -- Metadata
    s.response_id,
    s.sno AS submission_number,
    s.submit_date,
    s.location AS store_location,
    s.organization,
    
    -- User details (Auditor)
    ud.identifier AS auditor_id,
    CONCAT(ud.first_name, ' ', ud.last_name) AS auditor_name,
    ud.first_name AS auditor_first_name,
    ud.last_name AS auditor_last_name,
    ud.phone_number AS auditor_phone,
    ud.email AS auditor_email,
    ud.sub_division AS region,  -- This is the subdivision/region for UAE
    
    -- NEW: Additional auditor location fields
    ud.division AS auditor_division,
    ud.sub_division AS auditor_sub_division,
    ud.job_location AS auditor_job_location,
    
    -- Store/Location details
    l.location_name AS store_name,
    l.id AS store_id,
    sc.store_city,
    sc.store_division,
    tsc.total_store_count,  -- Total stores in this city (for pending calculation)
    tc.tasks_assigned,      -- Tasks assigned in this city for this quarter
    tc.tasks_completed,     -- Tasks completed in this city for this quarter
    tc.tasks_pending,       -- Pending tasks (assigned - completed)
    
    -- Date/Time fields
    DATE(s.submit_date) AS audit_date,
    EXTRACT(YEAR FROM s.submit_date)::INTEGER AS audit_year,
    EXTRACT(QUARTER FROM s.submit_date)::INTEGER AS audit_quarter,
    EXTRACT(MONTH FROM s.submit_date)::INTEGER AS audit_month,
    TO_CHAR(s.submit_date, 'YYYY-Q') AS year_quarter,
    TO_CHAR(s.submit_date, 'YYYY-MM') AS year_month,
    'Q' || EXTRACT(QUARTER FROM s.submit_date) || ' ' || EXTRACT(YEAR FROM s.submit_date) AS quarter_label,
    
    -- Scoring
    COALESCE(ss.total_score, 0) AS total_points_earned,
    150 AS total_possible_score,  -- As per dashboard
    ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) AS score_percentage,
    
    -- Risk Level Categorization
    CASE 
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 95 THEN '5 Star Low'
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 90 THEN '4 Star Medium-Low'
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 85 THEN '3 Star Medium'
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 80 THEN '2 Star Medium-High'
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 70 THEN '1 Star High'
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 60 THEN 'Re-audit'
        ELSE 'Critical'
    END AS risk_level,
    
    -- Risk Level Numeric (for sorting)
    CASE 
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 95 THEN 5
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 90 THEN 4
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 85 THEN 3
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 80 THEN 2
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 70 THEN 1
        WHEN ROUND((COALESCE(ss.total_score, 0) / 150.0) * 100, 2) >= 60 THEN 0
        ELSE -1
    END AS risk_level_numeric,
    
    -- Audit Status
    CASE 
        WHEN s.submit_date IS NOT NULL THEN 'Completed'
        ELSE 'Pending'
    END AS audit_status,
    
    -- All questions as individual columns

    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZC' THEN pr.response_value END) AS are_all_prepped_food_products_stored_in_separate_containers,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw8' THEN pr.response_value END) AS audited_store,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGy' THEN pr.response_value END) AS is_the_makeline_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8y' THEN pr.response_value END) AS additional_comments,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwD' THEN pr.response_value END) AS all_products_dated_as_per_dominos_shelflife_guide_and_produc,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw6' THEN pr.response_value END) AS audit_info,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xh' THEN pr.response_value END) AS is_the_makeline_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8f' THEN pr.response_value END) AS is_there_knowledge_of_the_health_of_food_handlers_and_their_,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8s' THEN pr.response_value END) AS all_practicable_measures_to_eradicate_and_prevent_the_harbor,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8g' THEN pr.response_value END) AS regulatory_or_local_health_inspections_knowledge_of_procedur,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwB' THEN pr.response_value END) AS food_safety_risk_factors,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdr' THEN pr.response_value END) AS calibrated_thermometers_in_use,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xi' THEN pr.response_value END) AS is_the_walkin_cooler_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8z' THEN pr.response_value END) AS additional_photographs,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8t' THEN pr.response_value END) AS maintain_the_food_premises_fixtures_fittings_and_equipment_t,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZD' THEN pr.response_value END) AS is_all_food_fully_thawed_prior_to_use,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGz' THEN pr.response_value END) AS is_the_walkin_cooler_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw9' THEN pr.response_value END) AS store_manager,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZE' THEN pr.response_value END) AS are_all_food_equipment_packaging_and_food_contact_items_stor,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwA' THEN pr.response_value END) AS franchisee_dco,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfds' THEN pr.response_value END) AS all_cooked_product_temperatures_165f_74c_or_above,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH-' THEN pr.response_value END) AS are_the_other_refrigeration_and_beverage_units_in_good_repai,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xf' THEN pr.response_value END) AS cleanliness,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8u' THEN pr.response_value END) AS ensure_the_public_is_adequately_protected_such_as_ceasing_op,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8h' THEN pr.response_value END) AS knowledge_of_employee_health_policy,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xj' THEN pr.response_value END) AS are_other_refrigeration_and_beverage_units_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xk' THEN pr.response_value END) AS are_the_freezer_units_clean,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdt' THEN pr.response_value END) AS are_all_refrigerated_products_held_at_41f_5c_or_lower,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8v' THEN pr.response_value END) AS maintain_the_integrity_of_product_quality_and_ensure_safety,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8i' THEN pr.response_value END) AS temperature_logs_are_available_and_complete_with_corrective_,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZF' THEN pr.response_value END) AS are_there_working_thermometers_in_the_walkin_cooler_makeline,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGw' THEN pr.response_value END) AS maintenance_and_facility,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH0' THEN pr.response_value END) AS are_the_freezer_units_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRP' THEN pr.response_value END) AS are_the_refrigeration_gaskets_maintained_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8j' THEN pr.response_value END) AS disease_control_and_emetic_event_kit_and_plan,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdu' THEN pr.response_value END) AS frozen_products_are_thawed_under_refrigeration,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZG' THEN pr.response_value END) AS are_chemicals_properly_labeled_and_are_sanitizer_and_deterge,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH1' THEN pr.response_value END) AS are_the_refrigeration_gaskets_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZA' THEN pr.response_value END) AS storage,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZH' THEN pr.response_value END) AS are_wiping_cloths_properly_stored_and_are_appropriate_test_s,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZK' THEN pr.response_value END) AS knowledge_and_compliance,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRQ' THEN pr.response_value END) AS are_the_oven_and_oven_hood_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH2' THEN pr.response_value END) AS is_the_oven_and_oven_hood_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8k' THEN pr.response_value END) AS ceramic_glass_or_glass_breakage_procedure_in_place,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdv' THEN pr.response_value END) AS are_all_food_products_fully_protected_from_crosscontaminatio,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZI' THEN pr.response_value END) AS are_personal_food_and_personal_items_stored_properly,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdw' THEN pr.response_value END) AS pest_control_services_completed_report_available_for_review_,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRR' THEN pr.response_value END) AS are_the_hot_rack_and_hot_holding_cabinets_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH3' THEN pr.response_value END) AS is_the_hot_holding_equipment_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8l' THEN pr.response_value END) AS sanitation_schedule_and_plan_in_place,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8q' THEN pr.response_value END) AS critical_violations,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH4' THEN pr.response_value END) AS is_the_hand_wash_sink_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8w' THEN pr.response_value END) AS additional_comments_2,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8m' THEN pr.response_value END) AS sds_available_for_all_chemicals_in_the_store,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRS' THEN pr.response_value END) AS are_the_hand_wash_sinks_clean_and_used_only_for_hand_washing,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZJ' THEN pr.response_value END) AS are_all_frozen_products_solid_to_the_touch,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdx' THEN pr.response_value END) AS no_evidence_of_pests,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8n' THEN pr.response_value END) AS food_safety_standards_or_reference_guide_available,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdy' THEN pr.response_value END) AS store_personnel_following_hair_and_hygiene_practices,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH5' THEN pr.response_value END) AS is_the_dishwashing_area_and_equipment_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRT' THEN pr.response_value END) AS is_the_dishwashing_area_clean,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdz' THEN pr.response_value END) AS are_all_hand_sinks_properly_stocked,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRU' THEN pr.response_value END) AS are_all_interior_trash_cans_and_the_dumpster_area_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH6' THEN pr.response_value END) AS are_all_interior_and_exterior_trash_cans_including_the_dumps,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8o' THEN pr.response_value END) AS allergen_policy_available,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRV' THEN pr.response_value END) AS are_the_floors_and_drains_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ-' THEN pr.response_value END) AS are_the_floors_and_drains_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8p' THEN pr.response_value END) AS liability_insurance,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe-' THEN pr.response_value END) AS are_hand_washing_and_sanitizing_practices_being_followed,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe0' THEN pr.response_value END) AS are_the_hot_bags_clean_and_wellmaintained,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRW' THEN pr.response_value END) AS are_the_walls_doors_and_baseboards_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ0' THEN pr.response_value END) AS are_the_walls_doors_and_baseboards_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRX' THEN pr.response_value END) AS are_the_ceiling_tiles_lights_and_light_covers_clean,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe1' THEN pr.response_value END) AS all_food_contact_surfaces_clean_and_sanitized,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ1' THEN pr.response_value END) AS are_the_ceiling_tiles_lights_and_light_covers_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe2' THEN pr.response_value END) AS all_foodcontact_surfaces_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRY' THEN pr.response_value END) AS is_the_storage_equipment_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ2' THEN pr.response_value END) AS is_the_storage_equipment_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRZ' THEN pr.response_value END) AS are_other_nonfood_contact_surfaces_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ3' THEN pr.response_value END) AS are_other_nonfood_contact_surfaces_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe3' THEN pr.response_value END) AS is_the_sanitizer_in_use_and_at_the_proper_concentration_or_t,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBR_' THEN pr.response_value END) AS is_the_dough_equipment_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ4' THEN pr.response_value END) AS is_the_dough_equipment_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xc' THEN pr.response_value END) AS is_the_current_food_safety_certification_available_as_requir,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xd' THEN pr.response_value END) AS are_all_products_purchased_from_approved_suppliers,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRa' THEN pr.response_value END) AS is_the_front_counter_clean,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ5' THEN pr.response_value END) AS is_the_front_counter_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ6' THEN pr.response_value END) AS are_the_restrooms_and_fixtures_in_good_repair,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGv' THEN pr.response_value END) AS are_the_restrooms_clean_and_sanitary,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xe' THEN pr.response_value END) AS eating_and_drinking_in_back_of_house,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ7' THEN pr.response_value END) AS no_temporary_repairs,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ8' THEN pr.response_value END) AS are_backflow_devices_and_air_breaksgaps_present,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ9' THEN pr.response_value END) AS are_the_cleaning_tools_and_equipment_in_good_repair_and_main,
    
    -- All scores as individual columns

    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZC' THEN pr.score_earned END) AS are_all_prepped_food_products_stored_in_separate_containers_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw8' THEN pr.score_earned END) AS audited_store_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGy' THEN pr.score_earned END) AS is_the_makeline_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8y' THEN pr.score_earned END) AS additional_comments_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwD' THEN pr.score_earned END) AS all_products_dated_as_per_dominos_shelflife_guide_and_produc_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw6' THEN pr.score_earned END) AS audit_info_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xh' THEN pr.score_earned END) AS is_the_makeline_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8f' THEN pr.score_earned END) AS is_there_knowledge_of_the_health_of_food_handlers_and_their__score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8s' THEN pr.score_earned END) AS all_practicable_measures_to_eradicate_and_prevent_the_harbor_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8g' THEN pr.score_earned END) AS regulatory_or_local_health_inspections_knowledge_of_procedur_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwB' THEN pr.score_earned END) AS food_safety_risk_factors_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdr' THEN pr.score_earned END) AS calibrated_thermometers_in_use_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xi' THEN pr.score_earned END) AS is_the_walkin_cooler_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8z' THEN pr.score_earned END) AS additional_photographs_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8t' THEN pr.score_earned END) AS maintain_the_food_premises_fixtures_fittings_and_equipment_t_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZD' THEN pr.score_earned END) AS is_all_food_fully_thawed_prior_to_use_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGz' THEN pr.score_earned END) AS is_the_walkin_cooler_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mw9' THEN pr.score_earned END) AS store_manager_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZE' THEN pr.score_earned END) AS are_all_food_equipment_packaging_and_food_contact_items_stor_score,
    MAX(CASE WHEN pr.qid = '-OFpARuyDWqWvWAi6mwA' THEN pr.score_earned END) AS franchisee_dco_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfds' THEN pr.score_earned END) AS all_cooked_product_temperatures_165f_74c_or_above_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH-' THEN pr.score_earned END) AS are_the_other_refrigeration_and_beverage_units_in_good_repai_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xf' THEN pr.score_earned END) AS cleanliness_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8u' THEN pr.score_earned END) AS ensure_the_public_is_adequately_protected_such_as_ceasing_op_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8h' THEN pr.score_earned END) AS knowledge_of_employee_health_policy_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xj' THEN pr.score_earned END) AS are_other_refrigeration_and_beverage_units_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xk' THEN pr.score_earned END) AS are_the_freezer_units_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdt' THEN pr.score_earned END) AS are_all_refrigerated_products_held_at_41f_5c_or_lower_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8v' THEN pr.score_earned END) AS maintain_the_integrity_of_product_quality_and_ensure_safety_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8i' THEN pr.score_earned END) AS temperature_logs_are_available_and_complete_with_corrective__score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZF' THEN pr.score_earned END) AS are_there_working_thermometers_in_the_walkin_cooler_makeline_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGw' THEN pr.score_earned END) AS maintenance_and_facility_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH0' THEN pr.score_earned END) AS are_the_freezer_units_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRP' THEN pr.score_earned END) AS are_the_refrigeration_gaskets_maintained_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8j' THEN pr.score_earned END) AS disease_control_and_emetic_event_kit_and_plan_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdu' THEN pr.score_earned END) AS frozen_products_are_thawed_under_refrigeration_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZG' THEN pr.score_earned END) AS are_chemicals_properly_labeled_and_are_sanitizer_and_deterge_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH1' THEN pr.score_earned END) AS are_the_refrigeration_gaskets_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZA' THEN pr.score_earned END) AS storage_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZH' THEN pr.score_earned END) AS are_wiping_cloths_properly_stored_and_are_appropriate_test_s_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZK' THEN pr.score_earned END) AS knowledge_and_compliance_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRQ' THEN pr.score_earned END) AS are_the_oven_and_oven_hood_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH2' THEN pr.score_earned END) AS is_the_oven_and_oven_hood_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8k' THEN pr.score_earned END) AS ceramic_glass_or_glass_breakage_procedure_in_place_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdv' THEN pr.score_earned END) AS are_all_food_products_fully_protected_from_crosscontaminatio_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZI' THEN pr.score_earned END) AS are_personal_food_and_personal_items_stored_properly_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdw' THEN pr.score_earned END) AS pest_control_services_completed_report_available_for_review__score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRR' THEN pr.score_earned END) AS are_the_hot_rack_and_hot_holding_cabinets_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH3' THEN pr.score_earned END) AS is_the_hot_holding_equipment_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8l' THEN pr.score_earned END) AS sanitation_schedule_and_plan_in_place_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8q' THEN pr.score_earned END) AS critical_violations_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH4' THEN pr.score_earned END) AS is_the_hand_wash_sink_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8w' THEN pr.score_earned END) AS additional_comments_2_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8m' THEN pr.score_earned END) AS sds_available_for_all_chemicals_in_the_store_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRS' THEN pr.score_earned END) AS are_the_hand_wash_sinks_clean_and_used_only_for_hand_washing_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZJ' THEN pr.score_earned END) AS are_all_frozen_products_solid_to_the_touch_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdx' THEN pr.score_earned END) AS no_evidence_of_pests_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8n' THEN pr.score_earned END) AS food_safety_standards_or_reference_guide_available_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdy' THEN pr.score_earned END) AS store_personnel_following_hair_and_hygiene_practices_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH5' THEN pr.score_earned END) AS is_the_dishwashing_area_and_equipment_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRT' THEN pr.score_earned END) AS is_the_dishwashing_area_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfdz' THEN pr.score_earned END) AS are_all_hand_sinks_properly_stocked_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRU' THEN pr.score_earned END) AS are_all_interior_trash_cans_and_the_dumpster_area_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKH6' THEN pr.score_earned END) AS are_all_interior_and_exterior_trash_cans_including_the_dumps_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8o' THEN pr.score_earned END) AS allergen_policy_available_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRV' THEN pr.score_earned END) AS are_the_floors_and_drains_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ-' THEN pr.score_earned END) AS are_the_floors_and_drains_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv3PueKOIVVyu8p' THEN pr.score_earned END) AS liability_insurance_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe-' THEN pr.score_earned END) AS are_hand_washing_and_sanitizing_practices_being_followed_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe0' THEN pr.score_earned END) AS are_the_hot_bags_clean_and_wellmaintained_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRW' THEN pr.score_earned END) AS are_the_walls_doors_and_baseboards_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ0' THEN pr.score_earned END) AS are_the_walls_doors_and_baseboards_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRX' THEN pr.score_earned END) AS are_the_ceiling_tiles_lights_and_light_covers_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe1' THEN pr.score_earned END) AS all_food_contact_surfaces_clean_and_sanitized_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ1' THEN pr.score_earned END) AS are_the_ceiling_tiles_lights_and_light_covers_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe2' THEN pr.score_earned END) AS all_foodcontact_surfaces_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRY' THEN pr.score_earned END) AS is_the_storage_equipment_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ2' THEN pr.score_earned END) AS is_the_storage_equipment_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRZ' THEN pr.score_earned END) AS are_other_nonfood_contact_surfaces_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ3' THEN pr.score_earned END) AS are_other_nonfood_contact_surfaces_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARuzOiMF8epCOfe3' THEN pr.score_earned END) AS is_the_sanitizer_in_use_and_at_the_proper_concentration_or_t_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBR_' THEN pr.score_earned END) AS is_the_dough_equipment_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ4' THEN pr.score_earned END) AS is_the_dough_equipment_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xc' THEN pr.score_earned END) AS is_the_current_food_safety_certification_available_as_requir_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xd' THEN pr.score_earned END) AS are_all_products_purchased_from_approved_suppliers_score,
    MAX(CASE WHEN pr.qid = '-OFpARv0O5JxaOPifBRa' THEN pr.score_earned END) AS is_the_front_counter_clean_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ5' THEN pr.score_earned END) AS is_the_front_counter_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ6' THEN pr.score_earned END) AS are_the_restrooms_and_fixtures_in_good_repair_score,
    MAX(CASE WHEN pr.qid = '-OFpARv1us09lKo9bKGv' THEN pr.score_earned END) AS are_the_restrooms_clean_and_sanitary_score,
    MAX(CASE WHEN pr.qid = '-OFpARv-2mlVjen-46Xe' THEN pr.score_earned END) AS eating_and_drinking_in_back_of_house_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ7' THEN pr.score_earned END) AS no_temporary_repairs_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ8' THEN pr.score_earned END) AS are_backflow_devices_and_air_breaksgaps_present_score,
    MAX(CASE WHEN pr.qid = '-OFpARv2NmxGOWdFILZ9' THEN pr.score_earned END) AS are_the_cleaning_tools_and_equipment_in_good_repair_and_main_score
    
FROM submissions s
LEFT JOIN responses_with_scores pr ON pr.submission_id = s.submission_id
LEFT JOIN submission_scores ss ON ss.submission_id = s.submission_id
LEFT JOIN user_details ud ON s.user_id = ud.uuid
LEFT JOIN locations l ON s.location = l.id
LEFT JOIN store_cities sc ON l.id = sc.job_location
LEFT JOIN total_stores_per_city tsc ON sc.store_city = tsc.store_city
LEFT JOIN task_counts_per_city tc ON sc.store_city = tc.store_city 
    AND EXTRACT(QUARTER FROM s.submit_date)::INTEGER = tc.task_quarter
    AND EXTRACT(YEAR FROM s.submit_date)::INTEGER = tc.task_year
GROUP BY 
    s.response_id, s.sno, s.submit_date, s.location, s.organization,
    ud.identifier, ud.first_name, ud.last_name, ud.phone_number, ud.email, ud.sub_division,
    ud.division, ud.job_location,
    l.location_name, l.id,
    sc.store_city, sc.store_division, tsc.total_store_count,
    tc.tasks_assigned, tc.tasks_completed, tc.tasks_pending,
    ss.total_score
ORDER BY s.submit_date DESC
```

---

## FSA Task Status_FSA Internal Audit.sql

**Tables referenced:** dm, dm_groups, dominos_task_status_table, rm, rm_groups, store_map, store_user_groups, stores, t.due_date, t.task_start, user_details, user_groups

**Original Query:**

```sql
-- Data Source: FSA Task Status
-- Dashboard: FSA Internal Audit
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:53:13
-- ============================================================

-- ============================================================================
-- FSA INTERNAL AUDIT - TASK STATUS DASHBOARD QUERY
-- Organization: AlaPtr-antenna
-- Filtered to: United Arab Emirates (UAE) only
-- Sub-divisions: Dubai, Abu Dhabi, Sharjah, Al Ain, Ajman, Ras Al Khaima, Fujairah, Umm Al Quwain
-- ============================================================================

WITH stores AS (
    SELECT 
        identifier AS store_id,
        last_name AS store_name,
        'United Arab Emirates' AS country,
        division AS region,
        sub_division AS city
    FROM user_details
    WHERE job_type ILIKE 'Store%'
    AND organization = 'AlaPtr-antenna'
    AND division ILIKE '%United Arab Emirates%'
),
dm AS (
    SELECT *
    FROM user_details
    WHERE designation IN ('DM', 'District Manager')
    AND organization = 'AlaPtr-antenna'
    AND is_active = true
),
rm AS (
    SELECT *
    FROM user_details
    WHERE designation IN ('RM', 'Regional Manager')
    AND organization = 'AlaPtr-antenna'
    AND is_active = true
),
dm_groups AS (
    SELECT dm.uuid, dm.first_name, dm.last_name, dm.identifier, ug.group_id
    FROM user_groups ug
    JOIN dm ON ug.user_id = dm.uuid AND ug.has_access = true
),
rm_groups AS (
    SELECT rm.uuid, rm.first_name, rm.last_name, rm.identifier, ug.group_id
    FROM user_groups ug
    JOIN rm ON ug.user_id = rm.uuid AND ug.has_access = true
),
store_user_groups AS (
    SELECT 
        s.store_id,
        s.store_name,
        s.country,
        s.region,
        s.city,
        ug.group_id
    FROM stores s
    LEFT JOIN user_details ud ON s.store_id = ud.identifier
    LEFT JOIN user_groups ug ON ud.uuid = ug.user_id AND ug.is_active = true
),
store_map AS (
    SELECT 
        sug.store_id,
        sug.store_name,
        sug.country,
        sug.region,
        sug.city,
        MAX(dm_groups.first_name || ' ' || dm_groups.last_name) AS dm_name,
        MAX(dm_groups.identifier) AS dm_identifier,
        MAX(rm_groups.first_name || ' ' || rm_groups.last_name) AS rm_name,
        MAX(rm_groups.identifier) AS rm_identifier
    FROM store_user_groups sug
    LEFT JOIN dm_groups ON sug.group_id = dm_groups.group_id
    LEFT JOIN rm_groups ON sug.group_id = rm_groups.group_id
    GROUP BY sug.store_id, sug.store_name, sug.country, sug.region, sug.city
)
SELECT DISTINCT ON (t.task_knid)
    t.task_knid,
    s.country,
    s.region,
    s.city,
    s.dm_name,
    s.rm_name,
    t.manager_designation,
    t.store_id,
    s.store_name,
    t."Checklist" AS checklist,
    t.month,
    CASE 
        WHEN EXTRACT('day' FROM t.task_start) > 27 
        THEN t.task_start + INTERVAL '1 day' 
        ELSE t.task_start 
    END AS task_start,
    t.due_date,
    t.task_status,
    CASE WHEN t.task_status = 'Completed' THEN 1 ELSE 0 END AS comp_task_count,
    t.task_done_by,
    t.task_done_on,
    t.avg_actual_score,
    t.max_score,
    t.avg_score_pct,
    t.checklist_knid,
    t.manager_knid,
    t.doer_knid,
    t.submission_knid,
    EXTRACT(QUARTER FROM t.due_date)::INTEGER AS quarter,
    EXTRACT(YEAR FROM t.due_date)::INTEGER AS year,
    'Q' || EXTRACT(QUARTER FROM t.due_date) || ' ' || EXTRACT(YEAR FROM t.due_date) AS quarter_label
FROM dominos_task_status_table t
INNER JOIN store_map s ON t.store_id = s.store_id
WHERE t."Checklist" ILIKE '%FOOD SAFETY%'
ORDER BY t.task_knid
```

---

## KSA Logbook_KSA Store Logbooks.sql

**Tables referenced:** acl, dm, dm_groups, form_compliance_v2, location_acl, organizations, rm, rm_groups, store_map, stores, user_details, user_groups

**Original Query:**

```sql
-- Data Source: KSA Logbook
-- Dashboard: KSA Store Logbooks
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:54:15
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
		"QueryTable 1"."region" AS "region",
		"QueryTable 1"."city" AS "city",
		"QueryTable 1"."dm_name" AS "dm_name"
FROM(with location_acl as (SELECT DISTINCT job_location
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
               WHERE ug2.user_id =@{{:UuidParameter}}
                 AND ug2.has_access = TRUE)
            AND ug1.is_active = TRUE))),
			stores AS
  (SELECT *
   FROM user_details
   WHERE job_type ILIKE 'Store%'
     AND organization ILIKE 'AlaPtr-antenna'),
     dm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('DM',
                         'District Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
     rm AS
  (SELECT *
   FROM user_details
   WHERE designation IN ('RM',
                         'Regional Manager')
     AND organization ILIKE 'AlaPtr-antenna'
  and is_active = 'true'),
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
   stores.last_name as store_name,
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
  group by 1, 2, 3, 4, 5),
   store_map as (SELECT acl.*,
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",
sm.region,sm.city,sm.dm_name
from form_compliance_v2 fc
left outer join store_map sm on fc."Location" = sm.store_id
join location_acl on location_acl.job_location = sm.store_id
where fc."Organization" =@{{:OrganizationParameter}}
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	AND "Location" NOT IN ('West Kootenay''s area', 'East Kootenay''s area', 'Alberta area')
	 and "Routine Name" ILIKE '%KSA%'
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## RM Tasks Top Missed Questions_RM Task Status.sql

**Tables referenced:** completed_submissions, cs.submit_date, dominos_task_status_table, form_responses, form_submissions, location_acl, parent_questions, question_aggregated, question_definitions, question_definitions_full, question_detail, question_performance, ranked_questions, recent_submissions, responses_with_scores, rm_tasks, stores, user_details, user_groups

**Columns needing snake_case conversion:**

- `parentQuestionId` -> `parent_question_id` (alias: `parent_question_id AS "parentQuestionId"`)


**Original Query:**

```sql
-- Data Source: RM Tasks Top Missed Questions
-- Dashboard: RM Task Status
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:52:39
-- ============================================================

-- ============================================================================
-- RM TASK STATUS - TOP MISSED QUESTIONS (UNPIVOTED DATA)
-- Use this data source for Top Missed Questions tables in RM Dashboard
-- ============================================================================
-- Audit Types: FOOD SAFETY, OER, OSA TRADITIONAL, OSA NON-TRADITIONAL
--
-- PERFORMANCE OPTIMIZATIONS:
-- - Last 30 days data only (adjustable)
-- - Pre-filter form submissions by date
-- - Only scoreable questions considered
-- - No Year-over-Year comparison
-- ============================================================================

WITH location_acl AS (
    SELECT DISTINCT job_location
    FROM user_details
    WHERE organization = @{{:OrganizationParameter}}
    AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
            SELECT DISTINCT user_id
            FROM user_groups ug1
            WHERE ug1.group_id IN (
                SELECT group_id FROM user_groups ug2
                WHERE ug2.user_id = @{{:UuidParameter}}
                AND ug2.has_access = TRUE
            )
            AND ug1.is_active = TRUE
        )
    )
),

stores AS (
    SELECT 
        identifier AS store_id,
        last_name AS store_name,
        CASE
            WHEN division ILIKE 'KSA%' THEN 'KSA'
            WHEN division ILIKE 'PK %' THEN 'Pakistan'
            ELSE division
        END AS country,
        division AS region,
        sub_division AS city
    FROM user_details
    WHERE job_type ILIKE 'Store%'
    AND organization ILIKE 'AlaPtr-antenna'
),

-- Pre-filter form submissions for last 30 days (better performance)
recent_submissions AS (
    SELECT id, response_id, form_id, submit_date
    FROM form_submissions
    WHERE submit_date >= CURRENT_DATE - INTERVAL '30 days'
),

-- Get completed RM tasks with normalized audit type (last 30 days)
rm_tasks AS (
    SELECT 
        t.submission_knid,
        t.store_id,
        t.due_date,
        t.checklist_knid,
        CASE 
            WHEN t."Checklist" ILIKE '%FOOD SAFETY%' THEN 'FOOD SAFETY'
            WHEN t."Checklist" ILIKE '%OER%' THEN 'OER'
            WHEN t."Checklist" ILIKE '%OPERATIONS%' AND t."Checklist" ILIKE '%NON-TRADITIONAL%' THEN 'OSA NON-TRADITIONAL'
            WHEN t."Checklist" ILIKE '%OPERATIONS%' AND t."Checklist" ILIKE '%TRADITIONAL%' THEN 'OSA TRADITIONAL'
            ELSE t."Checklist"
        END AS audit_type
    FROM dominos_task_status_table t
    WHERE t.task_status = 'Completed'
    AND t.submission_knid IS NOT NULL
    AND t.task_id ILIKE '%-RM-%'
    AND t.due_date >= CURRENT_DATE - INTERVAL '30 days'
),

-- Link tasks to form submissions with ACL filter
completed_submissions AS (
    SELECT 
        rt.audit_type,
        rt.store_id,
        rt.due_date,
        fs.id AS submission_id,
        fs.form_id,
        fs.submit_date,
        s.country,
        s.region,
        s.city
    FROM rm_tasks rt
    INNER JOIN recent_submissions fs ON rt.submission_knid = fs.response_id
    INNER JOIN stores s ON rt.store_id = s.store_id
    INNER JOIN location_acl acl ON s.store_id = acl.job_location
),

-- Get question definitions with max scores and criteria grouping
question_definitions_full AS (
    SELECT 
        qd.nugget_id AS form_id,
        qd.question_id AS qid,
        qd.question,
        qd.question_type,
        qd.definition->>'parentQuestionId' AS parent_question_id,
        MAX(COALESCE(NULLIF(opt.value->>'score', '')::numeric, 0)) AS max_score
    FROM question_definitions qd,
    LATERAL jsonb_array_elements(qd.definition->'options') AS opt
    WHERE qd.nugget_id IN (SELECT DISTINCT form_id FROM completed_submissions)
    AND qd.question_type NOT IN ('section', 'table', 'nested', 'upload_image', 'upload_file', 'upload_video', 'upload_mixed', 'signature', 'location')
    AND qd.definition->'options' IS NOT NULL
    AND opt.value->>'score' IS NOT NULL  -- Only consider options with scores
    GROUP BY qd.nugget_id, qd.question_id, qd.question, qd.question_type, qd.definition->>'parentQuestionId'
    HAVING MAX(COALESCE(NULLIF(opt.value->>'score', '')::numeric, 0)) > 0
),

-- Get parent questions for criteria grouping
parent_questions AS (
    SELECT DISTINCT
        pq.nugget_id AS form_id,
        pq.question_id,
        pq.question AS criteria_name
    FROM question_definitions qd
    INNER JOIN question_definitions pq 
        ON pq.question_id = qd.definition->>'parentQuestionId'
        AND pq.nugget_id = qd.nugget_id
    WHERE qd.nugget_id IN (SELECT DISTINCT form_id FROM completed_submissions)
    AND qd.definition->>'parentQuestionId' IS NOT NULL
),

-- Map questions to criteria
question_detail AS (
    SELECT 
        qd.form_id,
        qd.qid,
        qd.question,
        qd.max_score,
        COALESCE(pq.criteria_name, 'General') AS criteria
    FROM question_definitions_full qd
    LEFT JOIN parent_questions pq 
        ON pq.question_id = qd.parent_question_id 
        AND pq.form_id = qd.form_id
),

-- Get responses with scores (only for scoreable questions)
responses_with_scores AS (
    SELECT 
        fr.form_submit_id AS submission_id,
        fr.question_id AS qid,
        COALESCE(NULLIF(fr.response->>'score', '')::numeric, 0) AS score_earned
    FROM form_responses fr
    WHERE fr.form_submit_id IN (SELECT submission_id FROM completed_submissions)
    AND fr.question_type NOT IN ('section', 'table', 'nested')
    AND fr.response->>'score' IS NOT NULL
    AND fr.response->>'score' != ''
),

-- Combine submission details with question performance
question_performance AS (
    SELECT 
        cs.audit_type,
        cs.country,
        cs.region,
        cs.city,
        cs.submission_id,
        cs.submit_date,
        EXTRACT(YEAR FROM cs.submit_date)::INTEGER AS audit_year,
        EXTRACT(QUARTER FROM cs.submit_date)::INTEGER AS audit_quarter,
        'Q' || EXTRACT(QUARTER FROM cs.submit_date) || ' ' || EXTRACT(YEAR FROM cs.submit_date) AS quarter_label,
        qd.qid,
        qd.question,
        qd.criteria,
        qd.max_score,
        rws.score_earned,
        qd.max_score - rws.score_earned AS points_lost,
        CASE WHEN rws.score_earned = 0 THEN 1 ELSE 0 END AS is_missed
    FROM completed_submissions cs
    INNER JOIN responses_with_scores rws ON rws.submission_id = cs.submission_id
    INNER JOIN question_detail qd ON qd.qid = rws.qid AND qd.form_id = cs.form_id
),

-- Aggregate and rank questions per checklist
question_aggregated AS (
    SELECT 
        audit_type,
        criteria,
        qid,
        LEFT(question, 100) AS question_text,
        max_score,
        COUNT(*) AS times_asked,
        ROUND(AVG(score_earned), 2) AS avg_score_earned,
        ROUND(AVG(points_lost), 2) AS avg_points_lost,
        SUM(is_missed) AS times_missed,
        ROUND(100.0 * SUM(is_missed) / COUNT(*), 2) AS missed_percentage
    FROM question_performance
    GROUP BY audit_type, criteria, qid, LEFT(question, 100), max_score
    HAVING COUNT(*) >= 5  -- Minimum sample size
),
-- Rank within each audit_type
ranked_questions AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY audit_type ORDER BY missed_percentage DESC) AS rank_in_checklist
    FROM question_aggregated
)

-- Output: Top 5 per checklist, pre-ranked
SELECT 
    audit_type,
    criteria,
    qid,
    question_text,
    max_score,
    times_asked,
    avg_score_earned,
    avg_points_lost,
    times_missed,
    missed_percentage,
    rank_in_checklist
FROM ranked_questions
WHERE rank_in_checklist <= 5
ORDER BY audit_type, rank_in_checklist
```

---

## Routine ALamar_Checklist Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine ALamar
-- Dashboard: Checklist Compliance
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:53:12
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1".division AS "divison",
		"QueryTable 1".sub_division as "Sub Division",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
   and job_location not in ('KNOW', 'All', 'HO')
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
select fc.*, to_char("Date", 'YYYY-MM-DD') as "Date Mod",
	 ud.division,ud.sub_division
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
	 Join user_details ud on fc."Location" = ud.job_location
where fc."Organization" =@{{:OrganizationParameter}}
	 AND fc."Reminded At" BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
	 and "Routine Name"ILIKE ANY (
  ARRAY[
    '%AF-DOM-034 Cleaning and Sanitation Log - 2 Hrs V2%',
    '%FORM-AF-DOM-030 Temperature Monitoring Log (Equipment & Products) V2%',
    '%FORM-AF-DOM-018 Baking & Reheating Temperature Monitoring Log V2%',
    '%Shift Handover Checklist V2%',
    '%Cleaning & Maintenance Log - Monthly%',
    '%Cleaning & Maintenance Log - Weekly%',
    '%Cleaning & Maintenance Log - Daily%',
    '%Receiving Inspection Log V2%',
    '%PRP Product Monitoring Checklist V2%',
    '%Store Opening Checklist%',
    '%Store Closing Checklist%'
  ]
)
order by 1, 5, 2 desc, 6 desc, 4)"QueryTable 1"
```

---

## Routine Compliance Report Alamar Dominos_Alamar KSA Logbooks Compliance.sql

**Tables referenced:** filtered_data, final_summary, form_compliance_v2, location_acl, summary, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance Report Alamar Dominos
-- Dashboard: Alamar KSA Logbooks Compliance
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:54:06
-- ============================================================

WITH location_acl AS (
  SELECT DISTINCT job_location
  FROM user_details
  WHERE organization = 'AlaPtr-antenna'
    AND is_active = 'true'
    AND job_location NOT IN ('KNOW', 'All', 'HO')
    AND (
      uuid IN (SELECT uuid FROM user_details WHERE is_super_admin = TRUE)
      OR uuid IN (
        SELECT DISTINCT user_id
        FROM user_groups ug1
        WHERE ug1.group_id IN (
          SELECT group_id FROM user_groups ug2 WHERE ug2.has_access = TRUE
        ) AND ug1.is_active = TRUE
      )
    )
),
filtered_data AS (
  SELECT
    fc."Location",
    ud.division AS "Region",
    fc."Routine Name",
    fc."Compliance"
  FROM form_compliance_v2 fc
  JOIN location_acl ON fc."Location" = location_acl.job_location
  JOIN user_details ud ON fc."Location" = ud.job_location
  WHERE fc."Organization" = 'AlaPtr-antenna'
    AND fc."Reminded At" >= (CURRENT_DATE - INTERVAL '7 days')
    AND fc."Reminded At" < CURRENT_DATE
    AND fc."Routine Name" ILIKE ANY (
      ARRAY[
        '%KSA - Cleaning and Sanitation Log - 2 Hours%',
        '%KSA - Equipment Temperature Monitoring Log%',
        '%KSA - End Bake - Product Temperature Monitoring Log%',
        '%KSA - Banking Log%',
        '%KSA - Store Closing Checklist%',
        '%KSA - Store Opening Checklist%',
        '%KSA - Shift Handover Checklist%',
        '%KSA - FORM-AF-DOM-013 Thermometer Calibration Record%',
        '%Visitor Observation Form%',
        '%DM Observation Form%'
      ]
    )
),
summary AS (
  SELECT
    "Region",
    COUNT(DISTINCT "Location") AS "Total Stores",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Store Opening Checklist%' THEN "Compliance" END) * 100, 0) AS "KSA - Store Opening Checklist",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Store Closing Checklist%' THEN "Compliance" END) * 100, 0) AS "KSA - Store Closing Checklist",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - End Bake - Product Temperature Monitoring Log%' THEN "Compliance" END) * 100, 0) AS "KSA - End Bake - Product Temperature Monitoring Log",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Equipment Temperature Monitoring Log%' THEN "Compliance" END) * 100, 0) AS "KSA - Equipment Temperature Monitoring Log",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Cleaning and Sanitation Log - 2 Hours%' THEN "Compliance" END) * 100, 0) AS "KSA - Cleaning and Sanitation Log - 2 Hours",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Banking Log%' THEN "Compliance" END) * 100, 0) AS "KSA - Banking Log",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - Shift Handover Checklist%' THEN "Compliance" END) * 100, 0) AS "KSA - Shift Handover Checklist",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%KSA - FORM-AF-DOM-013 Thermometer Calibration Record%' THEN "Compliance" END) * 100, 0) AS "KSA - FORM-AF-DOM-013 Thermometer Calibration Record",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%Visitor Observation Form%' THEN "Compliance" END) * 100, 0) AS "Visitor Observation Form",
    ROUND(AVG(CASE WHEN "Routine Name" ILIKE '%DM Observation Form%' THEN "Compliance" END) * 100, 0) AS "DM Observation Form"
  FROM filtered_data
  GROUP BY "Region"
),
final_summary AS (
  SELECT *,
    ROUND((
      COALESCE("KSA - Store Opening Checklist", 0) +
      COALESCE("KSA - Store Closing Checklist", 0) +
      COALESCE("KSA - End Bake - Product Temperature Monitoring Log", 0) +
      COALESCE("KSA - Equipment Temperature Monitoring Log", 0) +
      COALESCE("KSA - Cleaning and Sanitation Log - 2 Hours", 0) +
      COALESCE("KSA - Banking Log", 0) +
      COALESCE("KSA - Shift Handover Checklist", 0) +
      COALESCE("KSA - FORM-AF-DOM-013 Thermometer Calibration Record", 0) +
      COALESCE("Visitor Observation Form", 0) +
      COALESCE("DM Observation Form", 0)
    ) / 10.0, 0) AS total_avg
  FROM summary
)

SELECT
  "Region",
  "Total Stores",
  TO_CHAR(COALESCE("KSA - Store Opening Checklist", 0), 'FM990%') AS "KSA - Store Opening Checklist",
  TO_CHAR(COALESCE("KSA - Store Closing Checklist", 0), 'FM990%') AS "KSA - Store Closing Checklist",
  TO_CHAR(COALESCE("KSA - End Bake - Product Temperature Monitoring Log", 0), 'FM990%') AS "KSA - End Bake - Product Temperature Monitoring Log",
  TO_CHAR(COALESCE("KSA - Equipment Temperature Monitoring Log", 0), 'FM990%') AS "KSA - Equipment Temperature Monitoring Log",
  TO_CHAR(COALESCE("KSA - Cleaning and Sanitation Log - 2 Hours", 0), 'FM990%') AS "KSA - Cleaning and Sanitation Log - 2 Hours",
  -- Uncomment below if needed again:
  -- TO_CHAR(COALESCE("KSA - Banking Log", 0), 'FM990%') AS "KSA - Banking Log",
  -- TO_CHAR(COALESCE("KSA - Shift Handover Checklist", 0), 'FM990%') AS "KSA - Shift Handover Checklist",
  -- TO_CHAR(COALESCE("KSA - FORM-AF-DOM-013 Thermometer Calibration Record", 0), 'FM990%') AS "KSA - FORM-AF-DOM-013 Thermometer Calibration Record",
  -- TO_CHAR(COALESCE("Visitor Observation Form", 0), 'FM990%') AS "Visitor Observation Form",
  -- TO_CHAR(COALESCE("DM Observation Form", 0), 'FM990%') AS "DM Observation Form",
  TO_CHAR(COALESCE(total_avg, 0), 'FM990%') AS "Total Avg"
FROM final_summary
ORDER BY "Region"
```

---

## alamar checklists_Checklist Compliance.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: alamar checklists
-- Dashboard: Checklist Compliance
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:53:35
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:Routine ALamar.UuidParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:Routine ALamar.UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'AlaPtr-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
 WHERE title ILIKE ANY (
  ARRAY[
    '%AF-DOM-034 Cleaning and Sanitation Log - 2 Hrs V2%',
    '%FORM-AF-DOM-030 Temperature Monitoring Log (Equipment & Products) V2%',
    '%FORM-AF-DOM-018 Baking & Reheating Temperature Monitoring Log V2%',
    '%Shift Handover Checklist V2%',
    '%Cleaning & Maintenance Log - Monthly%',
    '%Cleaning & Maintenance Log - Weekly%',
    '%Cleaning & Maintenance Log - Daily%',
    '%Receiving Inspection Log V2%',
    '%PRP Product Monitoring Checklist V2%',
    '%Store Opening Checklist%',
    '%Store Closing Checklist%'
  ]
)
     AND organization = 'AlaPtr-antenna'
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
        where submit_date at time zone 'Asia/Dubai' between @{{:Routine ALamar.Date Range.START}}::timestamp and 
	  @{{:Routine ALamar.Date Range.END}}::timestamp + interval '1 day'
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
          ud.division,
          ud.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   Join location_acl on fr.location = location_acl. job_location
   Join user_details ud on fr.location = ud.job_location
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
SELECT *
FROM raw
where q_type = 'multiple_choice'
and response ILIKE ANY (
  ARRAY[
   'Yes', 'No'
  ]
)
```

---

## alamar temp-copy_1749537581_Baking Temp Log.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, stores, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: alamar temp-copy_1749537581
-- Dashboard: Baking Temp Log
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:55:17
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
               AND ug1.is_active = TRUE))),td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'AlaPtr-antenna'
   GROUP BY 1,
            2),stores AS
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
     AND organization ILIKE 'AlaPtr-antenna'),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ANY (
  ARRAY[
    '%FORM-AF-DOM-018 Baking & Reheating Temperature Monitoring Log%'
  ]
)
     AND organization = 'AlaPtr-antenna'
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
          fr.location
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
   14
   ORDER BY 1,
            2,
            3)
SELECT 
    form_name, 
    sno, 
    rn,
    submit_date,
	country,
         region,
         city, 
    location,
    
    MAX(CASE WHEN raw.question ILIKE '%Product Type%' THEN response END) AS product_type,
    MAX(CASE WHEN raw.question ILIKE '%Product Name%' THEN response END) AS product_name,
 COALESCE(
        MAX(
            CASE 
                WHEN raw.question ILIKE '%Product Temperature (°C)%' 
                     AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
                THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
                ELSE NULL
            END
        ), 
        0
    ) AS product_temp,

    -- Baking temp status (above 75)
    MAX(CASE 
        WHEN form_name ILIKE '%FORM-AF-DOM-018%' 
             AND raw.question ILIKE '%Product Temperature (°C)%' 
             AND (
                 CASE 
                     WHEN regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$' 
                     THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS FLOAT) 
                     ELSE NULL 
                 END
             ) > 75 THEN 'IN RANGE'
        WHEN form_name ILIKE '%FORM-AF-DOM-018%' 
             AND raw.question ILIKE '%Product Temperature (°C)%' 
             AND (
                 CASE 
                     WHEN regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$' 
                     THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS FLOAT) 
                     ELSE NULL 
                 END
             ) <= 75 THEN 'OUT OF RANGE'
        ELSE NULL
    END) AS product_temp_baking_status
FROM raw
left outer JOIN stores on raw.location = stores.store_id
GROUP BY 1,2,3,4,5,6,7,8
HAVING MAX(CASE WHEN raw.question ILIKE '%Product Type%' THEN response END) IS NOT NULL
   AND TRIM(MAX(CASE WHEN raw.question ILIKE '%Product Type%' THEN response END)) <> ''
ORDER BY submit_date DESC
```

---

## alamar temp_Equipment Temp Log.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, stores, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: alamar temp
-- Dashboard: Equipment Temp Log
-- Category: Alamar Dominos
-- Extracted: 2026-01-29 16:55:17
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'AlaPtr-antenna'
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
               AND ug1.is_active = TRUE))),td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'AlaPtr-antenna'
   GROUP BY 1,
            2),stores AS
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
     AND organization ILIKE 'AlaPtr-antenna'),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ANY (
  ARRAY[
    '%FORM-AF-DOM-030 Temperature Monitoring Log (Equipment & Products)%'
  ]
)
     AND organization = 'AlaPtr-antenna'
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
          fr.location
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
   14
   ORDER BY 1,
            2,
            3)
SELECT 
    form_name, 
    sno, 
    rn,
    submit_date,
	country,
         region,
         city, 
    location,
MAX(CASE 
        WHEN raw.question ILIKE '%Makeline Cabinets - Equipment Temperature (°C)%' 
             AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
        ELSE NULL 
    END) AS "Makeline Cabinet",

    MAX(CASE 
        WHEN raw.question ILIKE '%Makeline Bins - Equipment Temperature (°C)%' 
             AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
        ELSE NULL 
    END) AS "Makeline Bin",

    MAX(CASE 
        WHEN raw.question ILIKE '%Walk In Cooler - Equipment Temperature (°C)%' 
             AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
        ELSE NULL 
    END) AS "Walk In Cooler",

    MAX(CASE 
        WHEN raw.question ILIKE '%Beverages - Temperature (°C)%' 
             AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
        THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
        ELSE NULL 
    END) AS "Beverages",
    MAX(CASE WHEN raw.question ILIKE '%Product Name%' THEN response END) AS product_name,
    MAX(
  CASE 
    WHEN raw.question ILIKE '%Product Temperature (°C)%' 
         AND regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$'
    THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS numeric)
    ELSE NULL
  END
) AS product_temp,

    -- Storage product temp status (0-5)
    MAX(CASE 
        WHEN form_name ILIKE '%FORM-AF-DOM-030%' 
             AND raw.question ILIKE '%Product Temperature (°C)%' 
             AND (
                 CASE 
                     WHEN regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$' 
                     THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS FLOAT) 
                     ELSE NULL 
                 END
             ) BETWEEN 0 AND 5 THEN 'IN RANGE'
        WHEN form_name ILIKE '%FORM-AF-DOM-030%' 
             AND raw.question ILIKE '%Product Temperature (°C)%' 
             AND (
                 CASE 
                     WHEN regexp_replace(response, '[^0-9.-]', '', 'g') ~ '^-?[0-9]+(\.[0-9]+)?$' 
                     THEN CAST(regexp_replace(response, '[^0-9.-]', '', 'g') AS FLOAT) 
                     ELSE NULL 
                 END
             ) NOT BETWEEN 0 AND 5 THEN 'OUT OF RANGE'
        ELSE NULL
    END) AS product_temp_storage_status

FROM raw
left outer JOIN stores on raw.location = stores.store_id
GROUP BY 1,2,3,4,5,6,7,8
ORDER BY submit_date DESC
```

---
