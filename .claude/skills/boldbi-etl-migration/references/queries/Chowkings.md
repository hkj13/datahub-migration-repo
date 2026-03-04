# Chowkings

> Auto-generated on 2026-03-04 08:13

**Total queries:** 7

---

## Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413-copy_1744271895-copy_1744272660_Equipment - Temp Reading.sql

**Tables referenced:** chowkings_responses

**Original Query:**

```sql
-- Data Source: Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413-copy_1744271895-copy_1744272660
-- Dashboard: Equipment - Temp Reading
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:34
-- ============================================================

SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Checklist 1" AS "Checklist 1"
FROM(select *,regexp_replace( "Checklist", '\s*\(.*$', '', 'g') AS "Checklist 1"
from chowkings_responses
 WHERE question IN (
    'Marinated Split Vat (no standard)',
    'Marinated Full Vat (no standard)',
    'Dimsum Vat (no standard)',
    'Pao Cabinet',
    'Overhead Warmer',
    'Baine Marie',
    'Noodle Boiler',
    'Soup Boiler',
    'Beef Warmer - Server',
    'Beef Warmer - Toastmaster'
)
and "Submitted At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY "Reminded Hour")"QueryTable 1"
```

---

## Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413-copy_1744271895_Equipment Calibration.sql

**Tables referenced:** chowkings_responses

**Original Query:**

```sql
-- Data Source: Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413-copy_1744271895
-- Dashboard: Equipment Calibration
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:35
-- ============================================================

SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Checklist 1" AS "Checklist 1",
		"QueryTable 1"."product" AS "product"
FROM(select *,regexp_replace("Checklist", '\s*\(.*$', '', 'g') AS "Checklist 1",
CASE
  WHEN question LIKE 'Did the Induction Woks passed the water boil test%' THEN 'Induction Wok'
  WHEN question LIKE 'Did the Short Order Range passed the water boil test%' THEN 'Short Order Range'
  WHEN question LIKE 'Is Ice Shaver Machine calibrated%' THEN 'Ice Shaver Machine'
  WHEN question = 'Is the Low Pressure Burner calibrated?' THEN 'Low Pressure Burner'
  WHEN question = 'Is the oil in gold standard quality?' THEN 'Cooking Oil'
  WHEN question LIKE 'Is the Rice and Dimsum Steamer calibrated%' THEN 'Rice and Dimsum Steamer'
  ELSE NULL
END AS product
from chowkings_responses
 WHERE question IN (
    'Did the Induction Woks passed the water boil test? (Note: Water Boil Test - 1 L of boiling within 2 mins - 2:20mins',
    'Did the Short Order Range passed the water boil test? (Note: 1 L of boiling within 1:30mins - 2:30mins)',
    'Is Ice Shaver Machine calibrated? (Note: "Shaved Ice" Weight - not more than 300kg Appearance - snow white flakes Texture - Fine to medium; no presence of ice beads)',
    'Is the Low Pressure Burner calibrated?',
    'Is the oil in gold standard quality?',
    'Is the Rice and Dimsum Steamer calibrated? (Note: Eqpt Readiness Indicator: - No steam coming out of the sides of the door - Water is at the Correct Level (Ready Light Indicator is ON) - Flame of Burner must be BLUE - Cabinet temp should reach 95 deg C within 30 mins pre-heating)'
) and "Submitted At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY "Reminded Hour")"QueryTable 1"
```

---

## Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413_Cold Storage.sql

**Tables referenced:** chowkings_responses

**Original Query:**

```sql
-- Data Source: Chowking_Insights-copy_1744266984-copy_1744269006-copy_1744270413
-- Dashboard: Cold Storage
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:33
-- ============================================================

SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Checklist 1" AS "Checklist 1",
		"QueryTable 1"."product_name" AS "product_name",
		"QueryTable 1"."Freezer Lower" AS "Freezer Lower",
		"QueryTable 1"."Freezer Upper" AS "Freezer Upper"
FROM(select *,regexp_replace("Checklist", '\s*\(.*$', '', 'g') AS "Checklist 1",
CASE
  WHEN question = 'Walk-in Freezer' THEN 'Walk-in Freezer'
  WHEN question = 'Walk-in Chiller' THEN 'Walk-in Chiller'
  WHEN question = 'Reach-in Freezer' THEN 'Reach-in Freezer'
  WHEN question = 'Reach-in Chiller' THEN 'Reach-in Chiller'
  WHEN question = 'Stir Fry' THEN 'Undercounter Stir Fry'
  WHEN question = 'Noodles' THEN 'Undercounter Noodles'
  WHEN question = 'Ice Cream Freezer' THEN 'Ice Cream Freezer'
  ELSE NULL
END AS product_name,
-22 AS "Freezer Lower",
  -20 AS "Freezer Upper"
from chowkings_responses
WHERE question IN (
  'Walk-in Freezer',
  'Walk-in Chiller',
  'Reach-in Freezer',
  'Reach-in Chiller',
  'Stir Fry',
'Noodles',
  'Ice Cream Freezer'
)
and "Submitted At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY "Reminded Hour")"QueryTable 1"
```

---

## Chowking_Insights-copy_1744266984-copy_1744269006_Product Temp Reading.sql

**Tables referenced:** chowkings_responses

**Original Query:**

```sql
-- Data Source: Chowking_Insights-copy_1744266984-copy_1744269006
-- Dashboard: Product Temp Reading
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:33
-- ============================================================

SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Shift" AS "Shift",
		"QueryTable 1"."Checklist 1" AS "Checklist 1",
		"QueryTable 1"."product" AS "product"
FROM(select *,regexp_replace("Checklist", '\s*\(.*$', '', 'g') AS "Checklist 1",
CASE
  WHEN question = 'Final Cooked Temperature of Pork Chao Fan' THEN 'Pork Chao Fan'
  WHEN question = 'Final Cooked Temperature of Chinese Style Fried Chicken' THEN 'Chinese Style Fried Chicken'
  WHEN question = 'Chicken Asado Siopao' THEN 'Asado Siopao'
  ELSE NULL
END AS product
from chowkings_responses
WHERE question IN (
  'Final Cooked Temperature of Pork Chao Fan',
  'Final Cooked Temperature of Chinese Style Fried Chicken',
  'Chicken Asado Siopao'
)
and "Submitted At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY "Reminded Hour")"QueryTable 1"
```

---

## Chowking_Insights-copy_1744266984_GSC Score.sql

**Tables referenced:** chowkings_responses

**Original Query:**

```sql
-- Data Source: Chowking_Insights-copy_1744266984
-- Dashboard: GSC Score
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:35
-- ============================================================

SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Shift" AS "Shift"
FROM(select *
from chowkings_responses
WHERE question = 'Is Pork Chao Fan in Gold Standard Quality?'
and "Submitted At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
ORDER BY "Reminded Hour")"QueryTable 1"
```

---

## Chowking_Insights_Store Insights Dashboard.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, metadata, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, store_map, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Chowking_Insights
-- Dashboard: Store Insights Dashboard
-- Category: Chowkings
-- Extracted: 2026-01-29 16:56:20
-- ============================================================

 SELECT
		"QueryTable 1"."Checklist" AS "Checklist",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Submission No" AS "Submission No",
		"QueryTable 1"."Submitted At" AS "Submitted At",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."question" AS "question",
		"QueryTable 1"."Value" AS "Value",
		"QueryTable 1"."Status" AS "Status"
FROM(WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'chowking-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-OLDG2b3j2vehmUyLROw',
                '-OL7OgdeHH4gVZbsud2b',
                '-OL7PJslPa9Z0bC9W_Lm',
                '-OINqYP4VYGc5LUasNGh',
                '-OIP40nDaMosFGL_V71D',
                '-OIP5MpunaV1hxQizk-L',
                '-OIP5gWTaJm1WR_XCn3j',
                '-OHaiweC9EPrNP-BjRQS',
                '-OKyChx9CKnQlKQsGk3u')
     AND organization = 'chowking-cartwheel'
     AND is_deleted = FALSE
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
   WHERE question_type NOT IN ('table') ),
     qdntwl_prework AS
  (SELECT *,
          jsonb_array_elements(definition -> 'logic') -> 'questions' q
   FROM forms
   JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
   WHERE qd.definition -> 'logic' IS NOT NULL ),
     qd_non_table_with_logic AS
  (SELECT nugget_id AS form_knid,
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
   WHERE definition ->>'logic' IS NOT NULL ),
     qd_table AS
  (SELECT nugget_id AS form_knid,
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
   WHERE qd.question_type IN ('table') ),
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
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date BETWEEN '2025-04-28'::TIMESTAMP AND '2025-05-04'::TIMESTAMP + interval '1 day' ),
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
          LOCATION
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
                LOCATION
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
             LOCATION
      FROM form_responses fr
      JOIN fs ON fs.id = fr.form_submit_id
      JOIN td ON fs.organization = td.organization,
                 jsonb_array_elements(response) WITH
      ORDINALITY AS base
      WHERE question_type = 'table' ) base1
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
                                 'audit') THEN fr.response -> 'selected' ->> 0
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
                                 'formula') THEN fr.response ->> 0
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
          fr.location,
          fr.user_id,
          ud.division,
          ud.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   LEFT JOIN user_details ud ON fr.user_id = ud.uuid
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
            17
   ORDER BY 1,
            2,
            3), metadata AS
  (SELECT form_name AS "Checklist",
          response_id AS "Submission KNID",
          sno AS "Submission No",
          submit_date AS "Submitted At",
          max(CASE
                  WHEN q_type = 'location' THEN response
                  ELSE NULL
              END) AS "Store"
   FROM RAW
   GROUP BY 1,
            2,
            3,
            4),
                store_map AS
  (SELECT DISTINCT ON (job_location) job_location AS "Store",
                      division AS "RBU",
                      substring(sub_division, position('.' IN sub_division)-1, 1) AS "District",
                      substring(sub_division, position('.' IN sub_division)+1, 1) AS "Area"
   FROM user_details
   WHERE organization = 'chowking-cartwheel'
     AND is_active = 'true'
   ORDER BY job_location,
            created_at DESC)
SELECT md.*,
       store_map."RBU",
       store_map."District",
       store_map."Area",
       question,
       CASE
           WHEN question IN ('Baine Marie',
                             'Final Cooked Temperature of Chinese Style Fried Chicken',
                             'Final Cooked Temperature of Pork Chao Fan',
                             'Ice Cream Freezer',
                             'Input display temperature of fryer',
                             'Noodle Boiler',
                             'Overhead Warmer',
                             'Pao Cabinet',
                             'Reach-in Chiller',
                             'Reach-in Freezer',
                             'Soup Boiler',
                             'Walk-in Chiller',
                             'Walk-in Freezer',
                             'What is your actual profit for the day?',
                             'What is your actual sales for the day?') THEN response::numeric
           ELSE NULL
       END AS "Value",
       CASE
           WHEN question = 'Final Cooked Temperature of Pork Chao Fan'
                AND response::numeric BETWEEN 75 AND 80 THEN 'Yes'
           WHEN question = 'Final Cooked Temperature of Chinese Style Fried Chicken'
                AND response::numeric BETWEEN 90 AND 95 THEN 'Yes'
           WHEN question = 'Final cooked temp of Asado Siopao'
                AND response::numeric BETWEEN 80 AND 85 THEN 'Yes'
           WHEN question = 'Walk-in Freezer'
                AND response::numeric BETWEEN -20 AND -15 THEN 'Yes'
           WHEN question = 'Walk-in Chiller'
                AND response::numeric BETWEEN 2 AND 4 THEN 'Yes'
           WHEN question = 'Reach-in Freezer'
                AND response::numeric BETWEEN -20 AND -15 THEN 'Yes'
           WHEN question = 'Reach-in Chiller'
                AND response::numeric BETWEEN 2 AND 4 THEN 'Yes'
           WHEN question = 'Undercounter Refrigerator'
                AND response::numeric BETWEEN 0 AND 4 THEN 'Yes'
           WHEN question = 'Undercounter Refrigerator'
                AND response::numeric BETWEEN 0 AND 4 THEN 'Yes'
           WHEN question = 'Undercounter Refrigerator'
                AND response::numeric BETWEEN 0 AND 4 THEN 'Yes'
           WHEN question = 'Undercounter Refrigerator'
                AND response::numeric BETWEEN 0 AND 4 THEN 'Yes'
           WHEN question = 'Ice Cream Freezer'
                AND response::numeric BETWEEN -22 AND -20 THEN 'Yes'
           WHEN question = 'Pao Cabinet'
                AND response::numeric BETWEEN 80 AND 85 THEN 'Yes'
           WHEN question = 'Overhead Warmer'
                AND response::numeric BETWEEN 40 AND 60 THEN 'Yes'
           WHEN question = 'Baine Marie'
                AND response::numeric BETWEEN 92 AND 95 THEN 'Yes'
           WHEN question = 'Noodle Boiler'
                AND response::numeric BETWEEN 98 AND 100 THEN 'Yes'
           WHEN question = 'Soup Boiler'
                AND response::numeric BETWEEN 90 AND 95 THEN 'Yes'
           WHEN question = 'Beef Warmer - Server'
                AND response::numeric BETWEEN 70 AND 75 THEN 'Yes'
           WHEN question = 'Beef Warmer - Toastmaster'
                AND response::numeric BETWEEN 93 AND 97 THEN 'Yes'
           WHEN question IN ('Did the Induction Woks passed the water boil test? (Note: Water Boil Test - 1 L of boiling within 2 mins - 2:20mins',
                             'Did the Short Order Range passed the water boil test? (Note: 1 L of boiling within 1:30mins - 2:30mins)',
                             'Is Ice Shaver Machine calibrated? (Note: "Shaved Ice" Weight - not more than 300kg Appearance - snow white flakes Texture - Fine to medium; no presence of ice beads)',
                             'Is Pork Chao Fan in Gold Standard Quality?',
                             'Is the Low Pressure Burner calibrated?',
                             'Is the oil in gold standard quality?',
                             'Is the Rice and Dimsum Steamer calibrated? (Note: Eqpt Readiness Indicator: - No steam coming out of the sides of the door - Water is at the Correct Level (Ready Light Indicator is ON) - Flame of Burner must be BLUE - Cabinet temp should reach 95 deg C within 30 mins pre-heating)') THEN response
           WHEN question IN ('Input display temperature of fryer',
                             'What is your actual sales for the day?',
                             'What is your actual profit for the day?') THEN 'N/A'
           ELSE 'No'
       END AS "Status"
FROM RAW
JOIN metadata md ON raw.response_id = md."Submission KNID"
JOIN store_map ON md."Store" = store_map."Store"
WHERE question IN ('Baine Marie',
                   'Did the Induction Woks passed the water boil test? (Note: Water Boil Test - 1 L of boiling within 2 mins - 2:20mins',
                   'Did the Short Order Range passed the water boil test? (Note: 1 L of boiling within 1:30mins - 2:30mins)',
                   'Final Cooked Temperature of Chinese Style Fried Chicken',
                   'Final Cooked Temperature of Pork Chao Fan',
                   'Ice Cream Freezer',
                   'Input display temperature of fryer',
                   'Is Ice Shaver Machine calibrated? (Note: "Shaved Ice" Weight - not more than 300kg Appearance - snow white flakes Texture - Fine to medium; no presence of ice beads)',
                   'Is Pork Chao Fan in Gold Standard Quality?',
                   'Is the Low Pressure Burner calibrated?',
                   'Is the oil in gold standard quality?',
                   'Is the Rice and Dimsum Steamer calibrated? (Note: Eqpt Readiness Indicator: - No steam coming out of the sides of the door - Water is at the Correct Level (Ready Light Indicator is ON) - Flame of Burner must be BLUE - Cabinet temp should reach 95 deg C within 30 mins pre-heating)',
                   'Noodle Boiler',
                   'Overhead Warmer',
                   'Pao Cabinet',
                   'Reach-in Chiller',
                   'Reach-in Freezer',
                   'Soup Boiler',
                   'Walk-in Chiller',
                   'Walk-in Freezer',
                   'What is your actual profit for the day?',
                   'What is your actual sales for the day?')
				   ORDER BY 1, 6, 7, 8, 5, 4, 3, 9)"QueryTable 1"
```

---

## Routine_Routine Compliance.sql

**Tables referenced:** form_compliance_v2, organizations, store_map, user_details

**Original Query:**

```sql
-- Data Source: Routine
-- Dashboard: Routine Compliance
-- Category: Chowkings
-- Extracted: 2026-01-29 16:55:32
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Store" AS "Store",
		"QueryTable 1"."RBU" AS "RBU",
		"QueryTable 1"."District" AS "District",
		"QueryTable 1"."Area" AS "Area",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Reminded Hour" AS "Reminded Hour",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID",
		"QueryTable 1"."Routine #" AS "Routine #",
		"QueryTable 1"."Date Mod" AS "Date Mod"
FROM(WITH 
  store_map AS (
    SELECT DISTINCT ON (job_location) 
           job_location AS "Store",
           division AS "RBU",
           substring(sub_division, position('.' IN sub_division)-1, 1) AS "District",
           substring(sub_division, position('.' IN sub_division)+1, 1) AS "Area"
    FROM user_details
    WHERE organization = 'chowking-cartwheel'
      AND is_active = 'true'
	AND division NOT LIKE '%KNOW%' AND division NOT LIKE '%HQ%'
	AND sub_division NOT LIKE '%K%'
	and sub_division IS NOT NULL
	and job_location NOT like '%HEAD OFFICE%'
    ORDER BY job_location, created_at DESC
  ),
  
  td AS (
    SELECT id AS organization, interval '1 min' * tzoffset AS diff 
    FROM organizations 
    WHERE id = 'chowking-cartwheel'
  )

SELECT
    "QueryTable 1"."Organization" AS "Organization",
    "QueryTable 1"."Date" AS "Date",
    "QueryTable 1"."Routine KNID" AS "Routine KNID",
    regexp_replace( "QueryTable 1"."Routine Name", '\s*\(.*$', '', 'g') AS "Routine Name",
    "QueryTable 1"."Location" AS "Location",
    store_map."Store",
    store_map."RBU",
    store_map."District",
    store_map."Area",
    "QueryTable 1"."Reminded At" AS "Reminded At",
	EXTRACT(HOUR FROM "QueryTable 1"."Reminded At") AS "Reminded Hour",
    "QueryTable 1"."Responded At" AS "Responded At",
    "QueryTable 1"."Compliance" AS "Compliance",
    "QueryTable 1"."Submission KNID" AS "Submission KNID",
    "QueryTable 1"."Routine #" AS "Routine #",
    "QueryTable 1"."Date Mod" AS "Date Mod"
FROM (
    SELECT fc.*, 
           to_char("Date", 'YYYY-MM-DD') AS "Date Mod"
    FROM form_compliance_v2 fc
    WHERE fc."Organization" = 'chowking-cartwheel'
      AND fc."Reminded At" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
    ORDER BY 1, 5, 2 DESC, 6 DESC, 4
) "QueryTable 1"
 JOIN store_map ON "QueryTable 1"."Location" = store_map."Store"
 WHERE "RBU" NOT LIKE '%KNOW%' AND "RBU" NOT LIKE '%HQ%'
 and "District" IS NOT NULL
  and "Area" IS NOT NULL
AND "Area" NOT LIKE 'K'
ORDER BY "Reminded Hour", store_map."Store"

)"QueryTable 1"
```

---
