# Grain

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Grain - Hygiene_Hygiene Dashboard.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Grain - Hygiene
-- Dashboard: Hygiene Dashboard
-- Category: Grain
-- Extracted: 2026-01-29 16:54:38
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'grain-cartwheel'
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
   WHERE id = 'grain-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id in ('-NmjPpEBE5Nn14Ep4dBI',
'-NmjQ21biv0OlgIGLLDB',
'-NmjPO7h8df3etWY1O-g',
'-NmjP8CUPyrxxoRcMx05',
'-NmjOsU3ey_L0tt61bNT',
'-NmjOch_D4M7QCJf3FZ5',
'-Nmi5oUwrsdRyKum5qaY',
'-Nmi6yB0dRufWMpXB7FX',
'-Nmi7pEamEsbhJWVcMBY',
'-Nmi8CJLbQMJF7B0kt1t',
'-Nmi8xD2tHqGpRh03rDP',
'-Nmi9P_iDSGiIiHU2puG')
     AND organization = 'grain-cartwheel'
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
                                 'upload_video',
								'upload_file') THEN (fr.response)->0->>'response'
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
         ud.first_name || ud.last_name as "Form Submitter" 
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN user_details ud on fr.user_id = ud.uuid
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
   14,15
   ORDER BY 1,
            2,
            3)
SELECT form_name,sno,"Form Submitter",
submit_date, location,MAX(CASE WHEN question = 'Area Hygiene Check' THEN response END) AS "Area Hygiene Check",
  MAX(CASE WHEN question = 'Personal Hygiene Check' THEN response END) AS "Personal Hygiene Check",
  MAX(CASE WHEN question = 'Staff Name' THEN response END) AS "Staff Name",
MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Lighting, ventilation/exhaust system are in good working order%' THEN 'Yes' ELSE 'No' END) AS "Lighting & Ventilation",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Cleaning chem icals are properly labelled%' THEN 'Yes' ELSE 'No' END) AS "Chemicals Labelled",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Food preparation sinks and ware washing areas are clean%' THEN 'Yes' ELSE 'No' END) AS "Prep & Washing Clean",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Floor is clean and dry%' THEN 'Yes' ELSE 'No' END) AS "Floor Clean",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%No sign of infestation%' THEN 'Yes' ELSE 'No' END) AS "No Infestation",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Adequate number of covered pedal bins%' THEN 'Yes' ELSE 'No' END) AS "Pedal Bins Available",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Handwashing facilities are easily accessible%' THEN 'Yes' ELSE 'No' END) AS "Handwashing Facilities",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Walls are clean, windows are closed%' THEN 'Yes' ELSE 'No' END) AS "Walls/Windows Clean",
  MAX(CASE WHEN question = 'Area Hygiene Check' AND response ILIKE '%Equipment, crockery and utensils are clean%' THEN 'Yes' ELSE 'No' END) AS "Equipment Clean",

  -- Personal Hygiene options
  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%Hands are properly washed%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "Hands Properly Washed",

  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%Fingernails are short%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "Fingernails Short",

  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%Production attire is complete%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "Proper Production Attire",

  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%Hair is kept tidy%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "Hair Covered",

  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%Health status is in good%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "Good Health",

  MAX(CASE 
      WHEN question = 'Personal Hygiene Check' AND response ILIKE '%No jewellery is worn%' 
      THEN 'Yes' ELSE 'No' 
  END) AS "No Jewellery",
  MAX(CASE WHEN question = 'Upload photos of the area' THEN response END) AS "Upload photos of the area",
  MAX(CASE WHEN question = 'Remarks about area cleanliness' THEN response END) AS "Remarks about area cleanliness",
  MAX(CASE WHEN question = 'Remarks on personal hygiene' THEN response END) AS "Remarks on personal hygiene",
  MAX(CASE WHEN question = 'Upload photos of personal hygiene' THEN response END) AS "Upload photos of personal hygiene"
FROM raw
WHERE 
    raw.question not LIKE '%Chiller Temperature%' 
    and raw.question not LIKE '%Freezer Temperature%'
    and raw.question not LIKE '%Warmer Temperature%'
	and raw.question not LIKE '%Signature%'
	GROUP BY 1,2,3,4,5
```

---

## Grain Temp_Temp Log.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Grain Temp
-- Dashboard: Temp Log
-- Category: Grain
-- Extracted: 2026-01-29 16:54:30
-- ============================================================

WITH location_acl AS (
  SELECT DISTINCT job_location
  FROM user_details
  WHERE organization = 'grain-cartwheel'
    AND is_active = 'true'
    AND job_location NOT IN ('KNOW', 'HQ', 'Head Office', 'All')
    AND job_location NOT ILIKE 'Head Office%'
    AND (
      (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
      OR uuid IN (
        SELECT DISTINCT user_id
        FROM user_groups ug1
        WHERE ug1.group_id IN (
          SELECT group_id
          FROM user_groups ug2
          WHERE ug2.user_id = @{{:UuidParameter}}
            AND ug2.has_access = TRUE
        )
        AND ug1.is_active = TRUE
      )
    )
),
forms AS (
  SELECT id AS form_knid, title AS form_name
  FROM nuggets n
  WHERE (title ILIKE '%Pre-Ops Checklist%' OR title ILIKE '%Post-Ops Checklist%')
    AND organization = 'grain-cartwheel'
    AND is_deleted = false
  GROUP BY 1, 2
),
qd_non_table_non_logic AS (
  SELECT nugget_id AS form_knid,
         form_name,
         CASE WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer END AS section_no,
         CASE WHEN qd.question_type = 'section' THEN 0
              ELSE sqno::integer * 10000 END AS q_no,
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
  SELECT *, jsonb_array_elements(definition -> 'logic') -> 'questions' q
  FROM forms
  JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
  WHERE qd.definition -> 'logic' IS NOT NULL
),
qd_non_table_with_logic AS (
  SELECT nugget_id AS form_knid,
         form_name,
         CASE WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer END AS section_no,
         sqno::integer * 10000 + (def.value ->> 'order')::integer AS q_no,
         section_id,
         question_id AS parent_qid,
         question_type AS parent_q_type,
         question AS parent_question,
         def.key AS qid,
         def.value ->> 'question_type' AS q_type,
         def.value ->> 'question' AS question
  FROM qdntwl_prework qd
  CROSS JOIN jsonb_each(qd.q) def
  WHERE definition ->> 'logic' IS NOT NULL
),
qd_table AS (
  SELECT nugget_id AS form_knid,
         form_name,
         CASE WHEN qd.section_id = 'section' THEN 1
              ELSE replace(section_id, 'section-', '')::integer END AS section_no,
         sqno::integer * 10000 + (def.value ->> 'order')::integer AS q_no,
         section_id,
         question_id AS parent_qid,
         question_type AS parent_q_type,
         question AS parent_question,
         def.key AS qid,
         def.value ->> 'question_type' AS q_type,
         def.value ->> 'question' AS question
  FROM forms
  JOIN question_definitions qd ON forms.form_knid = qd.nugget_id
  CROSS JOIN jsonb_each(definition -> 'questions') def
  WHERE qd.question_type IN ('table')
),
final_definition AS (
  SELECT * FROM qd_non_table_non_logic
  UNION SELECT * FROM qd_non_table_with_logic
  UNION SELECT * FROM qd_table
  ORDER BY 1, 2, 3, 5 DESC, 7 DESC
),
_fs AS (
  SELECT DISTINCT ON (response_id) form_submissions.*, form_name
  FROM forms
  JOIN form_submissions ON forms.form_knid = form_submissions.form_id
  ORDER BY response_id, id DESC
),
fs AS (
  SELECT *
  FROM _fs
  WHERE submit_date AT TIME ZONE 'Asia/Singapore' BETWEEN @{{:Date Range.START}}::timestamp
    AND @{{:Date Range.END}}::timestamp + interval '1 day'
),
fr AS (
  SELECT fs.organization,
         form_submit_id,
         form_id,
         form_name,
         sno,
         (submit_date AT TIME ZONE 'Asia/Singapore') AS submit_date,
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
  WHERE question_type NOT IN ('table', 'nested')

  UNION

  SELECT organization,
         form_submit_id,
         form_id,
         form_name,
         sno,
         (submit_date AT TIME ZONE 'Asia/Singapore') AS submit_date,
         user_id,
         response_id,
         question_id AS parent_qid,
         res.key AS qid,
         question_type,
         res.value AS response,
         rn,
         location
  FROM (
    SELECT fs.organization,
           form_submit_id,
           form_id,
           form_name,
           sno,
           (submit_date AT TIME ZONE 'Asia/Singapore') AS submit_date,
           user_id,
           response_id,
           question_id,
           question_type,
           base.value,
           base.ordinality AS rn,
           location
    FROM form_responses fr
    JOIN fs ON fs.id = fr.form_submit_id,
         jsonb_array_elements(response) WITH ORDINALITY AS base
    WHERE question_type = 'table'
  ) base1
  CROSS JOIN jsonb_each(base1.value) res
),
RAW AS (
  SELECT fr.sno,
         fd.section_no,
         fd.q_no,
         fd.parent_question,
         fd.question,
         q_type,
         CASE
             WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
             WHEN fd.q_type IN ('dropdown','multiple_choice','linear_scale','audit') THEN fr.response -> 'selected' ->> 0
             WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY(
                 SELECT jsonb_array_elements_text(fr.response -> 'selected')
                 UNION
                 SELECT CASE WHEN fr.response ->> 'otherText' IS NOT NULL THEN fr.response ->> 'otherText' ELSE NULL END
             ), ', ')
             WHEN fd.q_type IN ('date','datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Singapore', 'YYYY-MM-DD HH24:MI:SS')
             WHEN fd.q_type IN ('long_text_field','single_text_field','qr_code','formula') THEN fr.response ->> 0
             WHEN fd.q_type IN ('user') THEN fr.response::text
             WHEN fd.q_type IN ('upload_mixed','upload_image','upload_video') THEN (fr.response) -> 0 ->> 'response'
             WHEN fd.q_type IN ('signature','location','division','sub_division') THEN fr.response ->> 'name'
             ELSE NULL
         END AS response,
         CASE WHEN fd.q_type = 'section' THEN fr.response ELSE NULL END AS section_response,
         rn,
         fr.form_name,
         fr.form_id,
         fr.response_id,
         fr.submit_date,
         fr.location
  FROM final_definition fd
  JOIN fr ON fr.qid = fd.qid AND fr.form_id = fd.form_knid
  JOIN location_acl ON fr.location = location_acl.job_location
  GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14
  ORDER BY 1,2,3
)
SELECT form_name,
       sno,
       submit_date,
       location,
       CASE
           WHEN raw.question LIKE '%Chiller Temperature%' THEN 'Chiller'
           WHEN raw.question LIKE '%Freezer Temperature%' THEN 'Freezer'
           WHEN raw.question LIKE '%Warmer Temperature%' THEN 'Warmer'
       END AS equipment_type,
       raw.question AS equipment_no,
       response::numeric AS reading,
       CASE
           WHEN LOWER(question) LIKE '%chiller%' AND CAST(response AS FLOAT) BETWEEN 0 AND 4 THEN 'In Range'
           WHEN LOWER(question) LIKE '%freezer%' AND CAST(response AS FLOAT) <= -18 THEN 'In Range'
           WHEN LOWER(question) LIKE '%warmer%' AND CAST(response AS FLOAT) >= 70 THEN 'In Range'
           ELSE 'Out of Range'
       END AS reading_status,
       CASE
           WHEN LOWER(form_name) LIKE '%pre%' THEN 'Pre'
           WHEN LOWER(form_name) LIKE '%post%' THEN 'Post'
           ELSE 'Unknown'
       END AS recording_type
FROM RAW
WHERE raw.question LIKE '%Chiller Temperature%'
   OR raw.question LIKE '%Freezer Temperature%'
   OR raw.question LIKE '%Warmer Temperature%'
```

---
