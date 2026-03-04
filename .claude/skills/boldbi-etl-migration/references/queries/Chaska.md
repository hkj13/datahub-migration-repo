# Chaska

> Auto-generated on 2026-03-04 08:13

**Total queries:** 1

---

## Chaska Inventory Log_Inventory Log.sql

**Tables referenced:** RAW, amount, cat, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, metadata, nuggets, organizations, qd, qty, question_definitions, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Chaska Inventory Log
-- Dashboard: Inventory Log
-- Category: Chaska
-- Extracted: 2026-01-29 16:57:51
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'chaska-phoenix'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-OBao1ddvC5aLNzo1uHh',
                '-O4corz2S_36HajLXPPV',
                '-O4K5dBQmDQTAahXAavs',
                '-O4JjdQD6Qd15F0lhJYP')
   GROUP BY 1,
            2),
     qd AS
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
   WHERE question_type NOT IN ('table')
   ORDER BY 1,
            2,
            3),
     cat AS
  (SELECT form_knid, q_no,
          question AS name
   FROM qd
   WHERE q_type = 'title_description'),
     final_definition AS
  (SELECT qd.*,

     COALESCE((SELECT cat.name
      FROM cat
      WHERE cat. q_no < qd.q_no
	  and cat.form_knid = qd.form_knid
      ORDER BY cat.q_no DESC
      LIMIT 1), 'Other') AS category
   FROM qd
   WHERE qd.q_type != 'title_description'
   ORDER BY 1,
            2,
            3),
     fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   JOIN td ON form_submissions.organization = td.organization
   WHERE (form_submissions.submit_date + td.diff) BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP
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
          fd.category,
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
   LEFT OUTER JOIN fr ON fr.qid = fd.qid
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
            3), metadata AS
  (SELECT response_id,
          submit_date AS "Date",
          response AS "Location",
          sno AS "Submission No",
          form_name AS "Supplier"
   FROM RAW
   WHERE question = 'Location'
   GROUP BY 1,
            2,
            3,
            4,
            5),
                qty AS
  (SELECT response_id,
          category AS "Category",
          split_part(question, ' | ', 1) AS "Item",
          replace(split_part(question, ' | ', 2), 'UOM: ', '') AS "UOM",
          response::numeric AS "Qty"
   FROM RAW
   WHERE q_type = 'single_text_field'
     AND question ILIKE '%UOM%'
   GROUP BY 1,
            2,
            3,
            4,
            5),
                amount AS
  (SELECT response_id,
          category AS "Category",
          split_part(question, ' | ', 1) AS "Item",
          replace(split_part(question, ' | ', 2), 'UOM: ', '') AS "UOM",
          response::numeric AS "Amount"
   FROM RAW
   WHERE q_type = 'formula'
     AND question ILIKE '%UOM%'
   GROUP BY 1,
            2,
            3,
            4,
            5)
SELECT metadata.*,
       qty."Category",
       qty."Item",
       qty."UOM",
       qty."Qty",
	   case when qty."Qty" > 0 then round(amount."Amount"/qty."Qty", 1) else null end as "Cost",
       amount."Amount"	   
FROM metadata
JOIN qty ON metadata.response_id = qty.response_id
JOIN amount ON amount.response_id = metadata.response_id
AND amount."Category" = qty."Category"
AND amount."Item" = qty."Item"
AND amount."UOM" = qty."UOM"
ORDER BY 3,
         2,
         5,
         6,
         7
```

---
