# JFC

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## JFC Brand Standard_Brand Standards.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: JFC Brand Standard
-- Dashboard: Brand Standards
-- Category: JFC
-- Extracted: 2026-01-29 16:55:13
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'jfc-quality-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Brand Standards%')
     AND organization = 'jfc-quality-cartwheel'
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location
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
            13,
            14
   ORDER BY 1,
            2,
            3)
SELECT sno,
MAX(CASE WHEN question ILIKE '%Audited Location%' THEN response END) AS "Audited Location",
MAX(CASE WHEN question ILIKE '%Store Code%' THEN response END) AS "Store Code",
MAX(CASE WHEN question ILIKE 'BU' THEN response END) AS "BU",
MAX(CASE WHEN question ILIKE '%RBU%' THEN response END) AS "RBU",
MAX(CASE WHEN question ILIKE '%District%' THEN response END) AS "District",
MAX(CASE WHEN question ILIKE '%Area%' THEN response END) AS "Area",
MAX(CASE WHEN question ILIKE '%Audit Type%' THEN response END) AS "Audit Type",
MAX(CASE WHEN question ILIKE '%Start Time%' THEN response END) AS "Start Time",
MAX(CASE WHEN question ILIKE '%End Time%' THEN response END) AS "End Time",
MAX(CASE WHEN question ILIKE '%Conducted By%' THEN response END) AS "Conducted By",
MAX(CASE WHEN question ILIKE '%Product 1 : Choose the Products%' THEN response END) AS "Product 1 : Choose the Products",
(
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF1A%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF1B%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF1C%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF1D%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF1E%' THEN response END) AS INTEGER), 0)
) AS "Product 1 Total Score",
MAX(CASE WHEN question ILIKE '%Product 2: Choose the Products%' THEN response END) AS "Product 2: Choose the Products",
(
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF2A%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF2B%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF2C%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF2D%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF2E%' THEN response END) AS INTEGER), 0)
) AS "Product 2 Total Score",
MAX(CASE WHEN question ILIKE '%Product 3: Choose the Products%' THEN response END) AS "Product 3: Choose the Products",
(
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF3A%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF3B%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF3C%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF3D%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF3E%' THEN response END) AS INTEGER), 0)
) AS "Product 3 Total Score",
MAX(CASE WHEN question ILIKE '%Product 4- Choose the Products%' THEN response END) AS "Product 4- Choose the Products",
(
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF4A%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF4B%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF4C%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF4D%' THEN response END) AS INTEGER), 0) +
  COALESCE(CAST(MAX(CASE WHEN question ILIKE '%Q-FF4E%' THEN response END) AS INTEGER), 0)
) AS "Product 4 Total Score",
MAX(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response::numeric END) AS "Total Audit Scores",
CASE 
  WHEN MAX(CAST(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response END AS NUMERIC)) <= 15 THEN 'Pass'
  ELSE 'Fail'
END AS "Result",
MAX(CASE WHEN question ILIKE '%Q-S16: Transaction 3: Dine / Take home order met speed standards (Minor or Major)%' THEN response END) AS "Q-S16: Transaction 3: Dine / Take home order met speed standards (Minor or Major)",
MAX(CASE 
        WHEN question ILIKE '%Q-S16: Transaction 3: Dine / Take home order met speed standards (Minor or Major)%' AND response = '0' 
        THEN 'Compliant'
        WHEN question ILIKE '%Q-S16: Transaction 3: Dine / Take home order met speed standards (Minor or Major)%' AND response IS NOT NULL 
        THEN 'Non-Compliant'
    END) AS "Q-S16: Compliance Status",
	CASE 
  WHEN MAX(CAST(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response END AS NUMERIC)) BETWEEN 0 AND 5 THEN 'High'
  WHEN MAX(CAST(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response END AS NUMERIC)) BETWEEN 6 AND 15 THEN 'Medium'
  WHEN MAX(CAST(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response END AS NUMERIC)) BETWEEN 16 AND 20 THEN 'Low'
  WHEN MAX(CAST(CASE WHEN question ILIKE '%Total Audit Scores%' THEN response END AS NUMERIC)) >= 21 THEN 'Critical'
  ELSE NULL
END AS "Performance Category"
FROM raw
group by sno
```

---

## JFC GSC_Brand Standards.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, product_questions, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: JFC GSC
-- Dashboard: Brand Standards
-- Category: JFC
-- Extracted: 2026-01-29 16:55:12
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'jfc-quality-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Brand Standards%')
     AND organization = 'jfc-quality-cartwheel'
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location
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
            13,
            14
   ORDER BY 1,
            2,
            3)
,product_questions AS (
  SELECT 
    sno,
    MAX(CASE WHEN question ILIKE '%Audited Location%' THEN response END) AS "Audited Location",
    MAX(CASE WHEN question ILIKE '%Store Code%' THEN response END) AS "Store Code",
    MAX(CASE WHEN question ILIKE 'BU' THEN response END) AS "BU",
    MAX(CASE WHEN question ILIKE '%RBU%' THEN response END) AS "RBU",
    MAX(CASE WHEN question ILIKE '%District%' THEN response END) AS "District",
    MAX(CASE WHEN question ILIKE '%Area%' THEN response END) AS "Area",

   -- Product 1
    MAX(CASE WHEN question ILIKE '%Product 1 : Choose the Products%' THEN response END) AS product_1_name,
    SUM(CASE WHEN question ILIKE '%Q-FF1%' THEN CAST(response AS INTEGER) ELSE 0 END) AS product_1_score,

    -- Product 2
    MAX(CASE WHEN question ILIKE '%Product 2: Choose the Products%' THEN response END) AS product_2_name,
    SUM(CASE WHEN question ILIKE '%Q-FF2%' THEN CAST(response AS INTEGER) ELSE 0 END) AS product_2_score,

    -- Product 3
    MAX(CASE WHEN question ILIKE '%Product 3: Choose the Products%' THEN response END) AS product_3_name,
    SUM(CASE WHEN question ILIKE '%Q-FF3%' THEN CAST(response AS INTEGER) ELSE 0 END) AS product_3_score,

    -- Product 4
    MAX(CASE WHEN question ILIKE '%Product 4- Choose the Products%' THEN response END) AS product_4_name,
    SUM(CASE WHEN question ILIKE '%Q-FF4%' THEN CAST(response AS INTEGER) ELSE 0 END) AS product_4_score

  FROM raw
  GROUP BY sno
)

SELECT 
  sno, "Audited Location", "Store Code", "BU", "RBU", "District", "Area",
  product_1_name AS "Product",
  product_1_score AS "Score",
  CASE 
    WHEN product_1_score = 0 THEN 'Conformance'
    ELSE 'Non-Conformance'
  END AS "Conformance Status"
FROM product_questions
WHERE product_1_name IS NOT NULL

UNION ALL

SELECT 
  sno, "Audited Location", "Store Code", "BU", "RBU", "District", "Area",
  product_2_name, product_2_score,
  CASE 
    WHEN product_2_score = 0 THEN 'Conformance'
    ELSE 'Non-Conformance'
  END
FROM product_questions
WHERE product_2_name IS NOT NULL

UNION ALL

SELECT 
  sno, "Audited Location", "Store Code", "BU", "RBU", "District", "Area",
  product_3_name, product_3_score,
  CASE 
    WHEN product_3_score = 0 THEN 'Conformance'
    ELSE 'Non-Conformance'
  END
FROM product_questions
WHERE product_3_name IS NOT NULL

UNION ALL

SELECT 
  sno, "Audited Location", "Store Code", "BU", "RBU", "District", "Area",
  product_4_name, product_4_score,
  CASE 
    WHEN product_4_score = 0 THEN 'Conformance'
    ELSE 'Non-Conformance'
  END
FROM product_questions
WHERE product_4_name IS NOT NULL
```

---
