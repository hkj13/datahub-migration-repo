# Mama Lou

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Mama Lou Temperature Compliance_Temp Compliance.sql

**Tables referenced:** RAW, base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, useR_details

**Columns needing snake_case conversion:**

- `eE` -> `e_e` (alias: `e_e AS "eE"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Mama Lou Temperature Compliance
-- Dashboard: Temp Compliance
-- Category: Mama Lou
-- Extracted: 2026-01-29 16:59:03
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.organization = 'mlhg-fireworks'
     AND n.title ILIKE 'Kitchen Leader%'
     AND n.classification_type = 'form'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
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
   WHERE qd.definition -> 'logic' IS NOT NULL
     AND jsonb_typeof(definition -> 'logic') = 'array'
   UNION SELECT *,
                definition -> 'logic' -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL
     AND jsonb_typeof(definition -> 'logic') != 'array'),
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
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          form_id,
          sno,
          submit_Date AT TIME ZONE 'Asia/Singapore' AS submitted_At,
                                   user_id,
                                   response_id,
                                   question_id AS parent_qid,
                                   question_id AS qid,
                                   question_type,
                                   response,
                                   1 AS rn
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   WHERE question_type NOT IN ('table',
                               'nested')
   UNION SELECT form_submit_id,
                form_id,
                sno,
                submitted_At,
                user_id,
                response_id,
                question_id AS parent_qid,
                res.key AS qid,
                question_type,
                res.value AS response,
                rn
   FROM
     (SELECT form_submit_id,
             form_id,
             sno,
             submit_Date AT TIME ZONE 'Asia/Singapore' AS submitted_At,
                                      user_id,
                                      response_id,
                                      question_id,
                                      question_type,
                                      base.value,
                                      base.ordinality AS rn
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res),
                                                                                       RAW AS
  (SELECT fd.organization,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid,
          fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.q_type,
          rn,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime')
                   AND fr.response->>0 ~ '^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$' THEN to_char(to_timestamp(((fr.response->>0)::numeric)/1000) AT TIME ZONE 'Asia/Singapore', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'time') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response
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
            13), base AS
  (SELECT organization,
          form_name,
          form_knid,
          form_response_knid,
          sno,
          to_timestamp(max(CASE
                               WHEN section_no = 1
                                    AND q_no = 0 THEN (section_response->>'sentAt')::numeric
                               ELSE NULL
                           END)/1000) AT TIME ZONE 'Asia/Singapore' AS submitted_at,
                                                   max(CASE
                                                           WHEN section_no = 1
                                                                AND q_no = 0 THEN section_response->'sender'->>'userId'
                                                           ELSE NULL
                                                       END) AS submitter_knid,
                                                   max(CASE
                                                           WHEN question = 'Are the chillers between 0 to 4°C' THEN response
                                                           ELSE NULL
                                                       END) AS "Chiller Temp in range",
                                                   max(CASE
                                                           WHEN question = 'Are the freezers between 0 to -18° C' THEN response
                                                           ELSE NULL
                                                       END) AS "Freezer Temp in range"
   FROM RAW
   GROUP BY 1,
            2,
            3,
            4,
            5)
SELECT base.organization AS "Org",
       substring(form_name, 22, 8) AS "Shift",
       form_knid AS "Form KNID",
       form_response_knid AS "Form Response KNID",
       sno AS "Submission No",
       submitted_at AS "Submitted At",
       ud.job_location AS "Location",
       "Chiller Temp in range",
       "Freezer Temp in range"
FROM base
JOIN useR_details ud ON base.submitter_knid = ud.uuid
ORDER BY 1,
         7,
         6,
         2
```

---

## RESTAURANT BOH AUDIT_RESTAURANT BOH AUDIT.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, location_acl, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: RESTAURANT BOH AUDIT
-- Dashboard: RESTAURANT BOH AUDIT
-- Category: Mama Lou
-- Extracted: 2026-01-29 16:55:15
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
    -- AND is_active = 'true'
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
 AND store_id NOT ILIKE '%HO'
     and audit_main_theme ilike '%RESTAURANT BOH AUDIT%')
SELECT 
    organization_id AS "Org",
    store_id AS "Location",
    audit_main_theme AS "Audit",
    audit_submitted_at AS "Audit Date",
    audit_submission_number AS "Audit Report No",
    audit_submission_knid AS "Audit Report KNID",
    auditor_name AS "Auditor",
    theme AS "Theme",
     -- Extract the part before the last ' - '
    LEFT(theme, LENGTH(theme) - POSITION(' - ' IN REVERSE(theme)) - 2) AS "Theme Checkpoint Name",
    
    -- Extract the part after the last ' - '
    RIGHT(theme, POSITION(' - ' IN REVERSE(theme)) - 1) AS "Theme Category",
    SUM(result_score) AS "Actual Score",
    SUM(max_score) AS "Max Score",
    SUM(result_score) / SUM(max_score) AS "Audit Score",
    COUNT(CASE WHEN is_critical_question_failed = 'true' THEN checkpoint_knid ELSE NULL END) AS "Critical Failed Count",
    SUM(total_follow_up_tasks) AS "Total Follow Ups",
    SUM(total_closed_follow_up_tasks) AS "Total Closed Follow Ups",
    "Audit No in Year"
FROM location_acl acl
LEFT OUTER JOIN base ON acl.job_location = base.store_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 17
ORDER BY 1, 2, 4
```

---
