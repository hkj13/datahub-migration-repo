# Freshbus

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Freshbus Service Cancellation_Service Cancellation Report.sql

**Tables referenced:** Ops, RAW, base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Freshbus Service Cancellation
-- Dashboard: Service Cancellation Report
-- Category: Freshbus
-- Extracted: 2026-01-29 16:59:08
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike 'Service Delay/Cancel communication%'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
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
   WHERE (submit_date AT TIME ZONE 'Asia/Kolkata') BETWEEN @{{:Form Submitted At.START}}::timestamp AND @{{:Form Submitted At.END}}::TIMESTAMP + interval '1 day'
   ORDER BY response_id,
            id DESC),
                                                                                       fr AS
  (SELECT form_submit_id,
          form_id,
          LOCATION,
          sno,
          submit_Date AT TIME ZONE 'Asia/Kolkata' AS submitted_At,
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
             submit_Date AT TIME ZONE 'Asia/Kolkata' AS submitted_At,
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
                                                                                       RAW AS
  (SELECT fd.organization AS "Organization",
          fr.location AS "Location",
          form_name AS "Form Name",
          submitted_at AS "Submitted At",
          fr.sno AS "Submission No",
          fd.section_no AS "Section No",
          fd.q_no AS "Question No",
          fd.parent_question AS "Parent Question",
          fd.question AS "Question",
          fd.q_type AS "Question Type",
          rn AS "Row No",
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Kolkata', 'YYYY-MM-DD HH24:MI:SS')
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
            15,
            16), base as (
SELECT raw."Organization",
       raw."Form KNID",
       raw."Form Name",
       raw."Submission KNID",
       raw."Submission No",
       raw."Submitted At",
       raw."Location" AS "Region",
       max(CASE
               WHEN raw."Question" = 'Date of Journey' THEN raw."Response"::DATE
               ELSE NULL
           END) AS "Date of Journey",
       max(CASE
               WHEN raw."Question" = 'Bus Number' THEN raw."Response"
               ELSE NULL
           END) AS "Vehicle Number",
       max(CASE
               WHEN raw."Question" = 'Service Number' THEN raw."Response"
               ELSE NULL
           END) AS "Service Number",
       max(CASE
               WHEN raw."Question" = 'Issue type' THEN raw."Response"
               ELSE NULL
           END) AS "Issue Type",
       max(CASE
               WHEN raw."Question" = 'Issue Subtype' THEN raw."Response"
               ELSE NULL
           END) AS "Issue Subtype",
       max(CASE
               WHEN raw."Question" = 'Delay Duration' THEN raw."Response"::numeric
               ELSE NULL
           END) AS "Delay Duration",
       max(CASE
               WHEN raw."Question" = 'Cancel / Delay Description(Remarks)%' THEN raw."Response"
               ELSE NULL
           END) AS "Remarks",
       max(CASE
               WHEN raw."Question" = 'Does the information shared to the cx from Ops?%' THEN raw."Response"
               ELSE NULL
           END) AS "Informed CX?",
       max(CASE
               WHEN raw."Question" = 'Stage 1' THEN raw."Section Response"->'sender'->>'userName'
               ELSE NULL
           END) AS "Submitted By"
FROM RAW
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7)
		 
		 select * from base where base."Date of Journey" between @{{:Date of Journey.START}}::timestamp and @{{:Date of Journey.END}}::timestamp + interval '1 day'
		 
ORDER BY 1,
         2,
         3,
         7,
         8,
         10
```

---
