# Dank

> Auto-generated on 2026-03-04 08:13

**Total queries:** 4

---

## Dank Customer Complaints_Customer Complaints.sql

**Tables referenced:** LATERAL, RAW, base, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Dank Customer Complaints
-- Dashboard: Customer Complaints
-- Category: Dank
-- Extracted: 2026-01-29 16:54:23
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'dank-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = @{{:formId}}
     AND organization = 'dank-antenna'
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
          x.elem AS q -- each logic item as a JSONB value

   FROM forms f
   JOIN question_definitions qd ON qd.nugget_id = f.form_knid -- defensively expand either an array at 'logic' or an object with a 'questions' array

   CROSS JOIN LATERAL jsonb_array_elements(CASE jsonb_typeof(qd.definition -> 'logic')
                                               WHEN 'array' THEN qd.definition -> 'logic'
                                               WHEN 'object' THEN COALESCE(qd.definition -> 'logic' -> 'questions', '[]'::jsonb)
                                               ELSE '[]'::jsonb
                                           END) AS x(elem) -- keep only rows that have some 'logic' present

   WHERE qd.definition -> 'logic' IS NOT NULL ),
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
     fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
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
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
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
            3), base AS
  (SELECT sno AS "Complaint No",
          form_id AS "Complaint Form KNID",
          response_id AS "Complaint KNID",
          MAX(CASE
                  WHEN question ILIKE 'Complaint Date%' THEN to_date(response, 'YYYY-MM-DD HH24:MI:SS')
                  ELSE NULL
              END) AS "Complaint Date",
          MAX(CASE
                  WHEN question ILIKE 'City%' THEN response
                  ELSE NULL
              END) AS "City",
          max(CASE
                  WHEN question ILIKE 'Branch%' THEN response
                  ELSE NULL
              END) AS "Branch",
          max(CASE
                  WHEN question ILIKE 'Channel%' THEN response
                  ELSE NULL
              END) AS "Channel",
          max(CASE
                  WHEN question ILIKE 'Order By%' THEN response
                  ELSE NULL
              END) AS "Order By",
          max(CASE
                  WHEN question ILIKE 'Order Number /%' THEN response
                  ELSE NULL
              END) AS "Order No",
          max(CASE
                  WHEN question ILIKE 'Complaint Type%' THEN response
                  ELSE NULL
              END) AS "Complaint Type",
          max(CASE
                  WHEN question ILIKE 'Sub-Type Complaint%' THEN response
                  ELSE NULL
              END) AS "Sub-Type",
          max(CASE
                  WHEN question ILIKE 'Main Type%' THEN response
                  ELSE NULL
              END) AS "Main Type",
          max(CASE
                  WHEN question ILIKE 'Procedure%' THEN response
                  ELSE NULL
              END) AS "Procedure",
          max(CASE
                  WHEN question ILIKE 'What is the % of the Coupon%' THEN response::numeric
                  ELSE NULL
              END) AS "Coupon %",
          max(CASE
                  WHEN question ILIKE 'What is the amount of the refund%' THEN response::numeric
                  ELSE NULL
              END) AS "Refund Amount",
          max(CASE
                  WHEN question ILIKE 'Agent Name%' THEN response
                  ELSE NULL
              END) AS "Agent Name",
          max(CASE
                  WHEN question ILIKE 'Customer Name%' THEN response
                  ELSE NULL
              END) AS "Customer Name",
          max(CASE
                  WHEN question ILIKE 'Customer phone number%' THEN response
                  ELSE NULL
              END) AS "Customer Ph No",
          max(CASE
                  WHEN question ILIKE 'Complain Description%' THEN response
                  ELSE NULL
              END) AS "Complaint",
          max(CASE
                  WHEN question ILIKE 'Notes%' THEN response
                  ELSE NULL
              END) AS "Notes",
          max(CASE
                  WHEN question ILIKE 'Proof of the procedure%' THEN response
                  ELSE NULL
              END) AS "Procedure Proof"
   FROM RAW
   GROUP BY 1,
            2,
            3)
SELECT *
FROM base
WHERE "Complaint Date" BETWEEN @{{:startDate}} AND @{{:endDate}}
ORDER BY 4,
         5,
         6,
         7,
         1
```

---

## Dank Evaluation Form Analytics_Evaluation Form Analytics.sql

**Tables referenced:** RAW, fd, fds, form_responses, form_submissions, forms, fr, fs, metadata, nuggets, organizations, question_definitions, td

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Dank Evaluation Form Analytics
-- Dashboard: Evaluation Form Analytics
-- Category: Dank
-- Extracted: 2026-01-29 16:58:00
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'dank-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = @{{:formId}}),
     fd AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::int AS q_no,
          section_id,
          question_id AS qid,
          question_type AS q_type,
          question
   FROM question_definitions
   WHERE nugget_id IN
       (SELECT distinct form_knid
        FROM forms)),
     fds AS
  (SELECT nugget_id AS form_knid,
          CASE
              WHEN section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer
          END AS section_no,
          sqno::int AS q_no,
          section_id,
          question_id AS qid,
          question_type AS q_type,
          question,
          options.value->>'value' AS OPTION,
                          5-options.ordinality AS score
   FROM question_definitions,
        jsonb_array_elements(definition->'options') WITH
   ORDINALITY OPTIONS
   WHERE nugget_id IN
       (SELECT distinct form_knid
        FROM forms)
     AND question_type = 'multiple_choice'),
     fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   JOIN td ON form_submissions.organization = td.organization
   where submit_date + td.diff between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          response_id,
          question_id AS qid,
          question_type,
          response
   FROM form_responses fr
   JOIN fs ON fs.id = fr.form_submit_id
   JOIN td ON fs.organization = td.organization),
     RAW AS
  (SELECT fr.organization,
          fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          fd.q_type,
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
          fds.score,
          CASE
              WHEN fd.q_type = 'multiple_choice' THEN 4
              ELSE NULL
          END AS max_score,
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date
   FROM fr
   JOIN fd ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   LEFT OUTER JOIN fds ON fr.qid = fds.qid
   AND fr.form_id = fds.form_knid
   AND fr.response -> 'selected'->>0 = fds.option
   JOIN td ON fr.organization = td.organization
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
            3), metadata AS
  (SELECT raw.organization AS "Organization",
          raw.form_name AS "Form",
          raw.sno AS "Submission No",
          raw.submit_date AS "Submitted At",
          max(CASE
                  WHEN section_no = 1
                       AND q_type = 'section' THEN section_response -> 'sender' ->> 'name'
                  ELSE NULL
              END) AS "Submitted By",
          max(CASE
                  WHEN section_no = 1
                       AND q_type = 'location' THEN response
                  ELSE NULL
              END) AS "Location",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'What suggestions do you have for improving the portioning & procedure quality guide to make it more practical and user-friendly for your team?' THEN response
                  ELSE NULL
              END) AS "Suggestions",
          form_id AS "Form KNID",
          raw.response_id AS "Submission KNID",
          max(CASE
                  WHEN section_no = 1
                       AND q_type = 'section' THEN section_response -> 'sender' ->> 'userId'
                  ELSE NULL
              END) AS "Submitter KNID",
          max(CASE
                  WHEN section_no = 1
                       AND q_type = 'section' THEN (section_response ->> 'sentAt')::bigint
                  ELSE NULL
              END) AS "Submitted At Epoch",
          sum(CASE
                  WHEN q_type = 'multiple_choice' THEN score
                  ELSE NULL
              END) / sum(CASE
                             WHEN q_type = 'multiple_choice' THEN max_score
                             ELSE NULL
                         END) AS "Audit Score"
   FROM RAW
   GROUP BY 1,
            2,
            3,
            4,
            8,
            9)
SELECT md.*,
       raw.question AS "Checkpoint",
       raw.response AS "Response",
       raw.score AS "Checkpoint Score",
       raw.max_score AS "Checkpoint Max Score"
FROM metadata md
LEFT OUTER JOIN RAW ON md."Form KNID" = raw.form_id
AND md."Submission KNID" = raw.response_id
AND raw.q_type = 'multiple_choice'
ORDER BY 1,
         2,
         6,
         4,
         raw.q_no
```

---

## Dank OOS Stock_OOS Stock.sql

**Tables referenced:** final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, oos, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Dank OOS Stock
-- Dashboard: OOS Stock
-- Category: Dank
-- Extracted: 2026-01-29 16:56:45
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'dank-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-OLBZVLAYQdfo9uRIdQo')
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
  ( SELECT *
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
  ( SELECT DISTINCT ON (response_id) form_submissions.*,
                       form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   join td on form_submissions.organization = td.organization
   where (form_submissions.submit_date + td.diff) >= '2025-03-10'
   ORDER BY response_id,
            id DESC),
     fr AS
  ( SELECT fs.organization,
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
     RAW AS
  ( SELECT fr.sno,
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
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
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
            3),            oos as (
            select sno, question as category, unnest(string_to_array(response, ', ')) as item from raw 
            where section_no = 1 and q_type = 'dropdown' group by 1, 2, 3
            )
            select raw.sno as "Submission No", submit_date as "Submitted On", max(case when section_no = 2 and q_no = 0 and response is NULL then 'Pending' else 'Marked OOS' end) as "Marking OOS Status",
            max(case when section_no = 1 and question = 'Location' then response else null end) as "Branch",
            oos.category as "Category", oos.item as "OOS Item"
            from raw
			left outer join oos on raw.sno = oos.sno
			where oos.item is not null and oos.item != ''
			group by 1, 2, 5, 6
			order by 2, 5, 6
```

---

## Dank QIR_Quality Incident Report.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Dank QIR
-- Dashboard: Quality Incident Report
-- Category: Dank
-- Extracted: 2026-01-29 16:58:01
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'dank-antenna'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE 'Quality Incident%'
     AND organization = 'dank-antenna'
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
     fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   where submit_date between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
   ORDER BY response_id,
            id DESC),
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
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
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
SELECT form_name AS "Form",
       form_id AS "Form KNID",
       response_id AS "Submission KNID",
       sno AS "Submission No",
       submit_date AS "Submitted At",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN section_response -> 'sender' ->>'userName'
               ELSE NULL
           END) AS "Submitted By",
       max(CASE
               WHEN q_type = 'location' THEN response
               ELSE NULL
           END) AS "Location",
       max(CASE
               WHEN question ILIKE '%risk level%' THEN response
               ELSE NULL
           END) AS "Risk Level",
       max(CASE
               WHEN question ILIKE '%kind of incident%' THEN response
               ELSE NULL
           END) AS "Category",
       max(CASE
               WHEN question ILIKE '%Describe the incident%' THEN response
               ELSE NULL
           END) AS "Incident",
       max(CASE
               WHEN question ILIKE '%Corrective%' THEN response
               ELSE NULL
           END) AS "Corrective Actions",
       max(CASE
               WHEN question ILIKE '%Type of wastage%' THEN response
               ELSE NULL
           END) AS "Wastage Type",
       max(CASE
               WHEN question ILIKE '%Amount of wastage%' THEN response
               ELSE NULL
           END) AS "Wastage Amount",
       max(CASE
               WHEN question ILIKE '%name of the employee%' THEN response
               ELSE NULL
           END) AS "Involved Employee Name",
       max(CASE
               WHEN question ILIKE '%employee id%' THEN response
               ELSE NULL
           END) AS "Involved Employee ID",
       max(CASE
               WHEN question ILIKE '% employee''s actions%' THEN response
               ELSE NULL
           END) AS "Employee Involvement",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN section_response -> 'sender' ->>'userId'
               ELSE NULL
           END) AS "Submitter KNID",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN (section_response ->>'sentAt')::bigint
               ELSE NULL
           END) AS "Submitted Epoch"
FROM RAW
GROUP BY 1,
         2,
         3,
         4,
         5
ORDER BY 1,
         4,
         5
```

---
