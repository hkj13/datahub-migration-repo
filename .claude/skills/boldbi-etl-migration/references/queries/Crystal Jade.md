# Crystal Jade

> Auto-generated on 2026-03-04 08:13

**Total queries:** 6

---

## Crystal-Jade-KT-GW-CCP_01_02_C_CCP-01 and 02 Chiller-Freezer Temperature.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Crystal-Jade-KT-GW-CCP_01_02_C
-- Dashboard: CCP-01 and 02 Chiller-Freezer Temperature
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:55:03
-- ============================================================

-- Create necessary indexes (run these separately before executing the query)
/*CREATE INDEX idx_form_submissions_submit_date ON form_submissions(submit_date);
CREATE INDEX idx_form_submissions_form_id ON form_submissions(form_id);
CREATE INDEX idx_form_responses_form_submit_id ON form_responses(form_submit_id);
CREATE INDEX idx_question_definitions_nugget_id ON question_definitions(nugget_id);
CREATE INDEX idx_organizations_id ON organizations(id);
CREATE INDEX idx_user_details_uuid ON user_details(uuid);*/

WITH td AS (
  SELECT id AS organization,
         tzoffset,
         interval '1 min' * tzoffset AS diff
  FROM organizations
  WHERE id = 'CJade-fireworks'
  GROUP BY 1, 2
),
forms AS (
  SELECT id AS form_knid,
         title AS form_name
  FROM nuggets n
  WHERE id in ('-NpVNODHtRBaso3t6gy_')
    AND organization = 'CJade-fireworks'
    AND is_deleted = false
  GROUP BY 1, 2
),
qd_non_table_non_logic AS (
  SELECT nugget_id AS form_knid,
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
  WHERE question_type NOT IN ('table')
),
qdntwl_prework AS (
  SELECT *,
         jsonb_array_elements(definition -> 'logic') -> 'questions' AS q
  FROM forms
  JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
  WHERE qd.definition -> 'logic' IS NOT NULL
),
qd_non_table_with_logic AS (
  SELECT nugget_id AS form_knid,
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
  WHERE definition ->> 'logic' IS NOT NULL
),
qd_table AS (
  SELECT nugget_id AS form_knid,
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
  WHERE qd.question_type IN ('table')
),
final_definition AS (
  SELECT * FROM qd_non_table_non_logic
  UNION ALL
  SELECT * FROM qd_non_table_with_logic
  UNION ALL
  SELECT * FROM qd_table
  ORDER BY 1, 2, 3, 5 DESC, 7 DESC
),
_fs AS (
  SELECT DISTINCT ON (response_id) form_submissions.*,
         form_name,
         ud.first_name AS name
  FROM forms
  JOIN form_submissions ON forms.form_knid = form_submissions.form_id
  JOIN user_details ud ON form_submissions.user_id = ud.uuid
  WHERE form_submissions.submit_date at time zone 'Asia/Singapore' BETWEEN @{{:startDate}}::date AND @{{:endDate}}::date + interval '1 day'
  ORDER BY response_id, id DESC
),
fs AS (
  SELECT * FROM _fs
),
fr AS (
  SELECT fs.organization,
         form_submit_id,
         form_id,
         form_name,
         sno,
         submit_date + td.diff AS submit_date,
         user_id,
         name,
         response_id,
         question_id AS parent_qid,
         question_id AS qid,
         question_type,
         response,
         1 AS rn
  FROM form_responses fr
  JOIN fs ON fs.id = fr.form_submit_id
  JOIN td ON fs.organization = td.organization
  WHERE question_type NOT IN ('table', 'nested')
  UNION ALL
  SELECT organization,
         form_submit_id,
         form_id,
         form_name,
         sno,
         submit_date,
         user_id,
         name,
         response_id,
         question_id AS parent_qid,
         res.key AS qid,
         question_type,
         res.value AS response,
         rn
  FROM (
    SELECT fs.organization,
           form_submit_id,
           form_id,
           form_name,
           sno,
           submit_date + td.diff AS submit_date,
           user_id,
           name,
           response_id,
           question_id,
           question_type,
           base.value,
           base.ordinality AS rn
    FROM form_responses fr
    JOIN fs ON fs.id = fr.form_submit_id
    JOIN td ON fs.organization = td.organization,
               jsonb_array_elements(response) WITH ORDINALITY AS base
    WHERE question_type = 'table'
  ) base1
  CROSS JOIN jsonb_each(base1.value) res
),
location_questions AS (
  SELECT DISTINCT ON (nugget_id) nugget_id, question_id
  FROM question_definitions qd
  WHERE nugget_id IN (SELECT form_knid FROM forms)
    AND question_type = 'location'
  ORDER BY nugget_id, section_id, sqno
),
location_response AS (
  SELECT form_submit_id, (response ->> 'name')::text AS location_name
  FROM form_responses fr
  WHERE question_id IN (SELECT question_id FROM location_questions)
    AND form_submit_id IN (SELECT id FROM fs)
),
raw AS (
  SELECT fr.sno,
         fd.section_no,
         fd.q_no,
         fd.parent_question,
         fd.question,
         fd.qid,
         q_type,
         CASE
             WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
             WHEN fd.q_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') THEN fr.response -> 'selected'->>0
             WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY(
                 SELECT jsonb_array_elements_text(fr.response->'selected')
                 UNION
                 SELECT CASE
                     WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                     ELSE NULL
                 END
             ), ', ')
             WHEN fd.q_type IN ('date', 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
             WHEN fd.q_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula') THEN fr.response->>0
             WHEN fd.q_type IN ('user') THEN fr.response::text
             WHEN fd.q_type IN ('upload_mixed', 'upload_image', 'upload_video') THEN (fr.response)->0->>'response'
             WHEN fd.q_type IN ('signature', 'location', 'division', 'sub_division') THEN fr.response ->> 'name'
             ELSE NULL
         END AS response,
         CASE
             WHEN fd.q_type = 'section' THEN fr.response
             ELSE NULL
         END AS section_response,
         rn,
         form_name,
         name,
         fr.form_id,
         fr.response_id,
         fr.submit_date AS submit_date,
         lr.location_name AS submission_location
  FROM final_definition fd
  JOIN fr ON fr.qid = fd.qid
    AND fr.form_id = fd.form_knid
  JOIN location_response lr ON lr.form_submit_id = fr.form_submit_id
  JOIN td ON fr.organization = td.organization
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
  ORDER BY 1, 2, 3
)
SELECT submit_date AS "CCP-01 & 02Date",
       name AS "Sender Name",
       submission_location AS "Outlet",
       MAX(response) FILTER (WHERE qid = '-NpVNODHtRBaso3t6gyd') AS "Dept 部门",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafm') AS "1",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafn') AS "Code编号 1",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafp') AS "C 1",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafq') AS "2",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafr') AS "Code编号 2",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOaft') AS "C 2",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafu') AS "3",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafv') AS "Code编号 3",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafx') AS "C 3",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafy') AS "4",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOafz') AS "Code编号 4",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag0') AS "C 4",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag1') AS "5",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag2') AS "Code编号 5",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag4') AS "C 5",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag5') AS "6",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag6') AS "Code编号 6",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag8') AS "C 6",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOag9') AS "7",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagA') AS "Code编号 7",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagC') AS "C 7",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagD') AS "8",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagE') AS "Code编号 8",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagG') AS "C 8",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagH') AS "9",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagI') AS "Code编号 9",
       MAX(response) FILTER (WHERE qid = '-NpVNODI1jQM1e6zOagK') AS "C 9"
FROM raw
GROUP BY 1, 2, 3
```

---

## Crystal-Jade-KT-GW-CCP_03_Cook_CCP-03 Cooked Food Cooking Temperature.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: Crystal-Jade-KT-GW-CCP_03_Cook
-- Dashboard: CCP-03 Cooked Food Cooking Temperature
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:55:04
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'CJade-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id=  '-NpVNkr30Bv6hA2BDfeK'
     AND organization = 'CJade-fireworks'
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
                      form_name, ud.first_name as name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   Join user_details ud on form_submissions.user_id = ud.uuid
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date at time zone 'Asia/Singapore' between @{{:startDate}}::date and @{{:endDate}}::date + interval '1 day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          name,
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
                name,
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
             name,
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
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.qid,
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
          name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join location_response lr
   on lr.form_submit_id = fr.form_submit_id
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
            14,
            15,
            16
   ORDER BY 1,
            2,
            3)
SELECT submit_date as "DATE - CCP-03 Cooking Temperature ", name as "Sender Name",
submission_location as "Outlet",
MAX(
           CASE WHEN raw.qid = '-NpVNkr30Bv6hA2BDfeM' THEN Response END) as "Dept 部门",
          MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhB' THEN Response END) as "1.Product",
           MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhC' THEN Response END) as "Time (min) 1",
           MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhE' THEN Response END) as "Core Temp. (°C>75°C) 1",
           MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhF' THEN Response END) as "2.Product",
           MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhG' THEN Response END) as "Time (min) 2",
           MAX(
           CASE WHEN raw.qid = '-NpVNkr49cif74eewRhI' THEN Response END) as "Core Temp. (°C>75°C) 2"
FROM raw
group by 1,2,3
```

---

## KT-GW-FHOFoodHy__FHO Food Hygiene Audit Checklist.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: KT-GW-FHOFoodHy_
-- Dashboard: FHO Food Hygiene Audit Checklist
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:55:06
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'CJade-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id=  '-OESlvTc9wt2vAVn5xEa'
     AND organization = 'CJade-fireworks'
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
                      form_name, ud.first_name as name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   Join user_details ud on form_submissions.user_id = ud.uuid
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date between null:: timestamp AND null:: timestamp + interval '1 day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          name,
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
                name,
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
             name,
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
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.qid,
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
          name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join location_response lr
   on lr.form_submit_id = fr.form_submit_id
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
            14,
            15,
            16
   ORDER BY 1,
            2,
            3)
SELECT submit_date as "FHO Date", name as "Sender Name",
submission_location as "Outlet",
MAX(CASE WHEN raw.qid = '-OESlvTd0CiPYxlhbq6C' THEN Response END) as "食品处理员适合工作，没有任何疾病症状（例如腹泻和呕吐）",
MAX(CASE WHEN raw.qid = '-OESlvTd0CiPYxlhbq6E' THEN Response END) as "在准备食物和提供食物服务时穿着干净的制服或围裙",
MAX(CASE WHEN raw.qid = '-OESlvTd0CiPYxlhbq6G' THEN Response END) as "确保没有佩戴任何首饰",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMoW' THEN Response END) as "头发保持整洁，并在适当的地方用干净的帽子或发网盖住",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMoY' THEN Response END) as "指甲短、干净、没有涂指甲油或指甲装饰",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMo_' THEN Response END) as "手上的任何伤口或割伤（如果有）需使用防水和鲜艳的胶贴",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMob' THEN Response END) as "勤洗手 - 经常在适当的时候并用肥皂和水彻底正确的洗手",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMod' THEN Response END) as "用干净的器具和手套处理食物",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMof' THEN Response END) as "定时经常更换一次性手套和/或在任务之间更换",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMoi' THEN Response END) as "收货区干净，没有食物残渣、盒子纸皮和其他垃圾",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMok' THEN Response END) as "食品供应来自许可或批准的供应商/货源",
MAX(CASE WHEN raw.qid = '-OESlvTezZXvAsKwvMom' THEN Response END) as "收到的食品/食材供应在收到时进行目视检查",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJwo' THEN Response END) as "冷藏和冷冻产品来货必须到达适当的温度",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJwq' THEN Response END) as "生食和即食品必须分类分开和妥善储存以避免交叉污染",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJws' THEN Response END) as "所有食品供应都必须及时/迅速转移到适当的储存区",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJwv' THEN Response END) as "食品储藏区清洁、无虫害、干燥、通风良好、维修状况良好",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJwx' THEN Response END) as "干货（例如罐头食品和饮料）和其他食品整齐地存放在架子上，远离地板和墙壁",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJwz' THEN Response END) as "确保封密保护食品以免受污染；包装完好，产品没有变质迹象",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJx0' THEN Response END) as "食品包装和储存容器有适当的标签，正确注明食材内容和有效期",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJx2' THEN Response END) as "适当的库存周转机制系统，例如先过期先出 (FEFO) 系统用于库存管理",
MAX(CASE WHEN raw.qid = '-OESlvTf7LwaefgzWJx4' THEN Response END) as "非食品/化学剂（例如杀虫剂、清洁剂和其他化学品）不与食品一起存放",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHyy' THEN Response END) as "个人物品必须存放在员工储物柜区或柜子里，远离食物储存区",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHz1' THEN Response END) as "冷藏柜和冷冻柜保持在正确的温度：冷藏柜 0°C 至 4°C；冷冻柜-12°C",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHz3' THEN Response END) as "冷藏柜和冷冻柜内外保持清洁和维护良好正常操作",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHz5' THEN Response END) as "食物储存不过量不会积压，以保持良好的空气流通",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHz7' THEN Response END) as "冷藏库/冷冻库内食品整齐分类分开储存在架子上和离地板和墙壁",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHz9' THEN Response END) as "食品用适当的容器妥善包装/封密/覆盖，并贴上适当的标签，正确注明内容和有效,,期",
MAX(CASE WHEN raw.qid = '-OESlvTgKyQn6BopmHzB' THEN Response END) as "适当的库存周转系统，例如先过期先出 (FEFO) 系统用于库存管理",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1_' THEN Response END) as "熟食/即食品存放在生食之上方",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1b' THEN Response END) as "冷冻柜和冷藏柜的温度计功能正常且经过校准的温度计监控",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1e' THEN Response END) as "食物处理区干净、无虫害且维修状况良好",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1g' THEN Response END) as "洗手设施完善易于使用，正常操作，并有提供肥皂",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1i' THEN Response END) as "食物不是在地板上、靠近排水管或靠近/在厕所里准备的",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1k' THEN Response END) as "使用的食材在烹饪前彻底清洗干净",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1m' THEN Response END) as "冷冻食品在冷藏柜、微波炉或流动水下解冻",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1o' THEN Response END) as "适当的工作流程和区域隔离，生食和熟食/即食品区之间没有交叉污染",
MAX(CASE WHEN raw.qid = '-OESlvThYJBfS4Jkx-1q' THEN Response END) as "熟食/即食品、生肉、海鲜和蔬菜适当分开，避免交叉污染",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucF5' THEN Response END) as "不同的砧板、刀具和其他器具用于熟食/即食和生食",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucF7' THEN Response END) as "食物彻底煮熟至所需的核心温度",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucF9' THEN Response END) as "食物在冷藏前迅速冷却",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFB' THEN Response END) as "制冰机与容器保持清洁和维护良好",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFD' THEN Response END) as "制冰机里只储存冰块，以防止冰块被污染",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFF' THEN Response END) as "设备、抽油烟机、所有用具保持清洁和维护良好",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFH' THEN Response END) as "脏/脏的设备、陶器和器皿在使用后立即清洗干净",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFJ' THEN Response END) as "设备、陶器和器皿没有碎裂、破损或破裂",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFL' THEN Response END) as "有足够数量的有盖垃圾踏式垃圾桶供使用，垃圾得到妥善管理和处置",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFN' THEN Response END) as "垃圾箱内有适当的塑料袋内衬，并在任何时候都盖好",
MAX(CASE WHEN raw.qid = '-OESlvTiqbAglKTsucFP' THEN Response END) as "垃圾在垃圾处理区/垃圾箱中心处理前已妥善装袋",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYz1' THEN Response END) as "食品被适当地包裹/覆盖在适当的容器中，并防止受到污染",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYz3' THEN Response END) as "冷食/食材盘保持在 0°C 至 4°C",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYz7' THEN Response END) as "热食/食材持在 60°C 以上",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYz9' THEN Response END) as "冷/或热保温器保持清洁和维护良好",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzC' THEN Response END) as "废物处理区/垃圾箱中心干净、无害虫、无溢出物",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzE' THEN Response END) as "垃圾袋丢弃在垃圾箱内，不放在地板上",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzG' THEN Response END) as "垃圾箱在任何时候都必须盖住",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzJ' THEN Response END) as "厕所干净、干燥且通风",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzL' THEN Response END) as "提供基本设施，例如肥皂、卫生纸、干手器/纸巾和垃圾桶",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzN' THEN Response END) as "厕所配件设施处于良好的工作状态",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzQ' THEN Response END) as "所有食品加工人员均持有效的基本食品卫生证书和有效的更新食品卫生证书（如适用）",
MAX(CASE WHEN raw.qid = '-OESlvTjtl1jvnvegYzS' THEN Response END) as "食品卫生管理员持有效的食品卫生官证书 8"
FROM raw
group by 1,2,3
```

---

## KT-GW-PRP_02_Stoc__PRP-02 Stock Receiving Temperature.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: KT-GW-PRP_02_Stoc_
-- Dashboard: PRP-02 Stock Receiving Temperature
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:54:49
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'CJade-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id=  '-NpVPSA1EDh8L6c5-k6E'
     AND organization = 'CJade-fireworks'
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
                      form_name, ud.first_name as name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   Join user_details ud on form_submissions.user_id = ud.uuid
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date between @{{:startDate}}:: timestamp AND @{{:endDate}}:: timestamp + interval '1 day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          name,
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
                name,
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
             name,
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
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.qid,
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
          name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join location_response lr
   on lr.form_submit_id = fr.form_submit_id
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
            14,
            15,
            16
   ORDER BY 1,
            2,
            3)
SELECT submit_date as "DATE PRP-02:Stock Receiving", name as "Sender Name",
submission_location as "Outlet",
MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6I' THEN Response END) as "Dept 部门",
          MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6J' THEN Response END) as "No.1 Product",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6L' THEN Response END) as "1 Frozen / Chilled",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6M' THEN Response END) as "1 C",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6O' THEN Response END) as "No.2 Product",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6Q' THEN Response END) as "2 Frozen / Chilled",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6R' THEN Response END) as "2 C",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6T' THEN Response END) as "No.3 Product",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6V' THEN Response END) as "3 Frozen / Chilled",
           MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6W' THEN Response END) as "3 C"
FROM raw
group by 1,2,3
```

---

## KT-GW-PRP_05_01_Po__PRP-05-01 Post-operation Dish Washing Checklist.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: KT-GW-PRP_05_01_Po_
-- Dashboard: PRP-05-01 Post-operation Dish Washing Checklist
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:54:50
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'CJade-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id=  '-NpVOymgYJLBW2SEIen4'
     AND organization = 'CJade-fireworks'
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
                      form_name, ud.first_name as name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   Join user_details ud on form_submissions.user_id = ud.uuid
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date between @{{:startDate}}:: timestamp AND @{{:endDate}}:: timestamp + interval '1 day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          name,
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
                name,
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
             name,
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
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.qid,
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
          name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join location_response lr
   on lr.form_submit_id = fr.form_submit_id
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
            14,
            15,
            16
   ORDER BY 1,
            2,
            3)
SELECT submit_date as "PRP-05-01 DATE", name as "Sender Name",
submission_location as "Outlet",
/*MAX(
           CASE WHEN raw.qid = '-NpVPSA1EDh8L6c5-k6I' THEN Response END) as "Dept 部门",*/
          MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIen8' THEN Response END) as "1 手部没伤口，衣着/制服干净，鞋子干净无破损，水鞋没有放置在工作岗位",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenA' THEN Response END) as "2.1 墙壁，隔板干净",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenB' THEN Response END) as "2.2 地板干净, 沒有汚积、干燥C",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenC' THEN Response END) as "2.3 洗碗机干净, 沒有遗留垃圾",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenD' THEN Response END) as "2.4 层架碗盘存放整齐,沒汚垢器皿都是倒置晾乾",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenE' THEN Response END) as "2.5 层架的器皿都是倒置晾乾",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenF' THEN Response END) as "2.6 天花板/牆壁/通风道清洁",
		   MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenG' THEN Response END) as "2.7 垃圾桶/垃圾己清理",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenH' THEN Response END) as "2.8 沟渠/排水口滤网清洁",
           MAX(
           CASE WHEN raw.qid = '-NpVOymgYJLBW2SEIenI' THEN Response END) as "2.9 沒有害虫出没",
           MAX(
           CASE WHEN raw.qid = '-NpVOymh1bUMX3zpjURM' THEN Response END) as "3.1 电灯操作正常",
           MAX(
           CASE WHEN raw.qid = '-NpVOymh1bUMX3zpjURO' THEN Response END) as "4.1 所有化学制品要有标签",
           MAX(
           CASE WHEN raw.qid = '-NpVOymh1bUMX3zpjURP' THEN Response END) as "4.2 地拖把挂起晾乾",
           MAX(
           CASE WHEN raw.qid = '-NpVOymh1bUMX3zpjURQ' THEN Response END) as "4.3 清洁物品适当地存放",
           MAX(
           CASE WHEN raw.qid = '-NpVOymh1bUMX3zpjURS' THEN Response END) as "5.1 工作岗位无私人物品/药品"
FROM raw
group by 1,2,3
```

---

## KT-GW-PRP_05_DailyP_2_PRP-05 Daily Post-operation Checklist.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, location_response, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: KT-GW-PRP_05_DailyP_2
-- Dashboard: PRP-05 Daily Post-operation Checklist
-- Category: Crystal Jade
-- Extracted: 2026-01-29 16:54:51
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'CJade-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-NpVOlfmy_cVTGON_wZI')
     AND organization = 'CJade-fireworks'
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
                      form_name, ud.first_name as name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   Join user_details ud on form_submissions.user_id = ud.uuid
   ORDER BY response_id,
            id DESC),
    fs as (
        select * from _fs
        where submit_date between @{{:startDate}}:: timestamp AND @{{:endDate}}:: timestamp + interval '1 day'
    ),
     fr AS
  (SELECT fs.organization,
          form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date + td.diff AS submit_date,
          user_id,
          name,
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
                name,
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
             name,
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
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr 
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          fd.qid,
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
          name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          lr.location_name as submission_location
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join location_response lr
   on lr.form_submit_id = fr.form_submit_id
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
            14,
            15,
            16
   ORDER BY 1,
            2,
            3)
SELECT submit_date as "DATE PRP-05", name as "Sender Name",
submission_location as "Outlet",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykK' THEN Response END) as "1.1 墙壁，壁砖干净",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykL' THEN Response END) as "1.2 地板干净、无垃圾",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykM' THEN Response END) as "1.3 工作枱清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykN' THEN Response END) as "1.4 微波炉有保持干净清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykO' THEN Response END) as "1.5 绞肉机干净没有遗留肉渣",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykP' THEN Response END) as "1.6 搅拌机干净没有食物残渣",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykQ' THEN Response END) as "1.7 保温炉干净没有水分残留",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykR' THEN Response END) as "1.8 烹煮区清洁灶头",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykT' THEN Response END) as "2.1 烹煮区清洁蒸炉",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykU' THEN Response END) as "2.2 烹煮区清洁油炸机",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykV' THEN Response END) as "2.3 烹煮区清洁油炉/烤炉",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykW' THEN Response END) as "2.4 厨房用具清洁/枮板/刀具等等",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykX' THEN Response END) as "2.5 餐具干净没有污迹",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykY' THEN Response END) as "2.6 窗口/通风管清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykZ' THEN Response END) as "2.7 煤气管水管清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5yk_' THEN Response END) as "2.8 垃圾桶清洁无异味",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5yka' THEN Response END) as "2.9 沟渠/排水道与滤网清洁无食物残渣",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykc' THEN Response END) as "3.1 确保沒有害虫踪迹",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5yke' THEN Response END) as "4.1 所有电灯操作正常",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykg' THEN Response END) as "5.1 排气罩清洁没有油垢",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5yki' THEN Response END) as "6.1 冷藏柜和冷冻柜/库干净",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykj' THEN Response END) as "6.2 储存架/柜清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykk' THEN Response END) as "6.3 地板清洁",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykl' THEN Response END) as "6.4 熟食与生材料须分开",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5ykm' THEN Response END) as "6.5 货物须标签时效，不杂乱",
MAX(CASE WHEN raw.qid = '-NpVOlfn3Uc1Y5Kk5yko' THEN Response END) as "7.1 工作岗位无私人物品/药品"
FROM raw
group by 1,2,3
```

---
