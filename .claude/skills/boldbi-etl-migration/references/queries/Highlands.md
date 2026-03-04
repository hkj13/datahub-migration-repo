# Highlands

> Auto-generated on 2026-03-04 08:13

**Total queries:** 4

---

## HIGHLANDS FOOD SAFETY AUDIT- Fireworks_OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT -.sql

**Tables referenced:** final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: HIGHLANDS FOOD SAFETY AUDIT- Fireworks
-- Dashboard: OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT -
-- Category: Highlands
-- Extracted: 2026-01-29 16:52:53
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'highlands-coffee-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.title ilike '%OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT%'
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
   CROSS JOIN jsonb_each(qd.q) def
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
            id ASC),
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
          fr.parent_qid,
          fr.qid,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit',
                                 'user') THEN fr.response -> 'selected'->>0
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
            13,
            14,
            15
   ORDER BY 1,
            2,
            3) 
SELECT
    sno,
    submit_date,

    -- BASE RESPONSES (safe casting inside aggregates)
    MAX(CASE WHEN parent_question = 'Audited Location' THEN response END) AS "Audited Location",

    ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "1. Finished Food (4 products)",

    ( MAX(CASE WHEN parent_question = '2.  Production Process'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "2. Production Process",

    ( MAX(CASE WHEN parent_question = '3.Service'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "3.Service",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Service Rating",

    ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "4. Cleanliness & Condition",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Cleanliness and Condition Rating",

    ( MAX(CASE WHEN parent_question = '5. Food Safety'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "5. Food Safety",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Food Safety Rating",

    ( MAX(CASE WHEN parent_question = 'Total Score'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "Total Score",

    (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) AS "Total Food Score",
	
	CASE
    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 0 AND 5 THEN 'A – High'

    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 6 AND 15 THEN 'B – Medium'

    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 16 AND 20 THEN 'C – Low'
	
	 WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) > 20 THEN 'D – Critical'

    ELSE NULL
END AS "Total Food Rating",


    CASE
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 0 AND 5 THEN 'A – High'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 6 AND 15 THEN 'B – Medium'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 16 AND 20 THEN 'C – Low'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int > 20 THEN 'D – Critical'
        ELSE NULL
    END AS "Rating",

    CASE
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 0 AND 5 THEN 'High'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 6 AND 15 THEN 'Medium'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 16 AND 20 THEN 'Low'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int > 20 THEN 'Critical'
        ELSE NULL
    END AS "Risk Level",

    -- === New: non-compliance counts by severity (safe numeric checks)
    -- Use response numeric check: CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END

    -- Major total
    SUM(
      CASE
        WHEN q_type <> 'title_description'
         AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
         AND question ~* 'MAJOR'
         AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC'
               OR question ~ '^[0-9]+\.'
             )
       THEN 1 ELSE 0
      END
    ) AS "Major_NC_Total",

    -- Major per section
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Major_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Major_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Major_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Major_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Major_NC_FoodSafety",

    -- Minor total
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC' OR question ~ '^[0-9]+\.'
             ) THEN 1 ELSE 0 END) AS "Minor_NC_Total",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Minor_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Minor_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Minor_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Minor_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Minor_NC_FoodSafety",

    -- Critical total
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC' OR question ~ '^[0-9]+\.'
             ) THEN 1 ELSE 0 END) AS "Critical_NC_Total",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Critical_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Critical_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Critical_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Critical_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Critical_NC_FoodSafety"

FROM raw
where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
GROUP BY 1,2
ORDER BY submit_date DESC, sno
```

---

## HIGHLANDS FOOD SAFETY AUDIT_OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT.sql

**Tables referenced:** final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: HIGHLANDS FOOD SAFETY AUDIT
-- Dashboard: OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT
-- Category: Highlands
-- Extracted: 2026-01-29 16:53:00
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'highlands-coffee-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.title ilike '%OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT%'
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
   CROSS JOIN jsonb_each(qd.q) def
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
            id ASC),
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
          fr.parent_qid,
          fr.qid,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit',
                                 'user') THEN fr.response -> 'selected'->>0
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
            13,
            14,
            15
   ORDER BY 1,
            2,
            3) 
SELECT
    sno,
    submit_date,

    -- BASE RESPONSES (safe casting inside aggregates)
    MAX(CASE WHEN parent_question = 'Audited Location' THEN response END) AS "Audited Location",

    ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "1. Finished Food (4 products)",

    ( MAX(CASE WHEN parent_question = '2.  Production Process'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "2. Production Process",

    ( MAX(CASE WHEN parent_question = '3.Service'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "3.Service",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '3.Service'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Service Rating",

    ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "4. Cleanliness & Condition",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '4. Cleanliness & Condition'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Cleanliness and Condition Rating",

    ( MAX(CASE WHEN parent_question = '5. Food Safety'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "5. Food Safety",
	
	CASE
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 0 AND 5 THEN 'A – High'
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 6 AND 15 THEN 'B – Medium'
		     WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int BETWEEN 16 AND 20 THEN 'C – Low'
    WHEN ( MAX(CASE WHEN parent_question = '5. Food Safety'
             THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
         )::int > 20 THEN 'D – Critical'
END AS "Food Safety Rating",

    ( MAX(CASE WHEN parent_question = 'Total Score'
        THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
    )::int AS "Total Score",

    (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) AS "Total Food Score",
	
	CASE
    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 0 AND 5 THEN 'A – High'

    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 6 AND 15 THEN 'B – Medium'

    WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) BETWEEN 16 AND 20 THEN 'C – Low'
	
	 WHEN (
        COALESCE(
          ( MAX(CASE WHEN parent_question = '1. Finished Food (4 products)'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
        +
        COALESCE(
          ( MAX(CASE WHEN parent_question = '2.  Production Process'
              THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
          )::int, 0
        )
    ) > 20 THEN 'D – Critical'

    ELSE NULL
END AS "Total Food Rating",


    CASE
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 0 AND 5 THEN 'A – High'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 6 AND 15 THEN 'B – Medium'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 16 AND 20 THEN 'C – Low'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int > 20 THEN 'D – Critical'
        ELSE NULL
    END AS "Rating",

    CASE
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 0 AND 5 THEN 'High'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 6 AND 15 THEN 'Medium'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int BETWEEN 16 AND 20 THEN 'Low'
        WHEN ( MAX(CASE WHEN parent_question = 'Total Score'
                 THEN CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response ELSE '0' END END)
             )::int > 20 THEN 'Critical'
        ELSE NULL
    END AS "Risk Level",

    -- === New: non-compliance counts by severity (safe numeric checks)
    -- Use response numeric check: CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END

    -- Major total
    SUM(
      CASE
        WHEN q_type <> 'title_description'
         AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
         AND question ~* 'MAJOR'
         AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC'
               OR question ~ '^[0-9]+\.'
             )
       THEN 1 ELSE 0
      END
    ) AS "Major_NC_Total",

    -- Major per section
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Major_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Major_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Major_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Major_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MAJOR' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Major_NC_FoodSafety",

    -- Minor total
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC' OR question ~ '^[0-9]+\.'
             ) THEN 1 ELSE 0 END) AS "Minor_NC_Total",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Minor_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Minor_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Minor_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Minor_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'MINOR' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Minor_NC_FoodSafety",

    -- Critical total
    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND (
               question ~* '^FF-' OR question ~* '^PP-' OR question ~* '^S-' OR question ~* '^CC' OR question ~ '^[0-9]+\.'
             ) THEN 1 ELSE 0 END) AS "Critical_NC_Total",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^FF-' THEN 1 ELSE 0 END) AS "Critical_NC_FinishedFood",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^PP-' THEN 1 ELSE 0 END) AS "Critical_NC_ProductionProcess",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^S-' THEN 1 ELSE 0 END) AS "Critical_NC_Service",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND question ~* '^CC' THEN 1 ELSE 0 END) AS "Critical_NC_Cleanliness",

    SUM(CASE WHEN q_type <> 'title_description'
             AND (CASE WHEN response ~ '^\s*-?\d+\s*$' THEN response::int ELSE 0 END) > 0
             AND question ~* 'CRITICAL' AND (question ~ '^[0-9]+\.' OR parent_question = '5. Food Safety') THEN 1 ELSE 0 END) AS "Critical_NC_FoodSafety"

FROM raw
where submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
GROUP BY 1,2
ORDER BY submit_date DESC, sno
```

---

## Highlands Food Safety Remarks Fireworks_OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT -.sql

**Tables referenced:** audited_loc, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, questions, raw, remarks, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Highlands Food Safety Remarks Fireworks
-- Dashboard: OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT -
-- Category: Highlands
-- Extracted: 2026-01-29 16:52:48
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'highlands-coffee-fireworks'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.title ilike '%OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT%'
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
   CROSS JOIN jsonb_each(qd.q) def
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
            id ASC),
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
          fr.parent_qid,
          fr.qid,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit',
                                 'user') THEN fr.response -> 'selected'->>0
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
            13,
            14,
            15
   ORDER BY 1,
            2,
            3),
questions AS (
    SELECT DISTINCT
        sno,
        submit_date,
        form_id,
        parent_qid,
        parent_question,
        -- Extract Code: after (SEVERITY): or (SEVERITY) :
        regexp_replace(parent_question,
            '^\s*\([^)]+\)\s*:\s*([A-Za-z0-9.]+)\s*[,:]?\s*.*$', '\1'
        ) AS code,
        -- Extract Requirement: the quoted or non-quoted text after code
        regexp_replace(parent_question,
            '^\s*\([^)]+\)\s*:\s*[A-Za-z0-9.]+\s*[,:]?\s*["""]?(.+?)["""]?\s*$', '\1'
        ) AS requirement,
        CASE
            WHEN parent_question ILIKE '%CRITICAL%' THEN 'Critical'
            WHEN parent_question ILIKE '%MAJOR%'    THEN 'Major'
            WHEN parent_question ILIKE '%MINOR%'    THEN 'Minor'
            ELSE NULL
        END AS risk
    FROM raw
    WHERE parent_question IS NOT NULL
      AND parent_question ~ '^\s*\([^)]+\)\s*:'   -- Match (SEVERITY): pattern
),

-- 2. Extract REMARKS (actual typed responses)
remarks AS (
    SELECT
        sno,
        form_id,
        parent_qid,
        response AS remarks
    FROM raw
    WHERE q_type = 'long_text_field'      
      AND question ILIKE '%remark%'       
      AND response IS NOT NULL
      AND trim(response) <> ''
),

-- 3. Audited Location
audited_loc AS (
    SELECT
        sno,
        submit_date,
        MAX(response) AS audited_location
    FROM raw
    WHERE parent_question = 'Audited Location'
    GROUP BY 1,2
)

-- FINAL SELECT
SELECT
    q.sno AS "SNO",
    al.audited_location AS "Audited Location",
    q.submit_date AS "Submit Date",

    q.code        AS "Code",
    q.requirement AS "Requirement",
    q.risk        AS "Risk",
    r.remarks     AS "Remarks"

FROM questions q
LEFT JOIN remarks r 
    ON q.sno = r.sno
   AND q.parent_qid = r.parent_qid
LEFT JOIN audited_loc al
    ON q.sno = al.sno
   AND q.submit_date = al.submit_date

ORDER BY q.sno, q.code
```

---

## Highlands Food Safety Remarks_OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT.sql

**Tables referenced:** audited_loc, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, questions, raw, remarks, td

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Highlands Food Safety Remarks
-- Dashboard: OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT
-- Category: Highlands
-- Extracted: 2026-01-29 16:53:18
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'highlands-coffee-cartwheel'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.title ilike '%OPERATIONAL EXCELLENCE AND FOOD SAFETY AUDIT%'
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
   CROSS JOIN jsonb_each(qd.q) def
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
            id ASC),
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
          fr.parent_qid,
          fr.qid,
          q_type,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale',
                                 'audit',
                                 'user') THEN fr.response -> 'selected'->>0
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
            13,
            14,
            15
   ORDER BY 1,
            2,
            3),
questions AS (
    SELECT DISTINCT
        sno,
        submit_date,
        form_id,
        parent_qid,
        parent_question,

        -- Extract Code (FF1A, FF-1A, CC1B, S1C, PP2A...)
        regexp_replace(parent_question,
            '^\s*([A-Za-z]{1,3}-?\d+[A-Za-z]?)\b.*$', '\1'
        ) AS code,

        -- Extract Requirement (English only)
        trim(
            regexp_replace(
                regexp_replace(
                    parent_question,
                    '^\s*[A-Za-z]{1,3}-?\d+[A-Za-z]?\s*[,:\-–—]\s*',
                    '',
                    'i'
                ),
                '\s*(CRITICAL|MAJOR|MINOR)\b.*$', ''
            )
        ) AS requirement,

        CASE
            WHEN parent_question ILIKE '%CRITICAL%' THEN 'Critical'
            WHEN parent_question ILIKE '%MAJOR%'    THEN 'Major'
            WHEN parent_question ILIKE '%MINOR%'    THEN 'Minor'
            ELSE NULL
        END AS risk
    FROM raw
    WHERE parent_question IS NOT NULL
      AND parent_question ~* '^[A-Za-z]{1,3}-?\d+'  
),

-- 2. Extract REMARKS (actual typed responses)
remarks AS (
    SELECT
        sno,
        form_id,
        parent_qid,
        response AS remarks
    FROM raw
    WHERE q_type = 'single_text_field'
      AND question ILIKE 'remarks'
      AND response IS NOT NULL
      AND trim(response) <> ''
),

-- 3. Audited Location
audited_loc AS (
    SELECT
        sno,
        submit_date,
        MAX(response) AS audited_location
    FROM raw
    WHERE parent_question = 'Audited Location'
    GROUP BY 1,2
)

-- FINAL SELECT
SELECT
    q.sno AS "SNO",
    al.audited_location AS "Audited Location",
    q.submit_date AS "Submit Date",

    q.code        AS "Code",
    q.requirement AS "Requirement",
    q.risk        AS "Risk",
    r.remarks     AS "Remarks"

FROM questions q
LEFT JOIN remarks r 
    ON q.sno = r.sno
   AND q.parent_qid = r.parent_qid
LEFT JOIN audited_loc al
    ON q.sno = al.sno
   AND q.submit_date = al.submit_date

ORDER BY q.sno, q.code
```

---
