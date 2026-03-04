# Big Basket

> Auto-generated on 2026-03-04 08:13

**Total queries:** 23

---

## BB 5K Audit - All Past Audits_5K Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB 5K Audit - All Past Audits
-- Dashboard: 5K Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:49
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_5K%'
  and store_id = @{{:BB 5K Audit - Single Audit.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" <= @{{:BB 5K Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB 5K Audit - Recommendations_5K Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, reco_database

**Original Query:**

```sql
-- Data Source: BB 5K Audit - Recommendations
-- Dashboard: 5K Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:48
-- ============================================================

WITH reco_database as (select null as process_owner, null as process, null as question, null as recommendation),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_5K%'
   and store_id = @{{:BB 5K Audit - Single Audit.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB 5K Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB 5K Audit - Single Audit_5K Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB 5K Audit - Single Audit
-- Dashboard: 5K Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:49
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_5K%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB Asset Movement Register_BB Asset Movement Register.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Original Query:**

```sql
-- Data Source: BB Asset Movement Register
-- Dashboard: BB Asset Movement Register
-- Category: Big Basket
-- Extracted: 2026-01-29 16:59:30
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-Nq1VuoGCL6mi9227L_e')), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
  (/*Non Table type Questions in Forms with Logic - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
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
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
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
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          sno,
          response_id,
          question_id AS parent_qid,
          question_id AS qid,
          response
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                sno,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                res.value AS response
   FROM
     (SELECT form_submit_id,
             sno,
             response_id,
             question_id,
             base.value
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                       RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
   ORDER BY 1,
            2,
            3)
SELECT form_name as "Form Name",
       form_knid as "Form KNID",
       form_response_knid as "Form Response KNID",
       sno as "Submission S No",
       max(CASE
               WHEN question = 'Location' THEN response
               ELSE NULL
           END) AS "Location",
       max(CASE
               WHEN question = 'Outward Form' THEN (to_timestamp((section_response->> 'st')::bigint/1000) AT TIME ZONE 'Asia/Kolkata')::date
               ELSE NULL
           END) AS "Date",
       max(CASE
               WHEN question = 'CEE ID (Delivery Boy Id)' THEN response
               ELSE NULL
           END) AS "CEE ID",
       count(CASE
                 WHEN parent_question = 'Saddle Bag'
                      AND section_no = 1 THEN response
                 ELSE NULL
             END) AS "Saddle Bag Outward #",
       count(CASE
                 WHEN parent_question = 'Insulated Bag Red'
                      AND section_no = 1 THEN response
                 ELSE NULL
             END) AS "Insulated Bag Red Outward #",
       count(CASE
                 WHEN parent_question = 'Syntex Box'
                      AND section_no = 1 THEN response
                 ELSE NULL
             END) AS "Syntex Box Outward #",
       count(CASE
                 WHEN parent_question = 'Insulated Bag Green'
                      AND section_no = 1 THEN response
                 ELSE NULL
             END) AS "Insulated Bag Green Outward #",
       max(CASE
               WHEN question = 'Banana Box'
                    AND section_no = 1 THEN response::int
               ELSE NULL
           END) AS "Banana Box Outward #",
       count(CASE
                 WHEN parent_question = 'Saddle Bag'
                      AND section_no = 2 THEN response
                 ELSE NULL
             END) AS "Saddle Bag Inward #",
       count(CASE
                 WHEN parent_question = 'Insulated Bag Red'
                      AND section_no = 2 THEN response
                 ELSE NULL
             END) AS "Insulated Bag Red Inward #",
       count(CASE
                 WHEN parent_question = 'Syntex Box'
                      AND section_no = 2 THEN response
                 ELSE NULL
             END) AS "Syntex Box Inward #",
       count(CASE
                 WHEN parent_question = 'Insulated Bag Green'
                      AND section_no = 2 THEN response
                 ELSE NULL
             END) AS "Insulated Bag Green Inward #",
       max(CASE
               WHEN question = 'Count of Banana Box'
                    AND section_no = 2 THEN response::int
               ELSE NULL
           END) AS "Banana Box Inward #"
FROM RAW
GROUP BY 1,
         2,
         3,
         4
ORDER BY 1,
         2,
         6,
         5,
         4
```

---

## BB Audit Summary_Process Audit Summary.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, with_audit_numbers

**Original Query:**

```sql
-- Data Source: BB Audit Summary
-- Dashboard: Process Audit Summary
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:13
-- ============================================================

WITH base AS
  (SELECT CASE
              WHEN position(':' IN theme) IS NULL THEN theme
              ELSE left(theme, position(':' IN theme)-1)
          END AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE organization_id = 'bigbasket-canis'
     AND audit_submitted_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
     AND (audit_main_theme ILIKE 'Process Audit Checklist T1%'
          OR audit_main_theme ILIKE 'T1 B2B%'
          OR audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%'
          OR audit_main_theme ILIKE 'T2 B2B%'
          OR audit_main_theme ILIKE 'T4 Audit%'
          OR audit_main_theme ILIKE 'Final_Audit_check_list_5K%')), 
		  with_audit_numbers AS
  (SELECT audit_submission_knid AS "Audit Report KNID",
          audit_submission_number AS "Audit Report Number",
          CASE
              WHEN audit_main_theme ILIKE 'Process Audit Checklist T1%' THEN 'T1 B2C'
              WHEN audit_main_theme ILIKE 'T1 B2B%' THEN 'T1 B2B'
              WHEN audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%' THEN 'T2 B2C'
              WHEN audit_main_theme ILIKE 'T2 B2B%' THEN 'T2 B2B'
              WHEN audit_main_theme ILIKE 'T4 Audit%' THEN 'T4 Process'
              WHEN audit_main_theme ILIKE 'Final_Audit_check_list_5K%' THEN '5K'
              ELSE audit_main_theme
          END AS "Audit Name",
          store_id AS "Location",
          (audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::date AS "Audit Submitted At",
                                          (extract('Year'
                                                   FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata'))::int AS "Audit Year",
                                          (row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          area,
                                                                          checkpoint_knid,
                                                                          extract('Year'
                                                                                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')
                                                             ORDER BY audit_submitted_at))::int AS "Audit No in Year",
                                                            auditor_name AS "Auditor",
                                                            process_owner AS "Process Owner",
                                                            area AS "Area",
                                                            checkpoint_knid AS "Checkpoint KNID",
                                                            CHECKPOINT AS "Checkpoint",
                                                                          RESULT AS "Result",
                                                                                    CASE
                                                                                        WHEN result_score != '' THEN result_score::numeric
                                                                                        ELSE 0
                                                                                    END AS "Actual Score",
                                                                                    CASE
                                                                                        WHEN result_score != '' THEN max_score::numeric
                                                                                        ELSE 0
                                                                                    END AS "Max Score",
   case when total_follow_up_tasks > 0 and total_follow_up_tasks > total_closed_follow_up_tasks then 'Open'
   when total_follow_up_tasks > 0 and total_follow_up_tasks <= total_closed_follow_up_tasks then 'Closed'
   else 'No Follow Up' end as "Follow up Status"
   FROM base)
SELECT *
FROM with_audit_numbers
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
HAVING "Auditor" NOT ILIKE 'KNOW%'
ORDER BY 5,
         3,
         4,
         9,
         10,
         12
```

---

## BB Follow Ups Summary_Process Audit Summary.sql

**Tables referenced:** CURRENT_TIMESTAMP, analytics_requests, assignee, audit_submitted_at, base, checkpoint_master_sheet_table, checkpoints, follow_ups, tasks, user_details

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `inProgress` -> `in_progress` (alias: `in_progress AS "inProgress"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedByUserName` -> `resolved_by_user_name` (alias: `resolved_by_user_name AS "resolvedByUserName"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: BB Follow Ups Summary
-- Dashboard: Process Audit Summary
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:11
-- ============================================================

WITH base AS
  (SELECT CASE
              WHEN position(':' IN theme) IS NULL THEN theme
              ELSE left(theme, position(':' IN theme)-1)
          END AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
   audit_submitted_at,
          store_id,
          checkpoint_knid,
          CHECKPOINT,
   criticality,
          RESULT,
   CASE
                                                                                        WHEN result_score != '' THEN result_score::numeric
                                                                                        ELSE 0
                                                                                    END AS result_score,
                                                                                    CASE
                                                                                        WHEN result_score != '' THEN max_score::numeric
                                                                                        ELSE 0
                                                                                    END AS max_score,
   auditor_observations,
          total_follow_up_tasks,
          total_closed_follow_up_tasks,
          auditor_name
   FROM checkpoint_master_sheet_table
   WHERE organization_id = 'bigbasket-canis'
     AND audit_submitted_at BETWEEN @{{:BB Audit Summary.Date Range.START}}::TIMESTAMP AND @{{:BB Audit Summary.Date Range.END}}::TIMESTAMP + interval '1 day'
     AND (audit_main_theme ILIKE 'Process Audit Checklist T1%'
          OR audit_main_theme ILIKE 'T1 B2B%'
          OR audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%'
          OR audit_main_theme ILIKE 'T2 B2B%'
          OR audit_main_theme ILIKE 'T4 Audit%'
          OR audit_main_theme ILIKE 'Final_Audit_check_list_5K%')),
     checkpoints AS
  (SELECT audit_submission_knid AS "Audit Report KNID",
          audit_submission_number AS "Audit Report Number",
   audit_submitted_at as "Audit Submitted At",
          CASE
              WHEN audit_main_theme ILIKE 'Process Audit Checklist T1%' THEN 'T1 B2C'
              WHEN audit_main_theme ILIKE 'T1 B2B%' THEN 'T1 B2B'
              WHEN audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%' THEN 'T2 B2C'
              WHEN audit_main_theme ILIKE 'T2 B2B%' THEN 'T2 B2B'
              WHEN audit_main_theme ILIKE 'T4 Audit%' THEN 'T4 Process'
              WHEN audit_main_theme ILIKE 'Final_Audit_check_list_5K%' THEN '5K'
              ELSE audit_main_theme
          END AS "Audit Name",
          store_id AS "Location", /*  (audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::date AS "Audit Submitted At",
                                          (extract('Year'
                                                   FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata'))::int AS "Audit Year",
                                          (row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          area,
                                                                          checkpoint_knid,
                                                                          extract('Year'
                                                                                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')
                                                             ORDER BY audit_submitted_at))::int AS "Audit No in Year",*/ auditor_name AS "Auditor",
                                                                                                                         process_owner AS "Process Owner",
                                                                                                                         area AS "Area",
                                                                                                                         checkpoint_knid AS "Checkpoint KNID",
                                                                                                                         CHECKPOINT AS "Checkpoint",
   criticality as "Criticality",
                                                                                                                                       RESULT AS "Result", auditor_observations as "Observation", result_score AS "Actual Score",
                                                                                    max_score AS "Max Score", CASE
                                                                                                              WHEN total_follow_up_tasks > 0
                                                                                                                   AND total_follow_up_tasks > total_closed_follow_up_tasks THEN 'Open'
                                                                                                              WHEN total_follow_up_tasks > 0
                                                                                                                   AND total_follow_up_tasks <= total_closed_follow_up_tasks THEN 'Closed'
                                                                                                              ELSE 'No Follow Up'
                                                                                                          END AS "Follow Up Status"
   FROM base
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
            11, 12, 13, 14, 15, 16
   HAVING auditor_name NOT ILIKE 'KNOW%'),
     follow_ups AS
  (SELECT CASE
              WHEN details->'auditDetails'->>'name' ILIKE 'Process Audit Checklist T1%' THEN 'T1 B2C'
              WHEN details->'auditDetails'->>'name' ILIKE 'T1 B2B%' THEN 'T1 B2B'
              WHEN details->'auditDetails'->>'name' ILIKE 'Final_Audit_check_list_T2_DC%' THEN 'T2 B2C'
              WHEN details->'auditDetails'->>'name' ILIKE 'T2 B2B%' THEN 'T2 B2B'
              WHEN details->'auditDetails'->>'name' ILIKE 'T4 Audit%' THEN 'T4 Process'
              WHEN details->'auditDetails'->>'name' ILIKE 'Final_Audit_check_list_5K%' THEN '5K'
              ELSE details->'auditDetails'->>'name'
          END AS "Audit Name",
          details->'auditDetails'->>'questionId' AS "Checkpoint KNID",
                                    details->'auditDetails'->>'responseId' AS "Audit Report KNID",
                                                              id AS "Action KNID",
                                                              title AS "Action",
                                                              CASE
                                                                  WHEN status = 'notStarted' THEN 'Not Started'
                                                                  WHEN status IN ('inProgress',
                                                                                  'started',
                                                                                  'reopened') THEN 'In Progress'
                                                                  WHEN status = 'completed' THEN 'Completed'
                                                                  ELSE NULL
                                                              END AS "Action Status",
                                                              CASE
                                                                  WHEN (status = 'completed'
                                                                        AND completed_at > deadline)
                                                                       OR (status != 'completed'
                                                                           AND extract(epoch
                                                                                       FROM CURRENT_TIMESTAMP) > deadline) THEN 'Delayed'
                                                                  ELSE 'Not Delayed'
                                                              END AS "On Time Status",
                                                              details->>'authorName' AS "Created By",
                                                                        details->>'resolvedByUserName' AS "Completed By",
                                                                                  details->>'comment' AS "Closure Comment",
                                                                                            to_timestamp(created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Created At",
                                                                                                                                       to_timestamp(deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                                to_timestamp(completed_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Completed At"
   FROM tasks
   WHERE organization = 'bigbasket-canis'
     AND (details->'auditDetails'->>'name' ILIKE 'Process Audit Checklist T1%'
          OR details->'auditDetails'->>'name' ILIKE 'T1 B2B%'
          OR details->'auditDetails'->>'name' ILIKE 'Final_Audit_check_list_T2_DC%'
          OR details->'auditDetails'->>'name' ILIKE 'T2 B2B%'
          OR details->'auditDetails'->>'name' ILIKE 'T4 Audit%'
          OR details->'auditDetails'->>'name' ILIKE 'Final_Audit_check_list_5K%')
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
            13),
     assignee AS
  (SELECT f."Action KNID",
          string_agg(ud.first_name||' '||ud.last_name, ', ') AS "Assigned To"
   FROM follow_ups f
   JOIN analytics_requests ar ON f."Action KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
   GROUP BY 1)
SELECT c."Audit Name",
       c."Location",
       c."Audit Report KNID",
	   c."Audit Submitted At",
       c."Process Owner",
       c."Area",
       c."Checkpoint",
	   c."Criticality",
	   c."Result",
	   c."Actual Score",
	   c."Max Score",
	   c."Observation",
       c."Follow Up Status",
       f."Action KNID",
       f."Action",
       f."Action Status",
       f."On Time Status",
       f."Closure Comment",
       f."Created By",
       a."Assigned To",
       f."Completed By",
       f."Created At",
       f."Deadline",
       f."Completed At"
FROM checkpoints c
LEFT OUTER JOIN follow_ups f ON c."Audit Report KNID" = f."Audit Report KNID"
AND c."Checkpoint KNID" = f."Checkpoint KNID"
LEFT OUTER JOIN assignee a ON f."Action KNID" = a."Action KNID"
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
         18, 19, 20, 21, 22, 23, 24
```

---

## BB T1 B2B Audit - All Past Audits_T1 B2B Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T1 B2B Audit - All Past Audits
-- Dashboard: T1 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:57
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC_%'
  and store_id = @{{:BB T1 B2B Audit - Single Audit.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE NULL
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE NULL
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE NULL
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE NULL
              END) AS non_critical_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          critical_actual_score AS "Critical Actual Score",
                                          critical_max_score AS "Critical Max Score",
                                          non_critical_actual_score AS "Non-critical Actual Score",
                                          non_critical_max_score AS "Non-critical Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT *
FROM with_audit_numbers
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
HAVING "Audit No in Year" <= @{{:BB T1 B2B Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T1 B2B Audit - Recommendations_T1 B2B Process Audit Report.sql

**Tables referenced:** B, Bin, Bulk, Crates, QC, Regional, Shelf, Vendor, audit_submitted_at, base, bulk, checkpoint_master_sheet_table, crates, current_timestamp, employee, excess, his, inventory, reco_database, stakeholders, system, the, vendor, vendors

**Original Query:**

```sql
-- Data Source: BB T1 B2B Audit - Recommendations
-- Dashboard: T1 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:52
-- ============================================================

WITH reco_database as (select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is 2 Times Energy drinks served to staffs in Summer Season ?' as question, 'Energy drinks must be served to all staffs during summer' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the 3-4 times Tea and Snacks served in DC / 5K DS ? (Snacks mandatory for night shift employees)' as question, '3 Times Tea and snacks must be provided.(Snack sis mandatory in night shift)' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Breakfast Lunch and Dinner served for Staffs in DC for Rs.10/-? (Breakfast for all staffs Employee can avail either lunch or dinner)' as question, 'Breakfast, Lunch and dinner must be served to staff.(Staffs can opt for lunch/Dinner)' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Bus Facility arranged for dropping Morning shift employees and pick up night shift employees drop night shift employees and pick up after noon shift employees ? (Applicable only for DC - Puzhal - Chennai DC - Pune DC - Chandu - NCR DC - Bhiwandi - Mumbai DC - Sakrial -Kolkata DC - Ahmedabad DC - Jigani - Bangalore)' as question, 'Bus facility must be provided for dropping of moring shift employees and pick up of mid night employees' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Changing Room Available for Woman Staffs ? (Applicable wherever Woman Staffs working)' as question, 'Changing rooms must be provided to female staff without fail' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the DC having Tie up with nearest Creche (Baby Care) within 1KM radius ?' as question, 'DC must tie up with near baby care center with in 1 KM radius.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Drinking Water dispensers installed in every 30 Sqmtrs and Water refilled timely ?' as question, 'Drinking water dispenser must be installed in every 30 Sqmtrs and water to be refilled timely.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Employee Help Desk and Grievance redressal desk available in the DC?' as question, 'Employee help desk must be available for grievance redressal and any issues with salary must be addressed and proper solution must be provided.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Lockers provided to each Employees in the Shift?' as question, 'Lockers must be provided to each employees of the shift and Locker must be available' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Rest Rooms provided to DC Staffs ? ( well ventilated with Fans Benches Minimum 2 Bunk Beds in Ds 8 Bunk Beds in DC)' as question, 'Rest rooms must be provided to staff to take rest with all necessary facilities' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Segmented plates spoons water dispenser hand wash basin dustbins available and efficient waste disposal Hygienically maintained ?' as question, 'plates spoons, Water dispenser, hand wash basin, Dustbin must be available.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Washrooms available in DC / DS Premises and Hygiene accessories available as per list? (Male - Minimum 2 urinal and 2 wc per 100 employee 1 water closet (Indian) and 1 water closet for 25 women (Sanitary waste disposal dustbin health faucet wash basin mirror soap hand dryer) Is the washrooms maintenance register maintained (to be cleaned every 4 Hours Checklist should be signed off by OC/SC every day.)' as question, 'Washrooms must be maintained clean and neat. Necessary accessories must be available.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Water Cooler / Dispenser serviced every 6 months once and water Tank maintained cleanly without dust inside as well outside?' as question, 'Water cooler & Dispenser must be serviced every 6 Months. Water tank must be maintained neat and clean' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'Is there any employee exit allowed without a proper investigation in the presence of the Regional HR Head? ( A detailed investigation report will be prepared by regional HR. This will be part of HR audit checklist. All such exits require Business Headâ€™s approval).' as question, 'Employees exit should not be allowed without proper investigation, Exit interview is must.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are Managers providing timely feedback to the employee? He should take time to explain to the employee where he is going wrong and coaches him on what is correct in a professional and respectful manner.' as question, 'Managers must provide timely feedback on employees. Manager must explain the strength and weakness of employees. He must help to overcome from  his weakness' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'If an employee resigns does the manager have a one on one to understand the reason behind this decision and try to retain the employee. Managers should follow the exit process laid down by the Company?' as question, 'Managers must sit for one on one when employees resigns, He must try to retain employees by understanding the challenges' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are the employees forced to do OT?' as question, 'Employees should not be forced to an OT' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager appreciate the employees when they do a good job and are the Managers participating actively in R and R and engagement events to make employees feel that they are valued?' as question, 'Managers must appreciate the employees when they do good job and he must participate R&R and appreciate' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager propagate a culture of respect?' as question, 'Managers must propagate culture of respect and values. His sub ordinates must leans from his behavior.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers ensure that the employees duty hours are maintained? Managers should also ensure that lunch timings for their reportees are not unnecessarily delayed and are maintained consistently.' as question, 'Managers must ensure duty hours of employees maintained and employees are having lunch on time and necessary breaks are given' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers lead by example?' as question, 'Managers must show positive response and lead by example to his fellow workers' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Dose the Managers in DC restrict OT to 2 hours post normal shift timings to ensure that the Associates are not overworked?' as question, 'Managers must restrict OT of associates to 2 Hours post normal shift timings.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'If an employee resigns is the manager having a one on one to understand the reason behind this decision and try to retain the employee. Also is the Managers following the exit process laid down by the Company?' as question, 'managers typically conduct exit interviews to understand reasons for resignation and may attempt retention efforts. They should also adhere to the company''s exit process protocols.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers being fair in granting leaves?' as question, 'Line managers must be fair in granting leaves. Discrimination should not be done for granting leaves.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers spending 1 hour with the new joiner on his 1st day in the floor after NHT (New Higher Training)/Induction to inform him about job responsibilities culture at bigbasket and any other information that makes his job easy' as question, 'Manager must spend 1 hour with the new joiner on his 1st day of floor' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are stocks received as per QC process/ Product Specification as per QC Manual? (Check Kirana specifications)' as question, 'Stock should receive as per BB specification' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is QC person carrying out calibration for all weighing scales and Bizerba using certified dead weight (Standard weight/ stone certified by weight and Measurement Department? Is all the Reports available?' as question, 'QC person has to carry the calibration for all weighing scales and Bizerba using certified dead weight ' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is any Fruits and Vegetables found rotten or spoilt in Bulk Area?' as question, 'Rotten, spoiled FV stocks should be removed from bulk area' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the FV QC Passed SKUs transferred to Clean bulk crate?' as question, 'Cleaned bulk crates must be used for F&V QC passed stocks' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the In-house QC happening daily basis in DC? Are the poor-quality stocks getting removed?' as question, 'In-house QC must be done on regular basis' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC happening 100% before receiving stocks from Vendor?' as question, '100% Quality check done for all stocks while receiving from Vendor' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the sorting and grading happening for RTV Stocks on the same Day? And any reusable quantity packed on the same immediately and moved to the picking area/location?' as question, 'Quality check must be done for All RTV stocks before moving to floor in same day' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is Crate QC done for all Crates staged in Hub movement area before Dispatch?' as question, 'Crate QC must be done for all the crates before moving to dispatch area.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the GRN matching with invoice Value? Is the Invoices submitted to Finance daily basis thru courier? Courier details available?' as question, 'GRN value must be match with invoice value and All GRN''s invoices to be sent to finance team on regular basis' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC-Manager monitoring all pending system transactions? (In warded but not GRN tracking Inter DC in process orders on Daily Basis? By 10am there should not be any inter dc orders in process.' as question, 'DC manager must be monitor all pending system transactions and close on daily basis' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are Cold room safety Jacket hand glove and shoes available as required/ Are staff entering Cold room wearing safety Jacket hand glove and shoes?' as question, 'Required PPE must be available and staff must be used the PPE while entering to cold rooms.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Waste collection bins placed in designated location to accumulate the Butchery generated Waste? Is all generated butchery waste moved to a designated waste collection center or shed by Housekeeping staff?' as question, 'Waste management process must be follow at DC. Waste collection bins must be at designated locations.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the DC team using adequate gel pack/ chilled pads as per process to ensure the desired Temperature of Product till it reached the customer Are syntax boxes used for Frozen articles?' as question, 'DC team Must be follow meat cold chain process,Required number of Gel packs must be used.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the GRN process followed as per the process: a. Is PO raised in Bulk and Child SKU Codes to the Vendor? b. Is the Stocks sourced from vendor in Bulk and Child SKU code? c. Is the GRN in system happening in Bulk and Chilled SKU code?' as question, 'Butcery GRN process must be followed for all transactions.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Returns handling process followed by the DC Team: QC check performed while receiving the return stock ( check Quality shelf life and temperatures the product in salable if non-salable stock details should be made available at the time of Audit.' as question, 'Return process must follow without any deviations and QC checks must be performed all return stocks' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Temperature of the Vehicle and Product checked before receiving. (+ or - 3Â° C) difference is acceptable and are the Chiller and Frozen SKUs receiving happens in cold room (Anti Room) checking Temperature as per (Permissible limit)?' as question, 'Temperature of the Vehicle and Products must be check before receiving and accept as per process' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the bulk TO vs child GRN details shared to B and M team every day by butchery in charge?' as question, 'TO vs GRN details must be shared to B&M team every day by Butchery team' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Were the Ice Boxes clean and Neat at the time of packing?' as question, 'Cleaned Constra boxes/chiled boxes must be use for picking' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'For Poor Performance Employee who is in the bottom 10% whether the refresher training has been imparted? (Employees should not be in bottom 10% consequently for 3 months he should not be asked to leave for this reason with out providing refresher training when his poor performance was identified) employee when in the bottom 10% the employee has to be put through refresher training' as question, 'Poor performance employees who is in bottom 10% must be facilitated the refresher training with training team.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is Managers having one on one with any employee who is in the bottom 10% in the department(DC). The manager should try to understand the reasons behind the gaps in performance and if the employee needs any help. This meeting should be held Weekly till the employee moves out of bottom 10%' as question, 'Managers must have one on one discussion who is bottom 10% picker. Manager must try to understand the reason behind gaps and help to overcome' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers always present in Daily Huddles and spread awareness on organizational targets policy changes etc.' as question, 'Line manager must always present in daily huddles and spread the awareness on organizational targets.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers have weekly meetings with the associates where they should talk about OKR, targets etc. These meetings should have action points which are minuted and status on the action points should be provided in the next meeting' as question, 'managers often hold weekly meetings with associates to discuss OKRs, targets, and establish action points. Minutes should be taken, and status updates on action points should be provided in subsequent meetings' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are all the Line Managers/Supervisors aware of policies and benefits provided by bb like number of leaves bb TRUST etc and communicate the same to the Associates' as question, 'Line manager and supervisor must aware of policies and benefits of the company.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Whole of F and V Work Place Bins Storage location processing area maintained neat and Clean and regular cleaning carried out?' as question, 'All F&V Work Place Bins, Storage location, processing area must be maintained neat and Clean and regular cleaning must be carried out' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is Separate A4 size traycrates kept in the security, Receiving area or applicable area for Collecting invoice DCs Other documents from vendors' as question, 'separate A4-size trays or crates are commonly used in security, receiving areas, or applicable locations to collect invoices, delivery notes, and other documents from vendors for organizational records and processing.' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Does the Critical Assets Breakdown addressed in time and resolved by raising Ticket in My MCS? Check for the details? Is the regular and critical assets requirement status available with follow up?' as question, 'My mcs call must be raised for all critical assets if get any Breakdown and resolve within 48 hours ' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Have all the Breakdown non-usable/repairable assets kept in a designated area with details updated in My Impact as on date in DC?' as question, 'All breackdown and un used/repairable assets should keep seperately in designated area with all updated details as on date.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are all HHDs and MHE batteries kept under charging while non-operational time?' as question, 'All Picking device and MHE batteries should keep under charge while non operational time.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are all Picked crates moved to Hub staging area after picking?' as question, 'All crates /chilled boxes must be sealed after picking with lids.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in FMCG Office? Refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'Is the First Aid Box Must be available in Office & Refilling should happen as required and all contents must be available in kit' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the staging area for the HUB clearly demarcated and well separated?' as question, 'Hub staging area must be demarcated and well saparated for each Hub' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'does the Picker picks SKUs as per sequence (Hard SKU to Soft SKU Leafy)?' as question, 'Picking should be happens as per Sequence to avoid damages and customer complaints (Hard SKU''s to soft SKU.leafy)' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are the crates filled with stocks as per SKU wise standard crate weight?' as question, 'F&V bulk crates must be filled with stocks as per SKU wise standard crate weight.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the receiving area being clean and neat? Any time receiving staging area to be clean?' as question, 'Receiving area to be maintain clean and neat at any time.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Trolley Movement happening in the DC for Picking? Is the Trolley used for picking by the picker always while picking?' as question, 'Trolley movement should happen while picking , Baby picking is strictly prohibited.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Pick Efficiency monitored for all pickers thru pick idle report?' as question, 'Pick efficiency must be monitor for all pickers thru pick idle report' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'After picking are all chiller boxes moved to the Hub area?' as question, 'All chiller boxes must be moved to Hub staging area after picking.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are all crates sealed immediately after picking? And are all crates covered with lids (after checking on staging area)?' as question, 'All crates /chilled boxes must be sealed after picking with lids.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are the cancelled orders forwarded to Hubs and getting returned thru RTV?' as question, 'All the cancelled orders must be formwarded to HUB and must be taken through RTV' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Are the stocks received only in Bulk receiving Crate? And moved to Predefined area? Is the FV Stocks received in Clean bulk crate as per process? Bulk crate color code for CC arrival Vendor Stocks Organics' as question, 'Stocks must be received in bulk receiving crates and must be moved to predefined area. Clean bulk crates must be used with colour code tag.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Does the DC have records of movable assets stock position at all time?' as question, 'DC must have records all movable asset stock position and track at all time.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is DC Team well trained on Cold Chain Process and are the staff aware on the process to be followed?' as question, 'Cold Chain training must be imparted to staffs and staffs must aware and follow cold chain process.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is Hand Gloves used while placing and retrieving gel pads in the Plate Freezer? is the plates removed from the Plate freezer and cleaned with dry cloth after production of every batch? Are plate freezer doors kept closed and locked while running?' as question, 'Hand Gloves must be used while placing and retrieving gel pads in the Plate Freezer,trays must be removed from the Plate freezer and clean with dry cloth after production of every batch, Are plate freezer doors kept closed and locked while running' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is Picker picking required number of PCM Packs and properly arranging it inside insulated box with correct combination as per cold chain process?' as question, 'Pickers must pick required number of PCM packs and arrnge it properly inside the insualted box as per cold chain process.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the FIFO followed in Bulk location?' as question, 'FIFO norms must be follow in bulk location without fail.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is Cold rooms/ Chiller/ Freezer maintained clean and neat? Is the Temperatures maintained at desired level? Refer the records maintain on temperature and visual check on cleanness' as question, 'Cold rooms,freezers,chillers must be maintain clean and neat and Temperature maintainance register must be maintain,if find any temperature abuse must be inform to concerns' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Movable Assets (Crates) TO & TI Process followed? Is reconciliation carried out on every fortnight? For inter DC Supplies (5K, T2, B2B), BBD, BB Instant, CC)' as question, 'the Movable Assets (Crates) TO & TI process is typically followed, with reconciliation conducted every fortnight for inter-DC supplies such as 5K, T2, B2B, BBD, BB Instant, and CC.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Picker picking PCM Packs only from the horizontal Freezer @ -25o at the time of Picking of orders?' as question, 'Pickers must pick PCM Packs only from the horizontal Freezer / @ -25o at the time of Picking  orders' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the crates and Chiller boxes washed cleanly? Are the old stickers removed from crates and chiller boxes while washing? Is the same dried and given for picking?' as question, 'Crates and chiller boxes must be washed on regular intervals. Old sticker must be removed from Crates and Chiller boxes.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Picking location defined for each SKUs and are SKUs available for picker to pick?' as question, 'Picking location must be define for each SKU and stocks should be available in location for picking' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the PO raised for Indent Qty before vendor arrival?' as question, 'PO must be raised for Indent Qty before vendor arrival.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Were the pickers using the clean crates with proper lids?' as question, 'Pickers should use clean crates for picking and with proper lids to close the crate.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the plate freezer Maintained Clean and Neat? If the lock found intact? Is my MCs call raised for any damage to the plate freezer? is my MCs call raised for any damage to the plate freezer? Are they using Plate freezer in batches' as question, 'Plate freezer must be maintained clean & neat.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is QC report sent to the respective Kirana HUB 100%?' as question, 'QC report must be sent to Hub each slot wise.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Bulk Storage Location for each SKU defined and Demarked?' as question, 'Bulk storage location must be defined for each SKU and stock must be placed at desiganted location only.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the Internal Audit checklist carried out and actioned on Gaps identified?' as question, 'Internal audit should be conducted and action to be taken to fix the gaps.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Operations' as process, 'Is the weighing scale and Bizerba calibrated as per schedule? And certificate made available near to each Machine?' as question, 'Weighing scales and Bizerba scales must be calibrated as per schedule time and certificate should be display at each scale point.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is All Emergency Contact Details available updated and displayed at Security Entry Gate / point?' as question, 'All Emergency contact details must be available and should display at Security Entry gate and must be display around the DC premises' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all Unwanted Lights fans and other electrical appliances/machinery switched off when they are not being used or required?' as question, 'All unwanted lights and fans,electrical Apliances,machenery must be switched off when they are not being used' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Is all Material Handling Equipment Checklist available for equipments used in DC? Are they checking daily? Records available? (Pallet truck stackers hand Trolleys Reach truck Forklift docking equipment goods lift other machines check list available?' as question, 'MHE checklist available for all MHE. MHE Opeartor must fill the checklist.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Petty Cash maintained at DC are all relevant supporting for receipt and expenses available and documents maintained on daily basis /recorded? Is vouchers available for any advance with proper approval?' as question, 'Petty cash must be maintain with all supporting documents and updated  tracker must be shared to Finance team on daily basis.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Measuring the OKR Performance for all Category as per the parameters defined and is the R and R Program conducted as per the Schedules and reports published to Head office on Time with records maintained in DC and Is the DC OKR presentation sent after validation to HO for Monthly Review on or before 7th of every Month?' as question, 'DC must measure team OKR performance and R & R must be conduct as per schedule and apriciate to best performer and all details must be sent HO team' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the training conducted for underperformance bottom 10% pick efficiency staffs and is the training records available and produced during audit?' as question, 'Training must be conduct for underperformance staff and records must be available in DC' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are the Electricity panels Switch boards maintained properly? Is the earthing done properly?' as question, 'All Safety measures must be follow in DC, No hangings of electrical panels and switch boards is allowed.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'IS Manual Call Point available and is it in working condition? (Alarm Siren Hooter)' as question, 'Manual Call point must be available in DC with working condition' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is required number of lights and Ventilators provided in DC? Are they maintained properly?' as question, 'Required number of lights and Ventilators must be provided in DC' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Individual OKR given to Shift controllers Inventory Controllers Receiving In charge and other roles? Is the same read and acknowledged by all individual and available in record and filed with signature or Mail communication available?' as question, 'Individual OKR must be shared to All G1 staff and G1 staff must be acknowledge the same and filed.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the E and S Audit happening Monthly?' as question, 'E & S audit must be conduct monthly and report must be shared to HO team (HSE & Projects)' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the facility having sufficient safety singes boards displayed in the DC? It is mandatory to have the signages as listed in the guidelines.' as question, 'All safety signage boards must be display in DC as per updated DC layout' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the required number of Fire extinguisher available in DC and placed in the right place as per layout Visible and easily accessible? Is it available with validity?' as question, 'Required number of Fire extingueshers must be available in DC as per HSE suggestion and same should be display as per Layout' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the security Personnel aware or trained on Firefighting equipment handling and First Aid Measures?' as question, 'All Security personnel must aware of fire safety & Fire fighting equipement handling / usage' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC issuing warning letters for any deviation and acknowledgements filed? Is the apology letter for the same obtained from employee and filed in his records?' as question, 'DC must be issue warning letter to staff if any deviations of company process / proceesors' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Manager Checklist- Internal Audit carried out and actioned on Gaps identified and is the reports flashed on time to HO?' as question, 'DC manager checklist must be available and internal audit must be carried out as per schedule and if finds any gaps must be closed' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Daily or weekly pest control Activity / service carried out as per agreed terms? Is Checklist maintained location wise? Is Pest Control service treatment schedule available in DC? Is service carried out as per schedule?' as question, 'Pest control activity checklist must be maintain in DC and pest control activities must be monitor to avaid pest incidents' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in Security Gate? Is the box refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'First Aid Kit must be available at Security gate with all required First Aid contents' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the pest assessment carried out and report shared to central HSE on 10th of every month and gap closure status shared before 20th of every month?' as question, 'pest assessments are typically conducted with reports shared to central HSE by the 10th of every month, and gap closure status is shared before the 20th of every month as part of regular procedures.' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Is Written-off Asset Scrap sale details maintained in DC and are all Quotes sale approval amount recovery details maintained and is the same captured in My Impact and is transaction details matching?' as question, 'Assets scrap sale process must be follow as defined and details must be updated in "my impact" with transaction details.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Monthly Incident Pest Control analysis report available with Project / facility and is all pest incident recorded?' as question, 'Monthly pest contol incident analysis report must be available in DC' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the housekeeping resource utilized properly? Are the DC premises toilets Cafeteria maintained clean and neat?' as question, 'Housekeeping resource must be utilized properly Entire DC premises must be maitain clean and neat always' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is regular training conducted for new implementation/ process or changes? Are the ground staff aware of the process?' as question, 'Regular training must be conduct to All staff on New implementations / process or changes and all staff must be aware of the same' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC opening closing register available along with key register at the security and are the Keys available and surrenders details recorded?' as question, 'DC opening and closing register must be avilable & maintained at security desk.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Security Attendance and Housekeeping Register Available and maintained at Security Desk? Is the Duty Handover happening properly? Is Handover log Book available?' as question, 'Security and house keeping In and out time needs to be captured properly in the register' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all outgoing stock movement recorded in the security outward register with time?' as question, 'All Out going stock movement must be recorded in security Outward register with complete details' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Daily Shift Huddle conducted by DC In charge/Shift Controllers? Is the Monthly MOM recorded and reviewed? Is record for the same available and shown during audit?' as question, 'Daily shift huddle must be conduct and reviewed. All Gaps must be closed.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is there a Visitors Register available and is the security capturing and Monitoring the Movement?' as question, 'Security must capture the visitor deatails & movemnt in visitor register.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security service provider regularly visiting to the site and is a register/Checklist available for the same at the security gate?' as question, 'Security service provider should visit to the site and checklist must be available and update ' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Incident occurrence register (complete shift log book) available and maintained at Security Desk? Is all abnormality/ untoward incidence recorded and available with security?' as question, 'Incident register must be maintain at DC and if any incident occures must be recorded / updated in register' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the staff movement register available and maintained at the security gate? Note: Staff Movement register: Is a register where entry of staff moved out of DC premises on official/ personal on permission is recorded. Brake time movements is not required to be considered in Staff Movement register.' as question, 'Staff movement register must be maintain at staff entry point and details must be recorded.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Does the security frisk all the staffs moving out of DC?' as question, 'Security must frisk all the staffs moving out of DC' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Are all the statutory licenses available valid and displayed in DC notice board?' as question, 'All Updated Statutory licenses must be available in DC and should display in Notice board.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Layout Displayed in and around DC premises with Fire extinguisher spot Emergency assembly spot and emergency Exit point?' as question, 'Updated DC Layout should be displayed around DC premises with Fire extinguesher spot,Emergency exit and Emergency assebly point.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Pest control Layout display in Notice Board and is location details like rodent box glue box etc. available in the layout?' as question, 'Pest control Layout must be display in DC and as per Layout Rodent boxes,glue box/pads must be available' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security conducting regular patrolling in the DC premises? (Inside/outside)' as question, 'Security must be conduct regular patrolling inside the DC' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Has the Inventory Manager reviewed the Final asset audit variance report with the respective RBH/project Manager/DCM and is the Signoff Copy sent to the central team ever month as per the process?' as question, 'Inventory manager must be reviewed Final asset audit variance report with the respective RBH,project amanger and DCM and signoff must be taken' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is MY-MCS call raised for any Breakdown of daily assets with proper validation and details?' as question, 'Mymcs call must be raised for All Breackdown of daily assets' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Daily Weekly and monthly asset Inventory carried out in DC as per process?' as question, 'Daily,weekly and monthly asset audit must be carried out in DC as per process' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Inventory Manager checking all stock transfers is done through MyMCS for any Assets moving out of DC? (repair / transfer to other location)' as question, 'Inventory manager must do stock tranfers thru Mymcs for assets movements.' as recommendation
union select 'Inventory Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all pallets strapped using belts for the stocks stored in the Heavy duty secondary storage location?' as question, 'Pallets should not be placed in the secondary location without strapped' as recommendation
union select 'Inventory Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Does the Stacker wear helmet while using stacker?' as question, 'Helmet is must while using the stacker' as recommendation
union select 'Inventory Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Stacker barricading the stacking are for non-movement of employees while stacking?' as question, 'Stacker must barricade the satcking area for non movement of employees while stacking' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are the Inventory controllers/stacker/Row in-charges conduct checks for Identifying non-salable stock (damage expiry and spoil non-returnable to vendor) from Shelf and initiate write-off from system with proper approvals?' as question, 'non-Salable stock must be removed from Bin,regular bin audit is must.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all the Sacks opened only through scissors?' as question, 'All sacks must be opened only through scissors and DC should be equipped with scissors.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Stock qty available in SKU code without rack Location?' as question, 'All stocks available in the rack must be scannable and linking must be done before stacking.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is details of near expiry stock communicated to the B and M and B2C DC Inventory Manager as per the Shelf life norms / Escalation Matrix and Is the FMCG near Expiry stocks being removed from the shelf as per the shelf life removal norms?' as question, 'Details of near expiry stocks available on the racks should be communicated to B&M and Stake holders.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is purchase return stock handed over happening on time and details informed to receiving in charge?' as question, 'Vendor return stocks must be handover to receiving in charge and complete details must be shared to receiving in-charge' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is stock stored in excess/ Overflow location has pick location assigned? Is regular bin replenishment happening from excess storage location to picking location?' as question, 'Regular bin replenishmnet must be done from Bulk Location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FEFO Followed out in Racks while stacking SKUs and Does Bin Audit happen every day?' as question, 'FEFO must be followed in the racks while stacking and bin audit should be carried out regularly.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Inter DC B2C to B2B ( TO vs GRN) Matching 100%? All reports to Match 100%' as question, 'Inter DC B2C & B2B (TO & GRN) must match 100%' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Pre-Bulk Storage area clean and neat? Is all aisle free for trolley movement?' as question, 'Pre-Bulk storage area must be neat and clean' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the return location active and any stock quantity parked in the location?' as question, 'the return location is typically active, and stock quantities may be parked there temporarily until further processing or redistribution occurs.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is there a designated area demarked for Damage Expired repacking RTV stock?' as question, 'All the movement needs to be followed as per the demarcation' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Internal Audit checklist for all in the Inventory Control Points carried out and actioned on Gaps identified?' as question, 'Internal audit checklist must be available with Inventory Controller and internal audit must be carried out as per schedule and gaps must be closed.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all manual indent PO getting created and GRN''d on same day? For manual indents is the approval obtained from stakeholders?' as question, 'manual indent purchase orders (POs) are generally created and goods received notes (GRNs) are processed on the same day. Approval from stakeholders is typically obtained for manual indents before processing.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Negative Qty SKUs available in Book Stocks ? (Should be nullified daily basis in stock update)' as question, 'Negative quantity SKUs in book stocks should ideally be nullified on a daily basis during stock updates to maintain accuracy and prevent discrepancies.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is less shelf life / expiry / spoilt SKU write off done on daily basis? Does the stacker maintain shelf life norms and removes SKUs as per process?' as question, 'Less shelf life/Expirya and spoilt SKU write off needs to be done on daily basis.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Cycle count happening daily as per schedule? Any discrepancy found in cycle count is recheck carried out by inventory controller? Is the DC having records of daily cycle count activity details and adjustment communication details shared to all stake holders? Also Dose the daily cycle count include count for Skus for all UD and IBND on daily basis?' as question, 'Daily cycle count must be done as per schedule and discrepancy must be adjusted with proper communicationa nd approvals.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any SKU''s stock updated in system multiple times within 30 days? Is bulk stock update done SKU''s without proper approvals?' as question, 'Stock updates for SKUs should ideally occur once within a 30-day period to maintain data accuracy. Bulk stock updates should only be performed with proper approvals to ensure data integrity and compliance with procedures.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the GRNâ€™d stock getting stacked to the respective bin the same day? Is the stacker using stacking app for Stacking?' as question, 'GRN''d stock is typically stacked into the respective bins on the same day, and a stacking app may be used by the stacker to facilitate efficient stacking processes.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the customer rejection / expiry/ spoilt SKUs write off completed daily basis? Is data available?' as question, 'QC and write off process must be follow for all customer returns' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is all Assets accounted in the system â€œMy Impactâ€ and is manual Asset register maintained and updated till date in DC with AMC details? Have all the Assets Numbered as per MY MCS IMPACT asset number?' as question, 'All assets must be accounted/updated in system thru My impact' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is GRN executed in the System in the sequence of Receiving Completion.' as question, 'GRN must be executed based on sequence of receiving completion' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is any Auto PO Edited? Is all More than PO qty being rejected by Receiver? If Edited is the edit done only in the B and M Head ID' as question, 'Auto PO should not be edited by receiving team and More than PO quantity should be rejected' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is pass in slip generated at the time of Arrival of Supply from Vendor/ and is the Is Gate Pass rejection done only by Receiving In charge with valid reason?' as question, 'Pass in slip must be raised for all Vendor at the time of arrival at DC and pass in slip should reject by receiving in-charge if any errors/descipancy' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is separate PO and GRN raised for all B2B SKUs?' as question, 'Separate PO & GRN must be raised for all B2B SKU' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Auto triggered mail configured for all vendor for all transactions GRN GDN PRN? Is the alert Mail sent? If not has the Receiving in charge communicated to the concerns to link email id? Is all GDN raised only through System E-Retail?' as question, 'All vendors /stackholders mail ID''s must be configured to Auto triggered communications for all transactions' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Internal Audit checklist for all the receiving control carried out and actioned on Gaps identified?' as question, 'Internal audit checklist musrt be available with receiving in-charge and internal audit must be carried out as per schedule and gaps must be closed' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiver doing Open Receiving of BBPL - non RTV Stocks in crates?' as question, 'Receiver must be follow open receiving process for All NRTV stocks while receiving' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiver moving the Stock to the receiving staging area after receipt?' as question, 'All received stocks must be moved to receiving staging area after receipt' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Vendor Invoice value and TCS value entered in GRN Screen for applicable vendor Invoices ?' as question, 'the Vendor Invoice value and TCS value are entered on the GRN screen for applicable vendor invoices.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the security Checking and verifying the Vehicle before moving out against any return after receiving? Vendor vehicle must move immediately once unloading happens vendor must place the unloaded material on pallet?' as question, 'Security must verify documents & vehicle while moving out side the gate' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Only "" and "-" Special Characters are allowed while entering the Full Invoice Number in the Invoice value field while doing the GRN. Strictly No other Special Characters allowed ex Blank Space, .(Dot),Comma etc is the Location following the rule?' as question, 'only "" and "-" special characters are allowed in the full invoice number for the Invoice value field during GRN. No other special characters, including blank space, ".", ",", etc., are permitted according to the location''s rule.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Are all RTV stock moved to QC immediately after TI?' as question, 'QC must be carried out immediately for All TI stocks without any delay.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Are all the good stocks moved to the racks and all the damage/expiry stocks write-off from the DC by taking necessary approval?' as question, 'All good stocks must be moved to bins and write off to be carried out for all expiry/spoilt/damaged stocks with necessary approvals.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is purchase return carried out as per the agreement between merchandiser and Supplier? Check based on the list available with the Inventory Controller?' as question, 'PRN must be carried out as per agrement between merchandiser and supplier' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the PRN gate pass in save mode till stock handover to vendor? No pile up in DC allowed' as question, 'PRN stocks should not piled up in DC and PRN gate pass should not be in save mode.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the write off Posted in system immediately after QC passed with appropriate remarks?' as question, 'Writeoff must be carried out immediately once QC process completion' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the Kirana Hub Returns TI happening 100%?' as question, 'RTV''s TI must be carried out thru scanning & variance must be escalated to All  stakeholder.s' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the receiving In charge conducting check for Non-RTV and RTV Vendor stocks before doing write off?' as question, 'Receiving in-charge must cross check RTV & NRTV stocks before book in writeoff.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is all pending GRN Getting Monitored? Is Same Day GRN happening and is any GRN found in Save Mode?' as question, 'All pending GRN''s must be monitor and All GRN''s must be complete in same day' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the second sale SKUs moved to second sale room and stacked properly? Is the Write-off sku Qty Vs Second sale Qty matching? Except perishable and liquid' as question, 'Second sale products must be moved to second sale room and should stake properly and second sale qty should not be exceed writeoff quantity.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the Kirana Hub Returns TI happening 100% thru scanning? Is the RTV vs TI variance escalated and reconciled? Is the PRN vs TI variance escalated to DC Head and reconciled?' as question, 'RTV vs TI must be match 100%' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is Manual Asset inward register maintained at DC and is the Receiving In charge ensuring the availability and are all movements recorded and Register validated weekly by Project/ receiving In-charge DS / DC Manager and Checked signature Available.' as question, 'Manual asset inward register must be available and all incoming assets must be record in register and required HOTO process must be follow and manual register vs My impact must be match' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'BY EOD is the MRP change report checked and shared to HO and B and M?' as question, 'MRP changes report must be shared to all stakeho;ders by EOD' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is Daily MRP Complaints analyzed and communicated for rectification to buyer?' as question, 'Daily MRP complaince analysis must be done and same should be communicated to B&M team on daily basisi' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the BBPL PRN policy followed as per latest process? Are they following Weekly? Is tracker available?' as question, 'BBPL prn policy must be followed as per process and tracker made available for the same.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Does the Vendor report with valid Purchase order reference and Invoice to security at the time of arrival for delivery at gate? Does the security cross check the details with vendor schedule and Is the details of unscheduled vendor Captured at the Security point?' as question, 'Security must be check all required valid documents at the time of vendor arrival and while raising pass in slip,if any erros/gaps must be informed to receiving in-charge' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Fixed Vendor schedule shared by B and M? Is any Changes Amended and same available with the receiving In charge?' as question, 'Updated Fixed vendor schedule should be available with receiving in-charge,is any changes in schedule same details must be available with receiving in-charge' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiving In charge sharing a copy of Vendor Appointment / Schedule to security on daily Basis?' as question, 'Updated Vendor schedule details must be shared to Security on daily basis' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiver mentioning the GRN and GDN ref number on the Invoice copy both on Vendor and buyer copy? (GDN if applicable once GRN Done on the Buyer Copy in supplier Copy only GDN Number with acknowledgement)' as question, 'Receiver must be mention GRN & GRN ref number on both Vendor and buyer copy' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Vendor Cut off time maintained and received before Cut off Time? Or are alternative arrangements made?' as question, 'Vendor cut off time must be follow and alternative arrangements must be made' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is all discrepancy again the receiving, GDN Raised and the same line item getting highlighted using highlighter on all the Copies with GDN number GDN Value, (Note: details must be mentioned on all Original, Duplicate and triplicate invoice copy send by the vendor)' as question, 'all discrepancies against the receiving, GDN raised, and the corresponding line items are highlighted using a highlighter on all copies with the GDN number and value. Details must be mentioned on all original, duplicate, and triplicate invoice copies sent by the vendor.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiving happening as per category shelf life Norms? For any product received below shelf life norms is the receiving approved by RBH/B and M Head?' as question, 'Defined shelf life norms must be follow 100% while receiving stocks and RBH / B&M approval must approval for below shelf life stocks receiving' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is the GRNGDN Scanned copy and GDN Handover photo stored in Common G-drive, and PRN Acknowledge and HANDOVER IMAGES also upload in the common G-drive?' as question, 'the GRN GDN scanned copy and GDN handover photo are stored in a common G-drive, and PRN acknowledge and handover images are also uploaded to the common G-drive' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is the receiving team ensuring to mention the Invoice Value less (-) GRN value, and less (-) GDN Value on all the 3 copies ( Vendor, Accounts and DC Copy)?' as question, 'the receiving team ensures to mention the invoice value less (-) GRN value and less (-) GDN value on all three copies (Vendor, Accounts, and DC Copy).' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is the PRN & GDN Ack Process followed by the Store Team?' as question, 'Confirm adherence to the PRN & GDN acknowledgment process by the store team.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the approval mail obtained from B and M for receiving unscheduled vendors? Or is the detail of unscheduled vendors receiving for the day sent to B and M?' as question, 'B & M approvals must be received for unschedule vendors for receiving (emergency)' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is the BB Inward sealÂ available on the Accounts Invoice copy?' as question, 'it is important to ensure that a seal is placed on all the accounts invoices copies' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the GRN Invoice sent to Finance daily basis thru courier or by Hand? Is the tracker maintained and made available during audit?' as question, 'All GRN''D invoices must be sent to finance team on regular basis and tracker must be maintain for the same' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operation' as process, 'Is the last 6 Months of PRNGDN Hard Copy records maintained in Store?' as question, '6 month documents should be maintained' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'For BBPL PRN stocks is acknowledgement attained from QC person?' as question, 'BBPL PRN stocks must be acknowledged and attained by QC person' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the write-off SKUs signed off from inventory controller before moving to second sale or dump?' as question, 'All write-off products must be signed off by inventory controller before moving to second sale.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Quotes available for Dump Sale and Carton Box sale in DC? Is Dump sale carton boxes disposal movement checked by the security and happening in presence of Security and is all movements recorded in register? And are the carton/scrap sales proceeds accounted in to DC petty cash?' as question, 'Defined second sale process must be follow. 3 Quotes must be availble for any dump sale/carton box sale.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is all Asset handover carried out with proper signoff between DC and Projects after every transaction and is the signoff records available and maintained in DC?' as question, 'All Assets HOTO process must be follow with proper signoff between DC & projects after every transaction with proper documentation' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any unaccounted excess stocks found in DC ?? (sys vs Physical)' as question, 'DC ahs to maintained system vs physical correctly' as recommendation
union select 'LMD Process' as process_owner, 'OC NC' as process, 'EP CEE''s shift wise roster signup sheet is updated or not' as question, 'CEE shift roster signup should be updated' as recommendation
union select 'LMD Process' as process_owner, 'OC NC' as process, 'Top performing CEE names on notice board every weekly/TDP (Month / TDP Details should be mentioned)' as question, 'Top performing CEE names should be displayed' as recommendation
union select 'LMD Process' as process_owner, 'OC NC' as process, 'Was the Hired vehicle report sent to Kirana head & TE on a daily Basis' as question, 'Hired vehicle report should be sent to Kirana head and TE' as recommendation
union select 'LMD Process' as process_owner, 'OC NC' as process, 'Are Vans parked in an orderly manner?' as question, 'Vans should be parked properly' as recommendation
union select 'LMD Process' as process_owner, 'OC C' as process, 'IBND details for the last TDP? with TOP 5 CEE names contributing to the IBND' as question, 'IBND details should be displayed in notice board' as recommendation
union select 'LMD Process' as process_owner, 'OC C' as process, 'Stock return to DC - acknowledgement hard copy or soft copy is maintained?' as question, 'Stock return acknowledgement copy should be maintained' as recommendation
union select 'LMD Process' as process_owner, 'OC C' as process, 'Is the dispatch area neat and organized' as question, 'Dispatch area should be neat and clean' as recommendation
union select 'LMD Process' as process_owner, 'OC C' as process, 'Is the SK sending mail to HM/KH, with details of CEEs with IBND for the day?' as question, 'SK should send IBND detail mails to HM/KH ' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'G1 Management Roster(only Hub) on the notice board' as question, 'G1 roster should be displayed in notice board' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'Does the store have any cash variance for more than 48 HRS?' as question, 'Store should be closed any variance within 48 hrs' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'Is petty cash statement sent to accounts daily -check the latest shared email' as question, 'Petty cash statement should be shared to Accounts team daily basis' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'Where the incidents of previous VCC & Transport audit cleared over email within 10 days(Previous audits response email or action plan)' as question, 'the incidents of previous VCC & Transport audit cleared over email within 10 days' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'There are no collection outstanding, older than 48 hrs' as question, 'Store should be closed any variance within 48 hrs' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'Are empty crates kept in specified area ?' as question, 'empty crates should be kept in specified area' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'There are no stocks lying in the RTV area of previous day' as question, 'Ensure that not stocks lying in RTV area' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager C' as process, 'Is the OC / HM logged in using his/her login (should not be logged in using others login)' as question, 'Ensure should not be logged in using others login' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager NC' as process, 'Has MCIP indents been sent on time before 7th of Every month.' as question, 'ensure MCIP indents been sent on time before 7th of Every month' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager NC' as process, 'Is Cash Bag Available With CEE?' as question, 'Ensure that cash bag should be available with CEE' as recommendation
union select 'LMD Process' as process_owner, 'Hub Manager NC' as process, 'Is any order shifted without the approval of Kirana or HORECA regional Head?' as question, 'Shifted order approvals should be taken from Regional Head' as recommendation
union select 'LMD Process' as process_owner, 'Transport C' as process, 'Van-Is the driver wearing the seat belt ( Applicable for 4W only)' as question, 'Van driver should be wear seat belt' as recommendation
union select 'LMD Process' as process_owner, 'Transport C' as process, 'Van-Does the Vehicle having valid Vehicle Insurance' as question, 'Vehicle should be have valid documents' as recommendation
union select 'LMD Process' as process_owner, 'Transport C' as process, 'Van-Does the Van have provision for Mobile charging with Cable?' as question, 'Mobile charging with cable should be placed in vehicle' as recommendation
union select 'LMD Process' as process_owner, 'Transport C' as process, 'Van-Does the Driver have Valid Driving license' as question, 'Vehicle should be have valid documents' as recommendation
union select 'LMD Process' as process_owner, 'Transport C' as process, 'Van-Does VAN has a proper Back Door with a functional lock?' as question, 'VAN has a proper Back Door with a functional lock' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van- Valid RC / Fittness certificate and OEM (in EV vehicle) is avilable?' as question, 'Vehicle should be have valid documents' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Does VAN have proper Head Lights' as question, 'VAN should proper Head Lights' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Does VAN have proper Number plate on all 4 sides' as question, ' VAN should proper Number plate on all 4 sides' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Does VAN have proper Back Lights (Brake Lights)' as question, ' VAN should proper Back Lights (Brake Lights)' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Does VAN have proper Back Cabin Light' as question, ' VAN should proper Back Cabin Light' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Is the delivery trolley available?' as question, 'Trolly should be available with vehicle' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Does the vehicle have Pollution Under Control Certificate' as question, 'Vehicle should be have valid documents' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Is vehicle no.available in master vehicle tracker' as question, 'Vehicle number should be available inmaster' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Is first aid box is avilable with required medicine' as question, 'FAB should be kept in the vehicle' as recommendation
union select 'LMD Process' as process_owner, 'Transport NC' as process, 'Van-Is first Fire extinguishers available?' as question, 'Fire extinguisher should be placed in the vehicle' as recommendation
),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'T1 B2B%'
   and store_id = @{{:BB T1 B2B Audit - Single Audit.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB T1 B2B Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB T1 B2B Audit - Single Audit_T1 B2B Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T1 B2B Audit - Single Audit
-- Dashboard: T1 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:56
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'T1 B2B%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE NULL
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE NULL
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE NULL
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE NULL
              END) AS non_critical_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          critical_actual_score AS "Critical Actual Score",
                                          critical_max_score AS "Critical Max Score",
                                          non_critical_actual_score AS "Non-critical Actual Score",
                                          non_critical_max_score AS "Non-critical Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT *
FROM with_audit_numbers
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
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T1 B2C Audit - All Past Audits_T1 B2C Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T1 B2C Audit - All Past Audits
-- Dashboard: T1 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:59
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Process Audit Checklist T1%'
  and store_id = @{{:BB T1 Audit - Single Audit.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" <= @{{:BB T1 Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T1 B2C Audit - Recommendations_T1 B2C Process Audit Report.sql

**Tables referenced:** B, Central, DC, DCM, Damage, FV, GDN, IH, LOB, Obstructions, QC, RBH, Regional, Shelf, Vendor, any, approved, audit_submitted_at, base, checkpoint_master_sheet_table, city, cob, crates, current_timestamp, discount, employee, employees, excess, finished, obstruction, off, outside, pest, pick, raw, reco_database, respective, smell, stains, system, the, vehicle, vendor, vendors

**Columns needing snake_case conversion:**

- `controllersstackerRow` -> `controllersstacker_row` (alias: `controllersstacker_row AS "controllersstackerRow"`)

- `degC` -> `deg_c` (alias: `deg_c AS "degC"`)


**Original Query:**

```sql
-- Data Source: BB T1 B2C Audit - Recommendations
-- Dashboard: T1 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:58
-- ============================================================

WITH reco_database as (select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'After picking are all chiller boxes moved to the respective Staging area (5K, BB Now, T4, Fresho & BBD?' as question, 'Ensure that the cold room chiller boxes have been appropriately moved to their designated staging areas after picking, ensuring alignment with the demarcated areas.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Are all Chiller & Frozen articles covered with required number of gel Packs? Is Picker picking required number of PCM Packs and properly arranging it inside insulated box with correct combination as per cold chain process? (Minimun 6 Big PCM pads required for 1 Consta box)' as question, '1.Gel Pack Coverage:'||chr(13)||chr(10)||'Ensure all Chiller and Frozen articles are stored with the required number of gel packs.'||chr(13)||chr(10)||'Maintain detailed records specifying the quantity of gel packs used for each article.'||chr(13)||chr(10)||'Regularly train staff on the correct gel pack placement and handling procedures.'||chr(13)||chr(10)||'2.Syntax Box Usage:'||chr(13)||chr(10)||'Use syntax boxes as designated for the storage of Frozen articles.'||chr(13)||chr(10)||'Regularly inspect syntax boxes for damage and replace any that are not in proper condition.'||chr(13)||chr(10)||'Train staff to follow the correct procedures for utilizing syntax boxes.'||chr(13)||chr(10)||'3.PCM Pack Handling:'||chr(13)||chr(10)||'Train pickers to pick the correct number of PCM packs for Chiller and Frozen articles.'||chr(13)||chr(10)||'Instruct pickers on the proper arrangement of PCM packs inside insulated boxes, adhering to the cold chain process.'||chr(13)||chr(10)||'Regularly update staff on any changes to PCM pack handling procedures.'||chr(13)||chr(10)||'4.Documentation Check:'||chr(13)||chr(10)||'Maintain accurate and up-to-date records of gel pack, syntax box, and PCM pack usage.'||chr(13)||chr(10)||'Clearly document deviations or exceptions in the packing process.'||chr(13)||chr(10)||'Make documentation accessible for audit purposes.'||chr(13)||chr(10)||'5.Training Verification:'||chr(13)||chr(10)||'Keep training records current and accessible.'||chr(13)||chr(10)||'Ensure that all staff involved in the packing process are trained in the correct usage of gel packs, syntax boxes, and PCM packs.'||chr(13)||chr(10)||'Periodically conduct refresher training sessions.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Cold rooms/ Chiller/ Freezer maintained clean & neat? Is the Temperatures maintained at desired level? Is the Ice formation found in cold room? Refer the records maintain on temperature and visual check on cleanness?' as question, '1. Ensure Cleanliness Maintenance:'||chr(13)||chr(10)||'Regularly clean and maintain Cold rooms/Chiller/Freezer.'||chr(13)||chr(10)||'Keep records of temperature and conduct visual checks for cleanliness.'||chr(13)||chr(10)||'2. Temperature Monitoring:'||chr(13)||chr(10)||'Regularly monitor and record temperatures in Cold rooms/Chiller/Freezer.'||chr(13)||chr(10)||'Ensure temperatures consistently align with desired levels.'||chr(13)||chr(10)||'3. Prevent Ice Formation:'||chr(13)||chr(10)||'Implement measures to prevent ice formation in cold rooms.'||chr(13)||chr(10)||'Conduct regular visual checks and maintain temperature records for audit compliance.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is DC Team well trained on Cold Chain Process & are the staff aware on the process to be followed? (Refer the training mail)' as question, 'Ensure all pickers, stacker and working under the cold chain is trained and training records been maintained. ' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Ice Creams packed and dispatched to 5K , BB NOW and Other LOBs as per cold chain process?' as question, 'Ensure during the picking and ensure cleaned chiller box hard frozen PCM are used for picking and no damages should be pick. ' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Plate Freezer process followed?  (Is the plate freezer Maintained Clean & Neat? Is the lock found intact? Is MYMCS/ Zoho call raised for any damage to the plate freezer.  Are they using Plate freezer in batch wise; and is the batch details captured in the register/ Know App? Is Hand Gloves used while placing and retrieving gel pads from the Plate Freezer? is the plates removed from the Plate freezer and cleaned with dry cloth after production of every batch? Are plate freezer doors kept closed and locked while running?)' as question, '1. Plate Freezer Process Adherence:'||chr(13)||chr(10)||'Follow the designated Plate Freezer process consistently.'||chr(13)||chr(10)||'2. Maintenance of Cleanliness:'||chr(13)||chr(10)||'Regularly clean and maintain the Plate Freezer in a neat condition. Ensure the lock is consistently intact.'||chr(13)||chr(10)||'3. Damage Reporting Protocol: Promptly raise MYMCS/Zoho calls for any Plate Freezer damage.'||chr(13)||chr(10)||'4. Batch-wise Usage Record: Use Plate Freezer in batches and maintain batch details in the register/Know App.'||chr(13)||chr(10)||'5. Safety Compliance:'||chr(13)||chr(10)||'Always use hand gloves when handling gel pads.'||chr(13)||chr(10)||'Clean plates with a dry cloth after every batch.'||chr(13)||chr(10)||'6. Door Closure and Lock Protocol: Keep Plate Freezer doors closed and locked during operation.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is the Color coding for ice boxes getting followed?' as question, 'Follow the CF picking process as per below'||chr(13)||chr(10)||'i. Blue PCM - Frozen orders'||chr(13)||chr(10)||'ii. Grey PCM - Chilled and cutveg orders'||chr(13)||chr(10)||'iii. Red PCM, Syntex & Consta - Fresho meat' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is the picker picking PCM Packs only from the horizontal Freezer @ -25o at the time of packing of orders?' as question, 'Ensure that the PCM pads are picked from the horizontal freezer or frozen room. Pickers should not pick directly from the plate freezer.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'PPEs (Hand gloves/Safety Shoes/Jacket) - 1. PPEs are in good condition 2. PPEs issue register/ Know App is maintained 3. All Employees are using PPEs at the time of Entering cold room 4. PPEs are stored in proper/Dedicated place 5. Awareness signage board is displayed 6. Sufficient PPEs are available' as question, 'Ensure PPEs are good condition' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is Crate QC done for all LOB Crates ? staged in dispatch stagging area and Is QC report sent to the respective active LOB''s? are they taken the action against of discrepency?' as question, 'Ensure 100% crate QC is carried and sending communication to sending location and quick action must be initiated for the discrepancy and preventive action must be in place.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the crates washed cleanly? Are the old stickers removed from crates while washing? Is the same dried and given for picking?and also is the picker removing if any stickers are available on the crate?' as question, 'Before beginning the picking, make certain that all stock is in clean crates and that any old labels have been removed.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the egg picked; moved to outbound staging area and stored in the separated demarked area; After Crate QC; is a Signage Board on the pallet as (Eggs Pallet- handle with Care) displayed; inform outbound team for Dispatch as per the best practice process circulated?' as question, 'Shift controller has to ensure that egg stocks should be dispatched seperately with proper demarkation in IHV to avoid damage' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the Internal Audit checklist carried out and actioned on Gaps identified and are they sharing the report to Central SCM spoc , DC manager & RBH?' as question, 'Conduct every month internal audit and communicate those mails to respective stakeholders with the gaps and actino plan' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the Trolley used for picking by the picker always while picking?' as question, 'Ensure that the picker always uses a trolly while picking. Make certain that there is no baby picking.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Are Invoice raised for all Inter - DC movement and dispatched along with Invoices in a vehicle? (DC to T2, 5K and other locations)' as question, 'Ensure invoice is generated and disatched stock along with poper documets' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Is any inter DC Order stocks dispatched partially to 5k , BB NOW, Fresho & BB Daily ? Are they communicated to the locations before dispatch ?' as question, 'Ensure partially dispatches is well communicated to receiving location and no gaps in the GRN and customer deliveries.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Is E-Way bill Generated for all the outward movement that required mandatory E-bill supporting as per the respective state law. Also; is the E-way bill number entered in the TMS -GP for all E-way bill raised Movements? E-way Bill is Mandatory for all the out-ward movement where the document value is equal to or More than 50;000- for all the states expect Mumbai and Kolkata; where the value is equal to or more than 100000-' as question, 'Ensure e-way bill is generated for and updated in the TMS Gate Pass report for all E-way bills numbers are available for Value is >50K' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is all orders cancelled before 12 mid-night  removed in the DC and send communication to T4 Team?' as question, 'Before dispatching, remove all cancelled order crates that were cancelled before 12:00 a.m. in DC and send those details to the T4 team through mail' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the crate QC done for all the T4 dispatches from the DC' as question, 'Ensure to complete t4 crate qc 100%' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the DC sending daily mail to T4 team for Picked crates vs QC vs GP details ?' as question, 'Ensure to match picked vs qc covered vs gp crates count.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the loading is happining from the DC as per the store wise ?' as question, 'Ensure to load the T4 vehicle as per below. The nearest store crates should load last in the vehicle, while the longest store crates should load first.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'Is the return stock unloaded? As soon as vehicles reach DC.' as question, 'Ensure to unload the return stocks from vehicle once reported to dc' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'Is the route charger handed over cash to OC and acknowledgment taken.' as question, 'Ensure to take acknowledgement if route-incharge carried the cash' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Are they checking  CC supply qty before buying the F&V stock from vendors , Vandor stock can buy if the CC doest not suppy the ident qty ?' as question, 'FV stock should not be purchase from vendor ifstock available in CC' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Are they received any F&V stock with a higher Cost Price (CP) compared to the CC inward for the respective region on the same day? Only they can buy if the CC does not supply the indent QTY?' as question, 'If the stock is already available in DC or CC arrival, do not receive it from the vendor higher CP' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Does the (DC) exceeded the purchase limit of 10% on indent Qty from vendors/farmers?' as question, 'Ensure that you acquire the most stock from the CC and that you get less than 12% of your stock from the direct vendor.' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is any F&V SKU received on the same day with different Cost Price (CP) stock? If receiving happens escalated through mail on same day?' as question, 'Receiving incharge has to ensure fv stocks which is receiving from vendor that should be same CP. If any CP changes he as to escalate to B&M through mail' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is Same SKU with different CP inwarded on same day from the same supplied being Monitored and Such Difference escalated to B&M?' as question, 'Same SKU with diff cp should be escalated on same day to B&M' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'is the Auto PO edited only Buyer or cat head ? Is the Receiver discussed with B&M team and take approval  for if any Excess qty received ?' as question, 'Receiving incharge has to ensure that POs edit should be done only by B&M Head' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is the B&M team actively sending emails and addressing the unpicked GDN cases, ensuring clearance of GDN stock within the 7-day threshold? In the event that stock remains unpicked for more than 7 days from GDN generation, is it the practice to dispose of the stock, and is it disposed from the GDN area?' as question, 'Ensure that the GDN is handed over to the vendor within 7 days or the stocks are disposed of, although mail communication with B&M is essential.' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is the F&V PO raised for Indent Qty before vendor arrival?' as question, 'Ensure that the PO is created prior to the vendor''s arrival in DC.' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Are the details of the pullback stock confirmation from the B&M team shared with the Central SCM Inventory and the Regional Inventory manager?' as question, 'Ensure that all pullback communication emails are marked with the Central Inventory team and the regional inventory manager.' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Has any stock been received for the pullback stock initiated by the B&M, considering various reasons such as Product Recall, Excess Inventory, Seasonal or Clearance Sales, etc.?' as question, 'All the Pullback PRNd Skus list must be available in B&M Mail' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Is the confirmation from the B&M team regarding ICM removal for the pullback SKUs recommended for PRN to prevent the generation of the next indent for these SKUs?' as question, 'Ensure that the pullback PRN is raised following the confirmation of ICM removal.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is 2 Times Energy drinks served to staffs in Summer Season ?' as question, 'Ensure to provide 2 times energy drinks in summer season' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the 3-4 times Tea & Snacks served in5K DS ? (Snacks mandatory for night shift employees)' as question, '3-4 times tea & snacks should be served in 5KDS. Snacks should provid in night shift' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Breakfast, Lunch and Dinner served for Staffs in DC for Rs.10/-? (Breakfast for all staffs, Employee can avail either lunch or dinner)' as question, 'Ensure the Breakfast, Lunch and Dinner served for Staffs in DC for Rs.10/-? (Breakfast for all staffs, Employee can avail either lunch or dinner)' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Bus Facility arranged for dropping Morning shift employees and pick up night shift employees, drop night shift employees and pick up after noon shift employees? (Applicable only for DC-Puzhal-Chennai, DC-Pune, DC-Chandu-NCR, DC-Bhiwandi-Mumbai, DC-Sakrial -Kolkata, DC-Ahmedabad, DC-Jigani-Bangalore)' as question, 'Ensure that Bus facility for pickup and drop for the employees for applicable DCs' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Changing Room Available for Woman Staffs ? (Applicable wherever Woman Staffs working)' as question, 'Ensure that the Changing Room Available for Woman Staffs. (Applicable wherever Woman Staffs working)' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the DC having Tie up with nearest Creche (Baby Care) within 1KM radius ?' as question, 'Ensure the DC having Tie up with nearest Creche (Baby Care) within 1KM radius ' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Drinking Water dispensers installed in every 30 Sqmtrs and Water refilled timely ?' as question, 'Drinking water dispenser should install every 30 sqmtr' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Employee Help Desk and Grievance redressal desk available in the DC?' as question, 'Ensure that Employee help desk and GR desk should available in DC' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Lockers provided to each Employees in the Shift?' as question, 'Ensure that lockers should be provided for all the staffs' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Rest Rooms provided to DC Staffs ? ( well ventilated with Fans , Benches , Minimum 2 Bunk Beds in DS)' as question, 'Rest rooms should be provided for DC staffs' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Segmented plates, spoons, water dispenser, hand wash basin, dustbins available and efficient waste disposal, Hygienically maintained ?' as question, 'Ensure that the Segmented plates, spoons, water dispenser, hand wash basin, dustbins available and efficient waste disposal, Hygienically maintained ' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Washrooms available in DS Premises and Hygiene accessories available as per list? (Male - Minimum 2 urinal and 2 wc per 100 employee, 1 water closet (Indian) and 1 water closet for 25 women (Sanitary waste disposal, dustbin, health faucet, wash bas' as question, 'Ensure that Male - Minimum 2 urinal and 2 wc per 100 employee, 1 water closet (Indian) and 1 water closet for 25 women (Sanitary waste disposal, dustbin, health faucet, wash basin)' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Water Cooler / Dispenser serviced every 6 months once and water Tank maintained cleanly without dust inside as well outside?' as question, 'Ensure that Water Cooler / Dispenser serviced every 6 months once and water Tank maintained cleanly without dust inside as well outside' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Are all assets in good condition, and are all electrical points safe and secure? Check physically' as question, 'Ensure that all the assets are in good condition' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Are the bunker beds in good condition and functioning properly?' as question, 'Ensure that bunker beds are in good condition' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Are the CCTV cameras in working condition and do they have a backup of 15 days? Check in the server room.' as question, 'Ensure that dormitory having CCTV cameras with minimum 15 days backup' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Are the installed fire extinguishers in active and good condition, and is the signboard displayed for the same?' as question, 'Ensure that installed FE with good condition with signage boards' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Do the dormitory facilities comply with the SOP/process? Check the approved drawing.' as question, 'Ensure that dormitory facilities comply with the SOP' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Does the dormitory have a storage room/locker facility to store staff belongings?' as question, 'Ensure that storage room/locker in dormitory to store staffs belongings' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Have all the signboards been displayed as per SOP/process?' as question, 'Ensure that all the sign signboards dormitory' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Have separate shoe racks been provided for staff shoe storage purposes, and are they in good condition? Check the rack/stand.' as question, 'Ensure that separate shoe rack in dormitory' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Is a monthly facility audit carried out? Gap closure details need to be checked.' as question, 'Ensure that monthly facility audit should be carried out' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Is the area in good hygienic condition? Physically walk and check the cleaning checklist' as question, 'Ensure that dormitory in good hygienic condition, Maintain the checklist' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Is the restroom/toilet in a good, hygienic condition, and equipped with a water facility?' as question, 'Ensure that restroom/toilet in good, hygienic condition' as recommendation
union select 'BB Engagement Model' as process_owner, 'Dormitory Facility and Management' as process, 'Is the Weekly Hygiene Checklist maintained and verified by location (DCM or PM)?' as question, 'Ensure that maintain the weekly hygiene checklist and DCM/PM should verify' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'For Poor Performance Employee who is in the bottom 10% whether the refresher training has been imparted? (Employees should not be in bottom 10% consequently for 3 months he should not be asked to leave for this reason with out providing refresher training' as question, 'Ensure that poor performance training should be conducted every month' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'If an employee resigns, does the manager have a one on one to understand the reason behind this decision and try to retain the employee. Managers should follow the exit process laid down by the Company?' as question, 'Conduct One-to-one with the resigned employees and understand the reason behind this decision' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'Is there any employee exit allowed without a proper investigation in the presence of the Regional HR Head? ( A detailed investigation report will be prepared by regional HR. This will be part of HR audit checklist. All such exits require Business Heads approval' as question, 'Ensure that detailed invenstigation report will be prepared for any employee exit' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are all the Line Managers/Supervisors aware of policies and benefits provided by bb like number of leaves, bb TRUST etc. and communicate the same to the Associates' as question, 'Ensure that all the line managers/Supervisors aware of policies and benefits' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are Managers providing timely feedback to the employee? He should take time to explain to the employee where he is going wrong and coaches him on what is correct in a professional and respectful manner.' as question, 'Manager should take time to explain to the employee where he is going wrong and coaches him on what is correct in a professional and respectful manner.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are the employees forced to do OT?' as question, 'Don''t force employees to do OT' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager appreciate the employees when they do a good job and are the Managers participating actively in R&R and engagement events, to make employees feel that they are valued?' as question, 'Ensure that managers actively engaging R&R' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager propagate a culture of respect?' as question, 'Ensure managers that propagate a culture of respect' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers ensure that the employees'' duty hours are maintained? Managers should also ensure that lunch timings for their reportees are not unnecessarily delayed and are maintained consistently.' as question, 'Managers should  ensure that lunch timings for their reportees are not unnecessarily delayed and are maintained consistently.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers have weekly meetings with the associates where they should talk about targets, etc. These meetings should have action points which are minuted and status on the action points should be provided in the next meeting' as question, 'Managers should conduct weekly meetings with associates to improve productivity' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers lead by example?' as question, '0' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Dose the Managers in DC restrict OT to 2 hours post normal shift timings to ensure that the Associates are not overworked?' as question, ' Managers should ensure in DC restrict OT to 2 hours post normal shift timings to ensure that the Associates are not overworked' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is Managers having one on one with any employee who is in the bottom 10% in the department(DC). The manager should try to understand the reasons behind the gaps in performance and if the employee needs any help. This meeting should be held Weekly till the' as question, 'Managers should have One-to-one with bottom 10% employees' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers always present in Daily Huddles and spread awareness on organizational targets, policy changes etc.,' as question, 'Line managers should be available in daily huddles and spread awareness on policy changes' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers being fair in granting leaves?' as question, 'Line managers should be fair in granting leaves' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers spending 1 hour with the new joiner on his 1st day in the floor after NHT (New Higher Training)/Induction to inform him about job responsibilities, culture at bigbasket and any other information that makes his job easy' as question, 'Ensure line manager should spend 1 hr with new joiners' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Air curtains and pvc strips are available at entrances and doors are equipped with self closing mechanism?' as question, 'Air curtains and PVC strips should be available in entrance' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Are all the assets clean and kept in the designated location?' as question, 'All assets should be clean and keep in the designated location' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Are Legal Metrology stamping available for all weighing balances and is the certificate available at the Butchery?' as question, 'Ensure that stamping should be available all weighing stones and certificates also need to be maintain for that stones' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Does Butchery have an updated FSSAI license displayed at a Notice board?' as question, 'Updated FSSAI license should be displayed in notice board' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is Adequate ventilation is provided within the premises?' as question, 'Adequate ventilation required in premises' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is QC person carrying out calibration for all weighing scales & Bizerba using certified dead weight (Standard weight stone certified by weight & Measurement Department? Is all the Reports available?' as question, 'Ensure to follow calibration process daily basis' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is the Labour license available and displayed at the notice board?' as question, 'Labor license should be displayed in notice board' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'The premise is well equipped with chilling room, freezing room, freezer store or freezer as per the operations and fitted with temperature measuring or recording devices.' as question, 'Ensure the premise is well equipped with chilling room, freezing room, freezer store or freezer as per the operations and fitted with temperature measuring or recording devices.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Dust bins being provided with dust bin bags? (Exception plastic banned cities) Is all Housekeeping tools & cleaning aids kept in designated place? Are any Butchery crates used for disposing process waste? Is all process wastage discarded into closed dust bins?' as question, 'Ensure all Dust bins being provided with dust bin bags (Exception plastic banned cities) Is all Housekeeping tools & cleaning aids kept in designated place Don''t use Butchery crates used for disposing process waste. Ensure is all process wastage discarded into closed dust bins' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are Butchers wearing PPEs (Hand gloves, Body Aprons, Head Cap and Shoes during Meat Processing? Jackets or aprons are cleaned and sanitised daily? Is the Nitrile gloves provided for all other butchers?' as question, 'Are Butchers should wear PPEs (Hand gloves, Body Aprons, Head Cap and Shoes during Meat Processing Jackets or aprons are cleaned and should be sanitised daily. Ensure Nitrile gloves provided for all other butchers' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are sufficient Fire Extinguishers available?' as question, 'Ensure sufficient Fire Extinguishers are present on-site.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is a First Aid box present in all butchery? With the listed medicine ?' as question, 'First aid box should be refilled as per HSE guidelines' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all fire safety system available (Fire extinguisher, Fire alarm system )in good working condition ? Check service details?' as question, 'Ensure all fire safety system working good' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all Safety signages (Butcher Related) Displayed and are the signages in Good Condition?' as question, 'Ensure all safety related signage board should be displayed in production area' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Personnel hygiene facilities are available including adequate number of toilets ( not opening directly into processing area), hand washing facilities and  change rooms.' as question, 'Ensure to maintain clean toilets and other hyiene facilities including hand washing facility in change rooms' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest control program is available & pest control activities are carried out by trained and experienced personnel. Check for records.' as question, 'Pest control activity should be carried out and maintain the required records during the audit' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Premise  has facility for  storage of waste &  inedible material such that contamination with food is avoided and is also free from any pest activity.' as question, 'Ensure to store waste material free from pest activity' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'All electrical equipment''s, accessories, panels and in good condition and cautionary sign boards?' as question, 'All electrical equipment''s, accessories, panels and in good condition and cautionary sign board should be available' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Chicken Cutting Machine equipped with Safety Guard and are all butchers using the Machine without bypassing?' as question, 'Are all Chicken Cutting Machine should be equipped with Safety Guard and are all butchers should be used the Machine without bypassing' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per the Butchery Process?' as question, 'Ensure Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Processed stocks kept in SS bins & stacked in racks provided? Is FIFO followed for dispatch?' as question, 'Ensure all Processed stocks kept in SS bins & stacked in racks provided. Is FIFO followed for dispatch.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are appropriate documentation and records maintained for a period of one year or the shelf-life of the product, whichever is longer?' as question, 'Shelf life documents should be maintained as per process' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are finished products properly packed and sealed with no defects in the seal, meeting proper labeling requirements according to FSSAI and Legal Metrology norms?' as question, 'Ensure all finished products should be packed propelry' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are incoming materials, semi-final products, and final products stored based on their temperature and humidity requirements in a hygienic environment? Is FIFO & FEFO practiced?' as question, 'All the products should be stored as that particulr product specific temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are monthly trend analysis and quarterly audit reports readily available?' as question, 'Monthly trend analysis should be maintained' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are raw materials inspected for food safety hazards, including temperature checks for products like frozen goods and monitoring temperature throughout the supply chain, especially for fish and seafood?' as question, 'Ensure to inspect raw materials without fail' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are recalled products held under supervision and either destroyed or reprocessed/reworked in a manner that ensures their safety? Are records checked for compliance?' as question, 'Ensure to check the recalled stocks' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are There any gaps on the floorcorners of the panel wall.? If anything is found same must be closed properly to restrict pest entry into facility. Are all Floor; tiles in intact condition without any damage?' as question, 'Ensure to close all the wall gaps to avoid pest entry' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is all received Bulk stocks stacked SKU wise in defined location & in desired temperature-controlled room following FEFO and receiving date identification (Labelled in crate Tray Hanger).' as question, 'Keep all received bulk stock in demarked location with specific temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt? Are all Utensils washed using cleaning aid suggested by Diversely Care after every use?' as question, 'Ensure all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt. Ensure all Utensils washed using cleaning aid suggested by Diversely Care after every use' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is any Write-off recorded in system apart from QC Certified Qty and Is all Write-Off raised with proper remarks and as per the approval metrics?' as question, 'All Wos sohuld be carried out with proper approvals' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is Cold rooms Chiller Freezer maintained clean & neat? Is the Temperatures maintained at desired level? Is the Ice formation found in cold room? Refer the records maintain on temperature and visual check on cleanness? Store Is the temperature for checked maintained less than 4 deg C at any point of time?' as question, 'Ensure to maintainall cold rooms clean nad neat, and maintain the records of temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is incoming material procured in accordance with internally laid down specifications from approved vendors? Are records checked for specifications, supplier information, batch numbers, and quantity procured?' as question, 'Incoming material should be procure with approval vendor.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Color coded crates maintained for the product handling during Operations ( Receiving and while processing as product should not touch the ground)? Red crate for - Chicken, Orange crate for - Mutton, and Bottom Crate for Chicken and Mutton - Green color. Blue crate for - fish, Yellow crate for prawn and bottom crate for Fish ad Prawn must be Brown' as question, 'Color coding should be maintained while handling the products' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the daily Cycle count is carried and variance is updated in the system as per the approval metrics?' as question, 'Butchery all SKUs should be done daily cycle count and corrections should be donw with proper approvals' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the medical test certificates available for all butchers as per FSSAI (Yearly once) and is the Certificates valid on the day of Audit?' as question, 'Medical certificate should be available for all the butchers and should be vaild during audit date' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the traceability exercise conducted once every three months, covering the journey from raw material to finished goods and from finished goods to dispatch locations?' as question, 'Traceability exercise should be conducted every 3 months without fail.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Training records available for all Machine operators Butchers? And are only trained Machine operators Butchers operating the Machines?' as question, 'All butchers should be trained and records shoud be maintained' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'The temperature in room for boning out & trimming are controlled & held suitably low(less than 12 degC), unless cleaning of equipment & utensils are carried out at least every four hours.' as question, 'Ensure to maintain room temperatue and clean the utensils atleast every 4 hours' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the dispatch register/ Know App is maintained and updated?' as question, 'Stock dispatches should be captured in register' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the shipper boxes are clean and free from off smell.Temperature inside shipper box is less than 5 deg C ?' as question, 'All the Shipper(Syntex) boxes should be clean and free from smell. Ensure to maintain temperature less than 5 deg C' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the transporting vehicle for food use are kept clean and maintained in good condition?' as question, 'Ensure that transport vehicle should be clean before the stock dispatch' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Bulk consumables stacked in bulk location & is any consumables found stacked inside production area?' as question, 'Ensure to keep all bulk consumables in bulk location instead of keeping inside the production area' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per Diversely care inputs after use?' as question, 'Ensure all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per Diversely care inputs after use?' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Dust bins being provided with dust bin bags? (Exception plastic banned cities)/ Is all Housekeeping tools & cleaning aids kept in designated place? Are any F & V crates used for disposing process waste? Is all process wastage discarded into closed dust bins?' as question, 'Ensure all Dust bins being provided with dust bin bags. (Exception plastic banned cities)/ all Housekeeping tools & cleaning aids should be kept in designated place. Don''t use any F & V crates used for disposing process waste. ENsure to all process wastage discarded into closed dust bins.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all F & V arranged properly in racks with segregation of Fruits & Vegetables? Are all Rotten stocks segregated from the bulk & discarded?' as question, 'Ensure all F & V arranged properly in racks with segregation of Fruits & Vegetables.Ensure all Rotten stocks segregated from the bulk & discarded.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Leafy vegetables fresh with roots properly cut?' as question, 'Roots cut preperly for leafy vegetables' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Mix Veg & fruit articles randomly checked for weights?' as question, 'Ensure to pack mix fruit & veg SKUs as per process' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Processed stocks kept in SS bins & stacked in racks provided?' as question, 'Ensure all Processed stocks kept in SS bins & stacked in racks provided.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all the packs properly labeled with Pack Wt.; Packed Date and Best Before Date with 5-day shelf life; including date of packing?' as question, 'Ensure to label the packed stocks with packed date,bbd with 5 days, include packing date' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are Clean crates used for raw material storage? Is any finished product found stacked in the Dirty crates inside production area?' as question, 'Ensure to use clean crates for raw material storage, Don’t use dirty crates inside cutve' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are closed Dust bins provided at hand wash area/chopping tables/weighing scale points/raw material entry location?' as question, 'Ensure to use closed Dust bins  at hand wash area/chopping tables/weighing scale points/raw material entry location' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are There any gaps on the floor/corners of the panel wall.? If anything is found same must be closed properly to restrict pest entry into facility. Are all Floor; tiles in intact condition without any damage?' as question, 'Ensure to close all the wall gaps to avoid pest entry' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Do the employees of cut veg section practices hygiene inside production or preparation area; are Empty Crates available without palletization in bulk area?' as question, 'Ensure the employees of cutveg practice hygine' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Does the Production staff sanitize their hands as suggested by Diversely care after every product change over?' as question, 'Production staffs should sanitize their hands every product change over' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Does the staff consume/ Carrying any food; chewing of tobacco/chewing gum inside the facility /processing area?' as question, 'Ensure the staff shouldn''t consume/ Carrying any food; chewing of tobacco/chewing gum inside the facility /processing area' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Employee should be wearing clean outer garments. (Uniform as provided) and is suggested Footwear used inside the cut-veg facility? Are the foot caps provided and used by the visitors?' as question, 'En sure all employees should be wearing clean outer garments. (Uniform as provided) and is suggested Footwear used inside the cut-veg facility. Ensure the foot caps provided and used by the visitors.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt? Are all Utensils washed using cleaning aid suggested by Diversely Care after every use?' as question, 'Ensure all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt, and all Utensils washed using cleaning aid suggested by Diversely Care after every use.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is any machinery under maintenance properly Labeled with “NOT IN USE” signage in the production space?' as question, 'Paste NOT IN USE sign of unused machines' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is any Raw Material/processed material kept below the Pest-O-Flash? Is Pest-O-Flash in working condition; switched ON & Trays & tubes of Pest-O-Flash clean.' as question, 'Don''t kept any raw/processed material under the Pest-O-Flash' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Area inside the facility free from cob webs in ceiling panels / behind racks / below chopping tables/and other possible places. Are any open cables found in side production space? If found any should be properly insulated.' as question, 'Ensure Area inside the facility free from cob webs in ceiling panels / behind racks / below chopping tables/and other possible places. Are any open cables found in side production space.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is CFTRI dozing preservative storage containers kept neat & clean with proper identification of chemical name. Is CFTRI dozing done as per article wise recommendations; using the Pocket weighing scale provided?' as question, 'Keep the CFTRI dozing containers kept neat and clean with identification' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Employee lockers & changing rooms clean without any unwanted material kept inside?' as question, 'Ensure employee lockers & changing rooms clean without any unwanted material kept inside' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is minimum of 1 ft. space available/Left for cleaning of dirt & dust between wall & Cutting tables/Machinery/SS Bin rack?' as question, 'Ensure to maintain minimum 1 ft space between wall &  Cutting tables/Machinery/SS Bin rack' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Staff; Raw Material entry doors provided with auto door closures & is the doors always kept closed to avoid pest entry from outside. Employee entry /raw material entry/Cold room chute door should be kept clean and free from stains.' as question, 'Entry doors should be provided with auto door closure and doors should be  closed always' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Cut veg & F&V Wastes segregated and disposed as per Waste Management Process? Is all the chipped of waste removed after the processing every 2 Hours or when the Bins are filled whichever is earlier?' as question, 'Ensure the Cut veg & F&V Wastes segregated and disposed as per Waste Management Process. all the chipped of waste removed after the processing every 2 Hours or when the Bins are filled whichever is earlier.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in Cut Veg Preparation Room? Refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'First aid box should be refilled as per HSE guidelines' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is there a floor mat available at the entry points and is it clean & neat? Is the floor maintained clean without dirt or dust & is the floor dry without stagnated water? Is Walls & ceiling panels clean without any dust; smudge; water leakages & stains?' as question, 'Floor mat should be available at the entry points' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'PPEs (Hand gloves/Head cap/Face mask) - 1. PPEs are in good condition 2. PPEs issue register/ Know App is maintained 3. All Employees are using PPEs at the time of Entering F&V 4. PPEs are stored in proper/Dedicated place 5. Awareness signage board is displayed 6. Sufficient PPEs are available 7. Used PPEs are stored & disposing properly' as question, 'Ensure to follow PPEs records and condition' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Were the hand wash sanitizers available at staff entry point? Is Production staff washing their hands on entering the cutveg section using sanitize and even are they following the same after using wash room?' as question, 'Ensure to keep hand wash sanitizers at staff entry point' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Are the Prepared raw materials packed as per packing norms given?' as question, 'Ensure to pack prepared raw materials as per packing norms' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Does the cut-veg Incharge check the quality of stock received from FV? Are the stocks received from FV for production; QC certified by the QC Incharge? Is the rejection happening for poor quality stocks?' as question, 'Cutveg incharge has to check the quality before stock receiving' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is FIFO/FEFO principal followed while stacking for all products in the cold room?' as question, 'Incharge has to ensure follow FIFO/FEFO while stacking the stocks' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Indent raised as per forecast norms and shared to B&M? Is forecast and indent data available (manual & Excel)? Is the data recorded for SKU wise TO; GRN Qty with GRN no; Preparation waste Qty; Closing stock qty? Is the Packed SKUs qty has been noted and GRN posted in system? Is cut veg Incharge/ Supervisor monitoring the pending GRN? (In warded but not GRNd)' as question, 'Indent should be raised as per forcating norms. Forcasting & indent data sould be maintained last audit date to till date during the audit' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the metal Detector being used after Packing?' as question, 'Metal detector should be used after packing' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Packed raw material stickered with Fresho- CFTRI label with requisite fields available in it?' as question, 'Ensure Packed raw material stickered with Fresho- CFTRI label with requisite fields available in it' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Prepared SKUs moved to Cold room immediately after labelling and stacked in location? Is the SKUs available for picker at all time?' as question, 'Ensure the Prepared SKUs moved to Cold room immediately after labelling and stacked in location.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the weighing scale & Bizerba calibrated as per schedule? And certificate made available near to each Machine?' as question, 'Weighing scale & Bizerba should be calibrated as per schedule and certificate should be pasted near to the each machine' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is all legal documents of the Vehicle & Driver available? Photo Copies should be filed in DC?' as question, 'Ensure All documents pertaining to dedicated vehicles must be filed in DC with validity' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is all vehicles in good condition as per the agreed clauses ? (Inter DC Vehicles)' as question, 'Ensure switch off unused electronic appliances when not in use' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is Separate A4 size tray crates kept in the security, Receiving area or applicable area for Collecting invoice DCs Other documents from vendors' as question, 'Separate A4 size tray should be placed in receiving security area to colloect invoices' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is the documents verified and condition fullfilled while onboarding the IHV vehciles?' as question, 'Ensure all the vehicle documents to be upto dated while onboarding the IHVs' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Does the Critical Assets Breakdown addressed in time and resolved by raising Ticket in My MCS/ Zoho? Check for the details Is the regular and critical assets requirement status available with follow up?' as question, 'If there are any critical asset damages, make sure to raise MYMCS or Zoho.' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Have all the Breakdown non-usable/repairable assets kept in a designated area with details updated in My Impact as on date in DC?' as question, 'Store all damaged assets in their designated areas. Updated with the same facts in Myimpact' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Is all Material Handling Equipment Checklist/ Know app available for equipments used in DC? Are they checking daily? Records available? (Pallet truck; stackers; hand Trolleys; Reach truck; Forklift; docking equipment; goods lift; other machines check list available?' as question, 'MHE checklist should be maintained for all the related machines daily' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Are all HHDs and MHE batteries are kept under charging while non-operational time?' as question, 'Ensure that all the unsued batteries under charging section at non-operational time' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Does the security frisk all the staffs moving out of DC?' as question, 'Ensure all staffs & visiter should be frisk while out from DC premises' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'GM article >500 Value items write off vs Available status with condition to be verified by the DC manager and secondary auditor every week & Tracker must be available' as question, 'Keep track of GM articles'' physical availability vs their WO, and maintain useable stocks.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is a certified Electrician / Plumber available in DC? dose the Electrician / Plumber wear safety gloves and shoes while working?' as question, 'Make sure to hire certified electricians and plumbers, and while working, always use safety precautions.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is All Emergency Contact Details available; updated and displayed at Security Entry Gate / point?' as question, 'Ensure to update upto date emergency contact details in entry point' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all outgoing stock movement recorded in the security outward register/ Know App with time?' as question, 'Ensure all outward movements should be recorded in register/Know app' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all Unwanted Lights; fans & other electrical appliances/machinery switched off when theyre not being used or required?' as question, 'Ensure switch off unused electronic appliances when not in use' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC issuing warning letters for any deviation and acknowledgements filed? Is the apology letter for the same obtained from employee and filed in his records?' as question, 'Make sure that every process deviation and improper practice receives a warning or apology letter.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC-Manager monitoring all pending system transactions? (In warded but not GRNd-FMCG; Cut-veg; FV)' as question, 'Ensure to complete all the inwards GRN same day. If any delays communicate to DCM through mail' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is GSTIN displayed at appropriate place on name board or sign board or near front door of the premises? Also; is the registration certificate displayed in the business premises?' as question, 'Ensure Both the registration certificate and the GSTIN number should be visible at the entrance and notice board, respectively. (Location name also available in Notice board GST certifiate)' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Petty Cash maintained at DC; are all relevant supporting for receipt and expenses available and documents maintained on daily basis /recorded? Is vouchers available for any advance with proper approval?' as question, 'Keep track of all the bills pertaining to petty cash without losing track.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is regular training conducted for new implementation/ process or changes? Are the ground staff aware of the process?' as question, 'Ensure to train all the staffs for recent releases' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Security Attendance & Housekeeping register/ Know App Available and maintained at Security Desk? Is the Duty Handover happening properly? Is Handover log Book available?' as question, 'Ensure proper shift handover to securities and housekeeping' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Daily Shift Huddle conducted by DC In charge/Shift Controllers? Is the Monthly MOM recorded and reviewed? Is record for the same available and shown during audit?' as question, 'Ensure to conduct daily huddles and record the details' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Layout Displayed in and around DC premises with Fire extinguisher spot; Emergency assembly spot & emergency Exit point?' as question, 'Ensure to update updated DC layout with emergency exit plan and FE spot' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Measuring the OKR Performance for all Category as per the parameters defined & is the R&R Program conducted as per the Schedules & reports published to Head office on Time with records maintained in DC' as question, 'Ensure to update OKR in darwinbox with description. And conduct R&R as per schedule' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Individual OKR given to Shift controllers; Inventory Controllers; Assistant Manager; Row In charges? Is the same read and acknowledged by all individual and available in record & filed with signature or Mail communication available? Check Darwinbox OKR plan' as question, 'Ensure the Individual OKR given to Shift controllers; Inventory Controllers; Assistant Manager; Row In charges. Is the same read and acknowledged by all individual and available in record & filed with signature or Mail communication available. Same should be updated in Darwin box' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security conducting regular patrolling in the DC premises? (Inside/outside)' as question, 'Ensure securities to do the patrolling' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security service provider regularly visiting to the site & is a register/ Know App/Checklist available for the same at the security gate?' as question, 'Security service provider has to visit the site frequantly' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the staff movement register/ Know App available and maintained at the security gate?' as question, 'Security service provider has to visit the site frequantly' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Warehouse agreement and inter hub vehicle transporter agreement available in DC? Is the agreement being received and valid as on date and filled required details?' as question, 'Ensure the Warehouse agreement and inter hub vehicle transporter agreement available in DC. Is the agreement being received and valid as on date and filled required details.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is there a Visitors register/ Know App available & is the security capturing & Monitoring the Movement?' as question, 'All visitors movement should be captured in secutry point' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Key register/ Know App at the security & are the Keys available & surrenders details recorded?' as question, 'Key register and handover surrender details should be maintained in the security gate' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all staffs wearing valid ID card? (Including HK, Security, G1 & G2)' as question, 'Ensure that all the unsued batteries under charging section at non-operational time' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'CCTV system - 1. CCTVs are installed at required places 2. Location details are available 3. Backup is available - Minimum 15 days 4. All CCTVs are in working condition' as question, 'Make sure there is CCTV surveillance throughout the entire DC area. Ascertain a minimum backup of 15 days.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'E & S Audit - 1. Audit is conducting monthly basis 2. Report sent to respective dept. regularly 3. Gaps are closed based on risk priority. 4 Previous month report must be share before 5th of next month' as question, 'Ensure to conduct E&S audit every month and share the reports as per the criteiria' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Electrical Service - All Electricity panels; Switch boards maintained in good condition 2.All earthing points & lines are in good condition 3. All panels are free from obstruction 4. For Panel room Suitable FE is placed 5. Cautionary signage is displayed at entrance of the area/room' as question, 'Ensure- 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Emergency/Alert system - 1. Alarm System is available at cold room 2.Installed alarm system is in working condition 3. Periodic check register/ Know App is maintained' as question, 'Ensure alarm in working condition' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Facility - Ventilation & Lighting - 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as question, 'Ensure- 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Fire Alarm System - 1. Fire Alarm system is available (Detector/MCP/Hooter/Panel) 2. Manual Call Point -MCP is placed at easy accessible locations 3. All Detectors are in working condition 4. FAP - Panel is in working condition 5. Backup power is connected to Panel 6. Service AMC details are available' as question, 'Ensure- 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Fire Extinguishers - 1. FE list is displayed at notice board 2. FE placed as per layout design/drawing 3. Sufficient No. of FE are available 4. All FEs are free from Obstructions 5. Service / Refill Info sticker is pasted on All FE 6. All FE are in good condition - No FE are in low pressure; accessories are damaged 7. Signage board is fixed for all FEs for easy identification' as question, 'Ensure- 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'First Aid Box  - 1. Sufficient FAB are available as per requirement(At least 1for 150 employees) 2. Standard listed Items are available in the box 3. FA Items list is available or pasted on box 3. FA incident register/ Know App is maintained 4. FAB monthly checking register/ Know App is maintained 5. All items are within the Expiry dates 6. Signage board display' as question, 'First aid box should be refilled as per HSE guidelines' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Incident / Accident Occurrence register/ Know App - 1. Incident / Accident occurrence register/ Know App (complete shift log book) is available at security desk 2. All First aid / abnormality incidence /accident are recorded 3. All incidents are reviewed by DCM & taken actions to avoid repetitions.' as question, 'Ensure to maintain Incident register and all the HSE related records should be maintained' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is racks and shelfs free from Damage / Dent? Visible check' as question, 'Ensure to periodic check of rack damages' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the pest assessment carried out and report shared to central HSE on 10th of every month and gap closure status shared before 20th of every month?' as question, 'Ensure to get pest assessment report from pest vendor and complete the gaps closure' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Loading & Unloading - 1. Safe procedures are following for Loading & Unloading 2. Trolley movement area is free from obstruction 3. Cleanliness is maintained at floor 4. Security / respective dept. persons are present at the time of Loading & unloading 5. Materials are transfer through only trolleys - No man lifting of heavy loads 6. Area is illuminated with proper lighting 7. Vehicle wheel stoppers are available' as question, 'Ensure to follow safety precautions while loading and unloading the IHVs' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'MHE-Stacker/Reach truck/Forklift - 1. Operators are Using PPPEs - Hand gloves-Helmet & Safety shoes & Reflecting Jackets 2. Operators are trained to handle the Equipment 3. Sufficient PPEs are available 4. register/ Know App is maintained for PPEs issue & stock' as question, 'Ensure to follow safety precautions while operating MHEs, BOPTs' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Activity - 1. Daily or weekly pest control Activity / service carried out as per agreed terms 2.Checklist is maintained 3.Pest Control service treatment schedule details available in DC' as question, 'Ensure that pest activity should be done as per agreement and checklist to maintained' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Layout - 1. Pest control Layout display in Notice Board 2.location details clarity -like rodent box; glue box etc.; available in the layout 3. Any changes in layout v/s actual availability of pest contents' as question, 'Pest layout should be displayed in notice board with glue pads, rodent boxes, Layout vs physical should match' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Report - 1. Monthly Incident Pest Control analysis report available with Project / facility team 2. All pest incident are recorded and its reviewed' as question, 'Ensure to get the pest control report every monthly from vendor and all the pest incidents should be captured in report.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Safety Signage Boards - 1.Facility having sufficient safety singes boards displayed in the DC 2.Mandatory to display the signages - FE/Emergency exit/Authorized person entry/MCP/Danger/MHE Charging point/First Aid box/ Racks -Load notice/Visitor guide etc.' as question, 'ensure to display all the safety related signages in DC premises' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Training - Security Team - 1. All security staff are trained on FE usage 2. All are aware about emergency handling 3. Aware about Fire alarm system & Hydrant operations 4. Training to be given periodically' as question, 'Ensure that security should aware the FE usafe and emergency handling' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Vehicle Movement - 1. Security is checking drivers Documents like - DL /ID 2. Vehicle documents - Insurance / Permit/ Emission certificates etc. . Vehicles are parked at designated area 3. Alcohol check is conducting at security (Optional)' as question, 'All the vehicle related documents should be available and vehicle parked in demarked locaiton' as recommendation
union select 'DC Manager' as process_owner, 'Labour and Establishment Compliance' as process, 'Display of abstracts,Fire License, FSSAI, notices, holiday list, S&E RC, CLRA RC, GST RC, ICC committee members list, Grievance redressal, Whistle blower policy and Trust benefits' as question, 'Ensure to display all related license in notice board' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all dedicated vehicles onboarded into TMS? And are drivers using TMS applications to start and end the trip?' as question, 'All dedicated vehicles lists in TMS must be updated. Drivers must initiate start and end trips in the TMS app.' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all delisted Inactive Dedicated vehicles checked for and deactivated in the TMS every fortnightly?' as question, 'Make sure you delist the inactive vehicle from the TMS every fortnight' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all the dedicated vehicle records correctly updated in TMS as per requirement?' as question, 'Ensure to update all the dedicated vehicle details in TMS while onboarding' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are dispatches carried out on-time as per the trip scheduled in TMS? Is schedules are prepared as per signed off from LOB City head' as question, 'Dispatched through TMS should be ontime and schedules should be taken approval from LOB City head' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Is all active Business location in the region onboarded on TMS and are all location movements happening through TMS?' as question, 'Ensure all the DC to Hub, CC to DC stock movements happen through TMS' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Is the TMS shedule time vs City haed sign off matching or not ?' as question, 'For all the TMS schedule get approval from city head' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'is the transport vendor payment and invoice process through TMS? Is the any excess vehicle used  approved by SCM Head?' as question, 'Transport billing should match with TMS billing, Ensure all the commertials updated 100%' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are empty carton boxes stored in the DC according to the defined layout? Has the auditor physically cross-checked to confirm this facility?' as question, 'Ensure to keep all disposable carton boxes should be kept in demarked location' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are empty vehicle weighment certificates and loaded weighment certificates available for scrap lifting (Applicable for Metal, Wood, Plastic scrap)? Has the auditor physically cross-checked these certificates and verified whether the DC team, under the DM Manager Direction project or Security, are authorized persons to go along with the vehicle for weighment?' as question, '1.Collect empty and loaded weighment certificates for all loads.'||chr(13)||chr(10)||'2. A security officer, a project manager, or a DC approved representative should accompany the vehicle for weighing.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are only approved vendors used to scrap the materials? Has the auditor cross-checked the approved vendor list and the register?' as question, 'Ensure that only authorized suppliers are used to remove scrap from DC.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are scrap carton boxes bundled within 50Kg in the DC? Has the auditor physically cross-checked to confirm whether the DC is following the bundling process?' as question, 'Scap cartons must be tied together in 50kg bundles. Check whether the bundleing procedure is being followed or not.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are the scrap corrugated/carton boxes sent back to DC in bundles of 5K and BB Now in the cage? If the 5Ks are not sent back, has approval been obtained from the regional business head and Head of the project for direct sale from 5K, following the same process?' as question, 'Inform the 5K crew to fill the cages with empty carton boxes; if not, obtain a mail of approval from RBH & RPH.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Has the vendor picked the carton box at the same price for the whole month? Has the auditor cross-checked the invoices for all sales?' as question, 'Ensure carton scap billing price be same' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is metal, wood, plastic scrapped monthly within 7 days from the date of the movable asset audit in T1 DC? Has the auditor cross-checked in the scrap register?' as question, 'Ensure all scrap must be disposed within 7 days of asset audit with proper documents' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the invoice request raised by the location project team every fortnight/monthly to HO, Finance Team? Have scanned copies of the scrap outward manual register been sent to the finance team with project manager and DC Manager sign-off? Has the auditor checked email communications to verify the frequency of invoice requests and the attachment of scanned copies of the register?' as question, 'Scrap invoice request should be raised by location project team as per timeline. Scanned copies and manual register should be share to finance team with Signoffs' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the scrap carton sales outward register/tracker maintained with mandatory columns? Has the auditor cross-checked whether the mandatory columns (Date, Scrap weight in Kgs, Per Kg value, Total sale Value, Security signature, DCM/SM sign, Vendor sign, and acknowledgment of receipt) are mentioned and updated?' as question, 'Ensure the scrap carton sales outward register/tracker maintained with mandatory columns. (Date, Scrap weight in Kgs, Per Kg value, Total sale Value, Security signature, DCM/SM sign, Vendor sign, and acknowledgment of receipt) are mentioned and updated' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the Scrap lifting (Carton box, Metal, Wood & Plastic) Vendor empaneled in accordance with the fulfillment of Process direction?' as question, 'Ensure the Scrap lifting (Carton box, Metal, Wood & Plastic) Vendor empaneled in accordance with the fulfillment of Process direction' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Are any salable products or Discount sale product moved and stored at dump storage area?' as question, 'Ensure that only completely unsaleable stock is transferred to the dump area.' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is all Dump disposed through authorized empaneled vendors only? Check vendor compliance documents? Check as per the process for all type of waste' as question, 'Ensure to dispose dump with authorized vendor and check the vendor compliance documents' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is all Inventory -Food Items including fruits and vegetables meat, bakeries and dairy products disposed only after removing packaging?' as question, 'Ensure to remove all the packaging before dispose' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is Dry and Wet waste stored separately with proper identification in the designated area or Room? Check physically' as question, 'Ensure physically is that wet & dry waste dispored seperately' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in FV Leafy Preparation Area? Refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'First aid box should be refilled as per HSE guidelines' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Whole of F&V Work Place Bins; Storage location; processing area maintained neat and Clean and regular cleaning carried out?' as question, 'Ensure to maintain floor hygiene in FV area' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Inward Management' as process, 'Is daily F&V MRP getting uploaded in Bizerba/Essaea Scales Once the MRP is determined against the S.P Upload File sent by the respective Buyers?' as question, 'FV MRPs should be updated daily basis in bizerba without fail as per b&m mail' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the crates filled with stocks as per SKU wise standard crate weight?' as question, 'Stocks shouldn''t fill more than standard crate weight' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the Packing tables; packing area clean and neat?' as question, 'Ensure to maintain packing table and area neat and clean' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the stocks received only in Bulk receiving Crate? And moved to Predefined area? Is the FV Stocks received in Clean bulk crate as per process? Bulk crate color code for CC arrival; Vendor Stocks; Organics.' as question, 'Ensure the stocks received only in Bulk receiving Crate. And moved to Predefined area. Is the FV Stocks received in Clean bulk crate as per process. Bulk crate color code for CC arrival; Vendor Stocks; Organics' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Does Orgonic covers ( Brown) used for Organic SKUs? Check in BBNow, BBD,packages' as question, 'Organic covers only need to use to pack the organic FV SKUs.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'does the Picker picks SKUs as per sequence (Hard SKU to Soft SKU; Leafy)? (Point applicable only in FSD model)' as question, 'Pickers should pick SKU hard to soft. Planogram need to be done hard to soft' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'For All Pieces SKUs (9 SKUs) that are pre-packed Punnet Packed from vendor, is a Standard PLU Barcode Label generated as mentioned in the SKU packet for all Pieces SKUs and stickered in the respective Pick Location Rack ?' as question, 'Ensure All Pieces SKUs (9 SKUs) that are pre-packed Punnet Packed from vendor, Standard PLU Barcode Label should be generated as mentioned in the SKU packet for all Pieces SKUs and stickered in the respective Pick Location Rack.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is all the packed SKUs weighed while packing and label stickered after packing? Is the barcode is readable or scanable condition ?' as question, 'Ensure all the packed SKUs weighed while packing and label stickered after packing. the barcode is readable or scanable condition.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is Cut-veg TO happening daily as per Indent received?' as question, 'Cutveg TO needs to be done daily basis' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Bulk Storage Location for each SKU defined & Demarked?' as question, 'Bulk storage should be demarked for each SKU to follow the FIFO' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the FIFO followed in Bulk location and Packing location?' as question, 'Ensure to follow FIFO in bulk location' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the GRN matching with invoice Value? Is the Invoices hard copies to Finance weekly basis through courier? And all the invoices soft copies sending to finance on daily basis Courier details available?' as question, 'GRN values should be match with invoice values and Hard copies should send weekly to Finance, soft copies daily basis' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the mushroom and Sprouts received in Cold-room? Is the temp logger maintained?' as question, 'Mushrooms and sprouts temperature should be captured while receiving, data should be maintained' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Packing done as per Packing Manual (Correct packing material for product is used)' as question, 'FV Packing should be done as per packing manual' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the receiving area being clean and neat?' as question, 'Ensure to maintain receiving area neat and clean' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Receiving Date stickered or Date written in the marker crate/cotton boxes for Exotic- Domestic / Imported SKU?s while receiving?' as question, 'Ensure to past date sticker or write the receiving date in imported SKUs to track the fifo' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Receiving Date stickers followed for FV received stocks?' as question, 'Receiving date sticker process should followe all the FV received stocks' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the staging area for All the dispatch locations clearly demarcated & well separated?' as question, 'Ensure staging area for All the dispatch locations clearly demarcated & well separated.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Standard Crate Weight for FV SKUs and 1Kg PLU Barcode stickered in all Crates in CC Supplies/ Scan the DLS QC Code if DLS process implemented ? If not followed by CC is that Escalated to CC In charges Stakeholders?.' as question, 'Ensure Standard Crate Weight /DLS QR code for FV SKUs and 1Kg PLU Barcode stickered in all Crates in CC Supplies/ Scan the DLS QC Code if DLS process implemented. If not followed by CC is that Escalated to CC In charges Stakeholders.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the table wiser packing list available? Is the packing happening as per the list? (Do a Random Check)' as question, 'Ensure that table wise packing list available. Ensure the packing happening as per the list? (Do a Random Check)' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the weighing scale & Bizerba calibrated as per schedule? And certificate made available near to each Machine?' as question, 'Weighing scale & Bizerba should be calibrated as per schedule and certificate should be pasted near to the each machine' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are all the crates stacked as per the stacking norms (standard weight of SKU per crate) for Regular F&V; Exotic F&V; Organic F&V without over loading?' as question, 'Ensure all the crates stacked as per the stacking norms (standard weight of SKU per crate) for Regular F&V; Exotic F&V; Organic F&V without over loading.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are the extra packed skus over an above the indent being removed at the end of the day?' as question, 'Ensure that extra packed skus over an above the indent being removed at the end of the day' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'As per the Total Quality Management process(TQM)are the rotten F&V being removed at the time of packaging?(No process of QC of CC arrival material)' as question, 'As per the Total Quality Management process(TQM)are the rotten F&V being removed at the time of packaging.(No process of QC of CC arrival material)' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the DILO(Day in the Life of)being filled by the QC person &  share the same with DCM & B&M copy to RBH & Central QC?' as question, 'Ensure the DILO(Day in the Life of)being filled by the QC person &  share the same with DCM & B&M copy to RBH & Central QC' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the FIFO followed in bulk Storage area? - are there date stickers on the crates?' as question, 'Is the FIFO followed in bulk Storage area? - are there date stickers on the crates?' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the FV QC Passed SKUs transferred to Clean bulk crate?Is the sorting and grading table being neat and clean?' as question, 'Ensure to transfer FV QC pased skus to clean crate' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the National Sourcing arrival coming with DQR (Dispatch Quality Report)?/TO ? Is the AQR prepared and sent to stakeholders for all shipments?' as question, 'Ensure the National Sourcing arrival coming with DQR (Dispatch Quality Report)/TO  Is the AQR prepared and sent to stakeholders for all shipments.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the packaging manual followed 100% as per the manual shared by HO Quality team?' as question, 'Ensure to followe packing manual 100%' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC check happening for bulk stock sent to Cut Veg from FV? QC certified by the FV Incharge; and does the transfer document contain his QC passed remark?' as question, 'Ensure to check Cutveg TO stocks should do 100% QC' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC happening 100% before receiving stocks from Vendor?' as question, 'Ensure the QC happening 100% before receiving stocks from Vendor' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC person along with the shift incharge carrying out calibration for all weighing scales & Bizerba using certified dead weight (Standard weight/ stone certified by weight & Measurement Department? Is all the Reports available?' as question, 'Ensure QC person along with the shift incharge carrying out calibration for all weighing scales & Bizerba using certified dead weight (Standard weight/ stone certified by weight & Measurement Department' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the sorting & grading happening for RTV Stocks on the same Day? And any reusable quantity packed on the same immediately and moved to the picking area/location?' as question, 'Ensure the sorting & grading happening for RTV Stocks on the same Day And ensure reusable quantity packed on the same immediately and moved to the picking area/location.' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is MY-MCS/ Zoho call raised for any Breakdown of daily assets with proper validation and details? (HHD; android device (handheld device) & Batteries)' as question, 'Ensure to raise MYMCS/Zoho for critical assets breakdown with proper details' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Daily critical asset Inventory carried out for HHD, Batteries and Hand Trolly, Pallet trolly in DC as per process? and daily records available?' as question, 'Ensure to do the cycle count for critical assets' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Inventory Incharge/DC Head checking all stock transfers is done through MyMCS for any Assets moving out of DC? (repair / transfer to other location)' as question, 'Inventory incharge/DC head has to check the asset transfer through MYMCS/Zoho' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the monthly fixed and movable asset(Wall to wall Inventory) carried out in DC as per process? Has the Inventory Manager reviewed the Final asset audit variance report with the respective RBH/project Manager/DCM & is the Signoff Copy sent to the central team ever month as per the process? Is the variance reconciled within 25 days?' as question, 'Ensure to conduct monthly fixed,moveable asset audit as per process and close the variance within 25 days' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Does the Discount sale proceed collected in cash, kept in safe reconciliation tallying with the nondeposited amount and is the deposit carried out every fortnightly into company’s account and information sent to finance/ accounts and is the invoice available up to the last transaction?' as question, 'Ensure Discount sale proceed collected in cash, kept in safe reconciliation tallying with the nondeposited amount and is the deposit carried out every fortnightly into company’s account and information sent to finance/ accounts and is the invoice available up to the last transaction' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is 100% QC carried out for the all the F&V write-off Stock and certified by the QC -Incharge? Is grading done categorizing product into B-Grade and D-Grade? And is the B-grade stored in crates and D-grade in covered bins with identification?' as question, '100% QC should be done by QC incharge before WO' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is all F&V B-grade stocks acknowledged in the register by the Discount sale in-charge which receiving at Discount sale area?' as question, 'ALL FV B Grade stocks should be recorded in register' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is any Discount sale value recovery being less than 30% of actual CP then is the RBH approval taken before sales? [Check approval mail against the transaction]' as question, 'Ensure to recovery more than 30% in actual CP if not get approval from RBH' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is the F&V Discount sale price obtained from the B&M by sharing the details of products available for Discount sale for the day and before start of Discount sale for the day?' as question, 'Ensure to get FV discount sale price from B&M before start of discount sale' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Are the invoices raised for all the Previous discount sale movements?' as question, 'Ensure all the discount sale stock properly segregated in to “Discount Sale Recovery Stock” and “Dump”. ' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Are there any unopened bags, box, bulk SKU available?' as question, 'Ensure to maintain hygiene standard in discount sale area' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is all the discount sale stock properly segregated in to “Discount Sale Recovery Stock” and “Dump”.? Is any Dump material “Spoilt, expired, infested, contaminated, damaged, spillage, complaint return and process waste” kept mixed-up along with Discount sale products? - (Check the storage area Physically) In case of any Expired material found, recover the Material, and give the credit to discount sale lifting vendor.' as question, 'Ensure to raise inoice for all discount sale movements' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the 5K return second sale tracking process is followed?' as question, 'Don''t kept any unwanted bags, box in discount sale area' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the area maintained with proper hygiene standards (Spillage leakage, odour smell, flies, and flies)' as question, 'Ensure to follow 5K return ss tracking' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the E-bidding QR code displayed at the “Inspection Area” (i.e., Discount Sale Area)? Note: “Inspection Area” (i.e., Discount Sale Area) Is the recommended H1 Vendor deposited the payment to Bigbasket Bank Account?' as question, 'Ensure to display E_bidding QC in the discount sale area' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the location initiated the E -auction/E- Bidding locally, with interested parties/ vendor, for discount sale?' as question, 'Ensure location initiated the E -auction/E- Bidding locally, with interested parties/ vendor, for discount sale?' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is there any difference in the Write-off report Vs actual Discount sales for the present lifted schedule?' as question, 'Ensure to match WO report vs discount sale for the schedule' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Recover the Material and give the credit to discount sale lifting vendor and move product to original location by accounting back into system?' as question, 'Ensure to remove all the saleable stocks from discount sale area' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was any BBPL Stock being handed over without removing the package during the lifting? While such products are identified - deface the package before handover, Collect proofs for the same.' as question, 'Ensure to handover BBPL stocks to vendor after removing after the packing cover' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was any RTV applicable SKU and PRN/GDN Stocks being moved through discount sale? Check Why this product was moved to this Discount sale area “ Reason for vendor rejection”. If still fit for RTV recover the Material and give the credit to discount sale lifting vendor. For any PRN/GDN stock they should be approval mail from Vendor for disposal.' as question, 'Ensure to don''t move RTV Applicable skus to discount sale area' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was the lifting carried out under the CCTV surveillance in presence of SSLP nominated person? - Check the facility in the CCTV room?' as question, 'Ensure to move discount sale dispatch infront of CCTV and SSLP presence' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was there any other major state of volition other than the above stated checkpoints?' as question, '0' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all FV RTV stock moved to QC immediately after TI?' as question, 'Ensure to fill 2 days inventory in pick location  to avoid hold' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all pallets strapped using belts for the stocks stored in the Heavy duty secondary storage location?' as question, 'Ensure to move Fv RTV stocks to QC after TI' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all the good stocks moved to the racks and all the damage/expiry stocks write-off from the DC; by taking necessary approval?' as question, 'Tolarance :100% Process to be followed , no deviations are acceptable' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all Positive and negative stock updates carried out having necessary approval and adjustment carried out as per approval? Also Is any stock correction done more than 3 times for any SKU having proper justifications? Mail approval should be taken from Regional SCM Head/DC Head. (Mail should be approved)' as question, 'Ensure to move all the good stock to the rack once TI complete' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all the Sacks opened only through scissors?' as question, 'Ensure to get approval from respective stackholder for stock corrections' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Negative Qty SKUs available in Book Stocks ? (Should be nullified daily basis in stock update)' as question, 'Ensure to use only scissors to open the bags' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Stock qty available in SKU code without rack Location?' as question, 'Ensure to clear negative stocks daily by EOD' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any unaccounted excess stocks found in DC ?? (sys vs Physical)' as question, 'Ensure to provide rack location for all the SKUs' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is bulk stock storing for Top SKUs allowed above the primary locations in the same rack ?' as question, 'Ensure all the systemvs physical sku Qty should match' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is details of near expiry stock communicated to the B&M & DC Manager; as per the Shelf life norms / Escalation Matrix?' as question, 'Ensure to store bulk stock top of the primary location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is less shelf life / expiry / spoilt SKU write-off done on daily basis? Does the stacker maintain shelf life norms and removes SKUs as per process?' as question, 'Commnicate near expiry details as per norms to B&M/DC Manager as per matrix' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is RECO carried out for the discrepancy after cycle count and is stock updated is carried out as per the final variance?' as question, 'Ensure to WO daily basis nearexpiry,damage skus' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is stock stored in excess/ Overflow location has pick location assigned? Is regular bin replenishment happening from excess storage location to picking location?' as question, 'Ensure to carry RECO after cycle count same needs to be update as final variance' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the as per schedule wall to wall Stock take happening for FV? Any differences found in inventory is the approval taken & written-off from the system?' as question, 'Ensure to replenishment happening from excess storage location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Bin Audit carried out on daily basis by the inventory Controller? Does the Inventory controllersstackerRow in-charges conduct checks for Identifying non-salable stock (damage; expiry & spoil; non-returnable to vendor) from Shelf & initiate write-off from system with proper approvals?' as question, 'Ensure to complete the FV wall to wall as per schedule' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Bins and Racks maintained Clean and Neat? Is any products found under the pallets or under the slotted angel racks?' as question, 'Ensure to remove damage,near expiry, spoil Skus from pick location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Contra SKUs receiving is happening in DC? Check the wrong complaints' as question, 'Maintain the bins and rack clean.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the critical ( BBPL) cycle count is carried out as per scheduling using cycle count app? (applicable T1 & T2 DC weekly once). It should be covered both offline cycle count and Stock take report' as question, 'Avoid receiving contra SKUs' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the critical ( High value, Transaction) cycle count is carried out as per scheduling using cycle count app? (applicable T1 & T2 DC weekly once)' as question, 'Ensure to do the cycle count for BBPL SKUs as per schedule' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the customer rejection / DS Rejection near expiry / expiry/ spoilt SKUs write off completed daily basis? Is data available?' as question, 'Ensure to complete the critical cycle count as per schedule through app' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the cut-veg customer returns write-off carried out at DC?' as question, 'Ensure to do the WO return nonsaleable SKUs' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Cycle Count carried out as per schedule and are all SKU''s covered in the month & is the cycle count included for all UD and IBND on daily basis?  It should be covered both offline cycle count and Stock take report' as question, 'Ensure to do the WO return nonsaleable SKUs' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FEFO followed in Racks while stacking SKUs?' as question, 'Ensure to follow the cycle count as per schedule and cover UD & IBND SKUs daily basis' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FMCG & FV Pre-Bulk Storage area clean and neat? Is all aisle free for trolley movement?' as question, 'Ensure to follow FEFO while stacking' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FMCG near Expiry stocks being removed from the shelf as per the shelf life removal norms?' as question, 'FV,FMCG Pre-bulk area should be free for trolly movement' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FV Closing stock shared to B&M daily basis on EOD? Is the shared detailed record (mail) available for the last 3days?' as question, 'Ensure to remove near expiry stock from pick location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the GRN?d stock getting stacked to the respective bin the same day? Is the stacker using stacking app for Stacking?' as question, 'Share daily basis FV closing stock details to B&M without fail' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the inventory team reverting for all discrepancy escalation mail received from 5K|T2|B2B|Inter DC and LT orders with in the Same day? (Stacking pendancy report of 5KT2B2B) for the auditing period? Once escalated is the discrepancy Reconciliation and actions completed with in 24 hours?' as question, 'GRN stocks should be stacked on same day' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Plannogram process followed, ensuring that hazardous articles are placed in a separate aisle and no stock is kept on top of slotted angle racks?' as question, 'Ensure to revert all discrepancy mails from 5k,t2,b2b and close the discrepancy within 24 hours' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the purchase return carried out in accordance with the agreement between the merchandiser and supplier, and is this verified based on the list available with the Inventory Controller? Additionally, is the purchase return stock handed over on time, and are the details communicated to the receiving Incharge?' as question, 'Ensure to keep Hazardous stock separate aisle' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the putaway team recording SKU Type, SKU and Rack Details in Pallet Tracker at the time of Receiving?' as question, 'Inventory controller should maintain RTV NRTV file and communicated need to given the receiving incharge while handovering the stocks' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the receiving Incharge conducting check for Non RTV & RTV Vendor stocks before doing write off?' as question, 'Ensure to capture product shelf life detail in pallet tracker' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the SKU Movement types for Inter-DC order uploaded in the Admin during assortment changes taking place?' as question, 'Ensurethe receiving Incharge conducting check for Non RTV & RTV Vendor stocks before doing write off' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Stacker wearing helmet while using stacker?' as question, 'Ensure to upload SKU movement type in admin' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the stock available in return location? Is stock moved based the Inventory Head approval?' as question, 'Stacker operator should use helmet while operating machine' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the two-day inventory available in primary pick locations?, Check Sample of minimum 20 SKUs' as question, 'Don''t keep stocks in return location. If available, approval required from IH' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the write off Posted in system immediately after QC passed with appropriate remarks?' as question, 'Ensure that write off Posted in system immediately after QC passed with appropriate remarks' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the write off SKUs moved to dump as per waste management process?' as question, 'Ensure to move WO stocks as per waste management proces' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Write-off Approval metrics configured every month in the system as per the approval given?' as question, 'Ensure to configure WO approval metrics every month as per process' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is there a designated area demarked for Damage; Expired; repacking; RTV stock? Is the products stored in the designated area ?' as question, 'Ensure to keep damage,expiry,rtv stocks in demarked location' as recommendation
union select 'Inventory Controller' as process_owner, 'Operations' as process, 'Is the Group locations uploaded for Auto Indenting to Mother DC?' as question, 'Ensure to upload group location for all SKUs for Auto indent' as recommendation
union select 'Inventory Controller' as process_owner, 'Operations' as process, 'Is the Type-1 Stocks indent raised separately and assigned to Stacker & picked by Stacker and prioritized for Dispatch?. Type-1 Stock should be picked only by Stacker' as question, 'Ensure to raise Type-1 indent seperatly and stacker to pick' as recommendation
union select 'Inventory Controller' as process_owner, 'T4 Operations' as process, 'Is the cash deposit happening on as per schedule, DC Is having acknowledgment and submitting to finance.' as question, 'Ensure that the cash deposit happening as per schedule' as recommendation
union select 'Inventory Controller' as process_owner, 'T4 Operations' as process, 'Is the RTV excess, damage, return pickup stocks handed over to OC by route in charger item wise' as question, 'Ensure to handover return stock handedover to OC by route incharge' as recommendation
union select 'Inventory Controller' as process_owner, 'T4 Operations' as process, 'is the virtual server is getting cleared (TO,TI) every day?' as question, 'Ensure to clear daily basis T4 server stock status' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is all Asset handover carried out with proper signoff between DC & Projects after every transaction and is the signoff records available & maintained in DC?' as question, 'Ensure that assets handover signoff should be available with DC team' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is Manual Asset inward register/ Know App maintained at DC and is the Receiving Incharge ensuring the availability and are all movements recorded and register/ Know App validated weekly by Project/ receiving In-charge; DS / DC Manager/ Inventory Manager & Checked signature Available.' as question, 'Ensure to capture all the asset inwards should be captured in asset inward register with records' as recommendation
union select 'Receiving Incharge' as process_owner, 'Cold Chain Operations' as process, 'Are the Chiller and Frozen SKUs receiving happens in cold room (Anti Room) checking Temperature as per (Permissible limit)?' as question, 'Ensure to receive CF stocks inside the anti-room with temperature check' as recommendation
union select 'Receiving Incharge' as process_owner, 'Cold Chain Operations' as process, 'Is the Imported fruits and exotic vegetables moved to cold room immediately after receiving for stacking? And is the receiving happening in anti-room?' as question, 'Ensure to move import/exotic skus to to cold room once receiving complete' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Are personal care products (condoms) packed with brown cover at the time of receiving?' as question, 'Ensure to pack personal care products should wrap with brown cover' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Are the Bundle Pack SKU; wrapped at the time of receiving and at the time of receiving are the bundle pack details captured in the device?' as question, 'Ensure to wrap bundle pack SKU with free stock while receiving and capture in device' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'At the time of receiving are the details of product , expire date for all products other being captured in the receiving Device?' as question, 'Ensure receiver to capture product shelf life details while receiving' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Every 3 months once vendor''s updated mail IDs needs to take from B&M team. Is that followed? Mail acknowledgement available' as question, 'Ensure that every 3 months updated vendor mails need to be uploaded for auto mail' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'If the GDN value is greater than 50K, is vendor mail apporval taken for the GDN before proceeding the GRN' as question, 'Ensure before raising GDN if value more than 50k vendor approval through mail need to be taken' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is all Lakme SKUs bubble wrapped while receiving or before moving the stock to stacking location?' as question, 'Ensure to wrap with bubble cover Lakme SKUs' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is all the type-1 SKUs is moved to the respective Rack locations  after completion of the receiving' as question, 'Ensure to move type-1 sku to rack location once receiving complete directly' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is All type 2 and Type-3 has moved to receiving stageing area afer receiving completion' as question, 'Ensure to move all Type-2,3 stocks to staging area' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is Daily MRP Complaints analysis and communication for rectification communicated to buyer' as question, 'Ensure to communicate the MRP changes to buyer' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is pass in slip Rejected by Receiving Incharge only or by the DC Managers Login Ids and is a valid reason recorded during rejection?' as question, 'Pass in slip should be reject only by receiving incharge//DCM' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the agreed vendor shcedule is updated in the system?' as question, 'Ensure to update vendir schedule in VSM' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the approval mail obtained from DCM for allowing receiving unscheduled vendors? Or is the detail of unscheduled vendors receiving for the day sent to B&M?' as question, 'For receiving unschedule vendor approval should be taken from DCM' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Auto triggered mail configured for all vendor for all transactions GRN; GDN; PRN? Is the alert Mail sent? If not  the Receiving Incharge has to send mails manually to respective Vendor & BandM? Is all GDN raised only through System E-Retail?' as question, 'Ensure to map auto alert mails to vendor, if not share daily to vendor mails ' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Express receiving designated and signage board is installed and used for express receiving in DC? As is the Location providing basis facilities to the vendor? And receiving key points signage boards are available ( Security, receivver, GRN and GDN) signage boards to be displayed' as question, 'Ensure to display express receiving signage baord and provide the basic facility to vendors' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the GRNd Invoice sent to Finance daily basis thru courier and scan copies updated in the google drive? Is the tracker maintained and made available during audit?' as question, 'GRN values should be match with invoice values and Hard copies should send weekly to Finance, soft copies daily basis. Tracker should be maintained' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiver mentioning the GRN & GDN ref number on the Invoice copy both on Vendor & buyer copy? (GDN if applicable once GRN Done on the Buyer Copy; in supplier Copy only GDN Number with acknowledgement)' as question, 'Ensure receiver to capture GRN,GDN numbmer values in both buyer,vendor copy' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiving happening as per category shelf life Norms? For any product received below shelf life norms is the receiving approved by RBH/B&M Head?' as question, 'Ensure receiving happeninng as per norms for all the SKUs to avoid norms.IF less shelf life receives approval required' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the same day FV GRN''d for vendor and CC arrivals? Including National sourcing' as question, 'Ensure to complete GRN on same day for FV' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the security Checking & verifying the Vehicle before moving out against any return after receiving? Vendor vehicle must move immediately once unloading happens; vendor must place the unloaded material on pallet?' as question, 'Security has to check and verify the vehicle before moving out.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is ther inward seal process is following , and all the details captured properly , are all the details ledgible including  ( seal and recordded data)' as question, 'Ensure to follow inward seal for all the invoice' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is there any wrong GRN transections are identified and if they created any PRN and necessory approval (Central SCM Receiving SPOC) carried out as per the process For Any wrong Transactions related to Receiving ?' as question, 'Ensure to do the grn for correct vendor and PO, if any wrong GRN happens approval shoul be taken from Central team for PRN' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Once GDN and PRN Stocks are handed overed to vendor that needs to take the photogrophy of the 1.stocks handover photos, 2.vehicle with Stocks and same email needs to send to vendor and buyer' as question, 'Ensure to take GDN,PRN handover photos, stock in vehicle photos ad send mail to respective vendor ' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Once vendor reported , is the pass in slip generated on time and receiving process is completed as per the process if any rejection or in process , is the receiving incharge communicated to all central and rgional team ( B&M and SCM)' as question, 'Ensure to communicate gp rejections to vendor and SCM' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Without PRN handover is that receiving happening in next supply' as question, 'Ensure that PRN should handover next supply without fail' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'For all BBNOW PRNs taking TI through bulk Excel upload?( No Manual TI Is allowed)' as question, 'Ensure all BBNOW PRNs should take excel bulk upload ti' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is All Eretail PRNs taking Single Click TI? (No manual TI is allowed)' as question, 'Ensure all Eretail PRNs (5K,T2,B2B,Fresho,etc) should take one click TI' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the PRN gate pass in save mode till stock handover to vendor? No pile up in DC allowed' as question, 'Ensure to keep PRN gatepass save mode until next vendeor supply.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the PRN vs TI variance escalated to 5K , BB Now, T4, Fresho, T2 and BBD Head T2 City Head and reconciled?' as question, 'Ensure to escalate PRN vs TI to LOB stakeholder and reconcile' as recommendation),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'Process Audit Checklist T1%'
   and store_id = @{{:BB T1 Audit - Single Audit.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB T1 Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB T1 B2C Audit - Single Audit_T1 B2C Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T1 B2C Audit - Single Audit
-- Dashboard: T1 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:58
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Process Audit Checklist T1%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T2 B2B Audit - All Past Audits_T2 B2B Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T2 B2B Audit - All Past Audits
-- Dashboard: T2 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:50
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'T2 B2B%'
  and store_id = @{{:BB T2 B2B Audit - Single Audit.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" <= @{{:BB T2 B2B Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T2 B2B Audit - Recommendations_T2 B2B Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, reco_database

**Original Query:**

```sql
-- Data Source: BB T2 B2B Audit - Recommendations
-- Dashboard: T2 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:50
-- ============================================================

WITH reco_database as (select null as process_owner, null as process, null as question, null as recommendation),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'T2 B2B%'
   and store_id = @{{:BB T2 B2B Audit - Single Audit.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB T2 B2B Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB T2 B2B Audit - Single Audit_T2 B2B Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T2 B2B Audit - Single Audit
-- Dashboard: T2 B2B Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:51
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'T2 B2B%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T2 B2C Audit - All Past Audits_T2 B2C Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T2 B2C Audit - All Past Audits
-- Dashboard: T2 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:55
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC_%'
  and store_id = @{{:BB T2 B2C Audit - Single Audit.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" <= @{{:BB T2 B2C Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T2 B2C Audit - Recommendations_T2 B2C Process Audit Report.sql

**Tables referenced:** B, CC, City, DC, DCM, Damage, FV, GDN, Inter, Obstructions, QC, RBH, Shelf, Vendor, any, approved, audit_submitted_at, base, both, bulk, checkpoint_master_sheet_table, city, cob, crates, current_timestamp, damage, discount, dust, employee, employees, excess, finished, obstruction, off, outside, pest, raw, reco_database, smell, stains, stores, system, the, vendor, vendors

**Columns needing snake_case conversion:**

- `controllersstackerRow` -> `controllersstacker_row` (alias: `controllersstacker_row AS "controllersstackerRow"`)

- `degC` -> `deg_c` (alias: `deg_c AS "degC"`)

- `iD` -> `i_d` (alias: `i_d AS "iD"`)


**Original Query:**

```sql
-- Data Source: BB T2 B2C Audit - Recommendations
-- Dashboard: T2 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:54
-- ============================================================

WITH reco_database as (select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'After picking are all chiller boxes moved to the respective Stageing area (Hub)' as question, 'Shift controllers and picking teams should ensure that all completed CF boxes are kept in their respective hub staging areas to complete the crate QC process. The shift controller has to ensure that none of the cf boxes that have finished the picking are lying on the cf room/floor.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Are all Chiller & Frozen articles covered with required number of gel Packs? Are syntax boxes used for Frozen articles? Is Picker picking required number of PCM Packs and properly arranging it inside insulated box with correct combination as per cold chain process?' as question, 'To preserve the products temperature till delivery, the shift controller must ensure that all frozen and chiller stocks are covered with the required amount of PCM pads in the correct color combination process. PCM pads must to be properly arranged inside the Syntex/Consta boxes.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Are Invoice raised for all Inter - DC movement and dispatched along with Invoices in a vehicle? (DC to T2, 5K and other locations)' as question, 'Check in the vehicle, driver or in the receiving location' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Is any inter DC Order stocks dispatched partially to any business line (5k , BB NOW, Fresho & BB Daily) ? Are they communicated to the locations before dispatch ?' as question, 'If an IDC orders are partial dispatch to a certain place, the same communication must be shared with the destination before the vehicle is dispatched from the DC. They will plan the grn and stacking based on that.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Cold rooms/ Chiller/ Freezer maintained clean & neat? Is the Temperatures maintained at desired level? Is the Ice formation found in cold room? Refer the records maintain on temperature and visual check on cleanness' as question, '1. Keep the cold room floor clean and orderly, avoid unneeded stocks, and keep empty carton boxes within the cold room. 2. Keep the cold room door closed at all times to avoid ice buildup. 3. Frequently register the cold room temperature in register/Know app' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is Crate QC done for all LOB Crates ? staged in disaptch stagging area and Is QC report sent to the respective active LOB''s? are they taken the action against of descrepency?' as question, '1. Complete the crate QC 100% for all the crates. 2. After the picking is finished, take all of the crates to the staging area. 3.After picking is complete, distribute the QC report to the appropriate area.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is DC Team well trained on Cold Chain Process & are the staff aware on the process to be followed? (Check training mail)' as question, 'Shift controllers must verify who is working in the cold chain area, and all employees must be aware of the cold chain process. Training and certification must be provided to all employees.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Out Bound Operations' as process, 'Is E-Way bill Generated for all the outward movement that required mandatory E-bill supporting as per the respective state law. Also; is the E-way bill number entered in the TMS (Manual) -GP for all E-way bill raised Movements? E-way Bill is Mandatory for all the out-ward movement where the document value is equal to or More than 50;000- for all the states expect Mumbai and Kolkata; where the value is equal to or more than 100000-' as question, 'If the dispatch value is more than the govt standard value, the shift controller/outbound incharge must ensure that an eway bill is generated and dispatch along wiith vehicle. If a lower-value invoice suffices,' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Ice Creams packed and dispatched to 5K , BB NOW, Hub and Other LOBs as per cold chain process?' as question, 'Pick the Ice cream with appropriate blue Pcm pads and load it lastas per Cold chain process' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Item QC done for all Ice Boxes? & is QC report is sent to the respective HUBs / DS/ T2/Kirana?' as question, 'Ensure that all ice boxes item Qc are completely covered, and communicate the item Qc report to the appropriate stakeholders.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is Plate Freezer process followed? (Is the plate freezer Maintained Clean & Neat? Is the lock found intact? Is MYMCS/ Zoho call raised for any damage to the plate freezer. Are they using Plate freezer in batch wise; and is the batch details captured in the register/ Know App? Is Hand Gloves used while placing and retrieving gel pads from the Plate Freezer? is the plates removed from the Plate freezer and cleaned with dry cloth after production of every batch? Are plate freezer doors kept closed and locked while running?)' as question, 'Ensure that the PCM production information are recorded in the register/Know app. After each production, wipe down with a dry cloth. If there is any damage, raise the MYMCS/Zoho call. When loading and unloading the PCM pads, wear handgloves. While the machine is operating, lock the door. Ensure to follow plate freezer process 100%' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is the Color coding for ice boxes getting followed?' as question, 'Follow the CF picking process as per below i. Blue PCM - Frozen orders ii. Grey PCM - Chilled and cutveg orders iii. Red PCM, Syntex & Consta - Fresho meat' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the crates washed cleanly? Are the old stickers removed from crates while washing? Is the same dried and given for picking?and also is the picker removing if any stickers are available on the crate?' as question, 'Before beginning the picking, make certain that all stock is in clean crates and that any old labels have been removed.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the egg picked; moved to outbound staging area and stored in the separated demarked area; After Crate QC; is a Signage Board on the pallet as (Eggs Pallet- handle with Care) displayed; inform outbound team for Dispatch as per the best practice process circulated?' as question, 'Shift controller must ensure that the egg is not damaged while in transit.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the Internal Audit checklist carried out and actioned on Gaps identified and are they sharing the report to Central SCM spoc , DC manager & RBH?' as question, 'Conduct every month internal audit and communicate those mails to respective stakeholders with the gaps and actino plan' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'Is the picker picking PCM Packs only from the horizontal Freezer @ -25o at the time of packing of orders?' as question, 'Ensure that the PCM pads are picked from the horizontal freezer or frozen room. Pickers should not pick directly from the plate freezer.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'DC Operations' as process, 'Is the Trolley used for picking by the picker always while picking? ' as question, 'Ensure that the picker always uses a trolly while picking. Make certain that there is no baby picking.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'Cold Chain Operations' as process, 'PPEs (Hand gloves/Safety Shoes/Jacket) - 1. PPEs are in good condition 2. PPEs issue register/ Know App is maintained 3. All Employees are using PPEs at the time of Entering cold room 4. PPEs are stored in proper/Dedicated place 5. Awareness signage board is displayed 6. Sufficient PPEs are available' as question, '1. Ensure that all PPE is in good working order. 2. An up-to-date PPE issue register/Know app should be maintained. 3. Ensure that employees are wearing PPE when working in a chilly room. 4. Ensure PPE signage board is displayed. 5. Personal protective equipment (PPE) should be stored neatly.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is all orders cancelled before 12 mid-night  removed in the DC and send communication to T4 Team?' as question, 'Before dispatching, remove all cancelled order crates that were cancelled before 12:00 a.m. in DC and send those details to the T4 team through mail' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the loading is happining from the DC as per the store wise ?' as question, 'Ensure to load the T4 vehicle as per below. The nearest store crates should load last in the vehicle, while the longest store crates should load first.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the DC sending daily mail to T4 team for Picked crates vs QC vs GP details ?' as question, 'Ensure to match picked vs qc covered vs gp crates count.' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is all orders cancelled before 12 mid-night  removed in the DC and send communication to T4 Team?' as question, 'Duplicate' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Does the (DC) exceeded the F&V purchase limit of 12% from vendors in DC?' as question, 'Ensure that you acquire the most stock from the CC and that you get less than 12% of your stock from the direct vendor.' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is any Auto PO Edited? Is all More than PO qty being rejected by Receiver? If Edited is the edit done only in the B&M Heads ID?' as question, 'Receiving incharge has to ensure that POs edit should be done only by B&M Head' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is any F&V stock received if the stock is already available in the CC. Check Forecast Report?' as question, 'B&M Has to ensure that the fv stocks should procure from CC, If CC don''t have the stocks then only they need to give PO to local vendors' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is any F&V SKU received on the same day with different Cost Price (CP) stock? If receiving happens escalated through mail on same day?' as question, 'Ensure to receive stocks from vendor with same CP' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is any stock received with a higher Cost Price (CP) compared to the CC inward for the respective region on the same day?' as question, 'If the stock is already available in DC or CC arrival, do not receive it from the vendor higher CP' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is the F&V PO raised for Indent Qty before vendor arrival?' as question, 'Ensure that the PO is created prior to the vendor''s arrival in DC.' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Are the details of the pullback stock confirmation from the B&M team shared with the Central SCM Inventory and the Regional Inventory manager?' as question, 'Ensure that all pullback communication emails are marked with the Central Inventory team and the regional inventory manager.' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Is the confirmation from the B&M team regarding ICM removal for the pullback SKUs recommended for PRN to prevent the generation of the next indent for these SKUs?' as question, 'Ensure that the pullback PRN is raised following the confirmation of ICM removal.' as recommendation
union select 'B&M' as process_owner, 'Return Management' as process, 'Has any stock been received for the pullback stock initiated by the B&M, considering various reasons such as Product Recall, Excess Inventory, Seasonal or Clearance Sales, etc.?' as question, 'All the Pullback PRNd Skus list must be available in B&M Mail' as recommendation
union select 'B&M' as process_owner, 'Inward Management' as process, 'Is the B&M team actively sending emails and addressing the unpicked GDN cases, ensuring clearance of GDN stock within the 7-day threshold? In the event that stock remains unpicked for more than 7 days from GDN generation, is it the practice to dispose of the stock, and is it disposed from the GDN area?' as question, 'Ensure that the GDN is handed over to the vendor within 7 days or the stocks are disposed of, although mail communication with B&M is essential.' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is 2 Times Energy drinks served to staffs in Summer Season ?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the 3-4 times Tea & Snacks served in5K DS ? (Snacks mandatory for night shift employees)' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Breakfast, Lunch and Dinner served for Staffs in DC for Rs.10/-? (Breakfast for all staffs, Employee can avail either lunch or dinner)' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Changing Room Available for Woman Staffs ? (Applicable wherever Woman Staffs working)' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the DC having Tie up with nearest Creche (Baby Care) within 1KM radius ?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Lockers provided to each Employees in the Shift?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Washrooms available in DS Premises and Hygiene accessories available as per list? (Male - Minimum 2 urinal and 2 wc per 100 employee, 1 water closet (Indian) and 1 water closet for 25 women (Sanitary waste disposal, dustbin, health faucet, wash bas' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Bus Facility arranged for dropping Morning shift employees and pick up night shift employees, drop night shift employees and pick up after noon shift employees? (Applicable only for DC-Puzhal-Chennai, DC-Pune, DC-Chandu-NCR, DC-Bhiwandi-Mumbai, DC-Sakrial -Kolkata, DC-Ahmedabad, DC-Jigani-Bangalore)' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Employee Help Desk and Grievance redressal desk available in the DC?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'If an employee resigns, does the manager have a one on one to understand the reason behind this decision and try to retain the employee. Managers should follow the exit process laid down by the Company?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'Is there any employee exit allowed without a proper investigation in the presence of the Regional HR Head? ( A detailed investigation report will be prepared by regional HR. This will be part of HR audit checklist. All such exits require Business Heads approval' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Handling Exits' as process, 'For Poor Performance Employee who is in the bottom 10% whether the refresher training has been imparted? (Employees should not be in bottom 10% consequently for 3 months he should not be asked to leave for this reason with out providing refresher training' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers spending 1 hour with the new joiner on his 1st day in the floor after NHT (New Higher Training)/Induction to inform him about job responsibilities, culture at bigbasket and any other information that makes his job easy' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Labour and Establishment Compliance' as process, 'Display of abstracts, notices, holiday list, S&E RC, CLRA RC, GST RC, ICC committee members list, Grievance redressal, Whistle blower policy and Trust benefits' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers being fair in granting leaves?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers lead by example?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are Managers providing timely feedback to the employee? He should take time to explain to the employee where he is going wrong and coaches him on what is correct in a professional and respectful manner.' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are all the Line Managers/Supervisors aware of policies and benefits provided by bb like number of leaves, bb TRUST etc. and communicate the same to the Associates' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Are the employees forced to do OT?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager appreciate the employees when they do a good job and are the Managers participating actively in R&R and engagement events, to make employees feel that they are valued?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Manager propagate a culture of respect?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers ensure that the employees'' duty hours are maintained? Managers should also ensure that lunch timings for their reportees are not unnecessarily delayed and are maintained consistently.' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Dose the Managers in DC restrict OT to 2 hours post normal shift timings to ensure that the Associates are not overworked?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is Managers having one on one with any employee who is in the bottom 10% in the department(DC). The manager should try to understand the reasons behind the gaps in performance and if the employee needs any help. This meeting should be held Weekly till the' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Is the Line Managers always present in Daily Huddles and spread awareness on organizational targets, policy changes etc.,' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Manager Behavior' as process, 'Does the Managers have weekly meetings with the associates where they should talk about targets, etc. These meetings should have action points which are minuted and status on the action points should be provided in the next meeting' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Drinking Water dispensers installed in every 30 Sqmtrs and Water refilled timely ?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Rest Rooms provided to DC Staffs ? ( well ventilated with Fans , Benches , Minimum 2 Bunk Beds in DS)' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Segmented plates, spoons, water dispenser, hand wash basin, dustbins available and efficient waste disposal, Hygienically maintained ?' as question, 'Pending' as recommendation
union select 'BB Engagement Model' as process_owner, 'Amenities' as process, 'Is the Water Cooler / Dispenser serviced every 6 months once and water Tank maintained cleanly without dust inside as well outside?' as question, 'Pending' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Air curtains and pvc strips are available at entrances and doors are equipped with self closing mechanism?' as question, 'Air curtains and PVC strips should be available in entrance' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'All electrical equipment''s, accessories, panels and in good condition and cautionary sign boards?' as question, 'All electrical equipment''s, accessories, panels and in good condition and cautionary sign board should be available' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Chicken Cutting Machine equipped with Safety Guard and are all butchers using the Machine without bypassing?' as question, 'Are all Chicken Cutting Machine should be equipped with Safety Guard and are all butchers should be used the Machine without bypassing' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per the Butchery Process?' as question, 'Ensure Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Dust bins being provided with dust bin bags? (Exception plastic banned cities) Is all Housekeeping tools & cleaning aids kept in designated place? Are any Butchery crates used for disposing process waste? Is all process wastage discarded into closed dust bins?' as question, 'Ensure all Dust bins being provided with dust bin bags (Exception plastic banned cities) Is all Housekeeping tools & cleaning aids kept in designated place Don''t use Butchery crates used for disposing process waste. Ensure is all process wastage discarded into closed dust bins' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are all Processed stocks kept in SS bins & stacked in racks provided? Is FIFO followed for dispatch?' as question, 'Ensure all Processed stocks kept in SS bins & stacked in racks provided. Is FIFO followed for dispatch.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Are all the assets clean and kept in the designated location?' as question, 'All assets should be clean and keep in the designated location' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are appropriate documentation and records maintained for a period of one year or the shelf-life of the product, whichever is longer?' as question, 'Shelf life documents should be maintained as per process' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are Butchers wearing PPEs (Hand gloves, Body Aprons, Head Cap and Shoes during Meat Processing? Jackets or aprons are cleaned and sanitised daily? Is the Nitrile gloves provided for all other butchers?' as question, 'Are Butchers should wear PPEs (Hand gloves, Body Aprons, Head Cap and Shoes during Meat Processing Jackets or aprons are cleaned and should be sanitised daily. Ensure Nitrile gloves provided for all other butchers' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are finished products properly packed and sealed with no defects in the seal, meeting proper labeling requirements according to FSSAI and Legal Metrology norms?' as question, 'Ensure all finished products should be packed propelry' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are incoming materials, semi-final products, and final products stored based on their temperature and humidity requirements in a hygienic environment? Is FIFO & FEFO practiced?' as question, 'All the products should be stored as that particulr product specific temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Are Legal Metrology stamping available for all weighing balances and is the certificate available at the Butchery?' as question, 'Ensure that stamping should be available all weighing stones and certificates also need to be maintain for that stones' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are monthly trend analysis and quarterly audit reports readily available?' as question, 'Monthly trend analysis should be maintained' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are raw materials inspected for food safety hazards, including temperature checks for products like frozen goods and monitoring temperature throughout the supply chain, especially for fish and seafood?' as question, 'Ensure to inspect raw materials without fail' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are recalled products held under supervision and either destroyed or reprocessed/reworked in a manner that ensures their safety? Are records checked for compliance?' as question, 'Ensure to check the recalled stocks' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are sufficient Fire Extinguishers available?' as question, 'Ensure sufficient Fire Extinguishers are present on-site.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Are There any gaps on the floorcorners of the panel wall.? If anything is found same must be closed properly to restrict pest entry into facility. Are all Floor; tiles in intact condition without any damage?' as question, 'Ensure to close all the wall gaps to avoid pest entry' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Does Butchery have an updated FSSAI license displayed at a Notice board?' as question, 'Updated FSSAI license should be displayed in notice board' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is a First Aid box present in all butchery? With the listed medicine ?' as question, 'First aid box should be refilled as per HSE guidelines' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is Adequate ventilation is provided within the premises?' as question, 'Adequate ventilation required in premises' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all fire safety system available (Fire extinguisher, Fire alarm system )in good working condition ? Check service details?' as question, 'Ensure all fire safety system working good' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is all received Bulk stocks stacked SKU wise in defined location & in desired temperature-controlled room following FEFO and receiving date identification (Labelled in crate Tray Hanger).' as question, 'Keep all received bulk stock in demarked location with specific temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all Safety signages (Butcher Related) Displayed and are the signages in Good Condition?' as question, 'Ensure all safety related signage board should be displayed in production area' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt? Are all Utensils washed using cleaning aid suggested by Diversely Care after every use?' as question, 'Ensure all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt. Ensure all Utensils washed using cleaning aid suggested by Diversely Care after every use' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is any Write-off recorded in system apart from QC Certified Qty and Is all Write-Off raised with proper remarks and as per the approval metrics?' as question, 'All Wos sohuld be carried out with proper approvals' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is Cold rooms Chiller Freezer maintained clean & neat? Is the Temperatures maintained at desired level? Is the Ice formation found in cold room? Refer the records maintain on temperature and visual check on cleanness? Store Is the temperature for checked maintained less than 4 deg C at any point of time?' as question, 'Ensure to maintainall cold rooms clean nad neat, and maintain the records of temperature' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is incoming material procured in accordance with internally laid down specifications from approved vendors? Are records checked for specifications, supplier information, batch numbers, and quantity procured?' as question, 'Incoming material should be procure with approval vendor.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is QC person carrying out calibration for all weighing scales & Bizerba using certified dead weight (Standard weight stone certified by weight & Measurement Department? Is all the Reports available? ' as question, 'Ensure to follow calibration process daily basis' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Color coded crates maintained for the product handling during Operations ( Receiving and while processing as product should not touch the ground)? Red crate for - Chicken, Orange crate for - Mutton, and Bottom Crate for Chicken and Mutton - Green color. Blue crate for - fish, Yellow crate for prawn and bottom crate for Fish ad Prawn must be Brown' as question, 'Color coding should be maintained while handling the products' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the daily Cycle count is carried and variance is updated in the system as per the approval metrics? ' as question, 'Butchery all SKUs should be done daily cycle count and corrections should be donw with proper approvals' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the dispatch register/ Know App is maintained and updated?' as question, 'Stock dispatches should be captured in register' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'Is the Labour license available and displayed at the notice board?' as question, 'Labor license should be displayed in notice board' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the medical test certificates available for all butchers as per FSSAI (Yearly once) and is the Certificates valid on the day of Audit?' as question, 'Medical certificate should be available for all the butchers and should be vaild during audit date' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the shipper boxes are clean and free from off smell.Temperature inside shipper box is less than 5 deg C ?' as question, 'All the Shipper(Syntex) boxes should be clean and free from smell. Ensure to maintain temperature less than 5 deg C' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the traceability exercise conducted once every three months, covering the journey from raw material to finished goods and from finished goods to dispatch locations?' as question, 'Traceability exercise should be conducted every 3 months without fail.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'Is the Training records available for all Machine operators Butchers? And are only trained Machine operators Butchers operating the Machines?' as question, 'All butchers should be trained and records shoud be maintained' as recommendation
union select 'Butchery Incharge' as process_owner, 'Out Bound Operations' as process, 'Is the transporting vehicle for food use are kept clean and maintained in good condition?' as question, 'Ensure that transport vehicle should be clean before the stock dispatch' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Personnel hygiene facilities are available including adequate number of toilets ( not opening directly into processing area), hand washing facilities and  change rooms. ' as question, 'Ensure to maintain clean toilets and other hyiene facilities including hand washing facility in change rooms' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest control program is available & pest control activities are carried out by trained and experienced personnel. Check for records.' as question, 'Pest control activity should be carried out and maintain the required records during the audit' as recommendation
union select 'Butchery Incharge' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Premise  has facility for  storage of waste &  inedible material such that contamination with food is avoided and is also free from any pest activity.' as question, 'Ensure to store waste material free from pest activity' as recommendation
union select 'Butchery Incharge' as process_owner, 'Administration' as process, 'The premise is well equipped with chilling room, freezing room, freezer store or freezer as per the operations and fitted with temperature measuring or recording devices.' as question, 'Ensure the premise is well equipped with chilling room, freezing room, freezer store or freezer as per the operations and fitted with temperature measuring or recording devices.' as recommendation
union select 'Butchery Incharge' as process_owner, 'Operations' as process, 'The temperature in room for boning out & trimming are controlled & held suitably low(less than 12 degC), unless cleaning of equipment & utensils are carried out at least every four hours.' as question, 'Ensure to maintain room temperatue and clean the utensils atleast every 4 hours' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Bulk consumables stacked in bulk location & is any consumables found stacked inside production area?' as question, 'Ensure to keep all bulk consumables in bulk location instead of keeping inside the production area' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per Diversely care inputs after use?' as question, 'Ensure all Chopping tools like knives & hand peelers; cutting & washing machinery cleaned & sanitized properly as per Diversely care inputs after use?' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Dust bins being provided with dust bin bags? (Exception plastic banned cities)/ Is all Housekeeping tools & cleaning aids kept in designated place? Are any F & V crates used for disposing process waste? Is all process wastage discarded into closed dust bins?' as question, 'Ensure all Dust bins being provided with dust bin bags. (Exception plastic banned cities)/ all Housekeeping tools & cleaning aids should be kept in designated place. Don''t use any F & V crates used for disposing process waste. ENsure to all process wastage discarded into closed dust bins.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all F & V arranged properly in racks with segregation of Fruits & Vegetables? Are all Rotten stocks segregated from the bulk & discarded?' as question, 'Ensure all F & V arranged properly in racks with segregation of Fruits & Vegetables.Ensure all Rotten stocks segregated from the bulk & discarded.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Leafy vegetables fresh with roots properly cut?' as question, 'Roots cut preperly for leafy vegetables' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Mix Veg & fruit articles randomly checked for weights?' as question, 'Ensure to pack mix fruit & veg SKUs as per process' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all Processed stocks kept in SS bins & stacked in racks provided?' as question, 'Ensure all Processed stocks kept in SS bins & stacked in racks provided.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all the packs properly labeled with Pack Wt.; Packed Date and Best Before Date with 5-day shelf life; including date of packing?' as question, 'Ensure to label the packed stocks with packed date,bbd with 5 days, include packing date' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are Clean crates used for raw material storage? Is any finished product found stacked in the Dirty crates inside production area?' as question, 'Ensure to use clean crates for raw material storage, Don’t use dirty crates inside cutveg area' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are closed Dust bins provided at hand wash area/chopping tables/weighing scale points/raw material entry location?' as question, 'Ensure to use closed Dust bins  at hand wash area/chopping tables/weighing scale points/raw material entry location' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Are the Prepared raw materials packed as per packing norms given?' as question, 'Prepared raw materials should be packed as per packing norms' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are There any gaps on the floor/corners of the panel wall.? If anything is found same must be closed properly to restrict pest entry into facility. Are all Floor; tiles in intact condition without any damage?' as question, 'Ensure to close all the wall gaps to avoid pest entry. If any damage MYMCS call has to be raise and close within the timeline' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Do the employees of cut veg section practices hygiene inside production or preparation area; are Empty Crates available without palletization in bulk area?' as question, 'Ensure the employees of cutveg practice hygine. Don''t place any empty crates in cutveg area without palletization' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Does the cut-veg Incharge check the quality of stock received from FV? Are the stocks received from FV for production; QC certified by the QC Incharge? Is the rejection happening for poor quality stocks?' as question, 'Cutveg incharge has to check the quality before stock receiving from FV. QC incharge has to certify the stock' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Does the Production staff sanitize their hands as suggested by Diversely care after every product change over?' as question, 'Staffs should be sanitize their hands whenever the production product change over' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Does the staff consume/ Carrying any food; chewing of tobacco/chewing gum inside the facility /processing area?' as question, 'Ensure the staff shouldn''t consume/ Carrying any food; chewing of tobacco/chewing gum inside the facility /processing area' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Employee should be wearing clean outer garments. (Uniform as provided) and is suggested Footwear used inside the cut-veg facility? Are the foot caps provided and used by the visitors?' as question, 'En sure all employees should be wearing clean outer garments. (Uniform as provided) and is suggested Footwear used inside the cut-veg facility. Ensure the foot caps provided and used by the visitors.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is all Utensils used in production space like SS containers; dozing bins; SS racks kept clean without any dust & dirt? Are all Utensils washed using cleaning aid suggested by Diversely Care after every use?' as question, 'Ensure SS containers; dozing bins; SS racks kept clean without any dust & dirt, and all Utensils washed using cleaning aid suggested by Diversely Care after every use.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is any machinery under maintenance properly Labeled with "NOT IN USE" signage in the production space?' as question, 'Paste NOT IN USE sign of unused machines' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is any Raw Material/processed material kept below the Pest-O-Flash? Is Pest-O-Flash in working condition; switched ON & Trays & tubes of Pest-O-Flash clean.' as question, 'Team has to ensure that to avoid storage under the Pest-o-flash' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Area inside the facility free from cob webs in ceiling panels / behind racks / below chopping tables/and other possible places. Are any open cables found in side production space? If found any should be properly insulated.' as question, 'Ensure Area inside the facility free from cob webs in ceiling panels / behind racks / below chopping tables/and other possible places. Are any open cables found in side production space.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is CFTRI dozing preservative storage containers kept neat & clean with proper identification of chemical name. Is CFTRI dozing done as per article wise recommendations; using the Pocket weighing scale provided?' as question, 'Keep the CFTRI dozing containers kept neat and clean with identification' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Employee lockers & changing rooms clean without any unwanted material kept inside?' as question, 'Ensure employee lockers & changing rooms clean without any unwanted material kept inside' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is FIFO/FEFO principal followed while stacking for all products in the cold room?' as question, 'Incharge has to ensure follow FIFO/FEFO while stacking the stocks' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is minimum of 1 ft. space available/Left for cleaning of dirt & dust between wall & Cutting tables/Machinery/SS Bin rack?' as question, 'Ensure a minimum of 1 ft. clearance between walls and equipment for cleaning. Regularly monitor and maintain this space to uphold safety and hygiene standard' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is Staff; Raw Material entry doors provided with auto door closures & is the doors always kept closed to avoid pest entry from outside. Employee entry /raw material entry/Cold room chute door should be kept clean and free from stains.' as question, 'Install auto door closures on staff and raw material entry doors, keeping them closed at all times to prevent pest entry. Regularly clean and maintain employee and raw material entry doors, as well as cold room chute doors, to ensure they remain free from stains.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Cut veg & F&V Wastes segregated and disposed as per Waste Management Process? Is all the chipped of waste removed after the processing every 2 Hours or when the Bins are filled whichever is earlier?' as question, 'cut veg & F&V wastes should be segregated and disposed of according to the Waste Management Process. All waste chips should be removed every 2 hours or when the bins are filled, whichever comes first, to maintain cleanliness and efficiency.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in Cut Veg Preparation Room? Refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'First Aid Box should be readily available in the Cut Veg Preparation Room, refilled as needed, and stocked with all recommended contents as per guidelines for immediate response to any injuries or emergencies.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Indent raised as per forecast norms and shared to B&M? Is forecast and indent data available (manual & Excel)? Is the data recorded for SKU wise TO; GRN Qty with GRN no; Preparation waste Qty; Closing stock qty? Is the Packed SKUs qty has been noted and GRN posted in system? Is cut veg Incharge/ Supervisor monitoring the pending GRN? (In warded but not GRNd)' as question, 'Indent should be raised as per forecast norms and shared with B&M, with forecast and indent data available both manually and in Excel. Record data for SKU-wise TO, GRN Qty with GRN no, Preparation waste Qty, and Closing stock qty. Ensure Packed SKUs qty is noted and GRN posted in the system, with the Cut Veg Incharge/Supervisor monitoring pending GRN (Inwarded but not GRN''d).' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the metal Detector being used after Packing?' as question, 'a metal detector should be utilized after packing to ensure product safety and quality control by detecting any metal contaminants that may be present in the packaged goods' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Packed raw material stickered with Fresho- CFTRI label with requisite fields available in it?' as question, 'the packed raw material should be labeled with a Fresho-CFTRI sticker containing all requisite fields as per standards to ensure proper identification and traceability.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the Prepared SKUs moved to Cold room immediately after labelling and stacked in location? Is the SKUs available for picker at all time?' as question, 'prepared SKUs should be promptly moved to the cold room after labeling and stacked in their designated location to maintain freshness and quality. SKUs should be readily available for pickers at all times to facilitate smooth operations and timely order fulfillment' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Operations' as process, 'Is the weighing scale & Bizerba calibrated as per schedule? And certificate made available near to each Machine?' as question, 'the weighing scale and Bizerba should be calibrated according to the schedule, with certificates displayed near each machine to ensure accuracy and compliance with standards.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is there a floor mat available at the entry points and is it clean & neat? Is the floor maintained clean without dirt or dust & is the floor dry without stagnated water? Is Walls & ceiling panels clean without any dust; smudge; water leakages & stains?' as question, 'there should be floor mats at entry points, maintained clean and neat. The floor should be kept clean, free of dirt and dust, and dry without stagnated water. Additionally, walls and ceiling panels should be clean, free from dust, smudges, water leakages, and stains for hygiene and safety.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'PPEs (Hand gloves/Head cap/Face mask) - 1. PPEs are in good condition 2. PPEs issue register/ Know App is maintained 3. All Employees are using PPEs at the time of Entering F&V 4. PPEs are stored in proper/Dedicated place 5. Awareness signage board is displayed 6. Sufficient PPEs are available 7. Used PPEs are stored & disposing properly' as question, 'Ensure PPEs (Hand gloves/Head cap/Face mask) are in good condition. Maintain a PPE issue register or use a designated app for tracking. All employees must wear PPEs upon entering F&V areas. Store PPEs in a proper and dedicated location. Display awareness signage boards regarding PPE usage. Ensure sufficient stock of PPEs is available at all times. Properly store and dispose of used PPEs according to guidelines.' as recommendation
union select 'Cut veg Incharge - Supervisor' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Were the hand wash sanitizers available at staff entry point? Is Production staff washing their hands on entering the cutveg section using sanitize and even are they following the same after using wash room?' as question, '1. Ensure hand wash sanitizers are available at staff entry points. 2. Monitor production staff to ensure they wash hands upon entering the cut veg section using sanitizer and follow the same after using the washroom to maintain hygiene standards.' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all dedicated vehicles onboarded into TMS? And are drivers using TMS applications to start and end the trip?' as question, 'All dedicated vehicles lists in TMS must be updated. Drivers must initiate start and end trips in the TMS app.' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all delisted Inactive Dedicated vehicles checked for and deactivated in the TMS every fortnightly?' as question, 'Make sure you delist the inactive vehicle from the TMS every fortnight' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Are all HHDs and MHE batteries are kept under charging while non-operational time?' as question, 'Ensure that all the unsued batteries under charging section at non-operational time' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Are all staffs wearing valid ID card? (Including HK, Security, G1 & G2)' as question, 'Ensure to wear the iD card for all the staffs' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are all the dedicated vehicle records correctly updated in TMS as per requirement?' as question, 'Ensure to update all the dedicated vehicle details in TMS while onboarding' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Are any salable products or Discount sale product moved and stored at dump storage area? ' as question, 'Ensure that only completely unsaleable stock is transferred to the dump area.' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Are dispatches carried out on-time as per the trip scheduled in TMS?' as question, 'Ensure to dispatch all the LOB stocks within the agreed cut-off timing' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are empty carton boxes stored in the DC according to the defined layout? Has the auditor physically cross-checked to confirm this facility?' as question, 'Ensure to keep all disposable carton boxes should be kept in demarked location' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are empty vehicle weighment certificates and loaded weighment certificates available for scrap lifting (Applicable for Metal, Wood, Plastic scrap)? Has the auditor physically cross-checked these certificates and verified whether the DC team, under the DM Manager Direction project or Security, are authorized persons to go along with the vehicle for weighment?' as question, '1.Collect empty and loaded weighment certificates for all loads. 2. A security officer, a project manager, or a DC approved representative should accompany the vehicle for weighing.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are only approved vendors used to scrap the materials? Has the auditor cross-checked the approved vendor list and the register?' as question, 'Ensure that only authorized suppliers are used to remove scrap from DC.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are scrap carton boxes bundled within 50Kg in the DC? Has the auditor physically cross-checked to confirm whether the DC is following the bundling process?' as question, 'Scap cartons must be tied together in 50kg bundles. Check whether the bundleing procedure is being followed or not.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Are the scrap corrugated/carton boxes sent back to DC in bundles of 5K and BB Now in the cage? If the 5Ks are not sent back, has approval been obtained from the regional business head and Head of the project for direct sale from 5K, following the same process?' as question, 'Inform the 5K crew to fill the cages with empty carton boxes; if not, obtain a mail of approval from RBH & RPH.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'CCTV system - 1. CCTVs are installed at required places 2. Location details are available 3. Backup is available - Minimum 15 days 4. All CCTVs are in working condition' as question, 'Make sure there is CCTV surveillance throughout the entire DC area. Ascertain a minimum backup of 15 days.' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Does the Critical Assets Breakdown addressed in time and resolved by raising Ticket in My MCS/ Zoho? Check for the details Is the regular and critical assets requirement status available with follow up?' as question, 'If there are any critical asset damages, make sure to raise MYMCS or Zoho.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Does the security frisk all the staffs moving out of DC?' as question, 'Ensure all staffs & visiter should be frisk while out from DC premises' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'E & S Audit - 1. Audit is conducting monthly basis 2. Report sent to respective dept. regularly 3. Gaps are closed based on risk priority. 4 Previous month report must be share before 5th of next month' as question, 'The prior month''s E&S audit mail should be circulated to the relevant stakeholders each month prior to the 5th' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Electrical Service - All Electricity panels; Switch boards maintained in good condition 2.All earthing points & lines are in good condition 3. All panels are free from obstruction 4. For Panel room Suitable FE is placed 5. Cautionary signage is displayed at entrance of the area/room' as question, 'Ensure All Electricity panels; Switch boards maintained in good condition 2.All earthing points & lines are in good condition 3. All panels are free from obstruction 4. For Panel room Suitable FE is placed 5. Cautionary signage is displayed at entrance of the area/room' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Emergency/Alert system - 1. Alarm System is available at cold room 2.Installed alarm system is in working condition 3. Periodic check register/ Know App is maintained' as question, 'Ensure alarm in working condition' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Facility - Ventilation & Lighting - 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as question, 'Ensure- 1. Sufficient number of lights & Ventilators provided 2. All are in working condition 3. Any complaints from employees / depts. 4. Emergency lights are working 5. All ventilation facilities at suitable manner' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Fire Alarm System - 1. Fire Alarm system is available (Detector/MCP/Hooter/Panel) 2. Manual Call Point -MCP is placed at easy accessible locations 3. All Detectors are in working condition 4. FAP - Panel is in working condition 5. Backup power is connected to Panel 6. Service AMC details are available' as question, 'Ensure - 1. Fire Alarm system is available (Detector/MCP/Hooter/Panel) 2. Manual Call Point -MCP is placed at easy accessible locations 3. All Detectors are in working condition 4. FAP - Panel is in working condition 5. Backup power is connected to Panel 6. Service AMC details are available' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Fire Extinguishers - 1. FE list is displayed at notice board 2. FE placed as per layout design/drawing 3. Sufficient No. of FE are available 4. All FEs are free from Obstructions 5. Service / Refill Info sticker is pasted on All FE 6. All FE are in good condition - No FE are in low pressure; accessories are damaged 7. Signage board is fixed for all FEs for easy identification' as question, 'Ensure- 1. FE list is displayed at notice board 2. FE placed as per layout design/drawing 3. Sufficient No. of FE are available 4. All FEs are free from Obstructions 5. Service / Refill Info sticker is pasted on All FE 6. All FE are in good condition - No FE are in low pressure; accessories are damaged 7. Signage board is fixed for all FEs for easy identification' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'First Aid Box  - 1. Sufficient FAB are available as per requirement(At least 1for 150 employees) 2. Standard listed Items are available in the box 3. FA Items list is available or pasted on box 3. FA incident register/ Know App is maintained 4. FAB monthly checking register/ Know App is maintained 5. All items are within the Expiry dates 6. Signage board display' as question, 'Ensure - 1. Sufficient FAB are available as per requirement(At least 1for 150 employees) 2. Standard listed Items are available in the box 3. FA Items list is available or pasted on box 3. FA incident register/ Know App is maintained 4. FAB monthly checking register/ Know App is maintained 5. All items are within the Expiry dates 6. Signage board display' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'GM article >500 Value items write off vs Available status with condition to be verified by the DC manager and secondary auditor every week & Tracker must be available' as question, 'Keep track of GM articles'' physical availability vs their WO, and maintain useable stocks.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Has the vendor picked the carton box at the same price for the whole month? Has the auditor cross-checked the invoices for all sales?' as question, 'Ensure carton scap billing price be same' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Have all the Breakdown non-usable/repairable assets kept in a designated area with details updated in My Impact as on date in DC?' as question, 'Store all damaged assets in their designated areas. Updated with the same facts in Myimpact' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Incident / Accident Occurrence register/ Know App - 1. Incident / Accident occurrence register/ Know App (complete shift log book) is available at security desk 2. All First aid / abnormality incidence /accident are recorded 3. All incidents are reviewed by DCM & taken actions to avoid repetitions.' as question, 'Capture all the incident in register/Know app and review with DCM to avoid repetitions' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is a certified Electrician / Plumber available in DC? dose the Electrician / Plumber wear safety gloves and shoes while working?' as question, 'Make sure to hire certified electricians and plumbers, and while working, always use safety precautions.' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Is all active Business location in the region onboarded on TMS and are all location movements happening through TMS?' as question, 'Ensure all the DC to Hub, CC to DC stock movements happen through TMS' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is all Dump disposed through authorized empaneled vendors only? Check vendor compliance documents? Check as per the process for all type of waste' as question, 'Ensure all dump is disposed of through authorized empaneled vendors only, checking their compliance documents regularly and following the proper process for all types of waste disposal to adhere to regulations and maintain environmental responsibility.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is All Emergency Contact Details available; updated and displayed at Security Entry Gate / point?' as question, 'Ensure to update upto date emergency contact details in entry point' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is all Inventory -Food Items including fruits and vegetables meat, bakeries and dairy products disposed only after removing packaging?' as question, 'Ensure to remove all the packaging before dispose' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is all legal documents of the Vehicle & Driver available? Photo Copies should be filed in DC?' as question, 'Ensure All documents pertaining to dedicated vehicles must be filed in DC with validity' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Is all Material Handling Equipment Checklist/ Know app available for equipments used in DC? Are they checking daily? Records available? (Pallet truck; stackers; hand Trolleys; Reach truck; Forklift; docking equipment; goods lift; other machines check list available?' as question, 'Ensure Every day, the checklist for every machine is updated in the Know app.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all outgoing stock movement recorded in the security outward register/ Know App with time?' as question, 'Ensure all outward movements should be recorded in register/Know app' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is all Unwanted Lights; fans & other electrical appliances/machinery switched off when theyre not being used or required?' as question, 'Ensure switch off unused electronic appliances when not in use' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is all vehicles in good condition as per the agreed clauses ? (Inter DC Vehicles)' as question, 'Ensure all the IHVs in good condition as per agreement' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC issuing warning letters for any deviation and acknowledgements filed? Is the apology letter for the same obtained from employee and filed in his records?' as question, 'Make sure that every process deviation and improper practice receives a warning or apology letter.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC opening closing register/ Know App available along with key register/ Know App at the security & are the Keys available & surrenders details recorded?' as question, 'Ensure to all the Keys takeover and handover records must be maintained in security' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is DC-Manager monitoring all pending system transactions? (In warded but not GRNd-FMCG; Cut-veg; FV)' as question, 'Ensure to complete all the inwards GRN same day. If any delays communicate to DCM through mail' as recommendation
union select 'DC Manager' as process_owner, 'Waste & Dump Disposal Management' as process, 'Is Dry and Wet waste stored separately with proper identification in the designated area or Room? Check physically' as question, 'Ensure physically is that wet & dry waste dispored seperately' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is GSTIN displayed at appropriate place on name board or sign board or near front door of the premises? Also; is the registration certificate displayed in the business premises?' as question, 'Ensure Both the registration certificate and the GSTIN number should be visible at the entrance and notice board, respectively. (Location name also available in Notice board GST certifiate)' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is metal, wood, plastic scrapped monthly within 7 days from the date of the movable asset audit in T1 DC? Has the auditor cross-checked in the scrap register?' as question, 'Ensure all scrap must be disposed within 7 days of asset audit with proper documents' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Petty Cash maintained at DC; are all relevant supporting for receipt and expenses available and documents maintained on daily basis /recorded? Is vouchers available for any advance with proper approval?' as question, 'Keep track of all the bills pertaining to petty cash without losing track.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is racks and shelfs free from Damage / Dent? Visible check' as question, 'Ensure to periodic check of rack damages' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is regular training conducted for new implementation/ process or changes? Are the ground staff aware of the process?' as question, 'Ensure to train all the staffs for recent releases' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is Security Attendance & Housekeeping register/ Know App Available and maintained at Security Desk? Is the Duty Handover happening properly? Is Handover log Book available?' as question, 'Ensure proper shift handover to securities and housekeeping' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is Separate A4 size tray crates kept in the security, Receiving area or applicable area for Collecting invoice DCs Other documents from vendors' as question, 'separate A4 size tray crates should be kept in the security, receiving area, or applicable locations for collecting invoices, delivery challans, and other documents from vendors to facilitate organized document management and streamline the receiving process.' as recommendation
union select 'DC Manager' as process_owner, 'Asset Management' as process, 'Is the Asset correction carried out as per the timelines? (Movable within 7 Days and Fixed by next fixed asset audit schedule?' as question, 'Make sure to obtain the necessary approvals and close all asset differences within 7 days.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Daily Shift Huddle conducted by DC In charge/Shift Controllers? Is the Monthly MOM recorded and reviewed? Is record for the same available and shown during audit?' as question, 'Ensure to conduct daily huddles and record the details' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Layout Displayed in and around DC premises with Fire extinguisher spot; Emergency assembly spot & emergency Exit point?' as question, 'Ensure to update updated DC layout with emergency exit plan and FE spot' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the DC Measuring the OKR Performance for all Category as per the parameters defined & is the R&R Program conducted as per the Schedules & reports published to Head office on Time with records maintained in DC and Is the DC OKR presentation sent after validation to HO for Monthly Review on or before 7th of every Month?' as question, 'Ensure to update OKR in darwinbox with description. And conduct R&R as per schedule' as recommendation
union select 'DC Manager' as process_owner, 'Administration' as process, 'Is the documents verified and condition fullfilled while onboarding the IHV vehciles?' as question, 'Ensure all the vehicle documents to be upto dated while onboarding the IHVs' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Individual OKR given to Shift controllers; Inventory Controllers; Assistant Manager; Row In charges? Is the same read and acknowledged by all individual and available in record & filed with signature or Mail communication available? Check Darwinbox OKR plan' as question, 'Ensure to update OKR in darwinbox with description.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the invoice request raised by the location project team every fortnight/monthly to HO, Finance Team? Have scanned copies of the scrap outward manual register been sent to the finance team with project manager and DC Manager sign-off? Has the auditor checked email communications to verify the frequency of invoice requests and the attachment of scanned copies of the register?' as question, 'Ensure the location project team raises invoice requests every fortnight/monthly to the HO Finance Team.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the pest assessment carried out and report shared to central HSE on 10th of every month and gap closure status shared before 20th of every month?' as question, 'Send scanned copies of the scrap outward manual register to the finance team with project manager and DC manager sign-off.' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the scrap carton sales outward register/tracker maintained with mandatory columns? Has the auditor cross-checked whether the mandatory columns (Date, Scrap weight in Kgs, Per Kg value, Total sale Value, Security signature, DCM/SM sign, Vendor sign, and acknowledgment of receipt) are mentioned and updated?' as question, 'Fill the register with required field' as recommendation
union select 'DC Manager' as process_owner, 'Scrap Sales Management' as process, 'Is the Scrap lifting (Carton box, Metal, Wood & Plastic) Vendor empaneled in accordance with the fulfillment of Process direction?' as question, 'Ensure the Scrap lifting vendor for carton box, metal, wood, and plastic is empaneled in accordance with the fulfillment of process directions to maintain compliance and efficient waste management practices.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security conducting regular patrolling in the DC premises? (Inside/outside)' as question, 'Ensure securities to do the patrolling' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the security service provider regularly visiting to the site & is a register/ Know App/Checklist available for the same at the security gate?' as question, 'Security service provider has to visit the site frequantly' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the staff movement register/ Know App available and maintained at the security gate?' as question, 'All the staffs who are going outside in duty hours they need to capture their movement in staff movement register/Know app in security gate' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'Is the TMS shedule time vs City haed sign off matching or not ?' as question, 'For all the TMS schedule get approval from city head' as recommendation
union select 'DC Manager' as process_owner, 'Out Bound Operations' as process, 'is the transport vendor payment and invoice process through TMS? Is the any excess vehicle used  approved by SCM Head?' as question, 'Transport billing should match with TMS billing, Ensure all the commertials updated 100%' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is the Warehouse agreement and inter hub vehicle transporter agreement available in DC? Is the agreement being received and valid as on date and filled required details?' as question, 'Verify the availability and validity of the Warehouse agreement and inter-hub vehicle transporter agreement in the DC, ensuring they are up to date and filled with the required details for legal and operational compliance.' as recommendation
union select 'DC Manager' as process_owner, 'DC Operations' as process, 'Is there a Visitors register/ Know App available & is the security capturing & Monitoring the Movement?' as question, 'All visitors movement should be captured in secutry point' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Loading & Unloading - 1. Safe procedures are following for Loading & Unloading 2. Trolley movement area is free from obstruction 3. Cleanliness is maintained at floor 4. Security / respective dept. persons are present at the time of Loading & unloading 5. Materials are transfer through only trolleys - No man lifting of heavy loads 6. Area is illuminated with proper lighting 7. Vehicle wheel stoppers are available' as question, 'Ensure safe procedures are followed for loading and unloading operations. Keep the trolley movement area clear of obstructions to facilitate smooth operations. Maintain cleanliness on the floor to prevent accidents and hazards. Have security or respective department personnel present during loading and unloading activities for supervision and assistance. Transfer materials only through trolleys to avoid manual lifting of heavy loads, ensuring employee safety. Illuminate the area with proper lighting for enhanced visibility and safety. Install vehicle wheel stoppers to prevent vehicle movement and accidents during loading and unloading processes.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'MHE-Stacker/Reach truck/Forklift - 1. Operators are Using PPPEs - Hand gloves-Helmet & Safety shoes & Reflecting Jackets 2. Operators are trained to handle the Equipment 3. Sufficient PPEs are available 4. register/ Know App is maintained for PPEs issue & stock' as question, 'Operators must use appropriate PPEs including hand gloves, helmet, safety shoes, and reflecting jackets. Ensure operators are adequately trained to handle stackers, reach trucks, and forklifts safely and efficiently. Maintain sufficient stock of PPEs for all operators. Maintain a register or use a designated app to track the issuance and stock of PPEs for accountability and compliance.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Activity - 1. Daily or weekly pest control Activity / service carried out as per agreed terms 2.Checklist is maintained 3.Pest Control service treatment schedule details available in DC' as question, 'Conduct daily or weekly pest control activities/services according to agreed terms to ensure effective pest management. Maintain a checklist to track pest control activities and ensure thoroughness. Keep pest control service treatment schedule details readily available in the DC for reference and compliance.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Layout - 1. Pest control Layout display in Notice Board 2.location details clarity -like rodent box; glue box etc.; available in the layout 3. Any changes in layout v/s actual availability of pest contents' as question, 'Display the pest control layout on the notice board for easy reference and awareness. Ensure clarity in location details on the layout, including rodent boxes, glue traps, etc. Regularly update the layout to reflect any changes in pest control measures compared to actual availability to maintain accuracy and effectiveness.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Pest Control Report - 1. Monthly Incident Pest Control analysis report available with Project / facility team 2. All pest incident are recorded and its reviewed' as question, 'Ensure availability of monthly incident pest control analysis report with the project/facility team for monitoring and analysis. Record all pest incidents and regularly review them to identify trends and take necessary preventive measures for effective pest management.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Safety Signage Boards - 1.Facility having sufficient safety singes boards displayed in the DC 2.Mandatory to display the signages - FE/Emergency exit/Authorized person entry/MCP/Danger/MHE Charging point/First Aid box/ Racks -Load notice/Visitor guide etc.' as question, 'Confirm the presence of sufficient safety signage boards displayed in the DC for enhanced safety awareness. Ensure mandatory signages such as FE/Emergency exit/Authorized person entry/MCP/Danger/MHE Charging point/First Aid box/Racks-Load notice/Visitor guide are prominently displayed as per regulations and safety protocols. ' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Training - Security Team - 1. All security staff are trained on FE usage 2. All are aware about emergency handling 3. Aware about Fire alarm system & Hydrant operations 4. Training to be given periodically' as question, 'Provide training to all security staff on fire extinguisher (FE) usage for emergency response. Ensure all security personnel are knowledgeable about emergency handling procedures. Train security team members on fire alarm system operation and hydrant procedures for effective response. Conduct periodic training sessions to refresh and reinforce security staff''s knowledge and skills in emergency preparedness and response.' as recommendation
union select 'DC Manager' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Vehicle Movement - 1. Security is checking drivers Documents like - DL /ID 2. Vehicle documents - Insurance / Permit/ Emission certificates etc. . Vehicles are parked at designated area 3. Alcohol check is conducting at security (Optional)' as question, 'Security personnel should check drivers'' documents such as Driver''s License (DL) and identification (ID) upon vehicle entry. Ensure vehicle documents including insurance, permit, emission certificates, etc., are verified and up to date; vehicles parked in designated areas. Optional: Conduct alcohol checks at security for added safety measures.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are all Picked crates moved to de-marked staging area after picking?' as question, 'ensure all picked crates are moved to the designated staging area after picking for organized and efficient inventory management.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the crates filled with stocks as per SKU wise standard crate weight?' as question, 'ensure that the crates are filled with stocks according to the SKU-wise standard crate weight to maintain consistency in inventory management and transportation efficiency.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the Packing tables; packing area clean and neat?' as question, 'maintain cleanliness and tidiness in the packing tables and packing area to ensure hygienic food handling practices and a conducive working environment.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the stocks moved to respective picking location after packing?' as question, 'ensure that stocks are promptly moved to their respective picking locations after packing to maintain organization and facilitate efficient order fulfillment processes.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Are the stocks received only in Bulk receiving Crate? And moved to Predefined area? Is the FV Stocks received in Clean bulk crate as per process? Bulk crate color code for CC arrival; Vendor Stocks; Organics.' as question, 'stocks should be received only in bulk receiving crates and then moved to predefined areas. Ensure that FV stocks are received in clean bulk crates as per the process. Implement a color-coded system for bulk crates, distinguishing between different arrivals such as CC, vendor stocks, and organics for efficient inventory management.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Does Orgonic covers ( Brown) used for Organic SKUs? Check in packages' as question, 'ensure that organic SKUs are covered with brown organic covers. Check packaging to confirm compliance with organic handling standards.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'does the Picker picks SKUs as per sequence (Hard SKU to Soft SKU; Leafy)?' as question, 'instruct the picker to pick SKUs in the designated sequence, starting with hard SKUs and progressing to soft SKUs, followed by leafy items, for efficient packing and preservation of product quality.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'For All Pieces SKUs (9 SKUs) that are pre-packed Punnet Packed from vendor, is a Standard PLU Barcode Label generated as mentioned in the SKU packet for all Pieces SKUs and stickered in the respective Pick Location Rack ?' as question, 'ensure that a standard PLU barcode label, as mentioned in the SKU packet, is generated for all pre-packed punnet pieces SKUs (9 SKUs) and stickered in their respective pick location racks for accurate inventory tracking and efficient picking processes.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is all the packed SKUs weighed while packing and label stickered after packing? Is the barcode is readable or scanable condition ?' as question, 'all packed SKUs should be weighed during packing, and labels should be stickered after packing. Ensure that the barcode is in readable or scannable condition to facilitate accurate inventory management and tracking.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is Cut-veg TO happening daily as per Indent received?' as question, 'Confirm whether cut-vegetable transfer orders (TO) are being processed daily in alignment with the received indent to maintain inventory levels and meet demand requirements efficiently.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Inward Management' as process, 'Is daily F&V MRP getting uploaded in Bizerba/Essaea Scales Once the MRP is determined against the S.P Upload File sent by the respective Buyers?' as question, 'ensure that the daily fruits and vegetables (F&V) maximum retail price (MRP) is uploaded into Bizerba/Essaea scales promptly after determining the MRP against the sales price (S.P) upload file provided by respective buyers for accurate pricing and compliance.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Bulk Storage Location for each SKU defined & Demarked?' as question, 'Yes, define and demarcate bulk storage locations for each SKU to facilitate organized storage and efficient retrieval of inventory items.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the FIFO followed in Bulk location and Packing location?' as question, 'ensure that FIFO (First In, First Out) method is followed both in bulk storage locations and packing locations to maintain freshness and minimize waste of perishable goods.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the First Aid Box kept available in FV Leafy Preparation Area? Refilled as and when required? And are all contents as advised in the guidelines available?' as question, 'ensure the availability of a First Aid Box in the FV Leafy Preparation Area, refilled as needed, and stocked with all recommended contents as per guidelines for immediate response to any injuries or emergencies.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Operations' as process, 'Is the GRN matching with invoice Value? Is the Invoices hard copies to Finance weekly basis through courier? And all the invoices soft copies sending to finance on daily basis Courier details available?' as question, 'Verify that GRN matches the invoice value accurately. Send hard copies of invoices to finance weekly via courier and ensure soft copies of all invoices are sent to finance daily. Maintain records of courier details for accountability and tracking purposes.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the mushroom and Sprouts received in Cold-room? Is the temp logger maintained?' as question, 'ensure mushrooms and sprouts are received in the cold room to maintain freshness. Additionally, maintain a temperature logger to monitor and record temperature levels in the cold room for quality control and compliance.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the National Sourcing & CC arrival getting GRN''D 100% on the same day of arrival ?' as question, 'Strive to ensure that both National Sourcing and CC arrival are GRN''d 100% on the same day of arrival to maintain efficient inventory management and accuracy in record-keeping.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the packaging manual followed 100% as per the manual shared by HO Quality team?' as question, 'Ensure that packaging procedures are followed 100% according to the manual provided by the HO Quality team to maintain consistency, quality, and compliance with standards.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the receiving area being clean and neat?' as question, 'Maintain cleanliness and tidiness in the receiving area to ensure hygiene, safety, and efficient operations.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Receiving Date stickered or Date written in the marker crate/cotton boxes for Exotic- Domestic / Imported SKU?s while receiving?' as question, 'ensure that the receiving date is clearly stickered or written with a marker on crates or boxes for both domestic and imported SKU''s to facilitate proper inventory management and rotation.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Receiving Date stickers followed for FV received stocks?' as question, 'ensure that receiving date stickers are consistently used for FV (fruits and vegetables) received stocks to maintain accurate inventory tracking and facilitate proper rotation of perishable items.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the staging area for All the dispatch locations clearly demarcated & well separated?' as question, 'ensure that the staging area for all dispatch locations is clearly demarcated and well-separated to prevent confusion and facilitate organized operations.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the Standard Crate Weight for FV SKUs and 1Kg PLU Barcode stickered in all Crates in CC Supplies ? If not followed by CC is that Escalated to CC In charges Stakeholders?' as question, 'ensure that the standard crate weight for FV SKUs and 1Kg PLU barcode stickers are placed on all crates in CC supplies. If not followed, escalate the issue to the CC in-charge and stakeholders for resolution and compliance.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the table wiser packing list (Hourly consolidation report for FSD models) available? Is the packing happening as per the list? (Do a Random Check)' as question, 'ensure the availability of table-wise packing lists (hourly consolidation reports for FSD models), and conduct random checks to verify if packing is being done according to the list to maintain accuracy and efficiency in packing operations.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Operations' as process, 'Is the weighing scale & Bizerba calibrated as per schedule? And certificate made available near to each Machine?' as question, 'ensure that the weighing scale and Bizerba are calibrated according to the schedule, with certificates available near each machine for verification and compliance.' as recommendation
union select 'FV Incharge - Shift Controller' as process_owner, 'Health, Safety, Environment and Hygiene' as process, 'Is the Whole of F&V Work Place Bins; Storage location; processing area maintained neat and Clean and regular cleaning carried out?' as question, 'maintain cleanliness throughout the F&V workplace including bins, storage locations, and processing areas, ensuring regular cleaning is carried out to uphold hygiene standards and a conducive working environmen' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are all the crates stacked as per the stacking norms (standard weight of SKU per crate) for Regular F&V; Exotic F&V; Organic F&V without over loading?' as question, 'ensure all crates are stacked according to stacking norms, considering the standard weight of SKU per crate, for Regular F&V, Exotic F&V, and Organic F&V, without overloading to prevent damage and ensure safe handling.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are the extra packed skus over an above the indent being removed at the end of the day?' as question, 'ensure that any extra packed SKUs beyond the indent are removed at the end of the day to maintain accurate inventory levels and prevent wastage.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'As per the Total Quality Management process(TQM)are the rotten F&V being removed at the time of packaging?(No process of QC of CC arrival material)' as question, 'implement the Total Quality Management process (TQM) to ensure that rotten F&V are removed at the time of packaging, even without a process for quality control of CC arrival material, to uphold product quality standards and customer satisfaction.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the DILO(Day in the Life of)being filled by the QC person &  share the same with DCM & B&M copy to RBH & Central QC?' as question, 'ensure that the Day in the Life of (DILO) report is filled out by the QC person and shared with the DCM and B&M, with copies sent to RBH and Central QC for effective communication and alignment of quality control processes.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the FIFO followed in bulk Storage area? - are there date stickers on the crates?' as question, 'FIFO (First In, First Out) should be followed in the bulk storage area. Ensure that date stickers are placed on the crates to facilitate proper rotation of inventory and adherence to FIFO principles.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the FV QC Passed SKUs transferred to Clean bulk crate?Is the sorting and grading table being neat and clean?' as question, 'ensure that FV QC passed SKUs are transferred to clean bulk crates for storage. Additionally, maintain cleanliness on the sorting and grading table to uphold hygiene standards and ensure the quality of products' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the National Sourcing arrival coming with DQR (Dispatch Quality Report)?/TO ? Is the AQR prepared and sent to stakeholders for all shipments?' as question, 'ensure National Sourcing arrivals come with DQR (Dispatch Quality Report) and TO (Transfer Order). Prepare and send AQR (Arrival Quality Report) to stakeholders for all shipments to maintain transparency and ensure quality standards are met.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the packaging manual followed 100% as per the manual shared by HO Quality team?' as question, 'ensure that the packaging manual is followed meticulously as per the guidelines provided by the HO Quality team to maintain consistency, quality, and compliance with standards.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC check happening for bulk stock sent to Cut Veg from FV? QC certified by the FV Incharge; and does the transfer document contain his QC passed remark?' as question, 'ensure QC checks are conducted for bulk stock sent to Cut Veg from FV, with certification provided by the FV Incharge. The transfer document should contain the QC passed remark to ensure proper documentation and accountability.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC happening 100% before receiving stocks from Vendor?' as question, 'ensure that QC checks are conducted 100% before receiving stocks from vendors to maintain quality standards and prevent the acceptance of substandard goods.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the QC person along with the shift incharge carrying out calibration for all weighing scales & Bizerba using certified dead weight (Standard weight/ stone certified by weight & Measurement Department? Is all the Reports available?' as question, 'the QC person along with the shift incharge should conduct calibration for all weighing scales and Bizerba using certified dead weight. Ensure all reports are available to document the calibration process for quality control and compliance purposes.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the sorting & grading happening for RTV Stocks on the same Day? And any reusable quantity packed on the same immediately and moved to the picking area/location?' as question, 'ensure that sorting and grading for RTV (Return to Vendor) stocks occur on the same day, with any reusable quantity packed immediately and moved to the picking area/location to expedite processing and minimize inventory holding time.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, ' Is all the discount sale stock properly segregated in to “Discount Sale Recovery Stock” and “Dump”.? Is any Dump material “Spoilt, expired, infested, contaminated, damaged, spillage, complaint return and process waste” kept mixed-up along with Discount sale products? - (Check the storage area Physically) In case of any Expired material found, recover the Material, and give the credit to discount sale lifting vendor.' as question, 'ensure all discount sale stock is properly segregated into "Discount Sale Recovery Stock" and "Dump." Avoid mixing any dump material (spoiled, expired, infested, contaminated, damaged, spillage, complaint return, and process waste) with discount sale products. Physically check the storage area to ensure compliance. In case of expired material, recover it and provide credit to the discount sale lifting vendor.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, ' Is the discount sale area maintained with proper hygiene standards (Spillage leakage, odour smell, flies, and flies)' as question, 'maintain the discount sale area with proper hygiene standards, ensuring cleanliness to prevent spillage, leakage, odour, and flies, which can affect product quality and customer experience.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the two-day inventory available in primary pick locations?, Check Sample of minimum 20 SKUs' as question, 'Ensure to refill the stocks in pick location from bulk location' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all pallets strapped using belts for the stocks stored in the Heavy duty secondary storage location?' as question, 'Tolarance :100% Process to be followed , no deviations are acceptable' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all FV RTV stock moved to QC immediately after TI?' as question, 'Once returns received from stores, move those to QC area to check the quality and do the repacking for good stocks' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Are all the good stocks moved to the racks and all the damage/expiry stocks write-off from the DC; by taking necessary approval?' as question, 'Ensure to move all the good stock to the rack once TI complete' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Are the invoices raised for all the Previous discount sale movements?' as question, 'Invoice should be raised for all the discount sale' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Are there any unopened bags, box, bulk SKU available?' as question, 'Check for any unopened bags, boxes, or bulk SKUs to ensure proper inventory management and prevent potential stock discrepancies or oversights.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Does the Discount sale proceed collected in cash, kept in safe reconciliation tallying with the nondeposited amount and is the deposit carried out every fortnightly into company’s account and information sent to finance/ accounts and is the invoice available up to the last transaction?' as question, 'ensure that the cash proceeds collected from discount sales are kept securely and reconciled with the non-deposited amount. Deposits should be made into the company''s account every fortnight, with information sent to finance/accounts. Maintain invoices for all transactions up to the last one for proper record-keeping and transparency.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is 100% QC carried out for the all the F&V write-off Stock and certified by the QC -Incharge? Is grading done categorizing product into B-Grade and D-Grade? And is the B-grade stored in crates and D-grade in covered bins with identification?' as question, 'QC should be covered for all the WO stocks without any deviation' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is all F&V B-grade stocks acknowledged in the register by the Discount sale in-charge which receiving at Discount sale area?' as question, 'ensure that all F&V B-grade stocks received at the discount sale area are acknowledged in the register by the Discount Sale In-charge for accurate record-keeping and accountability.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all Positive and negative stock updates carried out having necessary approval and adjustment carried out as per approval? Also Is any stock correction done more than 3 times for any SKU having proper justifications? Mail approval should be taken from City Head. (Mail should be approved)' as question, 'ensure all positive and negative stock updates are carried out with necessary approval, and adjustments are made accordingly. Any stock corrections done more than 3 times for any SKU should have proper justifications, and email approval should be obtained from the City Head, ensuring compliance and transparency in inventory management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is all the Sacks opened only through scissors?' as question, 'Ensure to use only scissors to open the bags' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is any Discount sale value recovery being less than 30% of actual CP then is the RBH approval taken before sales? [Check approval mail against the transaction]' as question, 'if any discount sale value recovery is less than 30% of the actual cost price, RBH approval should be sought before sales. Verify approval emails against the transaction to ensure compliance with this policy.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Negative Qty SKUs available in Book Stocks ? (Should be nullified daily basis in stock update)' as question, 'Ensure that there are no negative quantity SKUs available in book stocks by nullifying them on a daily basis during stock updates to maintain accurate inventory records and prevent discrepancies.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any Stock qty available in SKU code without rack Location?' as question, 'Ensure that there are no stock quantities available for SKU codes without rack locations to maintain accurate inventory management and prevent misplacement of items.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is any unaccounted excess stocks found in DC ?? (sys vs Physical)' as question, 'Regularly reconcile system inventory with physical inventory to identify and address any unaccounted excess stocks found in the distribution center to maintain accuracy and prevent discrepancies.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is bulk stock storing for Top SKUs allowed above the primary locations in the same rack ?' as question, 'bulk stock storing for top SKUs should not be allowed above the primary locations in the same rack to maintain organization, accessibility, and safety in the distribution center.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is details of near expiry stock communicated to the B&M & DC Manager; as per the Shelf life norms / Escalation Matrix?' as question, 'ensure that details of near expiry stock are communicated to the B&M and DC Manager according to the shelf life norms and escalation matrix to facilitate timely action and minimize waste.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is FEFO norms followed for products stacking?' as question, 'ensure that FEFO (First Expired, First Out) norms are followed for product stacking to minimize the risk of product expiration and ensure the freshness of goods.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is less shelf life / expiry / spoilt SKU write-off done on daily basis? Does the stacker maintain shelf life norms and removes SKUs as per process?' as question, 'ensure that less shelf life/expiry/spoiled SKU write-off is done on a daily basis to maintain inventory accuracy. Additionally, ensure that stackers adhere to shelf life norms and remove SKUs accordingly as per the process to minimize waste and ensure product quality.' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is MY-MCS/ Zoho call raised for any Breakdown of daily assets with proper validation and details? (HHD; android device (handheld device) & Batteries)' as question, 'ensure that MY-MCS/Zoho calls are raised for any breakdown of daily assets such as HHDs, Android devices (handheld devices), and batteries, with proper validation and details provided for prompt resolution and maintenance.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the purchase return carried out in accordance with the agreement between the merchandiser and supplier, and is this verified based on the list available with the Inventory Controller? Additionally, is the purchase return stock handed over on time, and are the details communicated to the receiving Incharge?' as question, 'purchase returns should be conducted in accordance with the agreement between the merchandiser and supplier, verified based on the list available with the Inventory Controller. Ensure that purchase return stock is handed over on time and details are communicated to the receiving Incharge for proper processing and reconciliation.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is RECO carried out for the discrepancy after cycle count and is stock updated is carried out as per the final variance?' as question, 'conduct RECO (Reconciliation) for discrepancies identified after cycle counts, and update stock accordingly based on the final variance to ensure accuracy in inventory records and resolve discrepancies promptly.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is stock stored in excess/ Overflow location has pick location assigned? Is regular bin replenishment happening from excess storage location to picking location?' as question, 'Ensure that stock stored in excess/overflow locations has pick locations assigned. Regularly replenish bins from the excess storage location to the picking location to maintain inventory accessibility and efficiency in order fulfillment processes.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Bin Audit carried out on daily basis by the inventory Controller? Does the Inventory controllersstackerRow in-charges conduct checks for Identifying non-salable stock (damage; expiry & spoil; non-returnable to vendor) from Shelf & initiate write-off from system with proper approvals?' as question, 'ensure that the Bin Audit is conducted daily by the inventory controller. Additionally, the inventory controller, stacker, and row in-charges should conduct checks to identify non-salable stock (damage, expiry, spoil, non-returnable to vendor) from the shelf and initiate write-offs from the system with proper approvals to maintain accurate inventory records.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Bins and Racks maintained Clean and Neat? Is any products found under the pallets or under the slotted angel racks?' as question, 'ensure bins and racks are maintained clean and neat, with no products found under the pallets or slotted angle racks to uphold hygiene standards and prevent potential safety hazards or damage to goods. Regular inspections should be conducted to ensure compliance.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FV Closing stock shared to B&M daily basis on EOD? Is the shared detailed record (mail) available for the last 3days?' as question, 'ensure that FV closing stock is shared with B&M on a daily basis at the end of the day. Maintain detailed records (emails) of the shared information' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Contra SKUs receiving is happening in DC? Check the wrong complaints' as question, 'verify if contra SKUs receiving is taking place in the DC and cross-check for any instances of wrong complaints to ensure accuracy in inventory management and address any discrepancies promptly.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the critical ( BBPL) cycle count is carried out as per scheduling using cycle count app? (applicable T1 & T2 DC weekly once). It should be covered both offline cycle count and Stock take report' as question, 'ensure that critical (BBPL) cycle counts are conducted as per scheduling using the cycle count app. These counts should occur weekly in both T1 and T2 DCs, covering both offline cycle counts and Stock Take reports to maintain accuracy in inventory records.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the customer rejection / DS Rejection near expiry / expiry/ spoilt SKUs write off completed daily basis? Is data available?' as question, 'ensure that the write-off of customer rejection/DS rejection near expiry/expiry/spoilt SKUs is completed on a daily basis. Maintain records of this data to track and manage inventory effectively.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the cut-veg customer returns write-off carried out at DC?' as question, 'the write-off of cut-vegetable customer returns should be carried out at the distribution center to maintain accurate inventory records and manage stock effectively.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Cycle Count carried out as per schedule and are all SKU''s covered in the month & is the cycle count included for all UD and IBND on daily basis?  It should be covered both offline cycle count and Stock take report' as question, 'ensure that cycle counts are carried out according to the schedule, covering all SKUs within the month. Cycle counts should include both UD (Unplanned Demand) and IBND (Inventory by Need Date) on a daily basis. Both offline cycle counts and stock take reports should be included to maintain accuracy in inventory management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Daily critical asset Inventory carried out for HHD, Batteries and Hand Trolly, Pallet trolly in DC as per process? and daily records available?' as question, 'ensure that daily critical asset inventory checks are conducted for HHDs, batteries, hand trolleys, and pallet trolleys in the DC as per the process. Maintain daily records of these checks to ensure accountability and proper maintenance of assets' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the E-bidding QR code displayed at the ||char(34)||Inspection Area||char(34)|| (i.e., Discount Sale Area)? Note: ||char(34)||Inspection Area||char(34)|| (i.e., Discount Sale Area) Is the recommended H1 Vendor deposited the payment to Bigbasket Bank Account?' as question, 'display the E-bidding QR code at the Inspection Area (i.e., Discount Sale Area) as recommended. Ensure that the recommended H1 vendor has deposited the payment to the Bigbasket Bank Account to complete the transaction process.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale Management F&V' as process, 'Is the F&V Discount sale price obtained from the B&M by sharing the details of products available for Discount sale for the day and before start of Discount sale for the day? ' as question, 'ensure that the F&V discount sale price is obtained from the B&M by sharing the details of products available for discount sale for the day before the start of the discount sale for the day to maintain transparency and alignment with pricing strategies.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FMCG near Expiry stocks being removed from the shelf as per the shelf life removal norms?' as question, 'ensure that FMCG near expiry stocks are removed from the shelf as per the shelf life removal norms to maintain product quality, prevent waste, and adhere to regulatory standards.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the GRN?d stock getting stacked to the respective bin the same day? Is the stacker using stacking app for Stacking? Except FV SKUs' as question, 'ensure that GRN''d stock is stacked to the respective bin on the same day of receipt. Additionally, ensure that the stacker is using a stacking app for stacking, except for FV SKUs, to maintain efficiency and accuracy in inventory management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Operations' as process, 'Is the Group locations uploaded for Auto Indenting to Mother DC?' as question, 'ensure that group locations are uploaded for auto-indenting to the Mother DC to streamline the inventory replenishment process and maintain optimal stock levels.' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the Inventory Incharge/DC Head checking all stock transfers is done through MyMCS for any Assets moving out of DC? (repair / transfer to other location)' as question, 'ensure that the Inventory Incharge/DC Head checks that all stock transfers, including assets moving out of the DC for repair or transfer to other locations, are done through MyMCS to maintain proper documentation and accountability.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the inventory team reverting for all discrepancy escalation mail received from 5K|BBNow|T2|B2B|Inter DC and LT orders with in the Same day? (Stacking pendancy report of 5KBBNT2B2B) for the auditing period?' as question, 'ensure that the inventory team reverts for all discrepancy escalation emails received from 5K, BBNow, T2, B2B, Inter DC, and LT orders within the same day for the auditing period, as per the stacking pendancy report. This ensures timely resolution and maintains accuracy in inventory management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is the location initiated the E -auction/E- Bidding locally, with interested parties/ vendor, for discount sale?' as question, 'ensure that the location initiates E-auction/E-bidding locally with interested parties/vendors for discount sales to facilitate transparent and competitive pricing, maximizing value for both the business and customers.' as recommendation
union select 'Inventory Controller' as process_owner, 'Asset Inventory' as process, 'Is the monthly fixed and movable asset(Wall to wall Inventory) carried out in DC as per process? Has the Inventory Manager reviewed the Final asset audit variance report with the respective RBH/project Manager/DCM & is the Signoff Copy sent to the central team ever month as per the process? Is the variance reconciled within 25 days?' as question, 'the monthly fixed and movable asset (wall-to-wall inventory) should be carried out in the DC as per the process. The Inventory Manager should review the final asset audit variance report with the respective RBH, Project Manager, and DCM. A signoff copy should be sent to the central team every month as per the process. Any variances should be reconciled within 25 days to ensure accuracy and compliance.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Plannogram process followed, ensuring that hazardous articles are placed in a separate aisle and no stock is kept on top of slotted angle racks?' as question, 'the plannogram process should be followed, ensuring that hazardous articles are placed in a separate aisle and no stock is kept on top of slotted angle racks to maintain safety standards and prevent accidents.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FMCG FV Pre-Bulk Storage area clean and neat? Is all aisle free for trolley movement?' as question, 'the FMCG FV Pre-Bulk Storage area should be kept clean and neat, with all aisles free for trolley movement to ensure efficient operations and safety.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the putaway team recording SKU Type, SKU and Rack Details in Pallet Tracker at the time of Receiving?' as question, 'the putaway team should record SKU Type, SKU, and Rack Details in the Pallet Tracker at the time of receiving to maintain accurate inventory records and facilitate efficient storage management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the receiving Incharge conducting check for Non RTV & RTV Vendor stocks before doing write off?' as question, 'the receiving Incharge should conduct checks for both Non-RTV and RTV (Return to Vendor) stocks before initiating any write-off processes to ensure accuracy and proper handling of inventory.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the SKU Movement types for Inter-DC order uploaded in the Admin during assortment changes taking place?' as question, 'SKU movement types for Inter-DC orders should be uploaded in the Admin during assortment changes to ensure accurate tracking and management of inventory movements between distribution cent' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Stacker wearing helmet while using stacker?' as question, 'it''s essential for the stacker operator to wear a helmet while using the stacker to ensure their safety and comply with workplace safety regulations.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the stock available in return location? Is stock moved based the Inventory Head approval?' as question, 'stock availability in the return location should be verified, and movement of stock should occur based on the approval of the Inventory Head to ensure proper management and accountability of inventory.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the as per schedule wall to wall Stock take happening for FV? Any differences found in inventory is the approval taken & written-off from the system?' as question, 'wall-to-wall stock takes should occur for FV as per schedule. Any differences found in inventory should be approved and written off from the system to ensure accurate inventory records and proper reconciliation of discrepancies.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the FV write off Posted in system immediately after QC passed with appropriate remarks?' as question, 'FV write-offs should be posted in the system immediately after QC passed with appropriate remarks to maintain accurate inventory records and ensure transparency in the process.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the write off SKUs moved to dump as per waste management process?' as question, 'the write-off SKUs should be moved to the dump as per the waste management process to ensure proper disposal and compliance with environmental regulations.' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is the Write-off Approval metrics configured every month in the system as per the approval given?' as question, 'Configure the write off approvals based on last 3 month sales' as recommendation
union select 'Inventory Controller' as process_owner, 'Inventory Management' as process, 'Is there a designated area demarked for Damage; Expired; repacking; RTV stock? Is the products stored in the designated area ?' as question, 'there should be designated areas demarcated for damaged, expired, repacking, and RTV (Return to Vendor) stock. Products should be stored in their respective designated areas to facilitate proper management and efficient handling of inventory.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Is there any difference in the Write-off report Vs actual Discount sales for the present lifted schedule?' as question, 'To ensure accuracy, it''s important to reconcile the write-off report with actual discount sales for the present lifted schedule. Any differences should be investigated and resolved promptly to maintain integrity in inventory management.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Recover the Material and give the credit to discount sale lifting vendor and move product to original location by accounting back into system?' as question, 'in case of discrepancies between the write-off report and actual discount sales, if material is recovered, credit should be given to the discount sale lifting vendor. The product should then be moved back to its original location by accounting for it back into the system to maintain accurate inventory records' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was any BBPL Stock being handed over without removing the package during the lifting? While such products are identified - deface the package before handover, Collect proofs for the same.' as question, 'BBPL stock should not be handed over without removing the package during lifting. If such products are identified, the package should be defaced before handover, and proofs should be collected for documentation and accountability purposes' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was any RTV applicable SKU and PRN/GDN Stocks being moved through discount sale? Check Why this product was moved to this Discount sale area " Reason for vendor rejection". If still fit for RTV recover the Material and give the credit to discount sale lifting vendor. For any PRN/GDN stock they should be approval mail from Vendor for disposal.' as question, 'if any RTV (Return to Vendor) applicable SKU or PRN/GDN stocks are moved through discount sale, it''s important to check the reason for vendor rejection. If the product is still fit for RTV, the material should be recovered, and credit should be given to the discount sale lifting vendor. For any PRN/GDN stock, there should be an approval email from the vendor for disposal.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was the lifting carried out under the CCTV surveillance? - Check the facility in the CCTV room?' as question, 'lifting should ideally be carried out under CCTV surveillance. Verify the functionality and coverage of the facility''s CCTV system to ensure proper monitoring and security measures are in place.' as recommendation
union select 'Inventory Controller' as process_owner, 'Discount Sale management FMCG' as process, 'Was there any other major state of volition other than the above stated checkpoints?' as question, '' as recommendation
union select 'Inventory Controller' as process_owner, 'T4 Operations' as process, 'Is the cash deposit happening on as per schedule, DC Is having acknowledgment and submitting to finance.' as question, 'cash deposits should occur according to the schedule, and the DC should have acknowledgment of these deposits, submitting relevant documentation to the finance department for record-keeping and reconciliation purposes' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'is the crate QC done for all the T4 dispatches from the DC' as question, 'QC) should be conducted for all T4 dispatches from the DC to ensure that the crates meet the required standards for transportation and storage of goods' as recommendation
union select 'Asst Manager - Shift Controller' as process_owner, 'T4 Operations' as process, 'Is the return stock unloaded? As soon as vehicles reach DC.' as question, 'return stock should be unloaded as soon as vehicles reach the DC to facilitate prompt processing, inspection, and proper management of the returned goods.' as recommendation
union select 'HUB Manager' as process_owner, 'T4 Operations' as process, 'Is the route charger handed over cash to OC and acknowledgment taken.' as question, '' as recommendation
union select 'HUB Manager' as process_owner, 'T4 Operations' as process, 'Is the RTV excess, damage, return pickup stocks handed over to OC by route in charger item wise' as question, '' as recommendation
union select 'Inventory Controller' as process_owner, 'T4 Operations' as process, 'is the virtual server is getting cleared (TO,TI) every day?' as question, 'it''s important to ensure that the virtual server is cleared daily to maintain optimal performance and efficiency. This includes clearing transactions (TO - Transfer Out, TI - Transfer In) to prevent data buildup and ensure accurate recording of current inventory movements.' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the SK sending mail to HM/SM, with details of CEEs with IBND for the day ?  Count of Uniform T-Shirts / Jackets' as question, 'Store team has to ensure that the registered is mainted to keep the records of the asset in hand and the asset that is distributed to the CEE''s. Stock Keeper has to ensure that every day the details of the IBND are shared with the HM/SM with all the relevant details.' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Any stock is lying in RTV area?' as question, 'HM/SM is responsible to ensure that the products parked in the RTV area are cleared on the same day. If the stocks are still parked under the RTV area for more than one day then the HM/SM have to drop an email communication to the SK to clear the RTV.' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are Bikes & Vans parked in an orderly manner?' as question, 'HM/SM have to ensure that all the vehicles should be parked under the designated parking area. ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are empty crates & Saddle bags kept in specified area ?' as question, 'Shift or Store Incharge are reponsible to take care of the assets handed over to the store. After every delivery when CEE returns to the store the saddle bags should be handed over back to the Security and securtity has to ensure that the saddle bags are kept in the designated place to ensure that there is no damage to the saddle bags. ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'EP CEE''s shift wise roster signup sheet is updated or not' as question, 'HM should Ensure that OCs are preparing the CEE roster Weekly/TDP/Monthly for active cee according to Order Capacity ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the CEE script available on notice board(With regional / English Language)' as question, 'OC should Ensure CEE Script should be Displayed on Notice board Shared By LMD Process Team' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the dispatch area neat and organized' as question, 'OC/HM Should Disscuss the Discipline and Cleaniness by CEE also Instruc HK is being Utilized ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Top performing CEE names on notice board every weekly/TDP (Month / TDP Details should be mentioned)' as question, 'OC/HM Should Ensure Weekly/TDP/Monthly Top Performing name are being displayed on Notice board details mentioned like Count of Order /IBND/Complaint/Present days Count etc ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are all D-1 complaints closed(CMS Start date 1st date of current month and end date should be D-1)' as question, 'OC Should Ensure all the Kapture complaint are closed by EOD or Tomorrow Morning First Half /HM Should Ensure OC are timley closing complaints and With Geniun comment/Action plan' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are all OCs in uniform (Big Basket Logo should be visible)' as question, 'HM Should Ensure OC should Have Sufficent Uniform and should wear Daily / Indent for Yellow Shirt should Be Accordingly ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are all the CEE''s mapped to the correct category? (EV / NEV/LSV/ BB / Vendor)' as question, 'OC should Ensure at time Onboarding CEE Details are correctly entered according to category /HM should have a weekly Check ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are the saddle bags in good condition?' as question, 'HM/OC Should ensure cee are handling the proper no over filling /Ensure bags are being washed weekly or Ten Day to maintain hyigien' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Does the asset match as per the book stock , check few assets randomly' as question, 'HM Should do monthly internal asset audit ensure assets are not damage /Lost/Theft /shortage in such scenario HM Should Look for Recovery /Highlight to Project looping HM & RBH and Follow the Instruction suggested buy Project ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Does the store have any cash variance for more than 48 HRS? Check the latest variance email sent by the finance team' as question, 'OC Sould ensure that there sould not be Collection Variance Its Should be resolved at customer door step with the Help of CS If still it reflect in variance then HM should ensure its clear within 48hr ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'G1 Management Roster(only Hub) on the notice board' as question, 'Shift Incharge or Store Manager has to ensure that every month on or before 1st of the Month the roster for the G1 staff is prepared and signed off from the Store Manager' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Has MCIP indents been sent on time, (check mail for confirmation)' as question, 'HM Sould Ensure MCIP are being raised timley for Uniform /Stationary/HK material to avoid operational impact ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'IBND details for the last TDP? with TOP 5 CEE names contributing to the IBND' as question, 'OC Should ensure TDP /Weekly IBND data should displayed also arrange refresher traning for CEE' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is all CEE/s are well groomed?' as question, 'OC should Discuss Gromming standards in huddle share the importance of Gromming and HM should ensure that its Being followed Strictly ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is petty cash statement sent to accounts daily -check the latest shared email' as question, 'Store Manager / Shift Incharge has to ensure that they are sharing the petty cash statement with the finance team with the latest expenses updated. They are also repnsible to ensure that a copy of all the bills or invoices for the expenses incurred to be sent to the Finance team, and a copy has to be maintained at the store. (Minimum of last 6 months records should be available at the store // If it''s a new store the records should be available from the time the store has been launched to the date of audit)' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the City Head "HUB visit" checklist maintained at HUB- G sheet' as question, 'https://drive.google.com/drive/folders/1w5RrUAahBTL8Ur9nbsJ_H_W7ahAebxwB?ths=true' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the OC / HM logged in using his login (should not be logged in using others login)' as question, 'HM Should Ensure OC Admin loggin ID are created   OC using Self Logging only ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the TE conducting regular transport audit & updating the data on notice board?' as question, 'TE /HM Should ensure transport audit are being conduct TDP to avoid operational impact ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is the team reconciling monthly asset count' as question, '' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Safety kits been procured for female riders and issued (Check entry in Register)' as question, 'Step 1: OC / HM/ SI are reponsible to issue the saftey kit to the female riders at the time of Joining. Step : Should record the issuance of the kit to the female riders in the register and same should be mantained at the store. Step: OC / HM / SM should ensure that female riders are carrying the saftey kit while they report to the work' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Where the incidents of previous VCC & Transport audit cleared over email within 10 days(Previous audits response email or action plan)' as question, 'HM Should ensure post audit score being shared HM should work on lost point and reply to Audit mail with action plan within 10 days of mailed Shared ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Does the CEE have Valid Driving license' as question, 'TE /Bike OC should Check and onboard with Proper and Valid Dcouments' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Does the CEE have valid Vehicle Insurance' as question, '' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Does the CEE have valid Vehicle Registration Certificate' as question, '' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Has safety kit been provided(for Female riders)' as question, 'Same As point 344' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Is the CEE wearing Helmet ?' as question, 'OC should have Daily check on Road Safety norm and Should Discuss Same with CEE in Huddle ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Is the CEE wearing Uniform?' as question, '' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-Is the saddle bag assembly lock available ?' as question, 'OC Should Ensure all Bike CEE are having Assembly lock and the importance of carrying it on delivery ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Bike-SOS app. Installed in rider mobile (applicable for female CEEs only)' as question, 'Store HR should SOS app is being installed while onboarding ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Has safety kit been provided(for Female riders). Pepper Spray - Female Rider only' as question, 'Point 344' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van- Valid RC / Fitness certificate and OEM (in EV vehicle) is available?' as question, 'TE /VAN OC should Check and onboard with Proper and Valid Dcouments' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does the Driver have Valid Driving license ' as question, 'TE /VAN OC should Check and onboard with Proper and Valid Dcouments' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does the Van have provision for Mobile charging with Cable?' as question, 'TE /VAN OC should Check and onboard with Proper and Valid Dcouments/Mobile charging & Cable available ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does the vehicle have Pollution Under Control Certificate' as question, 'TE /VAN OC should Check and onboard with Proper and Valid Dcouments' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does the Vehicle having valid Vehicle Insurance' as question, 'TE /VAN OC should Check and onboard with Proper and Valid Dcouments' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does VAN has a proper Back Door with a functional lock?' as question, 'OC Should Ensure every delivery van should have Lock is being used on Back door ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does VAN have proper Back Cabin Light' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does VAN have proper Back Lights (Break Lights)' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does VAN have proper Head Lights' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Does VAN have proper Number plate on all 4 sides' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Is first aid box is available with required medicine ' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Is first Fire extinguishers available? ' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Is the delivery trolley available?' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Is the driver wearing the seat belt ( Applicable for 4W only)' as question, 'TE /OC Should ensure van should back cabin Light /Van Condition light ,Horn, all safety check while on boarding or Audit ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Van-Is vehicle no. available in master vehicle tracker ' as question, 'https://docs.google.com/spreadsheets/d/1OWHvYMnOalUU31s0YLMksBYKkVYRETeHMYsB_gSHKzI/edit#gid=1628086798' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Are all SKUs from both Pre Cancellation and Post Cancellation orders verified to be returned to the DC?' as question, 'HM/OC should ensure all RTV/Cancelled order are getting cleared by EOD need to Verify Admin Stock Report ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Has the Return to Vendor (RTV) process been completed for all SKUs returned by the CEEs?' as question, 'HM/OC should ensure all RTV/Cancelled order are getting cleared by EOD need to Verify Admin Stock Report ' as recommendation
union select 'HUB Manager' as process_owner, 'LMD Operations' as process, 'Is there consistency between the type of vehicle used by the CEEs (EV or Non-EV) and their corresponding payout claims (EV or Non-EV)?' as question, '' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Are personal care products (condoms) packed with brown cover at the time of receiving?' as question, 'Typically, condoms are packaged discreetly to ensure privacy and confidentiality for customers. ' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Are the Bundle Pack SKU; wrapped at the time of receiving and at the time of receiving are the bundle pack details captured in the device?' as question, 'bundle pack SKUs should be wrapped at the time of receiving to maintain their integrity and ensure accurate inventory management. Additionally, details of bundle pack SKUs should be captured in the device or inventory management system to facilitate tracking and management of these products throughout the supply chain.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Cold Chain Operations' as process, 'Are the Chiller and Frozen SKUs receiving happens in cold room (Anti Room) checking Temperature as per (Permissible limit)?' as question, 'the receiving of chiller and frozen SKUs should ideally occur in a cold room or anteroom where the temperature is maintained within permissible limits to prevent spoilage and maintain product quality. Temperature checks should be conducted regularly to ensure compliance with storage requirements' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'At the time of receiving are the details of product , expire date for all products other being captured in the receiving Device?' as question, 'at the time of receiving, details such as product name, batch number, expiry date, and other relevant information for all products should ideally be captured in the receiving device or inventory management system. This ensures accurate recording of inventory data and facilitates proper stock management and traceability.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'If the GDN value is greater than 50K, is vendor mail apporval taken for the GDN before proceeding the GRN' as question, 'if the GDN (Goods Delivery Note) value exceeds 50K, it''s advisable to seek vendor approval via email before proceeding with the GRN (Goods Receipt Note). This ensures proper authorization for high-value transactions and mitigates the risk of discrepancies or disputes.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is all Asset handover carried out with proper signoff between DC & Projects after every transaction and is the signoff records available & maintained in DC?' as question, 'all asset handovers between the DC and projects should be accompanied by proper signoff documentation after every transaction. These signoff records should be available and maintained in the DC for reference and audit purposes, ensuring accountability and transparency in asset management.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is all Lakme SKUs bubble wrapped while receiving or before moving the stock to stacking location?' as question, 'all Lakme SKUs should ideally be bubble wrapped either while receiving or before moving the stock to the stacking location to ensure their protection from damage and maintain product quality.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is all the type-1 SKUs is moved to the respective Rack locations  after completion of the receiving. (Wherever type wise indent receiving, or else NA)' as question, 'll type-1 SKUs should be moved to their respective rack locations after completion of receiving, provided there is a type-wise indent receiving process in place. If there is no type-wise indent receiving, this would not be applicable (NA).' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is All type 2 and Type-3 has moved to receiving stageing area afer receiving completion (Wherever type wise indent receiving, or else NA)' as question, ', all type-2 and type-3 SKUs should be moved to the receiving staging area after receiving completion, provided there is a type-wise indent receiving process in place. If there is no type-wise indent receiving, this would not be applicable (NA).' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is Daily MRP Complaints analysis and communication for rectification communicated to buyer' as question, 'daily MRP complaints analysis and communication for rectification should be communicated to the buyer to address any issues promptly and ensure customer satisfaction.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Asset Management' as process, 'Is Manual Asset inward register/ Know App maintained at DC and is the Receiving Incharge ensuring the availability and are all movements recorded and register/ Know App validated weekly by Project/ receiving In-charge; DS / DC Manager/ Inventory Manager & Checked signature Available.' as question, 'a manual asset inward register or a digital app should be maintained at the DC. The Receiving Incharge should ensure its availability and record all movements. The register or app should be validated weekly by relevant personnel such as the Project/Receiving Incharge, DS/DC Manager, and Inventory Manager, with checked signatures available as proof of validation.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is pass in slip Rejected by Receiving Incharge only or by the DC Managers Login Ids and is a valid reason recorded during rejection?' as question, 'Pass-in slips should ideally be rejected by the Receiving Incharge and verified by the DC Manager''s login IDs. Additionally, a valid reason for rejection should be recorded during the process to provide clarity and accountability for the decision.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the agreed vendor shcedule is updated in the system?' as question, 'the agreed vendor schedule should be updated in the system to ensure accurate planning and scheduling of deliveries from vendors. This helps in managing inventory levels and meeting customer demand effectively.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the approval mail obtained from DCM for allowing receiving unscheduled vendors? Or is the detail of unscheduled vendors receiving for the day sent to B&M?' as question, 'approval should ideally be obtained from the DCM (Distribution Center Manager) for allowing receiving unscheduled vendors. Alternatively, the details of unscheduled vendors receiving for the day should be communicated to the B&M (Buying and Merchandising) team for proper coordination and management of inventory.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Auto triggered mail configured for all vendor for all transactions GRN; GDN; PRN? Is the alert Mail sent? If not the Receiving Incharge has to send mails manually to respective Vendor & BandM? Is all GDN raised only through System E-Retail?' as question, 'auto-triggered emails should ideally be configured for all vendor transactions including GRN (Goods Receipt Note), GDN (Goods Delivery Note), and PRN (Purchase Return Note). If such alerts are not configured, the Receiving Incharge may need to send emails manually to the respective vendors and B&M (Buying and Merchandising) team. Additionally, all GDNs should be raised only through the system, preferably the E-Retail system, to ensure accuracy and consistency in transaction records.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Express receiving designated and signage board is installed and used for express receiving in DC? As is the Location providing basis facilities to the vendor? And receiving key points signage boards are available ( Security, receivver, GRN and GDN) signage boards to be displayed' as question, 'in an efficient distribution center (DC), there should be an express receiving designated area with signage boards installed and utilized for quick processing of incoming shipments. It''s also important to provide basic facilities to vendors in this area. Additionally, signage boards highlighting key receiving points such as security, receiver, GRN (Goods Receipt Note), and GDN (Goods Delivery Note) should be displayed prominently for ease of navigation and efficient operations.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the GRNd Invoice sent to Finance daily basis thru courier and scan copies updated in the google drive? Is the tracker maintained and made available during audit?' as question, 'GRNd invoices are sent to Finance daily via courier, with scanned copies updated in Google Drive. The tracker is maintained and accessible during audits for transparency.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Cold Chain Operations' as process, 'Is the Imported fruits and exotic vegetables moved to cold room immediately after receiving for stacking? And is the receiving happening in anti-room?' as question, 'imported fruits and exotic vegetables are moved to the cold room immediately after receiving for stacking. Receiving typically occurs in the anti-room for proper temperature control and handling.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the PRN gate pass in save mode till stock handover to vendor? No pile up in DC allowed' as question, 'the PRN gate pass remains in a saved mode until stock handover to the vendor, with no pile-up allowed in the distribution center (DC).' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is the PRN vs TI variance escalated to 5K , BB Now, T4, Fresho, T2 and BBD Head City Head and reconciled?' as question, 'PRN vs TI variance exceeding 5K is escalated to relevant stakeholders including BB Now, T4, Fresho, T2, and BBD Head City Head for reconciliation.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiver mentioning the GRN & GDN ref number on the Invoice copy both on Vendor & buyer copy? (GDN if applicable once GRN Done on the Buyer Copy; in supplier Copy only GDN Number with acknowledgement)' as question, 'the receiver mentions the GRN & GDN reference numbers on both the vendor and buyer copies of the invoice. The GDN number is added on the supplier copy only, along with acknowledgment, once GRN is done on the buyer copy.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the Receiving happening as per category shelf life Norms? For any product received below shelf life norms is the receiving approved by RBH/B&M Head?' as question, 'receiving occurs according to category shelf life norms. Approval from RBH/B&M Head is required for any product received below these norms.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the same day FV GRN''d for vendor and CC arrivals? Including National sourcing' as question, 'the same-day FV (Fresh Vegetables) is GRN''d for both vendor and CC (Centralized Collection) arrivals, including national sourcing.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Is the security Checking & verifying the Vehicle before moving out against any return after receiving? Vendor vehicle must move immediately once unloading happens; vendor must place the unloaded material on pallet?' as question, 'security checks and verifies the vehicle before departure to prevent returns after receiving. Vendor vehicles must move promptly after unloading, and materials should be placed on pallets as per protocol.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is ther inward seal process is following , and all the details captured properly , are all the details ledgible including  ( seal and recordded data)' as question, 'the inward seal process is followed, ensuring all details are captured accurately and legibly, including the seal and recorded data.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'is there any wrong GRN transections are identified and if they created any PRN and necessory approval (Central SCM Receiving SPOC) carried out as per the process For Any wrong Transactions related to Receiving ?' as question, 'wrong GRN transactions are identified and corrected through PRN creation, with necessary approval from the Central SCM Receiving SPOC, following the established process for any receiving-related errors.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Once vendor reported , is the pass in slip generated on time and receiving process is completed as per the process if any rejection or in process , is the receiving incharge communicated to all central and regional team ( B&M and SCM)' as question, 'the pass-in slip is generated promptly upon vendor report, and the receiving process is completed as per protocol. Receiving in-charge communicates any rejections or ongoing processes to all central and regional teams (B&M and SCM).' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Once GDN and PRN Stocks are handed overed to vendor that needs to take the photogrophy of the 1.stocks handover photos, 2.vehicle with Stocks and same email needs to send to vendor and buyer' as question, 'After handing over GDN and PRN stocks to the vendor, photographs of the stock handover and vehicle with stocks need to be taken. These photos are then sent via email to both the vendor and buyer for documentation.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'Is All Eretail PRNs taking Single Click TI? (No manual TI is allowed)' as question, 'll Eretail PRNs are processed with single-click TI, and manual TI is not permitted.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Return Management' as process, 'For all BBNOW PRNs taking TI through bulk Excel upload?( No Manual TI Is allowed)' as question, 'for all BBNOW PRNs, TI is conducted through bulk Excel upload, and manual TI is not permitted.' as recommendation
union select 'Receiving Incharge' as process_owner, 'Inward Management' as process, 'Every 3 months once vendor''s updated mail IDs needs to take from B&M team. Is that followed? Mail acknowledgement available' as question, 'updated vendor mail IDs are obtained from the B&M team every three months, and mail acknowledgment is available to ensure compliance.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Are stocks received as per QC process/ Product Specification as per QC Manual?' as question, 'stocks are received in accordance with the QC process and product specifications outlined in the QC manual.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the Packing removed after picking in the night? (after S1; S2 Picking Completed - before Day end?)' as question, 'packing is removed after picking at night, specifically after S1 and S2 picking is completed, before the end of the day.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the Random sampling QC happening for stocks received from Inter DC / CC at the time of receiving? Is the register Maintained and sampling QC for 10% of the stock received being carried out? (If TQM implements mark as NA)' as question, 'random sampling QC occurs for stocks received from Inter DC/CC at the time of receiving, with a register maintained, and sampling QC conducted for 10% of the received stock. If TQM is implemented, it''s marked as NA.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is QC person carrying out tare weight for moisture loss and packing cover weight before starting packing in each packing table? Is all the Reports available?' as question, 'the QC person conducts tare weight for moisture loss and packing cover weight before starting packing at each packing table, with all reports available for reference.' as recommendation
union select 'FV QC Incharge' as process_owner, 'FV QC' as process, 'Is the In-house QC happening in DC at the time of packing? Are the poor-quality stocks getting removed and accounted for write off ? Are Register and Write off reports matching?' as question, 'in-house QC occurs during packing in the DC, ensuring removal of poor-quality stocks accounted for write-off. Registers and write-off reports are matched for accuracy.' as recommendation
),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%'
   and store_id = @{{:BB T2 B2C Audit - Single Audit.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB T2 B2C Audit - Single Audit.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB T2 B2C Audit - Single Audit_T2 B2C Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T2 B2C Audit - Single Audit
-- Dashboard: T2 B2C Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:56
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'Final_Audit_check_list_T2_DC%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T4 Audit - All Past Audits New_T4 Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T4 Audit - All Past Audits New
-- Dashboard: T4 Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:54
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'T4 Audit%'
  and store_id = @{{:BB T4 Audit - Single Audit New.Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" <= @{{:BB T4 Audit - Single Audit New.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BB T4 Audit - Recommendations_T4 Process Audit Report.sql

**Tables referenced:** Fino, RBH, audit_submitted_at, base, checkpoint_master_sheet_table, crates, current_timestamp, reco_database

**Original Query:**

```sql
-- Data Source: BB T4 Audit - Recommendations
-- Dashboard: T4 Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:52
-- ============================================================

WITH reco_database as (select 'Store Partner' as process_owner, 'Customer' as process, 'Is the Store partner (delivery partner appointed, Delivery representative) well-groomed and wearing BB T-shirt?' as question, 'the store partner (delivery representative) is required to be well-groomed and wear a BB T-shirt as part of the company''s dress code policy.' as recommendation
union select 'Store Partner' as process_owner, 'Customer' as process, 'Are the Delivery Bags checked for cleanliness before customer delivery?' as question, 'delivery bags are checked for cleanliness before customer delivery to maintain hygiene standards and ensure customer satisfaction.' as recommendation
union select 'Store Partner' as process_owner, 'Customer' as process, 'Is Hard to soft process article placement maintained, while transferring the stock from crates to Bags?' as question, 'the hard-to-soft article placement process is maintained while transferring stock from crates to bags to ensure proper handling and protection of goods during delivery.' as recommendation
union select 'Store Partner' as process_owner, 'Health and Safety Environment' as process, 'Is the Housekeeping activity carried out effectively and is the Store cleanliness and hygiene being maintained?' as question, 'housekeeping activities are carried out effectively to maintain store cleanliness and hygiene standards.' as recommendation
union select 'Store Partner' as process_owner, 'Health and Safety Environment' as process, 'Is Fire extinguisher available at store in the right place in its designated location with signage and is the pressure gauge or indicator in the operable range?' as question, 'the fire extinguisher is available at the store in its designated location with proper signage, and the pressure gauge or indicator is checked to ensure it''s within the operable range.' as recommendation
union select 'Store Partner' as process_owner, 'Health and Safety Environment' as process, 'Is First Aid Kit available, are the contents available as per list and is the First Aid Box in an accessible area?' as question, 'the First Aid Kit is available, its contents are checked to ensure they match the list, and the First Aid Box is placed in an accessible area.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is Cash Deposited in the Bank or UPI Payment done on time? or hand overed to Driver, details entered in TMS ""Processed"" asset type option by the store partner? Or Is the Fino cash deposit is carried for 26 days ? Is acknodloedmgnet message is received by Fino?' as question, 'cash is deposited in the bank or UPI payment is done on time. The handover to the driver and entry in TMS as ""Processed"" are completed by the store partner. Fino cash deposit is carried out within 26 days, and acknowledgment messages are received from Fino.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is the appointed store partner associated with any of the Co-business like sales of Liquor, Pesticide, meat ? And is the information on any new business started after association with bb Partnership being communicated to BB Stakeholders?' as question, 'the appointed store partner''s association with any co-business like sales of liquor, pesticide, or meat is communicated to BB stakeholders, ensuring transparency regarding any new business ventures initiated after partnering with BB.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Are any unwanted (expired/Old) pamphlets / Leaflets available in the store? Note: all out dated pamphlets / Leaflets must be sent back to the DC.' as question, 'any unwanted (expired/old) pamphlets or leaflets found in the store must be sent back to the DC for disposal.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is all the returns  crates & Empty Crates  loaded with  details of dispatched entered in the TMS  GP? (check Crate reconsolidation report should match)' as question, 'all returns including crates and empty crates loaded with details of dispatched items are entered into the TMS GP, ensuring accuracy and reconciliation with the Crate reconsolidation report.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is cash tallied and entered in the register / TMS ? Cash deposit vs CMS report matching ?' as question, 'cash is tallied and recorded in the register/TMS, ensuring accuracy. Cash deposit is reconciled with CMS reports to ensure matching records.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is the previous day  Cash collection communication sent to AM/BDM for closing RCC?' as question, 'communication regarding the previous day''s cash collection is sent to AM/BDM for closing RCC.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is the saddle bag delivery process followed?' as question, 'the saddle bag delivery process is followed as per protocol.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is the CEE being available at store and training is completed? (Check the CEE available status and process awareness) ' as question, 'the CEE''s availability at the store and completion of training are checked, ensuring awareness of processes.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is the rain protective gear provided and available with the store partner?' as question, 'rain protective gear is provided and available with the store partner for use as needed.' as recommendation
union select 'Store Partner' as process_owner, 'Project' as process, 'Is the store Safety Signage Boards available as per the standard List? ' as question, 'the store safety signage boards are available according to the standard list.' as recommendation
union select 'Store Partner' as process_owner, 'Project' as process, 'Is Pest control activity in practiced at the store ? ' as question, 'pest control activity is practiced at the store to maintain hygiene and cleanliness standards.' as recommendation
union select 'Store Partner' as process_owner, 'Project' as process, 'Is the Main Company Name Board displayed as per BB requirement? Check for (Logo & colour etc. & in proper visible condition)? Record a photo of the Main BB Signboard.' as question, 'the main company name board is displayed according to BB requirements, including the logo, colors, and proper visibility. A photo of the main BB signboard is recorded for verification.' as recommendation
union select 'Store Partner' as process_owner, 'Project' as process, 'Are all licenses displayed on the Notice Board and are they having Validity as on the day of Audit? FSSAI & Trade license? [ Note : FSSAI license has to be checked for Clause applicability, with Frame should be displayed]' as question, 'all licenses including FSSAI and trade licenses are displayed on the notice board with validity as of the audit day. FSSAI license is also checked for clause applicability, with the frame properly displayed.' as recommendation
union select 'Store Partner' as process_owner, 'Operations' as process, 'Is Delivery Marking happening real time?' as question, 'delivery marking occurs in real-time to ensure accurate tracking and management of deliveries' as recommendation
union select 'Store Partner' as process_owner, 'Project' as process, 'Is Escalation Matrix displayed in store? (Name, email ID, Contact No) Level 1 - BDM Level 2 - Area Manager Level 3 - RBH Level 4 - t4.escalation@bigbasket.com' as question, 'the escalation matrix is displayed in the store, including contact details for Level 1 (BDM), Level 2 (Area Manager), Level 3 (RBH), and Level 4 (t4.escalation@bigbasket.com).' as recommendation
union select 'T4 Management' as process_owner, 'Accounts and Payments' as process, 'Is the store partner payment getting credited as per standard timeline? Or Is the store partner sharing the PDF sign copy to the BDMs' as question, 'the store partner''s payment is credited as per the standard timeline. Alternatively, the store partner shares the PDF sign copy with the BDMs for documentation and verification.' as recommendation
union select 'T4 Management' as process_owner, 'BB Training' as process, 'Is Monthly Process Training Imparted to store partner and CEEs? Customer Exp 1. CEE Behaviour during Customer Delivery 2. Delivery 3. Marketing 4. TMS 5. Delivery App' as question, 'monthly process training is imparted to store partners and CEEs covering customer experience, including CEE behavior during customer delivery, delivery protocols, marketing strategies, TMS usage, and delivery app functionalities.' as recommendation
union select 'T4 Management' as process_owner, 'HUB Operations' as process, 'Are the store partners getting an update on complaints and are they aware and timely addressing the Concerns raised?' as question, 'store partners receive updates on complaints and are aware of and timely address the concerns raised to ensure customer satisfaction and resolution.' as recommendation
union select 'T4 Management' as process_owner, 'Project' as process, 'Is all Necessary standard Assets available and in working condition? Check Working status of Water Dispenser, Saddle bags, Table and Extra. Record Qty Available for each Asset along with Photos.' as question, 'all necessary standard assets are available and in working condition. The working status of water dispensers, saddle bags, tables, and any extras are checked, with the quantity available for each asset recorded along with photos for verification.' as recommendation
union select 'T4 Management' as process_owner, 'Operations' as process, 'Is Slot Changes/Cancellation communication sent by AM/BDM and approval taken from RBH?' as question, 'slot changes/cancellation communication is sent by AM/BDM, and approval is obtained from RBH as per protocol.' as recommendation
union select 'T4 Management' as process_owner, 'Customer' as process, 'Is mail sent to CS Team for Orders which will be delayed for Delivery to communicate to Customers?' as question, 'mails are sent to the CS team for orders which will be delayed for delivery, enabling communication with customers about the delay' as recommendation
union select 'T4 Management' as process_owner, 'Operations' as process, ' Documents to be displayed in store (FSSAI, Trade License & Are they Escalation Matrix to be displayed in the store ?' as question, 'documents such as FSSAI and trade licenses should be displayed in the store, and an escalation matrix should also be prominently displayed, typically including contact information for various levels of escalation.' as recommendation
union select 'T4 Management' as process_owner, 'Operations' as process, 'Are they maitaned documents Monthly sp performance. Sign off Copies properly in the drive?' as question, 'documents such as monthly SP performance reports and signed-off copies are maintained properly in the drive for reference and accountability.' as recommendation
union select 'T4 Management' as process_owner, 'Customer' as process, 'is the AM/BDM raising the Kapture ticket for slot change/Cancellation by 8:30 pm ?' as question, 'the AM/BDM raises the Kapture ticket for slot change/cancellation by 8:30 pm as per the standard procedure.' as recommendation
union select 'T4 Management' as process_owner, 'Operations' as process, 'Is the Area Manager maitained CEE data up to date in the tracker and training completed accordingly ?' as question, 'the Area Manager ensures that CEE data is kept up-to-date in the tracker and conducts training accordingly.' as recommendation
),
base as (
SELECT cms.store_id as "Location", cms.audit_main_theme AS "Audit Name",
          cms.audit_submission_number AS "Audit Report Number",left(cms.theme, position(':' IN theme)-1) AS "Process Owner",
          right(cms.theme, length(theme)-position(':' IN theme)-1) AS "Area",
          cms.checkpoint as "Checkpoint", 
  cms.auditor_observations as "Auditor Observations",
          reco.recommendation as "Recommendation",
		  extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          left(cms.theme, position(':' IN theme)-1),
                                                                          right(cms.theme, length(theme)-position(':' IN theme)-1),
															 checkpoint,
                                                                          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata')::int 
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM checkpoint_master_sheet_table cms
   left join reco_database reco on left(cms.theme, position(':' IN theme)-1) = reco.process_owner
and right(theme, length(cms.theme)-position(':' IN theme)-1) = reco.process
and cms.checkpoint = reco.question
   WHERE audit_main_theme ILIKE 'T4 Audit%'
   and store_id = @{{:BB T4 Audit - Single Audit New.Location}}
		and result_score is not null and result_score < max_score)
   select * from base
   GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10
		 HAVING "Audit No in Year" = @{{:BB T4 Audit - Single Audit New.Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
```

---

## BB T4 Audit - Single Audit New_T4 Process Audit Report.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, current_timestamp, with_audit_numbers, with_scores

**Original Query:**

```sql
-- Data Source: BB T4 Audit - Single Audit New
-- Dashboard: T4 Process Audit Report
-- Category: Big Basket
-- Extracted: 2026-01-29 16:58:53
-- ============================================================

WITH base AS
  (SELECT left(theme, position(':' IN theme)-1) AS process_owner,
          right(theme, length(theme)-position(':' IN theme)-1) AS area,
          *
   FROM checkpoint_master_sheet_table
   WHERE audit_main_theme ILIKE 'T4 Audit%'
  and store_id = @{{:Location}}),
     with_scores AS
  (SELECT audit_main_theme,
          audit_submission_knid,
          audit_submission_number,
          auditor_name,
          audit_submitted_at,
          extract('Year'
                  FROM audit_submitted_at AT TIME ZONE 'Asia/Kolkata') AS audit_year,
          store_id,
          process_owner,
          area,
          count(CASE
                    WHEN criticality = 'Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS critical_count,
          count(CASE
                    WHEN criticality = 'Non Critical'
                         AND result_score != '' THEN checkpoint_knid
                    ELSE NULL
                END) AS non_critical_count,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS critical_max_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS non_critical_actual_score,
          sum(CASE
                  WHEN criticality = 'Non Critical'
                       AND result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS non_critical_max_score,
   sum(CASE
                  WHEN result_score != '' THEN result_score::numeric
                  ELSE 0
              END) AS total_actual_score,
   sum(CASE
                  WHEN result_score != '' THEN max_score::numeric
                  ELSE 0
              END) AS total_max_score
   FROM base
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     with_audit_numbers AS
  (SELECT audit_main_theme AS "Audit Name",
          audit_submission_number AS "Audit Report Number",
          auditor_name AS "Auditor",
          audit_submitted_at AT TIME ZONE 'Asia/Kolkata' AS "Audit Submitted At",
                                          store_id AS "Location",
                                          process_owner AS "Process Owner",
                                          area AS "Area",
                                          critical_count AS "Critical Count",
                                          non_critical_count AS "Non Critical Count",
                                          case when critical_count = 0 then 0 else critical_actual_score end AS "Critical Actual Score",
                                          case when critical_count = 0 then 0 else critical_max_score end AS "Critical Max Score",
                                          case when non_critical_actual_score is null then 0 else non_critical_actual_score end AS "Non-critical Actual Score",
                                          case when non_critical_max_score is null then 0 else non_critical_max_score end AS "Non-critical Max Score",
                                          case when total_actual_score is null then 0 else total_actual_score end as "Total Actual Score",
                                          case when total_max_score is null then 0 else total_max_score end as "Total Max Score",
                                          audit_submission_knid AS "Audit Report KNID",
                                          audit_year::int AS "Audit Year",
                                          row_number() OVER (PARTITION BY store_id,
                                                                          audit_main_theme,
                                                                          process_owner,
                                                                          Area,
                                                                          audit_year
                                                             ORDER BY audit_submitted_at) AS "Audit No in Year"
   FROM with_scores)
SELECT * FROM with_audit_numbers
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10
		 ,11,12,13,14,15,16,17,18
HAVING "Audit No in Year" = @{{:Audit No in Year}}
and "Audit Year" = extract('Year' from current_timestamp at time zone 'Asia/Kolkata')::int
ORDER BY 1,
         2,
         3,
         4,
         5, 6, 7
```

---

## BigBasket Checkpoint Master_Audit Details.sql

**Original Query:**

```sql
-- Data Source: BigBasket Checkpoint Master
-- Dashboard: Audit Details
-- Category: Big Basket
-- Extracted: 2026-01-29 16:59:05
-- ============================================================

SELECT
		"checkpoint_master_sheet_table"."organization_id" AS "Org",
		CAST("checkpoint_master_sheet_table"."result_score" AS VARCHAR) AS "Result Score",
		CAST("checkpoint_master_sheet_table"."max_score" AS VARCHAR) AS "Max Score",
		CAST("checkpoint_master_sheet_table"."store_id" AS VARCHAR) AS "Location",
		CAST("checkpoint_master_sheet_table"."audit_type" AS VARCHAR) AS "Audit Folder",
		"checkpoint_master_sheet_table"."audit_main_theme" AS "Audit Name",
		"checkpoint_master_sheet_table"."theme" AS "Theme",
		"checkpoint_master_sheet_table"."audit_started_at" AS "Started At",
		"checkpoint_master_sheet_table"."audit_submitted_at" AS "Submitted At",
		"checkpoint_master_sheet_table"."audit_submission_number" AS "S No",
		"checkpoint_master_sheet_table"."audit_submission_knid" AS "Submission KNID",
		CAST("checkpoint_master_sheet_table"."auditor_name" AS VARCHAR) AS "Auditor",
		"checkpoint_master_sheet_table"."checkpoint_knid" AS "Checkpoint KNID",
		"checkpoint_master_sheet_table"."checkpoint" AS "Checkpoint",
		CAST("checkpoint_master_sheet_table"."how_or_what_to_check" AS VARCHAR) AS "Description",
		CAST("checkpoint_master_sheet_table"."result" AS VARCHAR) AS "Result",
		CAST("checkpoint_master_sheet_table"."criticality" AS VARCHAR) AS "Criticality",
		"checkpoint_master_sheet_table"."is_critical_question_failed" AS "Critical Failed?",
		CAST("checkpoint_master_sheet_table"."auditor_observations" AS VARCHAR) AS "Auditor Remarks",
		"checkpoint_master_sheet_table"."total_follow_up_tasks" AS "Total Follow Up Tasks",
		"checkpoint_master_sheet_table"."total_closed_follow_up_tasks" AS "Total Closed Follow Up Tasks",
		left(theme, position(':' IN theme)-1) AS "Process Owner",
          right(theme, length(theme)-position(':' IN theme)) AS "Area"
FROM "public"."checkpoint_master_sheet_table" AS "checkpoint_master_sheet_table"
```

---

## bigbasket_audit_form_Landlord Scope of Work.sql

**Tables referenced:** _fs, earliest_fr, earliest_fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: bigbasket_audit_form
-- Dashboard: Landlord Scope of Work
-- Category: Big Basket
-- Extracted: 2026-01-29 16:56:20
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'bigbasket-canis'
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
			   td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'bigbasket-canis'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id in ('-OMMoFu06thDdwKHzH4E')
     AND organization = 'bigbasket-canis'
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
        where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
    ),
	earliest_fs AS (
  SELECT DISTINCT ON (response_id) form_submissions.*, form_name
  FROM forms
  JOIN form_submissions ON forms.form_knid = form_submissions.form_id
where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  ORDER BY response_id, id ASC
),
earliest_fr AS (
  SELECT 
    fs.response_id,
    fs.user_id,
    (EXTRACT(EPOCH FROM (fs.submit_date + td.diff)) * 1000)::bigint AS earliest_epoch_submit_date
  FROM earliest_fs fs
  JOIN td ON fs.organization = td.organization
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
          q_type,fr.qid,
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
          form_name,fr,submit_date,
          fr.form_id,
          fr.response_id,
         ef.earliest_epoch_submit_date AS first_submit_epoch,
    ef.user_id AS first_submit_user_id,
          fr.location,
   fr.user_id,
   ud.first_name as auditor,fr.form_submit_id
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN user_details ud on fr.user_id = ud.uuid
   JOIN td ON fr.organization = td.organization
   JOIN location_acl on fr.location = location_acl.job_location
   LEFT JOIN earliest_fr ef ON fr.response_id = ef.response_id
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
            14,15,16,17,18,19,20,21
   ORDER BY 1,
            2,
            3)
SELECT 
form_id,form_submit_id,first_submit_epoch,first_submit_user_id,sno, submit_date,auditor,
MAX(CASE WHEN qid = '-OMMoFu06thDdwKHzH4F' THEN response ELSE NULL END) AS "Location Name",
MAX(CASE WHEN qid = '-OMMoFu06thDdwKHzH4G' THEN response ELSE NULL END) AS "Property Type",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdY5' THEN response ELSE NULL END) AS "Wall Constructed",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWV' THEN response ELSE NULL END) AS "Foundation",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdY6' THEN response ELSE NULL END) AS "Flooring_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWW' THEN response ELSE NULL END) AS "Plinth work",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdY7' THEN response ELSE NULL END) AS "Temp Power_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWX' THEN response ELSE NULL END) AS "Wal construction",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdY8' THEN response ELSE NULL END) AS "Shutter_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWY' THEN response ELSE NULL END) AS "Side sheeting work",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdY9' THEN response ELSE NULL END) AS "Painting_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWZ' THEN response ELSE NULL END) AS "MS support",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdYA' THEN response ELSE NULL END) AS "Washroom construction_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQW_' THEN response ELSE NULL END) AS "Roof installation",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdYB' THEN response ELSE NULL END) AS "Washroom fittings_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWa' THEN response ELSE NULL END) AS "Flooring_2",
MAX(CASE WHEN qid = '-OMMoFu1ytfr7NckJdYC' THEN response ELSE NULL END) AS "Removal of debris_1",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWb' THEN response ELSE NULL END) AS "Temp Power_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWc' THEN response ELSE NULL END) AS "Shutter_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWd' THEN response ELSE NULL END) AS "Painting_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWe' THEN response ELSE NULL END) AS "Washroom construction_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWf' THEN response ELSE NULL END) AS "Washroom fittings_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWg' THEN response ELSE NULL END) AS "Removal of debris_2",
MAX(CASE WHEN qid = '-OMMoFu2RHlRiyW2nQWh' THEN response ELSE NULL END) AS "Roof insulation"
FROM raw
group by 1,2,3,4,5,6,7
```

---
