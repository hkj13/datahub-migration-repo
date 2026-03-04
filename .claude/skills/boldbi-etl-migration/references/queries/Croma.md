# Croma

> Auto-generated on 2026-03-04 08:13

**Total queries:** 52

---

## ASMRSM Compliance_ASMRSM dashboard.sql

**Tables referenced:** compliance_flat, form_responses, form_submissions, forms, locations, nuggets, question_definitions, role_holders, roles, roles_mapping, store_roles, store_submissions, user_details

**Original Query:**

```sql
-- Data Source: ASMRSM Compliance
-- Dashboard: ASMRSM dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:21
-- ============================================================

WITH roles_mapping AS (
    SELECT 
        l.id AS store_id,
        l.location_name AS store_name,
        MAX(CASE WHEN r.name = 'ASM' THEN ud.first_name || ' ' || ud.last_name END) AS asm_name,
        MAX(CASE WHEN r.name = 'RSM' THEN ud.first_name || ' ' || ud.last_name END) AS rsm_name,
        MAX(CASE WHEN r.name = 'Zonal Manager' THEN ud.first_name || ' ' || ud.last_name END) AS zm_name,
        MAX(CASE WHEN r.name = 'Cluster Manager' THEN ud.first_name || ' ' || ud.last_name END) AS cm_name,
        MAX(ud.division) AS division
    FROM locations l
    LEFT JOIN role_holders rh 
        ON rh.location_id = l.id AND rh.is_active = TRUE
    LEFT JOIN roles r 
        ON r.id = rh.role_id 
       AND r.name IN ('ASM', 'RSM', 'Zonal Manager', 'Cluster Manager')
    LEFT JOIN user_details ud 
        ON ud.uuid = rh.role_holder_id AND ud.is_active = TRUE
    WHERE l.organization = 'croma-coma' 
      AND l.is_active = TRUE
    GROUP BY l.id, l.location_name
),

forms AS (
    SELECT id AS form_id
    FROM nuggets
    WHERE organization = 'croma-coma'
      AND is_deleted = FALSE
      AND title ILIKE '%OL ASM Checklist%'
),

store_submissions AS (
    SELECT DISTINCT
        COALESCE(l.id, NULL) AS store_id,
        date_trunc('month', fs.submit_date at time zone 'Asia/Kolkata')::date AS month_start
    FROM form_submissions fs
    JOIN forms f ON f.form_id = fs.form_id
    JOIN form_responses fr ON fr.form_submit_id = fs.id
    JOIN question_definitions qd
      ON qd.nugget_id = f.form_id
     AND LOWER(qd.question) LIKE '%store code%'
    LEFT JOIN locations l
      ON l.id::text = fr.response ->> 'id'
      OR l.location_name = fr.response ->> 'name'
    WHERE l.organization = 'croma-coma'
      AND fs.submit_date BETWEEN CAST(@{{:ASMRSM Dashboard.Date Range.START}} AS date)
                       AND CAST(@{{:ASMRSM Dashboard.Date Range.END}} AS date) + INTERVAL '1 day'
),

-- Map each store to its ASM, RSM, ZM, CM, and Division
store_roles AS (
    SELECT 
        rm.store_id,
        rm.store_name AS location,
        rm.asm_name AS asm,
        rm.rsm_name AS rsm,
        rm.zm_name AS zm,
        rm.cm_name AS cm,
        rm.division
    FROM roles_mapping rm
    WHERE rm.asm_name IS NOT NULL 
       OR rm.rsm_name IS NOT NULL
       OR rm.zm_name IS NOT NULL
       OR rm.cm_name IS NOT NULL
),

-- Combine with submissions to mark compliance
compliance_flat AS (
    SELECT 
        sr.store_id,
        sr.location,
        sr.asm,
        sr.rsm,
        sr.zm,
        sr.cm,
        sr.division,
        m.month_start,
        CASE WHEN ss.store_id IS NOT NULL THEN 1 ELSE 0 END AS compliant
    FROM store_roles sr
    CROSS JOIN (
        SELECT DISTINCT date_trunc('month', submit_date)::date AS month_start
        FROM form_submissions
        WHERE form_id IN (SELECT form_id FROM forms)
          AND submit_date BETWEEN CAST(@{{:ASMRSM Dashboard.Date Range.START}} AS date)
                       AND CAST(@{{:ASMRSM Dashboard.Date Range.END}} AS date) + INTERVAL '1 day'
    ) m
    LEFT JOIN store_submissions ss
      ON ss.store_id = sr.store_id
     AND ss.month_start = m.month_start
)

SELECT 
    TO_CHAR(month_start, 'YYYY-MM') AS month,
    division,
    rsm AS "RSM",
    asm AS "ASM",
    zm  AS "ZM",
    cm  AS "CM",
    location AS store,
    compliant
FROM compliance_flat
ORDER BY month_start DESC, division, rsm, asm, zm, cm, location
```

---

## ASMRSM Dashboard Questions_ASMRSM dashboard.sql

**Tables referenced:** FINAL, FINAL_DEDUP, RAW, ROLES, _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, task_responses, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: ASMRSM Dashboard Questions
-- Dashboard: ASMRSM dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:09
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:ASMRSM Dashboard.UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:ASMRSM Dashboard.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:ASMRSM Dashboard.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:ASMRSM Dashboard.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('ASM',
                  'Zonal Manager',
                  'RSM')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'croma-coma'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'ASM' THEN holder
              END) AS "ASM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'RSM' THEN holder
              END) AS "RSM"
   FROM lr
   GROUP BY store_id,
            store_name),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('%OL ASM Checklist%')
     AND organization = 'croma-coma'
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
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date BETWEEN @{{:ASMRSM Dashboard.Date Range.START}}::TIMESTAMP AND @{{:ASMRSM Dashboard.Date Range.END}}::TIMESTAMP + interval '1 day' ),
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
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as ( select distinct on (nugget_id) nugget_id, question_id from question_definitions qd where nugget_id in (select form_knid from forms) and question_type = 'location' order by nugget_id, section_id, sqno ), location_response as ( select form_submit_id, (response ->> 'name')::text location_name from form_responses fr where question_id in (select question_id from location_questions) and form_submit_id in (select id from fs) ),*/ RAW AS
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
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            3),  FINAL AS (
    SELECT 
        submit_date,
        form_name,
        sno,
        first_name AS "Submitter",
        department,
        MAX(CASE WHEN question = 'Store code' THEN response END) AS store,
        MAX(CASE WHEN question = 'Check the ticket price for any 5 random products' THEN response END) AS "Ticket Price",
        MAX(CASE WHEN question = 'Is the Bill Buster offer execution completed?' THEN response END) AS "Bill Buster",
        MAX(CASE WHEN question = 'Is the Quick Pick execution completed?' THEN response END) AS "Quick Pick",
        MAX(CASE WHEN question = 'Is the Dump Bin execution completed?' THEN response END) AS "Dump Bin",
        MAX(CASE WHEN question = 'Is the Bulk Stack execution completed?' THEN response END) AS "Bulk Stack",
        MAX(CASE WHEN question = 'Is the End Cap execution completed?' THEN response END) AS "End Cap",
        MAX(CASE WHEN question = 'Are all offer color posters executed on the shopfloor?' THEN response END) AS "Offer Poster",
        MAX(CASE WHEN question = 'Are all newly launched SKUs displayed with the correct ticket?' THEN response END) AS "Correct Ticket",
        MAX(CASE WHEN question = 'Upload an image of the Cookware Fixture' THEN response END) AS "Cookware Fixture",
        MAX(CASE WHEN question = 'Upload an image of the TV Wall Fixture' THEN response END) AS "TV Wall Fixture",
        MAX(CASE WHEN question = 'Are active ranges of OL ACs displayed with relevant family tickets?' THEN response END) AS "OL AC",
        MAX(CASE WHEN question = 'Are all active ranges of OL Washing Machines displayed with relevant family tickets?' THEN response END) AS "OL Washing Machine",
        MAX(CASE WHEN question = 'Are all active ranges of OL Microwaves displayed?' THEN response END) AS "OL Microwave",
        MAX(CASE WHEN question = 'Are all active ranges of OL LEDs displayed with relevant family ticketing?' THEN response END) AS "OL LEDs",
        MAX(CASE WHEN question = 'Are all active ranges of JMGs, Sandwich Makers, Toasters, and Food Processors displayed?' THEN response END) AS "Food Processors",
        MAX(CASE WHEN question = 'Are Water Purifiers, Cookware, and Foot & Leg Massagers displayed in prominent locations?' THEN response END) AS "Water Purifiers",
        MAX(CASE WHEN question = 'Are all audio products charged and live?' THEN response END) AS "Audio Products",
        MAX(CASE WHEN question = 'Are all the POSM for products executed?' THEN response END) AS "POSM",
	 MAX(CASE WHEN question = 'Are all active ranges of OL Refrigerators displayed with relevant family tickets?' THEN response END) AS "Refrigerator"
    FROM RAW
    GROUP BY 
        submit_date,
        sno,
        first_name,
        department,
        form_name
),
FINAL_DEDUP AS (
    SELECT *
    FROM (
        SELECT
            f.*,
            ROW_NUMBER() OVER (
                PARTITION BY
                    f.store,
                    DATE(f.submit_date)
                ORDER BY
                    f.submit_date DESC
            ) AS rn
        FROM FINAL f
    ) x
    WHERE rn = 1
),

task_responses AS (
    SELECT 'Ticket Price' AS task, LOWER("Ticket Price") AS response
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Bill Buster', LOWER("Bill Buster")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Quick Pick', LOWER("Quick Pick")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Dump Bin', LOWER("Dump Bin")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Bulk Stack', LOWER("Bulk Stack")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'End Cap', LOWER("End Cap")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Offer Posters', LOWER("Offer Poster")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'New Launch Ticket Display', LOWER("Correct Ticket")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Cookware Fixture', LOWER("Cookware Fixture")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'TV Wall Fixture', LOWER("TV Wall Fixture")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'OL AC Display', LOWER("OL AC")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'OL Washing Machine', LOWER("OL Washing Machine")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'OL Microwave', LOWER("OL Microwave")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'OL LEDs', LOWER("OL LEDs")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Food Preperation Range Display', LOWER("Food Processors")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Water Purifiers, Cookware & Massagers Range', LOWER("Water Purifiers")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'Audio Products', LOWER("Audio Products")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 'POSM', LOWER("POSM")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
      UNION ALL
    SELECT 'Refrigerator', LOWER("Refrigerator")
    FROM FINAL_DEDUP f
JOIN acl a ON f.store = a.store
)

SELECT 
    task,
    ROUND(100.0 * COUNT(CASE WHEN response = 'yes' THEN 1 END) / COUNT(*), 0) AS "Yes",
    ROUND(100.0 * COUNT(CASE WHEN response = 'no' THEN 1 END) / COUNT(*), 0) AS "No",
    ROUND(100.0 * COUNT(CASE WHEN response = 'na' THEN 1 END) / COUNT(*), 0) AS "N/A"
FROM task_responses
GROUP BY task
ORDER BY
    CASE task
        WHEN 'Ticket Price' THEN 1
        WHEN 'Bill Buster' THEN 2
        WHEN 'Quick Pick' THEN 3
        WHEN 'Dump Bin' THEN 4
        WHEN 'Bulk Stack' THEN 5
        WHEN 'End Cap' THEN 6
        WHEN 'Offer Posters' THEN 7
        WHEN 'New Launch Ticket Display' THEN 8
        WHEN 'Cookware Fixture' THEN 9
        WHEN 'TV Wall Fixture' THEN 10
        WHEN 'OL AC Display' THEN 11
        WHEN 'OL Washing Machine' THEN 12
        WHEN 'OL Microwave' THEN 13
        WHEN 'OL LEDs' THEN 14
        WHEN 'Food Preperation Range Display' THEN 15
        WHEN 'Water Purifiers, Cookware & Massagers Range' THEN 16
        WHEN 'Audio Products' THEN 17
        WHEN 'POSM' THEN 18
        WHEN 'Refrigerator' THEN 19
    END
```

---

## ASMRSM Dashboard_ASMRSM dashboard.sql

**Tables referenced:** FINAL, FINAL_DEDUP, RAW, ROLES, _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, location_questions, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: ASMRSM Dashboard
-- Dashboard: ASMRSM dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:10
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l), lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('ASM',
                  'Zonal Manager',
                  'RSM')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'croma-coma'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'ASM' THEN holder
              END) AS "ASM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'RSM' THEN holder
              END) AS "RSM"
   FROM lr
   GROUP BY store_id,
            store_name),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('%OL ASM Checklist%')
     AND organization = 'croma-coma'
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
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'),
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
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
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
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            3), FINAL AS
  (SELECT submit_date,
          form_name,
          sno,
          first_name AS "Submitter",
          department,
          MAX(CASE
                  WHEN question = 'Store code' THEN response
              END) AS store,
          MAX(CASE
                  WHEN question = 'Check the ticket price for any 5 random products' THEN response
              END) AS "Ticket Price",
          MAX(CASE
                  WHEN question = 'Is the Bill Buster offer execution completed?' THEN response
              END) AS "Bill Buster",
          MAX(CASE
                  WHEN question = 'Is the Quick Pick execution completed?' THEN response
              END) AS "Quick Pick",
          MAX(CASE
                  WHEN question = 'Is the Dump Bin execution completed?' THEN response
              END) AS "Dump Bin",
          MAX(CASE
                  WHEN question = 'Is the Bulk Stack execution completed?' THEN response
              END) AS "Bulk Stack",
          MAX(CASE
                  WHEN question = 'Is the End Cap execution completed?' THEN response
              END) AS "End Cap",
          MAX(CASE
                  WHEN question = 'Are all offer color posters executed on the shopfloor?' THEN response
              END) AS "Offer Poster",
          MAX(CASE
                  WHEN question = 'Are all newly launched SKUs displayed with the correct ticket?' THEN response
              END) AS "New Launch Ticket Display",
              MAX(CASE
                  WHEN question = 'Upload an image of the Cookware Fixture' THEN response
              END) AS "Cookware Fixture",
              MAX(CASE
                  WHEN question = 'Upload an image of the TV Wall Fixture' THEN response
              END) AS "TV Wall Fixture",
               MAX(CASE
                  WHEN question = 'Are active ranges of OL ACs displayed with relevant family tickets?' THEN response
              END) AS "OL AC", 
                MAX(CASE
                  WHEN question = 'Are all active ranges of OL Washing Machines displayed with relevant family tickets?' THEN response
              END) AS "OL Washing Machine", 
               MAX(CASE
                  WHEN question = 'Are all active ranges of OL Microwaves displayed?' THEN response
              END) AS "OL Microwave",
              MAX(CASE
                  WHEN question = 'Are all active ranges of OL LEDs displayed with relevant family ticketing?' THEN response
              END) AS "OL LEDs",
              MAX(CASE
                  WHEN question = 'Are all active ranges of JMGs, Sandwich Makers, Toasters, and Food Processors displayed?' THEN response
              END) AS "Food Preparation Range Display",
              MAX(CASE
                  WHEN question = 'Are Water Purifiers, Cookware, and Foot & Leg Massagers displayed in prominent locations?' THEN response
              END) AS "Water Purifiers, Cookware & Massagers Range Display",
              MAX(CASE
                  WHEN question = 'Are all audio products charged and live?' THEN response
              END) AS "Audio Products",
              MAX(CASE
                  WHEN question = 'Are all the POSM for products executed?' THEN response
              END) AS "POSM",
   MAX(CASE
                  WHEN question = 'Are all active ranges of OL Refrigerators displayed with relevant family tickets?' THEN response
              END) AS "Refrigerator"

   FROM RAW
   GROUP BY submit_date,
            sno,
            first_name,
            department,
            form_name),
			FINAL_DEDUP AS (
    SELECT *
    FROM (
        SELECT
            f.*,
            ROW_NUMBER() OVER (
                PARTITION BY
                    f.store,
                    DATE(f.submit_date)
                ORDER BY
                    f.submit_date DESC
            ) AS rn
        FROM FINAL f
    ) x
    WHERE x.rn = 1
)
SELECT
    f.submit_date,
    f.form_name,
    f.sno,
    f."Submitter",
    f.department,
    f.store,

    lm.store_id,
    lm.store_name,
    lm."ZM",
    lm."ASM",
    lm."RSM",

    f."Ticket Price",
    f."Bill Buster",
    f."Quick Pick",
    f."Dump Bin",
    f."Bulk Stack",
    f."End Cap",
    f."Offer Poster",
    f."New Launch Ticket Display",
    f."Cookware Fixture",
    f."TV Wall Fixture",
    f."OL AC",
    f."OL Washing Machine",
    f."OL Microwave",
    f."OL LEDs",
    f."Food Preparation Range Display",
    f."Water Purifiers, Cookware & Massagers Range Display",
    f."Audio Products",
    f."POSM",
	f."Refrigerator",

    -- Count Yes responses (all relevant columns)
    (
      (CASE WHEN LOWER(f."Ticket Price") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bill Buster") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Quick Pick") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Dump Bin") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bulk Stack") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."End Cap") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Offer Poster") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."New Launch Ticket Display") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Cookware Fixture") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."TV Wall Fixture") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL AC") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Washing Machine") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Microwave") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL LEDs") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Food Preparation Range Display") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Audio Products") = 'yes' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."POSM") = 'yes' THEN 1 ELSE 0 END)+
	  (CASE WHEN LOWER(f."Refrigerator") = 'yes' THEN 1 ELSE 0 END)
    ) AS yes_count,

    -- Count No responses
    (
      (CASE WHEN LOWER(f."Ticket Price") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bill Buster") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Quick Pick") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Dump Bin") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bulk Stack") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."End Cap") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Offer Poster") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."New Launch Ticket Display") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Cookware Fixture") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."TV Wall Fixture") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL AC") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Washing Machine") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Microwave") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL LEDs") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Food Preparation Range Display") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Audio Products") = 'no' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."POSM") = 'no' THEN 1 ELSE 0 END) +
	  (CASE WHEN LOWER(f."Refrigerator") = 'no' THEN 1 ELSE 0 END)
    ) AS no_count,

    -- Count NA responses
    (
      (CASE WHEN LOWER(f."Ticket Price") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bill Buster") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Quick Pick") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Dump Bin") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Bulk Stack") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."End Cap") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Offer Poster") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."New Launch Ticket Display") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Cookware Fixture") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."TV Wall Fixture") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL AC") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Washing Machine") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL Microwave") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."OL LEDs") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Food Preparation Range Display") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."Audio Products") = 'na' THEN 1 ELSE 0 END) +
      (CASE WHEN LOWER(f."POSM") = 'na' THEN 1 ELSE 0 END) +
	        (CASE WHEN LOWER(f."Refrigerator") = 'na' THEN 1 ELSE 0 END)
    ) AS na_count,

    -- pct_yes
    ROUND(
      100.0 *
      (
        (CASE WHEN LOWER(f."Ticket Price") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bill Buster") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Quick Pick") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Dump Bin") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bulk Stack") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."End Cap") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Offer Poster") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."New Launch Ticket Display") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Cookware Fixture") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."TV Wall Fixture") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL AC") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Washing Machine") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Microwave") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL LEDs") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Food Preparation Range Display") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Audio Products") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."POSM") = 'yes' THEN 1 ELSE 0 END) +
		(CASE WHEN LOWER(f."Refrigerator") = 'yes' THEN 1 ELSE 0 END)
      )::numeric
      /
      NULLIF(
        (
          (CASE WHEN LOWER(f."Ticket Price") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bill Buster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Quick Pick") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Dump Bin") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bulk Stack") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."End Cap") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Offer Poster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."New Launch Ticket Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Cookware Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."TV Wall Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL AC") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Washing Machine") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Microwave") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL LEDs") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Food Preparation Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Audio Products") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."POSM") IN ('yes','no','na') THEN 1 ELSE 0 END) +
		            (CASE WHEN LOWER(f."Refrigerator") IN ('yes','no','na') THEN 1 ELSE 0 END)
        )::numeric
      , 0)
    , 2) AS pct_yes,

    -- pct_no
    ROUND(
      100.0 *
      (
        (CASE WHEN LOWER(f."Ticket Price") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bill Buster") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Quick Pick") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Dump Bin") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bulk Stack") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."End Cap") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Offer Poster") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."New Launch Ticket Display") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Cookware Fixture") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."TV Wall Fixture") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL AC") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Washing Machine") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Microwave") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL LEDs") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Food Preparation Range Display") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Audio Products") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."POSM") = 'no' THEN 1 ELSE 0 END) +
		        (CASE WHEN LOWER(f."Refrigerator") = 'no' THEN 1 ELSE 0 END)
      )::numeric
      /
      NULLIF(
        (
          (CASE WHEN LOWER(f."Ticket Price") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bill Buster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Quick Pick") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Dump Bin") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bulk Stack") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."End Cap") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Offer Poster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."New Launch Ticket Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Cookware Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."TV Wall Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL AC") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Washing Machine") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Microwave") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL LEDs") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Food Preparation Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Audio Products") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."POSM") IN ('yes','no','na') THEN 1 ELSE 0 END) +
		            (CASE WHEN LOWER(f."Refrigerator") IN ('yes','no','na') THEN 1 ELSE 0 END)
        )::numeric
      , 0)
    , 2) AS pct_no,

    -- pct_na
    ROUND(
      100.0 *
      (
        (CASE WHEN LOWER(f."Ticket Price") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bill Buster") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Quick Pick") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Dump Bin") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Bulk Stack") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."End Cap") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Offer Poster") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."New Launch Ticket Display") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Cookware Fixture") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."TV Wall Fixture") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL AC") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Washing Machine") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL Microwave") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."OL LEDs") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Food Preparation Range Display") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."Audio Products") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f."POSM") = 'na' THEN 1 ELSE 0 END) +
		        (CASE WHEN LOWER(f."Refrigerator") = 'na' THEN 1 ELSE 0 END)
      )::numeric
      /
      NULLIF(
        (
          (CASE WHEN LOWER(f."Ticket Price") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bill Buster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Quick Pick") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Dump Bin") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Bulk Stack") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."End Cap") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Offer Poster") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."New Launch Ticket Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Cookware Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."TV Wall Fixture") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL AC") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Washing Machine") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL Microwave") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."OL LEDs") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Food Preparation Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Water Purifiers, Cookware & Massagers Range Display") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."Audio Products") IN ('yes','no','na') THEN 1 ELSE 0 END) +
          (CASE WHEN LOWER(f."POSM") IN ('yes','no','na') THEN 1 ELSE 0 END) +
		            (CASE WHEN LOWER(f."Refrigerator") IN ('yes','no','na') THEN 1 ELSE 0 END)
        )::numeric
      , 0)
    , 2) AS pct_na

FROM FINAL_DEDUP f
JOIN acl ON f.store = acl.store
LEFT JOIN lm ON lm.store_name = RIGHT(f.store, LENGTH(f.store) - 5)
```

---

## Croma - Roster and Attendance_Roster and Attendance.sql

**Tables referenced:** JOIN, ROLES, acl, brands, lm, locations, lr, role_holders, s, shift_attendance, tags, user_details, user_groups, user_tags

**Original Query:**

```sql
-- Data Source: Croma - Roster and Attendance
-- Dashboard: Roster and Attendance
-- Category: Croma
-- Extracted: 2026-01-29 16:52:40
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT acl.store,
          right(l.location_name, length(l.location_name)-5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store = l.location_name
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Head',
                  'Zonal Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   and rh.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store,
          lr.store_name,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1,
            2
   ORDER BY 1),
     s AS (
    SELECT DISTINCT ON (shift_id) shift_id,
        leave_type_id,
        to_date(shift_day, 'YYYYMMDD') AS "Date",
        user_id,
        lm."CM",
        lm."ZM",
        l.location_name,
        start_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' AS start_time,
        end_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' AS end_time,
        break_time,
        is_deleted,
        ud.first_name||' '||ud.last_name AS "Employee Name",
        ud.identifier AS "Employee ID",
        ud.division AS "State",
        ud.sub_division AS "City",
        ud.job_location AS "Home Location",
        ud.department AS "Department",
        ud.designation AS "Designation",
        ud.job_type AS "Employee Type"
    FROM "shifts_croma-coma" s
    JOIN user_details ud ON s.user_id = ud.uuid
    JOIN locations l ON s.location_id = l.id
    LEFT JOIN lm ON l.location_name = lm.store  -- Changed from JOIN to LEFT JOIN
    JOIN acl ON l.location_name = acl.store     -- Keep ACL filtering for access control
    WHERE is_planning = 'false'
    AND is_leave_request = 'false'
    AND to_date(shift_day, 'YYYYMMDD') BETWEEN @{{:Date Range.START}}::date AND @{{:Date Range.END}}::date + interval '1 day'
    ORDER BY s.shift_id, s.created_at DESC),
			brands as (SELECT ut.user_id,
       string_agg(t.tag, ',') as brand
FROM user_tags ut
JOIN tags t ON ut.tag_id = t.id
WHERE t.tag_key = 'brand'
  AND ut.is_active = 'true'
GROUP BY 1)
SELECT s.shift_id,
       s."Date",
       s.user_id AS "Employee KNID",
       s.location_name AS "Shift Location",
       s."Employee Name",
       s."Employee ID",
	   "CM",
   "ZM",
       s."State",
       s."City",
       s."Home Location",
       s."Department",
       s."Designation",
       s."Employee Type",
	   brands.brand as "Brand",
	   s.start_time AS "Scheduled Start Time",
       s.end_time AS "Scheduled End Time",
       s.break_time::numeric/60 AS "Scheduled Break Hours",
       a."Status",
       a."Actual Clockin Time" AT TIME ZONE 'Asia/Kolkata' AS "First Clockin Time",
                                            a."Actual Clockout Time" AT TIME ZONE 'Asia/Kolkata' AS "Last Clockout Time",
                                                                                  a."Clockin Geofence" AS "Clockin Location",
                                                                                  a."Clockout Geofence" AS "Clockout Location",
                                                                                  a."Actual Break Hours",
                                                                                  a."Actual Work Duration"
FROM s
LEFT OUTER JOIN shift_attendance a ON s.shift_id = a."Shift ID"
left outer join brands on s.user_id  = brands.user_id
WHERE s.is_deleted = 'false'
order by 2, 4, 12, 11, 5, 13
```

---

## Croma - User login status_User login status.sql

**Tables referenced:** analytics_requests, logged_in, user_details

**Original Query:**

```sql
-- Data Source: Croma - User login status
-- Dashboard: User login status
-- Category: Croma
-- Extracted: 2026-01-29 16:57:14
-- ============================================================

WITH logged_in AS (
    SELECT distinct user_id
    FROM analytics_requests
    WHERE organization = 'croma-coma'
      AND event_id > 1
)
SELECT
    user_details.first_name || ' ' || user_details.last_name AS "Name",
    user_details.phone_number AS "Phone Number",
    user_details.identifier AS "Emp ID",
	split_part(user_details.job_location, '-', 1) AS "Location",
    user_details.designation as "Designation",
    CASE
        WHEN logged_in.user_id is null THEN 'Not logged In'
        ELSE 'Logged in'
    END AS "Login Status"
FROM user_details
left join logged_in on user_details.uuid = logged_in.user_id
WHERE organization = 'croma-coma'
  AND is_active = true
  AND (email is null or email not ilike '%knownuggets%')
ORDER BY
    "Location",
    "Name",
    "Phone Number"
```

---

## Croma Announcements New_Croma Announcements.sql

**Tables referenced:** acl, croma.croma_announcements, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Announcements New
-- Dashboard: Croma Announcements
-- Category: Croma
-- Extracted: 2026-01-29 16:54:03
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store_id
  FROM (
    -- Direct user role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    WHERE rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
		OR l.location_name ILIKE '%ZO%'
      )

    UNION

    -- Group role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND role_holder_type = 'group'
      AND ug.is_active = TRUE
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
		OR l.location_name ILIKE '%ZO%'
      )

    UNION

    -- Job location
    SELECT job_location AS store_id
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = TRUE
      AND (
        substring(job_location FROM 2 FOR 3) ~ '^\d{3}$'
        OR job_location ILIKE '%SO%'
        OR job_location ILIKE '%DC%'
		OR job_location ILIKE '%ZO%'
      )
      AND (
        (SELECT is_super_admin
         FROM user_details
         WHERE uuid = @{{:UuidParameter}})
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
  ) l
)
select *
from croma.croma_announcements
JOIN acl on croma_announcements.location = acl.store_id
where "Communication Type" IS NOT NULL
```

---

## Croma Audit Tasks_Croma Audits.sql

**Tables referenced:** ACL, analytics_requests, assignees, checkpoint_master_sheet_table, form_submissions, lm, locations, lr, role_holders, roles, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Audit Tasks
-- Dashboard: Croma Audits
-- Category: Croma
-- Extracted: 2026-01-29 16:55:50
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:Croma Audits Summary.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:Croma Audits Summary.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:Croma Audits Summary.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:Croma Audits Summary.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  lr AS (
  SELECT l.id,
         RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder,
  regexp_replace(
    l.details->'gps'->>'address',
    '^.*?,\s*([^,]+?)(?:,?\s*\d{6})?,?\s*India$',
    '\1'
  ) as "division"
  FROM ACL
   LEFT OUTER JOIN locations l ON acl.store_id = L.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Regional Manager', 'Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'croma-coma' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         lr.store_name,MAX("division") AS division,
         MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         MAX(CASE WHEN ROLE = 'Regional Manager' THEN holder END) AS "RM",
         MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
  MAX(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head"
  FROM lr
  GROUP BY 1, 2
),
t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
         -- coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Dubai' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Dubai' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Dubai' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Dubai'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
  REGEXP_REPLACE(audit_main_theme, '\s*[-(].*$', '', 'g') AS "Audit",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality",CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
		lm."Head" as "Head", 
       lm."ZM" AS "ZM",
	   lm."CM" AS "CM",
   lm.division as "State",
   fs.approx_distance_in_km
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   JOIN lm ON cms.store_id = lm.store_id
   left outer join form_submissions fs on cms.audit_submission_knid = fs.response_id
   WHERE t.is_deleted = 'false'
     AND audit_main_theme NOT ILIKE '%tribe%'
   AND lm."Head" IS NOT NULL
     AND  lm."ZM" IS NOT NULL
	AND  lm."CM" IS NOT NULL
AND cms.audit_main_theme ILIKE ANY (ARRAY['%Process Excellence%', '%SMART Audit%', '%SOP Audit%'])
     AND cms.audit_submitted_at BETWEEN @{{:Croma Audits Summary.Date Range.START}}::timestamp AND @{{:Croma Audits Summary.Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'croma-coma'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40,41,42,43,44),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
	   assignees.assignee AS "Assigneee",
       assignees.department AS "Assignee Department"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
```

---

## Croma Audits Summary_Croma Audits.sql

**Tables referenced:** ACL, checkpoint_master_sheet_table, cms, form_submissions, fs, lm, locations, lr, role_holders, roles, submit_date, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Audits Summary
-- Dashboard: Croma Audits
-- Category: Croma
-- Extracted: 2026-01-29 16:55:51
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'    
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  lr AS (
  SELECT l.id,
         RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder,
  regexp_replace(
    l.details->'gps'->>'address',
    '^.*?,\s*([^,]+?)(?:,?\s*\d{6})?,?\s*India$',
    '\1'
  ) as "division"
  FROM ACL
   LEFT OUTER JOIN locations l ON acl.store_id = L.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Regional Manager', 'Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'croma-coma' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         lr.store_name,MAX("division") AS division,
         MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         MAX(CASE WHEN ROLE = 'Regional Manager' THEN holder END) AS "RM",
         MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
  MAX(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head"
  FROM lr
  GROUP BY 1, 2
),
cms as (
		select store_id, 
	   audit_type as "Audit Type",
       REGEXP_REPLACE(audit_main_theme, '\s*[-(].*$', '', 'g') AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
                     RESULT AS "Result",
                               criticality AS "Criticality",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL THEN 1
                                   ELSE 0
                               END AS "Checked Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score THEN 1
                                   ELSE 0
                               END AS "Failed Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score
                                        AND criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Failed Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
							THEN 1
                                   ELSE 0
                               END AS "Followup Points Count",
                               CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1
                                   ELSE 0
                               END AS "Closed Count",
							 CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1
                                   ELSE 0
                               END AS "Open Count",
							CASE   
                                   WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) and criticality = 'Critical' THEN 1
                                   ELSE 0
                               END AS "Critical Open Count"
FROM checkpoint_master_sheet_table cms
WHERE organization_id = 'croma-coma'
  AND store_id NOT ILIKE '%HO'						
						  and audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
  AND audit_main_theme NOT ILIKE '%tribe%'
AND audit_main_theme ILIKE ANY (ARRAY['%Process Excellence%', '%SMART Audit%', '%SOP Audit%'])),
						  fs as (select distinct on (response_id) response_id, form_id, extract(epoch from submit_date)*1000::bigint as submit_epoch, user_id as submitter_knid from form_submissions fs
								 join cms on cms."Audit Report KNID" = fs.response_id
								 order by fs.response_id, id desc)
  select lm.store_id AS "Store",
		lm."Head" as "Head", 
       lm."ZM" AS "ZM",
	   lm."CM" AS "CM",
	   lm.division as "State",
	   cms."Audit Type",
	   cms."Audit",
	   cms."Audited At",
	   cms."Auditor",
	   cms."Audit Report No",
	   cms."Audit Report KNID",
	   fs.form_id,
	   fs.submit_epoch,
	   fs.submitter_knid,
	   sum(cms."Actual Score")/sum(cms."Max Score") as "Audit Score",
	   sum(cms."Checked Count") as "Checked Count",
	   sum(cms."Failed Count") as "Failed Count",
	   sum(cms."Critical Failed Count") as "Critical Failed Count",
	   sum(cms."Followup Points Count") as "Followup Points Count",
	   sum(cms."Closed Count") as "Closed Count",
	   sum(cms."Open Count") as "Open Count",
	   sum(cms."Critical Open Count") as "Critical Open Count"
	   from lm
	   left outer join cms on lm.store_id = cms.store_id
	   left outer join fs on cms."Audit Report KNID" = fs.response_id
	   where cms."Audit" IS NOT NULL
	  AND lm."Head" IS NOT NULL
     AND  lm."ZM" IS NOT NULL
	AND  lm."CM" IS NOT NULL
	   group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14
	   order by 1, 2, 3, 4, 5, 6
```

---

## Croma Audits_Croma Audits.sql

**Tables referenced:** ACL, checkpoint_master_sheet_table, lm, locations, lr, role_holders, roles, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Audits
-- Dashboard: Croma Audits
-- Category: Croma
-- Extracted: 2026-01-29 16:55:50
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:Croma Audits Summary.UuidParameter}}
        AND role_holder_type = 'user'     
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:Croma Audits Summary.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'    
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:Croma Audits Summary.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:Croma Audits Summary.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
				  lr AS (
  SELECT l.id,
         RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder,
  regexp_replace(
    l.details->'gps'->>'address',
    '^.*?,\s*([^,]+?)(?:,?\s*\d{6})?,?\s*India$',
    '\1'
  ) as "division"
  FROM ACL
   LEFT OUTER JOIN locations l ON acl.store_id = L.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Regional Manager', 'Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'croma-coma' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         lr.store_name,MAX("division") AS division,
         MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         MAX(CASE WHEN ROLE = 'Regional Manager' THEN holder END) AS "RM",
         MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
  MAX(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head"
  FROM lr
  GROUP BY 1, 2
)
select lm.store_id as "Store" ,
lm."Head" AS "Head",
		lm."ZM" as "ZM", 
		lm."CM" as "CM",
		lm.division as "State",
	   audit_type as "Audit Type",
           REGEXP_REPLACE(audit_main_theme, '\s*[-(].*$', '', 'g') AS "Audit",
       audit_submitted_at AS "Audited At",
       auditor_name AS "Auditor",
       audit_submission_number AS "Audit Report No",
       audit_submission_knid AS "Audit Report KNID",
       theme AS "Theme",
       checkpoint_knid AS "Checkpoint KNID",
       CHECKPOINT AS "Checkpoint",
(SELECT jsonb_array_elements_text(cms.response_attachments) LIMIT 1) AS "Response",
	   auditor_observations,
                     RESULT AS "Result",
                               criticality AS "Criticality",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL THEN 1.0
                                   ELSE 0.0
                               END AS "Checked Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score THEN 1.0
                                   ELSE 0.0
                               END AS "Failed Count",
                               CASE
                                   WHEN result_score != ''
                                        AND result_score IS NOT NULL
                                        AND result_score < max_score
                                        AND criticality = 'Critical' THEN 1.0
                                   ELSE 0.0
                               END AS "Critical Failed Count",
                               CASE
                                   WHEN total_follow_up_tasks IS NULL
                                        OR total_follow_up_tasks = 0 THEN 'No Follow Up'
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 'Closed'
                                   ELSE 'Open'
                               END AS "Status",
							   CASE
                                   WHEN total_follow_up_tasks > 0
                                        AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1.0
                                   ELSE 0.0
                               END AS "Closed Count",
							   CASE
                                  WHEN total_follow_up_tasks > 0
                                        AND (total_follow_up_tasks > total_closed_follow_up_tasks or total_closed_follow_up_tasks is null) THEN 1.0
                                   ELSE 0.0
                               END AS "Open Count"
FROM lm 
left outer join checkpoint_master_sheet_table cms on cms.store_id = lm.store_id
WHERE organization_id = 'croma-coma'
  AND lm.store_id NOT ILIKE '%HO'
  and lm.store_id IS NOT NULL
    AND audit_main_theme NOT ILIKE '%tribe%'
	AND lm."Head" IS NOT NULL
     AND  lm."ZM" IS NOT NULL
	AND  lm."CM" IS NOT NULL
  AND audit_main_theme ILIKE ANY (ARRAY['%Process Excellence%', '%SMART Audit%', '%SOP Audit%'])
  and audit_submitted_at between @{{:Croma Audits Summary.Date Range.START}}::timestamp and @{{:Croma Audits Summary.Date Range.END}}::timestamp + interval '1 day'
  order by 1, 2, 3, 4, 5, 6, 10, 12
```

---

## Croma Bites_NPI.sql

**Original Query:**

```sql
-- Data Source: Croma Bites
-- Dashboard: NPI
-- Category: Croma
-- Extracted: 2026-01-29 16:52:55
-- ============================================================

select * from `coma-in.analytics.bite_analytics_summary_croma_last_95days`
where user_id is not null
```

---

## Croma Chatbot Responses - Wordcloud_Croma Chatbot Insights.sql

**Tables referenced:** chat_messages, chats, keywords, log, organizations, questions, td, user_details

**Original Query:**

```sql
-- Data Source: Croma Chatbot Responses - Wordcloud
-- Dashboard: Croma Chatbot Insights
-- Category: Croma
-- Extracted: 2026-01-29 16:54:09
-- ============================================================

WITH td AS (
  SELECT id AS org_id, (INTERVAL '1 minute' * tzoffset) AS diff
  FROM organizations
),
chats AS (
  SELECT cm.*
  FROM chat_messages cm
  WHERE (cm.to_id ILIKE 'croma-coma-gpt-bot' OR cm.from_id ILIKE 'croma-coma-gpt-bot')
    AND cm.is_deleted = FALSE
    AND cm.chat_type = 'user'
),
log AS (
  SELECT
    c.chat_id,
    s.uuid AS from_knid,
    r.uuid AS to_knid,
    c.message,
    to_timestamp(c.created_at/1000) + td.diff AS sent_at
  FROM chats c
  JOIN user_details s ON c.from_id = s.uuid
  JOIN user_details r ON c.to_id   = r.uuid
  JOIN td ON s.organization = td.org_id
),
questions AS (
  SELECT l.message AS question
  FROM log l
  WHERE l.to_knid = 'croma-coma-gpt-bot'
),
keywords AS (
  SELECT unnest(string_to_array(lower(q.question), ' ')) AS keyword
  FROM questions q
)
SELECT
  keyword AS "Question",
  COUNT(*) AS "Count of Questions"
FROM keywords
WHERE keyword NOT IN (
    'the','is','a','to','of','in','and','for','on','with','at','by',
    'an','as','it','this','that','be','are','was','were','from','if','or'
)
  AND keyword <> ''
GROUP BY keyword
ORDER BY "Count of Questions" DESC
```

---

## Croma Chatbot Responses_Croma Chatbot Insights.sql

**Tables referenced:** AggregatedAnswers, Questions, chat_messages, chats, log, organizations, td, user_details

**Original Query:**

```sql
-- Data Source: Croma Chatbot Responses
-- Dashboard: Croma Chatbot Insights
-- Category: Croma
-- Extracted: 2026-01-29 16:54:09
-- ============================================================

WITH td AS (
  SELECT
    id AS org_id,
    (INTERVAL '1 minute' * tzoffset) AS diff
  FROM organizations
),
chats AS (
  SELECT cm.*
  FROM chat_messages cm
  WHERE (cm.to_id ILIKE 'croma-coma-gpt-bot' OR cm.from_id ILIKE 'croma-coma-gpt-bot')
    AND cm.is_deleted = FALSE
    AND cm.chat_type = 'user'
),
log AS (
  SELECT
    c.chat_id AS "Chat ID",
    s.uuid       AS from_knid,
    r.uuid       AS to_knid,
    -- split name vs identifier for sender and receiver
    (s.first_name || ' ' || s.last_name) AS from_name,
    s.identifier                         AS from_identifier,
    s.job_location                       AS "Store",
    (r.first_name || ' ' || r.last_name) AS to_name,
    r.identifier                         AS to_identifier,
    r.job_location                       AS to_store,
    c.message                            AS "Message",
    -- apply org-specific offset to message timestamp (IST-aligned by tzoffset)
    (cast(to_timestamp(c.created_at/1000) as timestamptz) AT TIME ZONE 'Asia/Kolkata') AS "Sent At"
  FROM chats c
  JOIN user_details s ON c.from_id = s.uuid
  JOIN user_details r ON c.to_id   = r.uuid
  JOIN td ON s.organization = td.org_id
),
Questions AS (
  SELECT
    l.from_name        AS asking_user_name,
    l.from_identifier  AS asking_user_identifier,
    l."Store",
    l.from_knid        AS asking_user_knid,
    l."Sent At"        AS question_asked_at,
    l."Message"        AS question,
    LEAD(l."Sent At") OVER (PARTITION BY l.from_knid ORDER BY l."Sent At") AS next_question_time
  FROM log l
  WHERE l.to_knid = 'croma-coma-gpt-bot'
),
AggregatedAnswers AS (
  SELECT
    q.asking_user_name,
    q.asking_user_identifier,
    q."Store",
    q.question_asked_at,
    STRING_AGG(c."Message", E'\n\n- ' ORDER BY c."Sent At") AS aggregated_answer
  FROM Questions q
  LEFT JOIN log c
    ON c."Sent At" > q.question_asked_at
   AND (c."Sent At" < q.next_question_time OR q.next_question_time IS NULL)
   AND c.from_knid = 'croma-coma-gpt-bot'
   AND c.to_knid   = q.asking_user_knid
  GROUP BY
    q.asking_user_name,
    q.asking_user_identifier,
    q."Store",
    q.question_asked_at
)
SELECT
  q."Store",
  q.asking_user_name       AS "Staff Name",
  q.asking_user_identifier AS "Staff Identifier",
  q.question_asked_at      AS "Sent At",
  q.question               AS "Question",
  a.aggregated_answer      AS "Bot Response"
FROM Questions q
LEFT JOIN AggregatedAnswers a
  ON q.question_asked_at      = a.question_asked_at
 AND q.asking_user_name       = a.asking_user_name
 AND q.asking_user_identifier = a.asking_user_identifier
WHERE q.asking_user_name NOT ILIKE 'KNOW Support%'
ORDER BY 1, 2, 4
```

---

## Croma Checklist Adoption Trends_Checklists Compliance (Old).sql

**Tables referenced:** acl, croma.checklist_completions, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Checklist Adoption Trends
-- Dashboard: Checklists Compliance (Old)
-- Category: Croma
-- Extracted: 2026-01-29 16:52:37
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
SELECT cc.*
FROM acl
LEFT OUTER JOIN croma.checklist_completions cc ON acl.store_id = "Store ID"
WHERE cc."Date" >= date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days')
  AND cc."Date" < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
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
         17,18
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A474', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A734',  
'A736', 
'A508')
ORDER BY 10 DESC,
         1,
         2,
         3,
         4,
         5,
         9
```

---

## Croma Checklist Adoption Trends_Checklists Compliance.sql

**Tables referenced:** acl, croma.checklist_completions, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Checklist Adoption Trends
-- Dashboard: Checklists Compliance
-- Category: Croma
-- Extracted: 2026-01-29 16:52:37
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
SELECT cc.*
FROM acl
LEFT OUTER JOIN croma.checklist_completions cc ON acl.store_id = "Store ID"
WHERE cc."Date" >= date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days')
  AND cc."Date" < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
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
         17,18
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A474', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A734',  
'A736', 
'A508')
ORDER BY 10 DESC,
         1,
         2,
         3,
         4,
         5,
         9
```

---

## Croma Checklist Adoption_Checklists Compliance (Old).sql

**Tables referenced:** acl, croma.checklist_completions, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Checklist Adoption
-- Dashboard: Checklists Compliance (Old)
-- Category: Croma
-- Extracted: 2026-01-29 16:52:36
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id and ug.is_active = true
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  select cc.*, to_char(@{{:Date Range.START}}::date, 'YYYY-Mon-DD') as "Start Date", to_char(@{{:Date Range.END}}::date, 'YYYY-Mon-DD') as "End Date"
				  from acl
				  left outer join croma.checklist_completions cc on acl.store_id = "Store ID"
				  where cc."Date" >= @{{:Date Range.START}}::timestamp and cc."Date" < @{{:Date Range.END}}::timestamp + interval '1 day'
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
         17,18
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A734',  
'A508')
ORDER BY 10 DESC,
         1,
         2,
         3,
         4,
         5,
         9
```

---

## Croma Checklist Adoption_Checklists Compliance.sql

**Tables referenced:** acl, croma.checklist_completions, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Checklist Adoption
-- Dashboard: Checklists Compliance
-- Category: Croma
-- Extracted: 2026-01-29 16:52:36
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id and ug.is_active = true
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  select cc.*, to_char(@{{:Date Range.START}}::date, 'YYYY-Mon-DD') as "Start Date", to_char(@{{:Date Range.END}}::date, 'YYYY-Mon-DD') as "End Date"
				  from acl
				  left outer join croma.checklist_completions cc on acl.store_id = "Store ID"
				  where cc."Date" >= @{{:Date Range.START}}::timestamp and cc."Date" < @{{:Date Range.END}}::timestamp + interval '1 day'
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
         17,18
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A734',  
'A508')
ORDER BY 10 DESC,
         1,
         2,
         3,
         4,
         5,
         9
```

---

## Croma Completion Check_Routine Checks.sql

**Tables referenced:** base, form_reminders, form_submissions, fs, lfr, location_form_reminders, location_map, locations, nuggets, ufr, ufr_base, user_details, user_form_reminders

**Columns needing snake_case conversion:**

- `iThum` -> `i_thum` (alias: `i_thum AS "iThum"`)


**Original Query:**

```sql
-- Data Source: Croma Completion Check
-- Dashboard: Routine Checks
-- Category: Croma
-- Extracted: 2026-01-29 16:58:15
-- ============================================================

WITH location_map as (select 'A001' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Juhu' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'A' as store_category
union select 'A004' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Devarc' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'A' as store_category
union select 'A009' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Belapur' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'A' as store_category
union select 'A010' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Ghoddod' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'A' as store_category
union select 'A012' as store_id, 'Haryana' as state, 'Faridabad' as city, 'Faridabad-Crown Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'A' as store_category
union select 'A013' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Mulund' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'A' as store_category
union select 'A015' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Centre Square Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'B' as store_category
union select 'A017' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Thane-Bhayander' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'A' as store_category
union select 'A018' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-SS Manor' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'A' as store_category
union select 'A020' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Rohini' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'A' as store_category
union select 'A021' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Bandra Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'B' as store_category
union select 'A022' as store_id, 'Uttar Pradesh' as state, 'Ghaziabad' as city, 'Ghazibad-Pacific Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'D' as store_category
union select 'A023' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Greater Noida-Ansal Plaza Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A024' as store_id, 'Uttar Pradesh' as state, 'Ghaziabad' as city, 'Ghazibad-Aditya Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A026' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Fort' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'C' as store_category
union select 'A027' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-PMC Lower Parel Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'A' as store_category
union select 'A028' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Jubilee' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'C' as store_category
union select 'A029' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Panjagutta' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'B' as store_category
union select 'A032' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Kamlanagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'B' as store_category
union select 'A034' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Mount Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'A' as store_category
union select 'A035' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Ghatkopar Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'A' as store_category
union select 'A036' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Crystal Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'D' as store_category
union select 'A037' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Anna Nagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'A' as store_category
union select 'A038' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Pimpri' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'A' as store_category
union select 'A039' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Sion' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'A' as store_category
union select 'A040' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-T Nagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'A' as store_category
union select 'A041' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Oberoi Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'A' as store_category
union select 'A042' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Saket' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'A' as store_category
union select 'A044' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Rajouri' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'A' as store_category
union select 'A045' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Indira Nagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'C' as store_category
union select 'A048' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-SouthEx' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'A' as store_category
union select 'A049' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Kothrud' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'C' as store_category
union select 'A050' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Dlf Mega Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'A' as store_category
union select 'A053' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Ripple' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'C' as store_category
union select 'A055' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Connaught Place' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'A' as store_category
union select 'A056' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-J P Nagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'A' as store_category
union select 'A057' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Bel Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'C' as store_category
union select 'A058' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Koramangala' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'A' as store_category
union select 'A059' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Airport Terminal 3 International' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'Airport' as store_category
union select 'A060' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Marathahalli' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'A' as store_category
union select 'A062' as store_id, 'Maharashtra' as state, 'Chhatrapati Sambhaji Nagar' as city, 'Chhatrapati Sambhaji Nagar-Prozone Mall' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'A' as store_category
union select 'A064' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-East Of Kailash' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A066' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Bannerghatta Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'C' as store_category
union select 'A073' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Banshankari' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'B' as store_category
union select 'A074' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Breach Candy' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'C' as store_category
union select 'A080' as store_id, 'Chandigarh' as state, 'Chandigarh' as city, 'Chandigarh-Sector 22B' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'B' as store_category
union select 'A088' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-PMC Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'C' as store_category
union select 'A089' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Preet Vihar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'B' as store_category
union select 'A091' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Kondapur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'B' as store_category
union select 'A092' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Kandivali' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'A' as store_category
union select 'A093' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Rajaji Nagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'C' as store_category
union select 'A095' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Grand Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'C' as store_category
union select 'A097' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-PMC Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'C' as store_category
union select 'A104' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Pusa Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'C' as store_category
union select 'A105' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Adajan' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'A' as store_category
union select 'A107' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Ratna' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'B' as store_category
union select 'A108' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Solitario' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'A' as store_category
union select 'A112' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Select City Walk' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'A' as store_category
union select 'A113' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Jaynagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'C' as store_category
union select 'A114' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Total Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'D' as store_category
union select 'A115' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Seasons Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'A' as store_category
union select 'A116' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Kharghar' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'A' as store_category
union select 'A117' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Wakad' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'B' as store_category
union select 'A119' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Prabhadevi' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'A' as store_category
union select 'A120' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Sector 29' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'A' as store_category
union select 'A122' as store_id, 'Uttar Pradesh' as state, 'Ghaziabad' as city, 'Ghazibad- Gaur Central RDC Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A123' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-PMC Kurla Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'D' as store_category
union select 'A126' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-L B Nagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A127' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Andheri' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'A' as store_category
union select 'A129' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-PMC Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'B' as store_category
union select 'A131' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Rohini West Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'B' as store_category
union select 'A132' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Janakpuri' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'A' as store_category
union select 'A133' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Vashi' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'C' as store_category
union select 'A134' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-AS RaoNagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'C' as store_category
union select 'A135' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-Logix Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A137' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Deepkamal Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'C' as store_category
union select 'A140' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Bhandup Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'B' as store_category
union select 'A141' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Seawoods Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'B' as store_category
union select 'A142' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Growel101 Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'C' as store_category
union select 'A143' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Motera' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'C' as store_category
union select 'A144' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Ambience Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'A' as store_category
union select 'A145' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Mani Nagar' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'C' as store_category
union select 'A146' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Mogappair' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'C' as store_category
union select 'A147' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Borivali' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'A' as store_category
union select 'A148' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Kompally' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'C' as store_category
union select 'A149' as store_id, 'Telangana' as state, 'Secunderabad' as city, 'Secunderabad-New Vikrampuri' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'C' as store_category
union select 'A150' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Whitefield' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'B' as store_category
union select 'A151' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-Mall of India' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A152' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Attapur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'C' as store_category
union select 'A153' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Infiniti Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'A' as store_category
union select 'A156' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Baner' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'A' as store_category
union select 'A157' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Avadi' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A160' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Yelahanka' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'B' as store_category
union select 'A159' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Satyam64' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'B' as store_category
union select 'A165' as store_id, 'Gujarat' as state, 'Bhavnagar' as city, 'Bhavnagar-Sun Exotica' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'C' as store_category
union select 'A164' as store_id, 'Maharashtra' as state, 'Kolhapur' as city, 'Kolhapur-StarBazaar' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'B' as store_category
union select 'A161' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Vasant Kunj Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'A' as store_category
union select 'A162' as store_id, 'Punjab' as state, 'Mohali' as city, 'Mohali-VR Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A170' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Kukatpally' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'A' as store_category
union select 'A169' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Sarath City Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'C' as store_category
union select 'A166' as store_id, 'Gujarat' as state, 'Jamnagar' as city, 'Jamnagar-Shreeji One' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'C' as store_category
union select 'A163' as store_id, 'Punjab' as state, 'Jalandhar' as city, 'Jalandhar-Lajpat Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'C' as store_category
union select 'A138' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-BSR Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'C' as store_category
union select 'A167' as store_id, 'Karnataka' as state, 'Hubli' as city, 'Hubli-Gokul Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'D' as store_category
union select 'A173' as store_id, 'Karnataka' as state, 'Mysore' as city, 'Mysore-Double Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'A' as store_category
union select 'A177' as store_id, 'Gujarat' as state, 'Bhuj' as city, 'Bhuj-Seven Sky Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'D' as store_category
union select 'A180' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Sarat Bose Road' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'C' as store_category
union select 'A168' as store_id, 'Rajasthan' as state, 'Jaipur' as city, 'Jaipur-WTP Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'B' as store_category
union select 'A175' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Thane-Ghodbunder Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'A' as store_category
union select 'A172' as store_id, 'Goa' as state, 'Porvorim' as city, 'Porvorim-Bardez' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'A' as store_category
union select 'A179' as store_id, 'Karnataka' as state, 'Mandya' as city, 'Mandya-MC Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'D' as store_category
union select 'A154' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Ramanthapur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A181' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Chrompet' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'B' as store_category
union select 'A182' as store_id, 'Madhya Pradesh' as state, 'Gwalior' as city, 'Gwalior-City Center' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'B' as store_category
union select 'A184' as store_id, 'Maharashtra' as state, 'Baramati' as city, 'Baramati-Bhigwan Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'D' as store_category
union select 'A186' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Vijay Nagar Square' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'B' as store_category
union select 'A190' as store_id, 'Gujarat' as state, 'Gandhidham' as city, 'Gandhidham-RT Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'C' as store_category
union select 'A192' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-DB Mall' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'C' as store_category
union select 'A185' as store_id, 'Karnataka' as state, 'Davanagere' as city, 'Davanagere-Hadadi Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'C' as store_category
union select 'A195' as store_id, 'Gujarat' as state, 'Vapi' as city, 'Vapi-Daman Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'C' as store_category
union select 'A193' as store_id, 'Tamil Nadu' as state, 'Coimbatore' as city, 'Coimbatore-Prozone Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'C' as store_category
union select 'A188' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-Arera Colony' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A189' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-Gaur Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'A' as store_category
union select 'A191' as store_id, 'Maharashtra' as state, 'Chhatrapati Sambhaji Nagar' as city, 'Chhatrapati Sambhaji Nagar-Waluj' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'D' as store_category
union select 'A200' as store_id, 'Gujarat' as state, 'Junagadh' as city, 'Junagadh-Timbawadi Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'D' as store_category
union select 'A201' as store_id, 'Gujarat' as state, 'Anand' as city, 'Anand-Vidyanagar Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'C' as store_category
union select 'A197' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Rajarhat' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'A' as store_category
union select 'A204' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Vegas Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'A' as store_category
union select 'A199' as store_id, 'Tamil Nadu' as state, 'Coimbatore' as city, 'Coimbatore-Laxmi Mills' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'B' as store_category
union select 'A194' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Chinchawad' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'D' as store_category
union select 'A202' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Kareli Baug' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'A' as store_category
union select 'A208' as store_id, 'Gujarat' as state, 'Nadiad' as city, 'Nadiad-Uttarsanda Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'D' as store_category
union select 'A210' as store_id, 'Gujarat' as state, 'Bharuch' as city, 'Bharuch-Dahej Bypass Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'C' as store_category
union select 'A211' as store_id, 'Andhra Pradesh' as state, 'Visakhapatnam' as city, 'Vizag-Sripuram' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'C' as store_category
union select 'A205' as store_id, 'Andhra Pradesh' as state, 'Visakhapatnam' as city, 'Vizag-Muralinagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'A206' as store_id, 'Rajasthan' as state, 'Kota' as city, 'Kota-Dakaniya Station Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'D' as store_category
union select 'A221' as store_id, 'Karnataka' as state, 'Mangalore' as city, 'Mangalore-MAK Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'C' as store_category
union select 'A209' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Parvat Patiya' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'C' as store_category
union select 'A212' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Worldmark 2' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'C' as store_category
union select 'A178' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Kurla LBS Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'B' as store_category
union select 'A213' as store_id, 'Tamil Nadu' as state, 'Salem' as city, 'Salem-Bharathi Street' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'D' as store_category
union select 'A198' as store_id, 'Chhattisgarh' as state, 'Raipur' as city, 'Raipur-Pandri Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'D' as store_category
union select 'A223' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-OP Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'C' as store_category
union select 'A217' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-VIP Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'B' as store_category
union select 'A220' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Green Chinar' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'C' as store_category
union select 'A214' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Aliganj' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'C' as store_category
union select 'A219' as store_id, 'Chhattisgarh' as state, 'Raipur' as city, 'Raipur-VIP Chowk' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'D' as store_category
union select 'A207' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Hennur Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'C' as store_category
union select 'A222' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Katraj' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'B' as store_category
union select 'A228' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Vastral' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A227' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Karmanghat' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A224' as store_id, 'Andhra Pradesh' as state, 'Rajahmundry' as city, 'Rajahmundry-RTC Complex Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A215' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Nashik Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'A' as store_category
union select 'A226' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Barasat' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'D' as store_category
union select 'A174' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Chembur' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'B' as store_category
union select 'A218' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Nana Mawa Chowk' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'C' as store_category
union select 'A230' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Nikol' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'C' as store_category
union select 'A244' as store_id, 'Gujarat' as state, 'Navsari' as city, 'Navsari-Grid Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'C' as store_category
union select 'A229' as store_id, 'West Bengal' as state, 'Asansol' as city, 'Asansol-Bhagat Singh More' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'D' as store_category
union select 'A234' as store_id, 'Chhattisgarh' as state, 'Bilaspur' as city, 'Bilaspur-Srikant Verma Marg' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'D' as store_category
union select 'A236' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Malleshwaram' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'D' as store_category
union select 'A233' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Aerodrum Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'C' as store_category
union select 'A196' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Madinaguda' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'B' as store_category
union select 'A225' as store_id, 'Tamil Nadu' as state, 'Hosur' as city, 'Hosur-Bagalur Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'D' as store_category
union select 'A235' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Gunjur' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'C' as store_category
union select 'A247' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Maninagar South' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A238' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Kalikapur' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'C' as store_category
union select 'A249' as store_id, 'Gujarat' as state, 'Palanpur' as city, 'Palanpur-Delhi Highway' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'D' as store_category
union select 'A231' as store_id, 'Gujarat' as state, 'Mehsana' as city, 'Mehsana-Modhera Circle' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'D' as store_category
union select 'A252' as store_id, 'Andhra Pradesh' as state, 'Eluru' as city, 'Eluru-Narsimharaopet' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A243' as store_id, 'Maharashtra' as state, 'Solapur' as city, 'Solapur-Murarji Peth' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'C' as store_category
union select 'A260' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad -Science City' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'E' as store_category
union select 'A245' as store_id, 'Jharkhand' as state, 'Dhanbad' as city, 'Dhanbad-Prabhatam Grand Mall' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'D' as store_category
union select 'A242' as store_id, 'Andhra Pradesh' as state, 'Guntur' as city, 'Guntur-Lakshmipuram Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A263' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Kamrej' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'D' as store_category
union select 'A258' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi - Pitampura' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'C' as store_category
union select 'A256' as store_id, 'Maharashtra' as state, 'Latur' as city, 'Latur-Ambejogai Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'D' as store_category
union select 'A239' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Alambagh' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'B' as store_category
union select 'A270' as store_id, 'Andhra Pradesh' as state, 'Vijayawada' as city, 'Vijayawada-Benz Circle' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A277' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Electronic City' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'C' as store_category
union select 'A276' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Civil Lines' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'C' as store_category
union select 'A285' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Kandivali West' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'B' as store_category
union select 'A251' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Shyamal Cross Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'D' as store_category
union select 'A250' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Bopal' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'C' as store_category
union select 'A273' as store_id, 'Punjab' as state, 'Bathinda' as city, 'Bathinda-GT Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'D' as store_category
union select 'A274' as store_id, 'Andhra Pradesh' as state, 'Kurnool' as city, 'Kurnool-Raj Vihar Centre' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'D' as store_category
union select 'A282' as store_id, 'Kerala' as state, 'Thrissur' as city, 'Thrissur-MG Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'C' as store_category
union select 'A289' as store_id, 'Karnataka' as state, 'Hubli' as city, 'Hubli-Vidyanagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'E' as store_category
union select 'A283' as store_id, 'Rajasthan' as state, 'Jaipur' as city, 'Jaipur -Vaishali Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'C' as store_category
union select 'A255' as store_id, 'Punjab' as state, 'Patiala' as city, 'Patiala-Bhupendra Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A269' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Alwarpet' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A240' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Sector 12' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'C' as store_category
union select 'A275' as store_id, 'Maharashtra' as state, 'Kalyan' as city, 'Kalyan-Khadakpada' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'B' as store_category
union select 'A300' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad- Vanasthalipuram' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A278' as store_id, 'Chhattisgarh' as state, 'Bhilai' as city, 'Bhilai-Supela' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'D' as store_category
union select 'A284' as store_id, 'Uttar Pradesh' as state, 'Agra' as city, 'Agra-SRK Mall' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'D' as store_category
union select 'A246' as store_id, 'Gujarat' as state, 'Gandhinagar' as city, 'Gandhinagar-Sector 11' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'C' as store_category
union select 'A262' as store_id, 'Maharashtra' as state, 'Amravati' as city, 'Amravati - Badnera Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Vishal Phatak' as cm_name, 'D' as store_category
union select 'A316' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Mall Fifty One' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'C' as store_category
union select 'A331' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune - Chakan' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'C' as store_category
union select 'A334' as store_id, 'Andhra Pradesh' as state, 'Guntur' as city, 'Guntur -Tadepalle' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'E' as store_category
union select 'A259' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow - Vibhuti Khand' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'B' as store_category
union select 'A327' as store_id, 'Gujarat' as state, 'Surendranagar' as city, 'Surendranagar – Upasna circle' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A294' as store_id, 'Punjab' as state, 'Zirakhpur' as city, 'Zirakhpur- Garden Village' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A313' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Punjabi Bagh' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'D' as store_category
union select 'A320' as store_id, 'Kerala' as state, 'Kozhikode' as city, 'Kozhikode - Hilite Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'D' as store_category
union select 'A271' as store_id, 'Karnataka' as state, 'Belagavi' as city, 'Belagavi -Tilakwadi' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'C' as store_category
union select 'A342' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune - Westend Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'C' as store_category
union select 'A301' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad- Makarba' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'D' as store_category
union select 'A241' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Sinhgad Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'C' as store_category
union select 'A272' as store_id, 'Karnataka' as state, 'Shivamogga' as city, 'Shivamoga-Savalanga Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'D' as store_category
union select 'A311' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-DB Gupta Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'D' as store_category
union select 'A309' as store_id, 'Kerala' as state, 'Kochi' as city, 'Kochi-Bypass Road Vyttila' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'D' as store_category
union select 'A308' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad - Boduppal' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A203' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-JVA Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'C' as store_category
union select 'A340' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai - Adyar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A325' as store_id, 'Gujarat' as state, 'Amreli' as city, 'Amreli- Krushi Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A339' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Urapakkam' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A288' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Virar' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'C' as store_category
union select 'A303' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Wagholi' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'C' as store_category
union select 'A326' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Kanakpura' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'C' as store_category
union select 'A279' as store_id, 'Goa' as state, 'Dabolim' as city, 'Dabolim-Alsto' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'C' as store_category
union select 'A292' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Dilsukhnagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'D' as store_category
union select 'A291' as store_id, 'Rajasthan' as state, 'Udaipur' as city, 'Udaipur-RK Circle' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'D' as store_category
union select 'A348' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Bicholi Mardana' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A336' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Shahdara' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'B' as store_category
union select 'A298' as store_id, 'Karnataka' as state, 'Udupi' as city, 'Udupi-Manipal Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'D' as store_category
union select 'A267' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-GT Karnal Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'E' as store_category
union select 'A345' as store_id, 'Gujarat' as state, 'Porbandar' as city, 'Porbandar-Jalaram Colony' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A344' as store_id, 'Punjab' as state, 'Ludhiana' as city, 'Ludhiana-Sector 32A' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A358' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Pacific Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'C' as store_category
union select 'A328' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Zundal' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'C' as store_category
union select 'A373' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Madhapar' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A354' as store_id, 'Maharashtra' as state, 'Nagpur' as city, 'Nagpur-Wardha Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Vishal Phatak' as cm_name, 'C' as store_category
union select 'A382' as store_id, 'Chandigarh' as state, 'Chandigarh' as city, 'Chandigarh-Elante Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'C' as store_category
union select 'A323' as store_id, 'Kerala' as state, 'Kochi' as city, 'Kochi-Kalamassery' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'C' as store_category
union select 'A330' as store_id, 'Madhya Pradesh' as state, 'Ratlam' as city, 'Ratlam-Do Batti Chowk' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A312' as store_id, 'Uttarakhand' as state, 'Dehradun' as city, 'Dehradun-Rajpur Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'C' as store_category
union select 'A335' as store_id, 'Madhya Pradesh' as state, 'Ujjain' as city, 'Ujjain-Dewas Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A297' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Katargam' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'E' as store_category
union select 'A381' as store_id, 'Odisha' as state, 'Bhubaneshwar' as city, 'Bhubaneshwar-Janpath Road' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'C' as store_category
union select 'A380' as store_id, 'Jharkhand' as state, 'Jamshedpur' as city, 'Jamshedpur-Bistupur' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'C' as store_category
union select 'A377' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Datta Mandir Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'C' as store_category
union select 'A306' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Sector 86' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'B' as store_category
union select 'A391' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai - Vivira Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A356' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Ambattur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'C' as store_category
union select 'A357' as store_id, 'Andhra Pradesh' as state, 'Vijayawada' as city, 'Vijayawada - Eluru Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A307' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Sindhu Bhavan' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'D' as store_category
union select 'A264' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Hinjewadi' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'C' as store_category
union select 'A374' as store_id, 'Rajasthan' as state, 'Sriganganagar' as city, 'Sriganganagar-Ridhi Sidhi Enclave' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'E' as store_category
union select 'A399' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Bavdhan' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'D' as store_category
union select 'A411' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Ramol' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'E' as store_category
union select 'A355' as store_id, 'Haryana' as state, 'Yamunanagar' as city, 'Yamunanagar-Gobindpuri Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'D' as store_category
union select 'A388' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Palassio Mall' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'D' as store_category
union select 'A383' as store_id, 'Madhya Pradesh' as state, 'Khandwa' as city, 'Khandwa-Indore-Khandwa Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'E' as store_category
union select 'A392' as store_id, 'Odisha' as state, 'Bhubaneshwar' as city, 'Bhubaneshwar-Patia' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'D' as store_category
union select 'A398' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Reach 3 Roads' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'D' as store_category
union select 'A385' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Acropolis Mall' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'C' as store_category
union select 'A378' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Dum Dum' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'D' as store_category
union select 'A347' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Nava Naroda' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A402' as store_id, 'Telangana' as state, 'Karimnagar' as city, 'Karimnagar - Jagtial Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A396' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Kamothe' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'C' as store_category
union select 'A422' as store_id, 'Telangana' as state, 'Secunderabad' as city, 'Secunderabad-Nagaram' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'D' as store_category
union select 'A403' as store_id, 'Gujarat' as state, 'Morbi' as city, 'Morbi-Sanala Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'D' as store_category
union select 'A353' as store_id, 'Telangana' as state, 'Mahbubnagar' as city, 'Mahbubnagar-Rajendra Nagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'D' as store_category
union select 'A318' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Park Street' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'D' as store_category
union select 'A324' as store_id, 'Gujarat' as state, 'Bardoli' as city, 'Bardoli-Mota Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'E' as store_category
union select 'A352' as store_id, 'Maharashtra' as state, 'Chandrapur' as city, 'Chandrapur-Nagpur Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Vishal Phatak' as cm_name, 'D' as store_category
union select 'A299' as store_id, 'Kerala' as state, 'Palakkad' as city, 'Palakkad-Stadium Bypass Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'D' as store_category
union select 'A304' as store_id, 'Maharashtra' as state, 'Akola' as city, 'Akola-Kirti Nagar' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Vishal Phatak' as cm_name, 'D' as store_category
union select 'A443' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Janakpuri C1 Block' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'E' as store_category
union select 'A384' as store_id, 'Uttar Pradesh' as state, 'Ghaziabad' as city, 'Ghaziabad-Raj Nagar Extension' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'D' as store_category
union select 'A314' as store_id, 'Maharashtra' as state, 'Ahmednagar' as city, 'Ahmednagar-Kohinoor Mall' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'D' as store_category
union select 'A393' as store_id, 'Haryana' as state, 'Faridabad' as city, 'Faridabad-NIT' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'D' as store_category
union select 'A439' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-HSR Layout' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'C' as store_category
union select 'A370' as store_id, 'West Bengal' as state, 'Howrah' as city, 'Howrah-Avani Mall' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'C' as store_category
union select 'A290' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Bapunagar' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A421' as store_id, 'Haryana' as state, 'Panchkula' as city, 'Panchkula-Sector 11' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A445' as store_id, 'Maharashtra' as state, 'Kalyan' as city, 'Kalyan-Metro Junction Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'D' as store_category
union select 'A375' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Daryaganj' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A415' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Aero Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'D' as store_category
union select 'A425' as store_id, 'Uttarakhand' as state, 'Haridwar' as city, 'Haridwar-Ranipur Mod' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'D' as store_category
union select 'A322' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Sholinganallur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A412' as store_id, 'Gujarat' as state, 'Gandhinagar' as city, 'Gandhinagar-Sargasan Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'D' as store_category
union select 'A321' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Nagarbhavi' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'D' as store_category
union select 'A424' as store_id, 'West Bengal' as state, 'Howrah' as city, 'Howrah-Liluah' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'E' as store_category
union select 'A494' as store_id, 'Andhra Pradesh' as state, 'Vijayawada' as city, 'Vijayawada-Enikepadu' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'E' as store_category
union select 'A426' as store_id, 'Telangana' as state, 'Warangal' as city, 'Warangal-SV Patel Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'E' as store_category
union select 'A476' as store_id, 'Andhra Pradesh' as state, 'Madanapalle' as city, 'Madanapalle-NTR Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'E' as store_category
union select 'A397' as store_id, 'Andhra Pradesh' as state, 'Ongole' as city, 'Ongole-Trunk Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A413' as store_id, 'Maharashtra' as state, 'Jalna' as city, 'Jalna-Old Mondha' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'D' as store_category
union select 'A416' as store_id, 'Gujarat' as state, 'Ankleshwar' as city, 'Ankleshwar-Apple Plaza' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'D' as store_category
union select 'A436' as store_id, 'Haryana' as state, 'Panipat' as city, 'Panipat-Mittal Mega Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'E' as store_category
union select 'A371' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Faizabad Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'E' as store_category
union select 'A430' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Airport 2' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'Airport' as store_category
union select 'A465' as store_id, 'Rajasthan' as state, 'Jaipur' as city, 'Jaipur-Tonk Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'D' as store_category
union select 'A319' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Hathijan Circle' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'E' as store_category
union select 'A469' as store_id, 'Maharashtra' as state, 'Chhatrapati Sambhaji Nagar' as city, 'Chhatrapati Sambhaji Nagar-Jalna Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'C' as store_category
union select 'A498' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Malviya Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A467' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-NSC Bose Road' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'D' as store_category
union select 'A491' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Gangapur Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'D' as store_category
union select 'A486' as store_id, 'Gujarat' as state, 'Vapi' as city, 'Vapi-GIDC' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'D' as store_category
union select 'A455' as store_id, 'Punjab' as state, 'Mohali' as city, 'Mohali-CP 67' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A359' as store_id, 'Uttar Pradesh' as state, 'Kanpur' as city, 'Kanpur-Awas Vikas' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'D' as store_category
union select 'A379' as store_id, 'Punjab' as state, 'Pathankot' as city, 'Pathankot-Dalhousie Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A448' as store_id, 'Telangana' as state, 'Secunderabad' as city, 'Secunderabad-Nacharam' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'E' as store_category
union select 'A365' as store_id, 'Uttar Pradesh' as state, 'Kanpur' as city, 'Kanpur-Mall Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'E' as store_category
union select 'A515' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Gottigere' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'D' as store_category
union select 'A489' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Global Malls' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'E' as store_category
union select 'A280' as store_id, 'Karnataka' as state, 'Vijayapura' as city, 'Vijayapura-Lingad Gudi Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'D' as store_category
union select 'A458' as store_id, 'Maharashtra' as state, 'Solapur' as city, 'Solapur-Hotgi Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'D' as store_category
union select 'A473' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-West Patel Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'D' as store_category
union select 'A506' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Bhagal' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'D' as store_category
union select 'A495' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Hasthinapuram' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'E' as store_category
union select 'A523' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Kothi Char Rasta' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'D' as store_category
union select 'A461' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Ulhasnagar-Central Hospital Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'D' as store_category
union select 'A513' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Phoenix Citadel' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'E' as store_category
union select 'A363' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Nagavara' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'D' as store_category
union select 'A512' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Citi Centre Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'E' as store_category
union select 'A315' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Selaiyur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A470' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Hyderguda' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'D' as store_category
union select 'A478' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Nalasopara West' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'D' as store_category
union select 'A453' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-Kohefiza' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A454' as store_id, 'Odisha' as state, 'Cuttack' as city, 'Cuttack-College Square' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'D' as store_category
union select 'A527' as store_id, 'Kerala' as state, 'Perinthalmanna' as city, 'Perinthalmanna-Bypass Junction' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'E' as store_category
union select 'A493' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Powai' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'C' as store_category
union select 'A540' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Khajaguda' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'A462' as store_id, 'Gujarat' as state, 'Sanand' as city, 'Sanand-Vardhman Square' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'E' as store_category
union select 'A442' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-93 Avenue' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'D' as store_category
union select 'A248' as store_id, 'Gujarat' as state, 'Valsad' as city, 'Valsad-Dharampur Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'D' as store_category
union select 'A501' as store_id, 'Chhattisgarh' as state, 'Raipur' as city, 'Raipur-Bhatagaon' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'D' as store_category
union select 'A441' as store_id, 'Chhattisgarh' as state, 'Rajnandgaon' as city, 'Rajnandgaon-Basantpur Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'E' as store_category
union select 'A432' as store_id, 'Kerala' as state, 'Kottayam' as city, 'Kottayam-MC Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'E' as store_category
union select 'A480' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Virar East' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'D' as store_category
union select 'A532' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-CBD Shahdara' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A477' as store_id, 'Uttarakhand' as state, 'Dehradun' as city, 'Dehradun-Saharanpur Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'E' as store_category
union select 'A545' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Lajpat Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A266' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-EPICAH Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'D' as store_category
union select 'A417' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Patparganj' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A544' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-Golden I' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'C' as store_category
union select 'A507' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Ulwe' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'D' as store_category
union select 'A524' as store_id, 'Madhya Pradesh' as state, 'Sagar' as city, 'Sagar-Makroniya' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'D' as store_category
union select 'A529' as store_id, 'Madhya Pradesh' as state, 'Jabalpur' as city, 'Jabalpur-Gorakhpur Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'D' as store_category
union select 'A496' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Dr. Yagnik Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'D' as store_category
union select 'A487' as store_id, 'Chandigarh' as state, 'Chandigarh' as city, 'Chandigarh-Sector 35 B' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A386' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Kuvadava Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A287' as store_id, 'Haryana' as state, 'Sonipat' as city, 'Sonipat-Atlas Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Gunjan Jetly' as cm_name, 'E' as store_category
union select 'A406' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Memnagar' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Atul Morjaria' as cm_name, 'D' as store_category
union select 'A520' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Nana Chhiloda' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'E' as store_category
union select 'A481' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Raghuleela Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'D' as store_category
union select 'A542' as store_id, 'Madhya Pradesh' as state, 'Satna' as city, 'Satna-Panna Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A349' as store_id, 'Madhya Pradesh' as state, 'Rewa' as city, 'Rewa-Urrahat' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A537' as store_id, 'Kerala' as state, 'Kottayam' as city, 'Kottayam-KK Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'E' as store_category
union select 'A521' as store_id, 'Punjab' as state, 'Mohali' as city, 'Mohali-TDI Connaught Plaza' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'E' as store_category
union select 'A561' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Garuda Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'D' as store_category
union select 'A471' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Thane-Kalyan Shilphata Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'D' as store_category
union select 'A488' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Dindori Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'D' as store_category
union select 'A420' as store_id, 'Andhra Pradesh' as state, 'Tirupati' as city, 'Tirupati-TUDA Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'D' as store_category
union select 'A433' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Vadapalani' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A337' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Sohna Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'B' as store_category
union select 'A555' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-Sector 122' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'D' as store_category
union select 'A567' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Race course Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'C' as store_category
union select 'A361' as store_id, 'Uttar Pradesh' as state, 'Bulandshahr' as city, 'Bulandshahr-Raja Babu Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'E' as store_category
union select 'A427' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Narendrapur' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'E' as store_category
union select 'A530' as store_id, 'Gujarat' as state, 'Chikhli' as city, 'Chikhli-Thala' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'E' as store_category
union select 'A578' as store_id, 'Kerala' as state, 'Kozhikode' as city, 'Kozhikode-Mavoor Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'E' as store_category
union select 'A577' as store_id, 'Uttarakhand' as state, 'Dehradun' as city, 'Dehradun-Chakrata road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'D' as store_category
union select 'A533' as store_id, 'Punjab' as state, 'Sangrur' as city, 'Sangrur-Sunami Gate' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'E' as store_category
union select 'A509' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-Indrapuri' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A409' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Sapna Sangeeta Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A414' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Thane-Dombivali East' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'D' as store_category
union select 'A553' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Naranpura' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'E' as store_category
union select 'A571' as store_id, 'Punjab' as state, 'Muktsar' as city, 'Muktsar-Kotkapura road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'E' as store_category
union select 'A351' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-Hoshangabad Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A596' as store_id, 'Gujarat' as state, 'Rajkot' as city, 'Rajkot-Mavdi' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A466' as store_id, 'Maharashtra' as state, 'Miraj' as city, 'Miraj-Vantmure Corner' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'E' as store_category
union select 'A538' as store_id, 'Punjab' as state, 'Firozpur' as city, 'Firozpur-Mall Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'E' as store_category
union select 'A405' as store_id, 'Karnataka' as state, 'Hassan' as city, 'Hassan-BM Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'D' as store_category
union select 'A483' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Harni Sama Link Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'D' as store_category
union select 'A468' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Indra Nagar' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'D' as store_category
union select 'A451' as store_id, 'Punjab' as state, 'Moga' as city, 'Moga-GT Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'E' as store_category
union select 'A582' as store_id, 'Maharashtra' as state, 'Ratnagiri' as city, 'Ratnagiri-Arihant Mall' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Abhijeet Pardeshi' as cm_name, 'D' as store_category
union select 'A531' as store_id, 'Chhattisgarh' as state, 'Korba' as city, 'Korba-Transport Nagar' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'E' as store_category
union select 'A492' as store_id, 'Gujarat' as state, 'Bharuch' as city, 'Bharuch-Tavra Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'E' as store_category
union select 'A499' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Manjalpur' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'D' as store_category
union select 'A516' as store_id, 'Tamil Nadu' as state, 'Vellore' as city, 'Vellore-Katpadi' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'E' as store_category
union select 'A626' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-New VIP Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'D' as store_category
union select 'A610' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Govind Nagar' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'D' as store_category
union select 'T001' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Dwarka Sector 12-2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A338' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Vicino Mall' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'D' as store_category
union select 'A597' as store_id, 'Gujarat' as state, 'Anand' as city, 'Anand-Mota Bazaar' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'E' as store_category
union select 'A503' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Dwarka Sector 12' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'D' as store_category
union select 'A598' as store_id, 'Kerala' as state, 'Kochi' as city, 'Kochi-Terminal 1D' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'Airport' as store_category
union select 'T005' as store_id, 'Madhya Pradesh' as state, 'Dewas' as city, 'Dewas-Agroha Nagar' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A490' as store_id, 'Haryana' as state, 'Gurugram' as city, 'Gurugram-Sector 67' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Manoj Kumar' as cm_name, 'D' as store_category
union select 'A440' as store_id, 'Uttar Pradesh' as state, 'Gorakhpur' as city, 'Gorakhpur-Medical College Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'D' as store_category
union select 'A407' as store_id, 'West Bengal' as state, 'Sodepur' as city, 'Sodepur-BT Road' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'E' as store_category
union select 'A579' as store_id, 'Chhattisgarh' as state, 'Bilaspur' as city, 'Bilaspur-Sarkanada' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Rajaram Gavade' as cm_name, 'E' as store_category
union select 'T002' as store_id, 'Karnataka' as state, 'Vijayapura' as city, 'Vijayapura-Solapur Road' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'T003' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Gota' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A586' as store_id, 'Bihar' as state, 'Patna' as city, 'Patna-Patliputra Golambar' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'D' as store_category
union select 'A562' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Manikonda' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'A590' as store_id, 'Madhya Pradesh' as state, 'Damoh' as city, 'Damoh-Sagar Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A362' as store_id, 'Telangana' as state, 'Khammam' as city, 'Khammam-Wyra Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'D' as store_category
union select 'A564' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Vrindavan Yojna' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'D' as store_category
union select 'T006' as store_id, 'Tamil Nadu' as state, 'Erode' as city, 'Erode-Perundurai Road' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A627' as store_id, 'Madhya Pradesh' as state, 'Guna' as city, 'Guna-AB Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'E' as store_category
union select 'A633' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-Salt Lake Sector 1' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'E' as store_category
union select 'A508' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Ampa Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A563' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-YGR Mall' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'D' as store_category
union select 'A551' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Phoenix Mall Of The Millennium' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'D' as store_category
union select 'A566' as store_id, 'Maharashtra' as state, 'Nanded' as city, 'Nanded-ITI Road' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'D' as store_category
union select 'A557' as store_id, 'Gujarat' as state, 'Dahod' as city, 'Dahod-Godhra road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'E' as store_category
union select 'A592' as store_id, 'Kerala' as state, 'Kottakal' as city, 'Kottakal-Changuvetty' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'E' as store_category
union select 'A539' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Mall of Asia' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'D' as store_category
union select 'A317' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Ranna Park' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Bhavesh Bhasin' as cm_name, 'D' as store_category
union select 'A522' as store_id, 'Karnataka' as state, 'Ballari' as city, 'Ballari-Infantry Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'D' as store_category
union select 'A620' as store_id, 'Punjab' as state, 'Patiala' as city, 'Patiala-Spectra Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A595' as store_id, 'Punjab' as state, 'Ludhiana' as city, 'Ludhiana-Feroz Gandhi Market' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A518' as store_id, 'Punjab' as state, 'Malerkotla' as city, 'Malerkotla-Thandi Sadak' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'E' as store_category
union select 'A591' as store_id, 'Karnataka' as state, 'Tumkur' as city, 'Tumkur-BH Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'E' as store_category
union select 'A372' as store_id, 'Punjab' as state, 'Hoshiarpur' as city, 'Hoshiarpur-Mall Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'E' as store_category
union select 'A638' as store_id, 'Madhya Pradesh' as state, 'Chhindwara' as city, 'Chhindwara-Station Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A657' as store_id, 'Punjab' as state, 'Sunam' as city, 'Sunam-JP Tower' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Santosh Sahu' as cm_name, 'E' as store_category
union select 'A560' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Makarpura' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'E' as store_category
union select 'T010' as store_id, 'Gujarat' as state, 'Mehsana' as city, 'Mehsana-Radhanpur Road' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'T011' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Lulu Mall' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A400' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Varachha Main Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'D' as store_category
union select 'A636' as store_id, 'Uttar Pradesh' as state, 'Jaunpur' as city, 'Jaunpur-Wazidpur Tiraha' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A302' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Nizampura' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'D' as store_category
union select 'A572' as store_id, 'Rajasthan' as state, 'Jaipur' as city, 'Jaipur-Raja Park' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'D' as store_category
union select 'A584' as store_id, 'West Bengal' as state, 'Siliguri' as city, 'Siliguri-Golden Enclave' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'D' as store_category
union select 'A587' as store_id, 'Bihar' as state, 'Patna' as city, 'Patna-Frazer Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'D' as store_category
union select 'A642' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Vega City' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'D' as store_category
union select 'A621' as store_id, 'Goa' as state, 'Mapusa' as city, 'Goa-Mapusa' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'D' as store_category
union select 'A552' as store_id, 'Uttar Pradesh' as state, 'Kanpur' as city, 'Kanpur-Moti Jheel' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'D' as store_category
union select 'A589' as store_id, 'West Bengal' as state, 'Siliguri' as city, 'Siliguri-Dwarika Mahabir Square' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'E' as store_category
union select 'A459' as store_id, 'Punjab' as state, 'TarnTaran' as city, 'Tarn Taran-Amritsar road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'E' as store_category
union select 'A653' as store_id, 'West Bengal' as state, 'Jalpaiguri' as city, 'Jalpaiguri-Krishna Plaza' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'E' as store_category
union select 'A637' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-Airoli' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Ratnakar Patil' as cm_name, 'D' as store_category
union select 'A559' as store_id, 'Maharashtra' as state, 'Nagpur' as city, 'Nagpur-Manish Nagar' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Vishal Phatak' as cm_name, 'D' as store_category
union select 'A645' as store_id, 'Madhya Pradesh' as state, 'Narmadapuram' as city, 'Narmadapuram-Kothi Bazar' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'E' as store_category
union select 'A510' as store_id, 'Uttar Pradesh' as state, 'Saharanpur' as city, 'Saharanpur-Vasant Vihar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'E' as store_category
union select 'A673' as store_id, 'Uttar Pradesh' as state, 'Varanasi' as city, 'Varanasi-Sigra' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'D' as store_category
union select 'A435' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Kondhwa' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Sandeep Gogia' as cm_name, 'D' as store_category
union select 'T009' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Mira road' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A472' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Basavangudi' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Jafar Shaikh' as cm_name, 'D' as store_category
union select 'A662' as store_id, 'Bihar' as state, 'Darbhanga' as city, 'Darbhanga-Rajkumarganj Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A341' as store_id, 'Maharashtra' as state, 'Nashik' as city, 'Nashik-Pathardi Phata' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'D' as store_category
union select 'A450' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Odhav' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Sarbjeet Singh Bedi' as cm_name, 'D' as store_category
union select 'A651' as store_id, 'Tamil Nadu' as state, 'Coimbatore' as city, 'Coimbatore-Singanallur' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'A581' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-Kolar Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A541' as store_id, 'Andhra Pradesh' as state, 'Kadapa' as city, 'Kadapa-Koti Reddy Circle' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'E' as store_category
union select 'A360' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Ratan Khand' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'E' as store_category
union select 'A668' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Gaurav Path' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'D' as store_category
union select 'A650' as store_id, 'Tamil Nadu' as state, 'Madurai' as city, 'Madurai-100 Feet Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'A616' as store_id, 'Kerala' as state, 'Kochi' as city, 'Kochi-Thrippunithura' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'D' as store_category
union select 'A576' as store_id, 'Maharashtra' as state, 'Pune' as city, 'Pune-Moshi' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Bashruddin Sayyad' as cm_name, 'D' as store_category
union select 'A485' as store_id, 'Bihar' as state, 'Ara' as city, 'Ara-Katira Station Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A408' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-KPHB' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'T007' as store_id, 'Gujarat' as state, 'Palanpur' as city, 'Palanpur-Abu Road' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'T015' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Nagarbhavi 2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A617' as store_id, 'Telangana' as state, 'Hanamkonda' as city, 'Hanamkonda-Subedari' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Manish Gunda' as cm_name, 'D' as store_category
union select 'A404' as store_id, 'Andhra Pradesh' as state, 'Kakinada' as city, 'Kakinada-Bhanugudi Junction' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Naresh Kumar Kommuru' as cm_name, 'E' as store_category
union select 'T014' as store_id, 'Madhya Pradesh' as state, 'Jabalpur' as city, 'Jabalpur-Vijay Nagar 2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A670' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Ramphal Chowk' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'D' as store_category
union select 'T004' as store_id, 'Gujarat' as state, 'Ahmedabad' as city, 'Ahmedabad-Vastral' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A434' as store_id, 'Haryana' as state, 'Palwal' as city, 'Palwal-Mathura Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'D' as store_category
union select 'A401' as store_id, 'Maharashtra' as state, 'Thane' as city, 'Thane-Hiranandani Estate' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Deepak Vishwakarma' as cm_name, 'D' as store_category
union select 'A655' as store_id, 'Gujarat' as state, 'Godhra' as city, 'Godhra-Dahod Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'E' as store_category
union select 'A605' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Basaveshwar Nagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Mohammed Ehiya' as cm_name, 'D' as store_category
union select 'A517' as store_id, 'Madhya Pradesh' as state, 'Dewas' as city, 'Dewas-Gomti Nagar' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'E' as store_category
union select 'A622' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Uttam Nagar' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Pratish Sidana' as cm_name, 'D' as store_category
union select 'A689' as store_id, 'Rajasthan' as state, 'Jaipur' as city, 'Jaipur-Jagatpura' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'E' as store_category
union select 'A623' as store_id, 'Andhra Pradesh' as state, 'Nellore' as city, 'Nellore-Grand Trunk Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'D' as store_category
union select 'A624' as store_id, 'Delhi' as state, 'Delhi' as city, 'Delhi-Wazirabad Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Aashish Kumar' as cm_name, 'D' as store_category
union select 'A447' as store_id, 'Telangana' as state, 'Secunderabad' as city, 'Secunderabad-West Marredpally' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Satish Kumar Shivapnor' as cm_name, 'D' as store_category
union select 'A700' as store_id, 'Uttar Pradesh' as state, 'Agra' as city, 'Agra-Fatehabad Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'E' as store_category
union select 'T016' as store_id, 'Tamil Nadu' as state, 'Hosur' as city, 'Hosur-Bagalur Road 2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A667' as store_id, 'Madhya Pradesh' as state, 'Bhopal' as city, 'Bhopal-New Market' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'D' as store_category
union select 'A688' as store_id, 'West Bengal' as state, 'CoochBehar' as city, 'Cooch Behar-Purnima Mansion' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'E' as store_category
union select 'A680' as store_id, 'Assam' as state, 'Guwahati' as city, 'Guwahati-Beltola 2' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'E' as store_category
union select 'A660' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Goregaon West' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Reshma Shaikh' as cm_name, 'C' as store_category
union select 'A456' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Annapurna Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A543' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Tiruvanchery' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'D' as store_category
union select 'A418' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-GN Chetty Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sailesh Arava' as cm_name, 'E' as store_category
union select 'A502' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Kilpauk' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A669' as store_id, 'West Bengal' as state, 'Kolkata' as city, 'Kolkata-EM Bypass' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'D' as store_category
union select 'A333' as store_id, 'Gujarat' as state, 'Vadodara' as city, 'Vadodara-Gotri' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Mihir Padhiya' as cm_name, 'E' as store_category
union select 'A632' as store_id, 'Bihar' as state, 'Muzaffarpur' as city, 'Muzaffarpur-Icon Plaza Mall' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A672' as store_id, 'Maharashtra' as state, 'Boisar' as city, 'Boisar-Ostwal Empire' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'D' as store_category
union select 'A656' as store_id, 'Madhya Pradesh' as state, 'Chhatarpur' as city, 'Chhatarpur-Khajuraho Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A648' as store_id, 'Uttar Pradesh' as state, 'Varanasi' as city, 'Varanasi-Airport Road Shivpur' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'D' as store_category
union select 'A525' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Borivali East M G Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Swapnil Kadge' as cm_name, 'C' as store_category
union select 'A658' as store_id, 'Meghalaya' as state, 'Shillong' as city, 'Shillong-Laitumkhrah' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'D' as store_category
union select 'A612' as store_id, 'Uttar Pradesh' as state, 'Agra' as city, 'Agra-Church Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Manoj Subedi' as cm_name, 'D' as store_category
union select 'A549' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Kattupakkam' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A463' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Aparna Mall' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'A693' as store_id, 'Rajasthan' as state, 'Udaipur' as city, 'Udaipur-Surajpole' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'E' as store_category
union select 'A609' as store_id, 'Punjab' as state, 'Ludhiana' as city, 'Ludhiana-Sukhmani Square' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Garg' as cm_name, 'D' as store_category
union select 'A678' as store_id, 'Bihar' as state, 'Gaya' as city, 'Gaya-Jail Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A575' as store_id, 'Rajasthan' as state, 'Bhiwadi' as city, 'Bhiwadi-Legend Centra Mall' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Nitin Naik' as cm_name, 'E' as store_category
union select 'A528' as store_id, 'Gujarat' as state, 'Jamnagar' as city, 'Jamnagar-Lalpur Road' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Girish Andipara' as cm_name, 'E' as store_category
union select 'A674' as store_id, 'Uttarakhand' as state, 'Dehradun' as city, 'Dehradun-Mall of Dehradun' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'Rohit Yadav' as rm_name, 'Abhishek Roy' as cm_name, 'D' as store_category
union select 'A652' as store_id, 'Chandigarh' as state, 'Chandigarh' as city, 'Chandigarh-Sector 07' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Nitin Mohla' as cm_name, 'D' as store_category
union select 'A702' as store_id, 'Tamil Nadu' as state, 'Tiruppur' as city, 'Tiruppur-Avinashi Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'T013' as store_id, 'Maharashtra' as state, 'Mumbai' as city, 'Mumbai-Churchgate' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A558' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Sanath Nagar' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'D' as store_category
union select 'A484' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Carmelaram' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Arpit Sharma' as cm_name, 'D' as store_category
union select 'A699' as store_id, 'Kerala' as state, 'Thiruvananthapuram' as city, 'Thiruvananthapuram - NH Bypass Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'T.Senthil Kumar' as cm_name, 'D' as store_category
union select 'A675' as store_id, 'Madhya Pradesh' as state, 'Neemuch' as city, 'Neemuch-Ambedkar Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'D' as store_category
union select 'A649' as store_id, 'Tamil Nadu' as state, 'Madurai' as city, 'Madurai-Iyer Bungalow' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'A526' as store_id, 'Uttar Pradesh' as state, 'Lucknow' as city, 'Lucknow-Aliganj Ring Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Satyendra Singh' as cm_name, 'D' as store_category
union select 'T017' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-RT Nagar 2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A464' as store_id, 'Telangana' as state, 'Hyderabad' as city, 'Hyderabad-Miyapur' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Sugandh Nair' as cm_name, 'D' as store_category
union select 'A511' as store_id, 'Karnataka' as state, 'Mysore' as city, 'Mysore-Temple Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Lokesha C' as cm_name, 'D' as store_category
union select 'A639' as store_id, 'Bihar' as state, 'Aurangabad' as city, 'Aurangabad-Old GT Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Amit Rajput' as cm_name, 'E' as store_category
union select 'A479' as store_id, 'Maharashtra' as state, 'Beed' as city, 'Beed-Shivaji Maharaj Chowk' as store_name, 'Jenniton Lobo' as zm_name, 'NA' as rm_name, 'Sachin Zavar' as cm_name, 'D' as store_category
union select 'A536' as store_id, 'Goa' as state, 'Panjim' as city, 'Panjim-Taleigaon' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'D' as store_category
union select 'A573' as store_id, 'Tamil Nadu' as state, 'Dharmapuri' as city, 'Dharmapuri-Salem Main Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'A698' as store_id, 'Maharashtra' as state, 'Ambernath' as city, 'Ambernath-Kalyan Badlapur Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'E' as store_category
union select 'A705' as store_id, 'Assam' as state, 'Tezpur' as city, 'Tezpur-Hospital Road' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Abhijeet Chatterjee' as cm_name, 'E' as store_category
union select 'A687' as store_id, 'Madhya Pradesh' as state, 'Jabalpur' as city, 'Jabalpur – Vijay Nagar' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Vikrant Singh' as cm_name, 'E' as store_category
union select 'A419' as store_id, 'Maharashtra' as state, 'Badlapur' as city, 'Badlapur-MIDC Road' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'D' as store_category
union select 'A709' as store_id, 'Maharashtra' as state, 'NaviMumbai' as city, 'Navi Mumbai-New Panvel East' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Rajeshwar Sharma' as cm_name, 'D' as store_category
union select 'A685' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Jahangirabad' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'E' as store_category
union select 'A387' as store_id, 'Gujarat' as state, 'Himatnagar' as city, 'Himatnagar-Motipura Circle' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Chirag Sutaria' as cm_name, 'E' as store_category
union select 'A694' as store_id, 'Maharashtra' as state, 'Shahad' as city, 'Shahad-Kalyan Ahmednagar Highway' as store_name, 'Jenniton Lobo' as zm_name, 'Inder Singh' as rm_name, 'Nishant Chouksey' as cm_name, 'E' as store_category
union select 'A717' as store_id, 'Karnataka' as state, 'Kalaburagi' as city, 'Kalaburagi-Sardar Vallabhai Patel Road' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Yogesh Rijhwani' as cm_name, 'E' as store_category
union select 'A603' as store_id, 'Karnataka' as state, 'Belagavi' as city, 'Belagavi-Nehru Nagar' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Archit Maheshwary' as cm_name, 'D' as store_category
union select 'A618' as store_id, 'West Bengal' as state, 'Burdwan' as city, 'Burdwan-Regent Crown' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Subham Kumar Das' as cm_name, 'E' as store_category
union select 'A661' as store_id, 'Tamil Nadu' as state, 'Dindigul' as city, 'Dindigul-Palani Road' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Manjunath Shivanand' as cm_name, 'E' as store_category
union select 'A497' as store_id, 'Uttar Pradesh' as state, 'Noida' as city, 'Noida-iThum’s Galleria' as store_name, 'Arshdeep Singh Sandhu' as zm_name, 'NA' as rm_name, 'Kalyan Mahato' as cm_name, 'D' as store_category
union select 'A712' as store_id, 'Madhya Pradesh' as state, 'Indore' as city, 'Indore-Ranjeet Hanuman' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Yogesh Sharma' as cm_name, 'E' as store_category
union select 'T012' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-KR Puram 2' as store_name, 'ZM 1 - TRiBE' as zm_name, 'Devendra Singh Solanki' as rm_name, 'CM-TRiBE' as cm_name, 'Apple' as store_category
union select 'A701' as store_id, 'Tamil Nadu' as state, 'Chennai' as city, 'Chennai-Ramapuram' as store_name, 'Jaison Thomas' as zm_name, 'NA' as rm_name, 'Hari Ganesh' as cm_name, 'D' as store_category
union select 'A703' as store_id, 'Karnataka' as state, 'Bangalore' as city, 'Bangalore-Yeshwanthpur' as store_name, 'Senthil Kumar' as zm_name, 'NA' as rm_name, 'Bharat Khubchandani' as cm_name, 'E' as store_category
union select 'A431' as store_id, 'Gujarat' as state, 'Surat' as city, 'Surat-Mota Varachha' as store_name, 'Jenniton Lobo' as zm_name, 'Vishal Chandekar' as rm_name, 'Deepak Punjabi' as cm_name, 'D' as store_category
union select 'A580' as store_id, 'Madhya Pradesh' as state, 'Vidisha' as city, 'Vidisha-Sanchi Road' as store_name, 'Davinder Bijla' as zm_name, 'NA' as rm_name, 'Sumit Rohira' as cm_name, 'E' as store_category
union select 'A677' as store_id, 'Odisha' as state, 'Bhubaneswar' as city, 'Bhubaneswar-Lewis Road' as store_name, 'Sanjivkumar Jangade' as zm_name, 'NA' as rm_name, 'Manish Rawat' as cm_name, 'E' as store_category),
lfr AS
  (SELECT lfr.reminder_id,
          fr.organization,
          fr.tz_offset AS tz_offset_sec,
          fr.form_id,
          l.location_name AS LOCATION,
          to_timestamp(lfr.reminded_at/1000) AS reminded_at,
          to_timestamp(lfr.reminder_window_end/1000) AS reminder_window_end,
          lfr.form_response_id,
          CASE
              WHEN responded_at = 0 THEN NULL
              ELSE to_timestamp(lfr.responded_at/1000)
          END AS responded_at
   FROM location_form_reminders lfr
   JOIN form_reminders fr ON fr.id = lfr.reminder_id
   JOIN locations l ON lfr.location_id = l.id
   WHERE fr.organization ILIKE 'croma%'
     AND location_name NOT IN ('HQ',
                               'KNOW')
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     ufr_base AS
  (SELECT DISTINCT ON (ufr.reminder_id,
                       ufr.user_id,
                       fr.form_id) ufr.reminder_id,
                      fr.organization,
                      fr.tz_offset AS tz_offset_sec,
                      fr.form_id,
                      ufr.user_id,
                      to_timestamp(ufr.reminded_at/1000) AS reminded_at,
                      to_timestamp(ufr.reminder_window_end/1000) AS reminder_window_end,
                      ufr.form_response_id,
                      CASE
                          WHEN responded_at = 0 THEN NULL
                          ELSE to_timestamp(ufr.responded_at/1000)
                      END AS responded_at
   FROM user_form_reminders ufr
   JOIN form_reminders fr ON fr.id = ufr.reminder_id
   WHERE fr.organization ILIKE 'croma%'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9
   ORDER BY 1,
            4,
            5,
            reminded_at,
            responded_at),
     ufr AS
  (SELECT ufr_base.reminder_id,
          ufr_base.organization,
          ufr_base.tz_offset_sec,
          ufr_base.form_id,
          ud.job_location AS LOCATION,
          ufr_base.reminded_at,
          ufr_base.reminder_window_end,
          ufr_base.form_response_id,
          ufr_base.responded_at
   FROM ufr_base
   JOIN user_details ud ON ufr_base.user_id = ud.uuid
   AND job_location NOT IN ('HQ',
                            'KNOW')
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9),
     base AS
  (SELECT *
   FROM lfr
   UNION SELECT *
   FROM ufr),
     fs AS
  (SELECT DISTINCT ON ((submit_date AT TIME ZONE 'Asia/Kolkata')::date,
                       form_id) fs.*
   FROM form_submissions fs
   WHERE fs.organization ILIKE 'croma%'
     AND LOCATION NOT IN ('HQ',
                          'KNOW')
   ORDER BY (submit_date AT TIME ZONE 'Asia/Kolkata')::date,
            form_id,
            submit_date)
SELECT base.organization AS "Organization",
lm.state as "State",
lm.city as "City",
lm.zm_name as "ZM",
lm.rm_name as "RM",
lm.cm_name as "CM",
       (base.reminded_at + interval '1 sec'*base.tz_offset_Sec)::date AS "Date",
       base.form_id AS "Routine KNID",
       n.title AS "Routine Name",
       lm.store_id||' - '||lm.store_name AS "Location",
       base.reminded_at + interval '1 sec'*base.tz_offset_Sec AS "Reminded At",
                                   CASE
                                       WHEN fs.submit_date AT TIME ZONE 'Asia/Kolkata' IS NULL THEN 'Missed'
                                       WHEN fs.submit_date AT TIME ZONE 'Asia/Kolkata' <= base.reminder_window_end THEN 'Done On Time'
                                       WHEN fs.submit_date AT TIME ZONE 'Asia/Kolkata' > base.reminder_window_end THEN 'Done Late'
                                       ELSE NULL
                                   END AS "Status",
								    CASE
                                       WHEN fs.submit_date AT TIME ZONE 'Asia/Kolkata' IS NULL THEN 0
                                       ELSE 1
                                   END AS "Completion",
                                   fs.response_id AS "Submission KNID"
FROM base
JOIN nuggets n ON base.form_id = n.id
LEFT OUTER JOIN fs ON fs.form_id = base.form_id
AND (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date = (base.reminded_at AT TIME ZONE 'Asia/Kolkata')::date
left outer join location_map lm on base."location" = lm.store_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8, 9, 10, 11, 12, 13, 14
ORDER BY 1,
         3,
         5,
         2,
         6
```

---

## Croma Compliance Check Trends_Checklists Compliance (Old).sql

**Tables referenced:** ROLES, acl, final_definition, form_reminders, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, loc, locations, lr, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, remarks, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Compliance Check Trends
-- Dashboard: Checklists Compliance (Old)
-- Category: Croma
-- Extracted: 2026-01-29 16:57:12
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT acl.store_id,
          right(l.location_name, length(l.location_name)-5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store_id = left(l.location_name, 4)
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id,
          lr.store_name,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
                  ELSE NULL
              END) AS "RM",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder_id
                  ELSE NULL
              END) AS "RM KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1,
            2
   ORDER BY 1),
     forms AS
  (SELECT id AS form_knid,
          regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
   FROM nuggets
   WHERE organization = 'croma-coma'
     AND is_deleted = 'false'
     AND id IN
       (SELECT DISTINCT form_id
        FROM form_reminders
        WHERE to_timestamp(sent_at/1000) at time zone 'Asia/Kolkata' >= date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days') AND to_timestamp(sent_at/1000) at time zone 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
          AND title NOT ILIKE 'Maintenance%'
          AND title NOT ILIKE 'Test%')),
     qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
                                                                  title,
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
                                                                                                                       title,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                        title,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question_type AS parent_q_type,
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
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   WHERE submit_date AT TIME ZONE 'Asia/Kolkata' >= date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days') AND submit_date AT TIME ZONE 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
     loc AS
  (SELECT fr.response_id,
          left(fr.response->>'name', 4) AS store_id
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   WHERE fd.q_type = 'location'),
     remarks AS
  (SELECT fr.response_id,
          fd.q_no,
          fr.response->>0 AS rem
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   WHERE fd.question ILIKE '%Remark%'
     AND mod(fd.q_no, 10000) > 0)
SELECT fd.form_knid AS "Form",
       fd.title AS "Routine Name",
       fr.response_id AS "Submission KNID",
       (fr.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS "Date",
       lm."ZM",
       lm."RM",
       lm."CM",
       lm.store_id AS "Store ID",
       lm.store_name AS "Store Name",
       fd.q_no AS "Q No",
       fd.question AS "CheckPoint",
       fr.response->'selected'->>0 AS "Result",
                                 remarks.rem AS "Rem",
                                 CASE
                                     WHEN fr.response->'selected'->>0 IN ('Yes',
                                                                          'WIP') THEN 1
                                     WHEN fr.response->'selected'->>0 IN ('No') THEN 0
                                     ELSE NULL
                                 END AS "Compliance"
FROM final_definition fd
JOIN fr ON fr.question_id = fd.qid
JOIN loc ON fr.response_id = loc.response_id
LEFT OUTER JOIN remarks ON div(remarks.q_no, 10000) = div(fd.q_no, 10000)
AND remarks.response_id = fr.response_id
LEFT OUTER JOIN lm ON loc.store_id = lm.store_id
JOIN acl ON lm.store_id = acl.store_id
WHERE fd.q_type = 'dropdown'
  AND fr.response -> 'selected'->>0 IN ('Yes',
                                        'No',
                                        'WIP',
                                        'NA')
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
ORDER BY 4,
         5,
         6
```

---

## Croma Compliance Check Trends_Routine Checks.sql

**Tables referenced:** ROLES, acl, final_definition, form_reminders, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, loc, locations, lr, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, remarks, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Compliance Check Trends
-- Dashboard: Routine Checks
-- Category: Croma
-- Extracted: 2026-01-29 16:57:12
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT acl.store_id,
          right(l.location_name, length(l.location_name)-5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store_id = left(l.location_name, 4)
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id,
          lr.store_name,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
                  ELSE NULL
              END) AS "RM",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder_id
                  ELSE NULL
              END) AS "RM KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1,
            2
   ORDER BY 1),
     forms AS
  (SELECT id AS form_knid,
          regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
   FROM nuggets
   WHERE organization = 'croma-coma'
     AND is_deleted = 'false'
     AND id IN
       (SELECT DISTINCT form_id
        FROM form_reminders
        WHERE to_timestamp(sent_at/1000) at time zone 'Asia/Kolkata' >= date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days') AND to_timestamp(sent_at/1000) at time zone 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
          AND title NOT ILIKE 'Maintenance%'
          AND title NOT ILIKE 'Test%')),
     qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
                                                                  title,
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
                                                                                                                       title,
                                                                                                                       CASE
                                                                                                                           WHEN qd.section_id = 'section' THEN 1
                                                                                                                           ELSE replace(section_id, 'section-', '')::integer
                                                                                                                       END AS section_no,
                                                                                                                       sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                                       section_id,
                                                                                                                       question_id AS parent_qid,
                                                                                                                       question_type AS parent_q_type,
                                                                                                                       def.key AS qid,
                                                                                                                       def.value->>'question_type' AS q_type,
                                                                                                                                   def.value->>'question' AS question
   FROM qdntwl_prework qd
   CROSS JOIN jsonb_Each(qd.q) def
   WHERE definition ->>'logic' IS NOT NULL),
     qd_table AS
  (/*Table type Questions in Forms - SqNo will be in between the parent SqNo for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                                        title,
                                                                                                        CASE
                                                                                                            WHEN qd.section_id = 'section' THEN 1
                                                                                                            ELSE replace(section_id, 'section-', '')::integer
                                                                                                        END AS section_no,
                                                                                                        sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                                        section_id,
                                                                                                        question_id AS parent_qid,
                                                                                                        question_type AS parent_q_type,
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
  (SELECT DISTINCT ON (response_id) *
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   WHERE submit_date AT TIME ZONE 'Asia/Kolkata' >= date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata' - interval '7 days') AND submit_date AT TIME ZONE 'Asia/Kolkata' < date_trunc('Day', CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
     loc AS
  (SELECT fr.response_id,
          left(fr.response->>'name', 4) AS store_id
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   WHERE fd.q_type = 'location'),
     remarks AS
  (SELECT fr.response_id,
          fd.q_no,
          fr.response->>0 AS rem
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   WHERE fd.question ILIKE '%Remark%'
     AND mod(fd.q_no, 10000) > 0)
SELECT fd.form_knid AS "Form",
       fd.title AS "Routine Name",
       fr.response_id AS "Submission KNID",
       (fr.submit_date AT TIME ZONE 'Asia/Kolkata')::date AS "Date",
       lm."ZM",
       lm."RM",
       lm."CM",
       lm.store_id AS "Store ID",
       lm.store_name AS "Store Name",
       fd.q_no AS "Q No",
       fd.question AS "CheckPoint",
       fr.response->'selected'->>0 AS "Result",
                                 remarks.rem AS "Rem",
                                 CASE
                                     WHEN fr.response->'selected'->>0 IN ('Yes',
                                                                          'WIP') THEN 1
                                     WHEN fr.response->'selected'->>0 IN ('No') THEN 0
                                     ELSE NULL
                                 END AS "Compliance"
FROM final_definition fd
JOIN fr ON fr.question_id = fd.qid
JOIN loc ON fr.response_id = loc.response_id
LEFT OUTER JOIN remarks ON div(remarks.q_no, 10000) = div(fd.q_no, 10000)
AND remarks.response_id = fr.response_id
LEFT OUTER JOIN lm ON loc.store_id = lm.store_id
JOIN acl ON lm.store_id = acl.store_id
WHERE fd.q_type = 'dropdown'
  AND fr.response -> 'selected'->>0 IN ('Yes',
                                        'No',
                                        'WIP',
                                        'NA')
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
ORDER BY 4,
         5,
         6
```

---

## Croma Compliance Check_Checklists Compliance (Old).sql

**Tables referenced:** acl, croma.checklist_compliance, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Compliance Check
-- Dashboard: Checklists Compliance (Old)
-- Category: Croma
-- Extracted: 2026-01-29 16:52:37
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id and ug.is_active = true
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  select cc.*
				  from acl
				  left outer join croma.checklist_compliance cc on acl.store_id = "Store ID"
				  where cc."Date" >=@{{:Croma Checklist Adoption.Date Range.START}}::timestamp and cc."Date" < @{{:Croma Checklist Adoption.Date Range.END}}::timestamp + interval '1 day'
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
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A474', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A508')
ORDER BY 4, 5, 6
```

---

## Croma Compliance Check_Checklists Compliance.sql

**Tables referenced:** acl, croma.checklist_compliance, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Compliance Check
-- Dashboard: Checklists Compliance
-- Category: Croma
-- Extracted: 2026-01-29 16:52:37
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id and ug.is_active = true
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  select cc.*
				  from acl
				  left outer join croma.checklist_compliance cc on acl.store_id = "Store ID"
				  where cc."Date" >=@{{:Croma Checklist Adoption.Date Range.START}}::timestamp and cc."Date" < @{{:Croma Checklist Adoption.Date Range.END}}::timestamp + interval '1 day'
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
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A474', 
'A512', 
'A520', 
'A554', 
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A704', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A508')
ORDER BY 4, 5, 6
```

---

## Croma Compliments_Compliments.sql

**Tables referenced:** base, form_responses, form_submissions, location_acl, organizations, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Croma Compliments
-- Dashboard: Compliments
-- Category: Croma
-- Extracted: 2026-01-29 16:54:13
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = @{{:OrganizationParameter}}
   and is_active = 'true'
  and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
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
td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}}),
base  as (SELECT (submit_date + td.diff)::date AS date,
          max(CASE
                  WHEN question_id = 'section-1' THEN response -> 'sender' ->> 'userId'
                  ELSE NULL
              END) AS giver,
          max(CASE
                  WHEN question_id = '-notes' THEN response ->> 0
                  ELSE NULL
              END) AS compliment,
          max(CASE
                  WHEN question_id = '-compliment-type' THEN response -> 'selected' ->> 0
                  ELSE NULL
              END) AS compliment_type,
          max(CASE
                  WHEN question_id = '-compliment-to' THEN response -> 0 -> 'contact' ->> 'userId'
                  ELSE NULL
              END) AS recipient,
          form_submissions.id AS compliment_id
   FROM form_responses
   JOIN form_submissions ON form_responses.form_submit_id = form_submissions.id
		  join td on form_submissions.organization = td.organization
   WHERE submit_date + td.diff between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
     AND form_submissions.form_id = '-compliment-form'
     AND form_submissions.organization = @{{:OrganizationParameter}}
        GROUP BY 1,
            form_submit_id,
            6)
			
			SELECT base.date AS "Compliment Date",
       base.compliment_type AS "Compliment Type",
       base.compliment AS "Compliment",
       recipient_details.first_name||recipient_details.last_name AS "Compliment Recipient Name",
       recipient_details.identifier AS "Compliment Recipient Employee ID",
       recipient_details.designation as "Compliment Recipient Designation",
       recipient_details.job_location AS "Compliment Recipient Outlet",
	   giver_details.first_name||giver_details.last_name AS "Compliment Giver Name",
       giver_details.identifier AS "Compliment Giver Employee ID",
       giver_details.designation as "Compliment Giver Designation",
       giver_details.job_location AS "Compliment Giver Outlet",
       base.compliment_id AS "Compliment Submit ID (KNOW Internal)"
	   from base
	   JOIN user_details giver_details ON base.giver = giver_details.uuid
JOIN user_details recipient_details ON base.recipient = recipient_details.uuid
join location_acl loc on loc.job_location = giver_details.job_location or loc.job_location = recipient_details.job_location
order by 1 desc, 2, 4, 8
```

---

## Croma OJT_Croma OJT.sql

**Tables referenced:** _fs, analytics_requests, assigned_users, certification_status, filtered, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, latest_user_raw, lm, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, role_holders, roles, tasks, td, total_assigned_count, user_details, user_response_summary

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Croma OJT
-- Dashboard: Croma OJT
-- Category: Croma
-- Extracted: 2026-01-29 16:54:44
-- ============================================================

WITH lr AS (
  SELECT l.id,
         RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder
  FROM locations l
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Regional Manager', 'Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'croma-coma' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         MAX(CASE WHEN ROLE = 'Regional Manager' THEN holder END) AS "RM",
         MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
         MAX(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head"
  FROM lr
  GROUP BY 1
),
td AS (
  SELECT id AS organization,
         tzoffset, interval '1 min'*tzoffset AS diff
  FROM organizations
  WHERE id = 'croma-coma'
  GROUP BY 1, 2
),
forms AS (
  SELECT id AS form_knid,
         title AS form_name
  FROM nuggets n
  WHERE title ILIKE '%OJT Activities%'
    AND organization = 'croma-coma'
    AND is_deleted = false
),
qd_non_table_non_logic AS (
  SELECT nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
         CASE WHEN qd.question_type = 'section' THEN 0 ELSE sqno::integer*10000 END AS q_no,
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
         jsonb_array_elements(definition -> 'logic') -> 'questions' q
  FROM forms
  JOIN question_definitions qd ON qd.nugget_id = forms.form_knid
  WHERE qd.definition -> 'logic' IS NOT NULL
),
qd_non_table_with_logic AS (
  SELECT nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
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
  WHERE definition ->>'logic' IS NOT NULL
),
qd_table AS (
  SELECT nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
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
  WHERE qd.question_type IN ('table')
),
final_definition AS (
  SELECT * FROM qd_non_table_non_logic
  UNION ALL
  SELECT * FROM qd_non_table_with_logic
  UNION ALL
  SELECT * FROM qd_table
),
_fs AS (
  SELECT DISTINCT ON (response_id) form_submissions.*, form_name
  FROM forms
  JOIN form_submissions ON forms.form_knid = form_submissions.form_id
  ORDER BY response_id, id DESC
),
fs AS (
  SELECT * FROM _fs
  WHERE submit_date >= current_timestamp - interval '2 months'
),
fr AS (
  SELECT fs.organization,
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
  WHERE question_type NOT IN ('table','nested')
  UNION
  SELECT organization,
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
  FROM (
    SELECT fs.organization,
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
         jsonb_array_elements(response) WITH ORDINALITY AS base
    WHERE question_type = 'table'
  ) base1
  CROSS JOIN jsonb_each(base1.value) res
),
raw AS (
  SELECT fr.sno,
         fd.section_no,
         fd.q_no,
         fd.parent_question,
         fd.question,
         q_type,
         CASE
           WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
           WHEN fd.q_type IN ('dropdown','multiple_choice','linear_scale','audit') THEN fr.response -> 'selected'->>0
           WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY(
             SELECT jsonb_array_elements_text(fr.response->'selected')
             UNION SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText' ELSE NULL END
           ), ', ')
           WHEN fd.q_type IN ('date','datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
           WHEN fd.q_type IN ('long_text_field','single_text_field','qr_code','formula') THEN fr.response->>0
           WHEN fd.q_type IN ('user') THEN fr.response::text
           WHEN fd.q_type IN ('upload_mixed','upload_image','upload_video') THEN (fr.response)->0->>'response'
           WHEN fd.q_type IN ('signature','location','division','sub_division') THEN fr.response ->> 'name'
           ELSE NULL
         END AS response,
         CASE WHEN fd.q_type = 'section' THEN fr.response ELSE NULL END AS section_response,
         rn,
         form_name,
         fr.form_id,
         fr.form_submit_id,
         fr.response_id,
         fr.submit_date AS submit_date,
         fr.location,
         ud.division,
         ud.department,
         ud.identifier,
         ud.first_name,
         ud.designation,
         lm."Head",
         lm."ZM",
         lm."CM"
  FROM final_definition fd
  JOIN fr ON fr.qid = fd.qid AND fr.form_id = fd.form_knid
  JOIN user_details ud ON fr.user_id = ud.uuid
  JOIN td ON fr.organization = td.organization
  JOIN lm ON fr.location = lm.store_id
),
  filtered AS (
  SELECT 
    ud.uuid AS user_uuid,
    ud.identifier,
    ud.first_name,
    response,
    CASE WHEN LOWER(TRIM(response)) = 'yes' THEN 1 ELSE 0 END AS is_yes,
    CASE WHEN LOWER(TRIM(response)) = 'no' THEN 1 ELSE 0 END AS is_no
  FROM raw
  JOIN user_details ud ON raw.identifier = ud.identifier
  WHERE question ILIKE '%Has the new joinee understood and conducted all the activities as per standards?%'
),
  user_response_summary AS (
  SELECT 
    user_uuid,
    identifier,
    first_name,
    COUNT(*) AS total_responses,
    SUM(is_yes) AS yes_count,
    SUM(is_no) AS no_count
  FROM filtered
  GROUP BY user_uuid, identifier, first_name
),
  certification_status AS (
  SELECT 
    user_uuid,
    identifier,
    first_name,
    total_responses,
    yes_count,
    no_count,
    CASE 
      WHEN no_count > 0 THEN 'Not Certified'
      WHEN yes_count = 10 THEN 'Certified'
      WHEN yes_count < 10 THEN 'In Progress'
    END AS certification_status
  FROM user_response_summary
),
  assigned_users AS (
  SELECT DISTINCT ud.uuid AS user_uuid
  FROM tasks t
  JOIN analytics_requests ar ON t.id = ar.nugget_id
  JOIN user_details ud ON ar.user_id = ud.uuid
  JOIN nuggets n ON n.id = t.linked_form_id
  WHERE t.title LIKE 'OJT Activities - Set%'
    AND ar.event_id = 1
    AND n.title ILIKE '%OJT Activities%'
),
  latest_user_raw AS (
  SELECT DISTINCT ON (ud.uuid)
         ud.uuid AS user_uuid,
         raw.identifier,
         raw.first_name,
         raw.submit_date,
         raw.location,
         raw.form_name,
         raw.division,
         raw.department,
         raw.designation,
         raw."Head",
         raw."ZM",
         raw."CM"
  FROM raw
  JOIN user_details ud ON raw.identifier = ud.identifier
  WHERE raw.question ILIKE '%Has the new joinee understood and conducted all the activities as per standards?%'
  ORDER BY ud.uuid, raw.submit_date DESC
),

  total_assigned_count AS (
  SELECT COUNT(DISTINCT user_uuid) AS total_assigned_users
  FROM assigned_users
)

SELECT 
  cs.identifier,
  cs.first_name,
  cs.total_responses,
  cs.yes_count,
  cs.no_count,
  cs.certification_status,
  lur.submit_date,
  lur.location,
  lur.form_name,
  lur.division,
  lur.department,
  lur.designation,
  lur."Head",
  lur."ZM",
  lur."CM",
  COUNT(*) FILTER (WHERE cs.certification_status = 'Certified') OVER () AS certified_count,
  COUNT(*) FILTER (WHERE cs.certification_status = 'Not Certified') OVER () AS not_certified_count,
  COUNT(*) FILTER (WHERE cs.certification_status = 'In Progress') OVER () AS in_progress_count,
  tac.total_assigned_users,
  ROUND(
    COUNT(*) FILTER (WHERE cs.certification_status = 'Certified') OVER () * 100.0 / 
    NULLIF(tac.total_assigned_users, 0), 2
  ) AS certification_percentage
FROM certification_status cs
LEFT JOIN latest_user_raw lur ON cs.user_uuid = lur.user_uuid
RIGHT JOIN assigned_users au ON au.user_uuid = cs.user_uuid
CROSS JOIN total_assigned_count tac
```

---

## Croma Projects_Projects.sql

**Tables referenced:** ROLES, acl, analytics_requests, assignees, checkpoint_master_sheet_table, lm, locations, lr, ranked, role_holders, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Croma Projects
-- Dashboard: Projects
-- Category: Croma
-- Extracted: 2026-01-29 16:52:32
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
  lr AS
  (SELECT acl.store,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store = l.location_name
   LEFT JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
     AND r.name IN ('Cluster Manager',
                    'Head',
                    'Zonal Manager')
   JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1
   ORDER BY 1),
    t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
  TRIM(SPLIT_PART(title, ':', 2)) AS ops,
   SPLIT_PART(t.title, ':', 1) AS "Store Code",
   SPLIT_PART(t.ext_id, ':', 2) AS "Store Location",
   t.location_id AS "Task Location",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   notes as "Details",
          /*coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",*/
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							/*CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
    CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted'    																																																																											
                                                                                                                                                                                                                                                                                                     THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Not Started Task Count", 
   CASE
                                                                                                                                                                                                                                                                                               WHEN  t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                      THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Started Task Count",
                                                                                                                                                                                                                                                                                           /*CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
   ud.designation,
   COALESCE(
  NULLIF(JSON_EXTRACT_PATH_TEXT(ud.profile::json, 'userTags', 'subdepartment', '0', 'value'), ''),
  NULL
) AS subdepartment/*,
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality"*/
   FROM tasks t
   LEFT OUTER JOIN user_details ud on t.author = ud.uuid
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   /*left outer JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid*/
   WHERE t.is_deleted = 'false'
     --AND cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'croma-coma'
   and ud.identifier IN ('21914',
								   '67032',
								   'CSO035_CON')
  --and to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' >= '2025-01-01'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   --and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' > '2025-01-08'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23,24,25,26,27,28,29,30,31),
                           assignees AS (
  WITH ranked AS (
    SELECT
      t."Task KNID",
      initcap(ud.first_name || ' ' || ud.last_name) AS reassign_user,
      initcap(au.first_name || ' ' || au.last_name) AS author_user,
      COALESCE(ud.division, au.division) AS "State",
      COALESCE(ud.sub_division, au.sub_division) AS "City",
      COALESCE(ud.job_location, au.job_location) AS store,
      COALESCE(ud.designation, au.designation) AS designation,
      COALESCE(ud.department, au.department) AS department,
      COALESCE(
        NULLIF(JSON_EXTRACT_PATH_TEXT(ud.profile::json, 'userTags', 'subdepartment', '0', 'value'), ''),
        NULLIF(JSON_EXTRACT_PATH_TEXT(au.profile::json, 'userTags', 'subdepartment', '0', 'value'), '')
      ) AS subdepartment,
      ar.updated_at,
      ROW_NUMBER() OVER (PARTITION BY t."Task KNID" ORDER BY ar.updated_at ASC)  AS rn_first,
      ROW_NUMBER() OVER (PARTITION BY t."Task KNID" ORDER BY ar.updated_at DESC) AS rn_last
    FROM t
    LEFT JOIN analytics_requests ar 
           ON t."Task KNID" = ar.nugget_id 
          AND ar.event_id = 1
    LEFT JOIN user_details ud 
           ON ar.user_id = ud.uuid 
          AND ud.uuid != t.author
    LEFT JOIN user_details au 
           ON t.author = au.uuid
    WHERE (
      COALESCE(ud.job_location, au.job_location) IN (SELECT store FROM acl) 
      OR t.author = @{{:UuidParameter}}
    )
  )
  SELECT
    "Task KNID",
    COALESCE(MAX(CASE WHEN rn_first = 1 THEN reassign_user END), MAX(author_user)) AS old_assignee,
    COALESCE(MAX(CASE WHEN rn_last = 1 THEN reassign_user END), MAX(author_user))  AS assignee,
    MAX("State")        AS "State",
    MAX("City")         AS "City",
    MAX(store)          AS store,
    MAX(designation)    AS designation,
    MAX(department)     AS department,
    MAX(subdepartment)  AS subdepartment
  FROM ranked
  GROUP BY "Task KNID"
)
SELECT t.*,
       a.assignee             AS "Assignee",
       a.old_assignee         AS "Old Assignee",
       a."State",
       a."City",
       a.store                AS "Location",
       a.department           AS "Assignee Department",
       a.designation          AS "Assignee Designation",
       a.subdepartment        AS "Assignee Subdepartment"
FROM t
LEFT JOIN assignees a ON t."Task KNID" = a."Task KNID"
LEFT JOIN lm
  ON lm.store =
       t."Store Code" || '-' || t."Store Location"
ORDER BY 12 DESC, 25, 26, 27, 28, 29, 30, 24, 4
```

---

## Croma Registers Adoption_Digital Docket.sql

**Tables referenced:** acl, croma.register_adoptions, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Registers Adoption
-- Dashboard: Digital Docket
-- Category: Croma
-- Extracted: 2026-01-29 16:54:44
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and l.is_active = 'true'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and l.is_active = 'true'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  
				  select ra.* ,
				  CASE 
        WHEN ra."Register Name" = 'People Register - 1' THEN 'Staff Check-in & Check-out' 
		WHEN ra."Register Name" = 'RGP Register' THEN 'Returnable Gate Pass'
				WHEN ra."Register Name" = 'Key - 1 Register' THEN 'Key'
								WHEN ra."Register Name" = 'Staff Sale' THEN 'Staff Purchase'
																WHEN ra."Register Name" = 'Power Reading Register - 1' THEN 'Power Reading'
										WHEN ra."Register Name" = 'Visitor Log Register' THEN 'Visitor Check-in & Check-out'	
										WHEN ra."Register Name" = 'Uniform Register' THEN 'Uniform'
        ELSE ra."Register Name" 
    END AS "Register Name (Updated)",
	to_char(@{{:Date Range.START}}::date, 'DD-Mon-YYYY') as "Start Date",
	to_char(@{{:Date Range.END}}::date, 'DD-Mon-YYYY') as "End Date"
	from acl
				 left outer join croma.register_adoptions ra on acl.store_id = ra."Store ID"
				 where ra."Date" between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7, 8, 9, 10
		 having ("Store ID" ilike 'A%' or "Store ID" ilike 'T%')
   and "Store ID" not in ('A021', 
'A051', 
'A079', 
'A114', 
'A142', 
'A164', 
'A198', 
'A267', 
'A296', 
'A320', 
'A366', 
'A375', 
'A423', 
'A424', 
'A429', 
'A443', 
'A474', 
'A512', 
'A520',  
'A569', 
'A583', 
'A588', 
'A594', 
'A606', 
'A608', 
'A614', 
'A615', 
'A619', 
'A628', 
'A629', 
'A631', 
'A634', 
'A647', 
'A654', 
'A657', 
'A663', 
'A664', 
'A665', 
'A671', 
'A683', 
'A684', 
'A691', 
'A704', 
'A713', 
'A719', 
'A720', 
'A722', 
'A728', 
'A730', 
'A732', 
'A733', 
'A734', 
'A735', 
'A736', 
'A737', 
'A738', 
'A508')
ORDER BY 1,
         2,
         3,
         4,
         5,
         6,
         7
```

---

## Croma Safety Incidents_Safety Incidents.sql

**Tables referenced:** ROLES, acl, ds, fl, form_responses, form_submissions, fs, lm, locations, lr, organizations, role_holders, sc, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Safety Incidents
-- Dashboard: Safety Incidents
-- Category: Croma
-- Extracted: 2026-01-29 16:54:27
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and ug.is_active = 'true'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
td AS
  (SELECT id AS organization, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma' ),
     lr AS
  (SELECT l.id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name || ' ' || ud.last_name AS holder,
          ud."division"
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager',
                  'Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = 'true'
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true' ),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
          MAX("division") AS division,
          MAX(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
              END) AS "CM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'Head' THEN holder
              END) AS "Head",
          CASE
              WHEN lr.id ILIKE 'D%' THEN 'DC'
              WHEN lr.id ILIKE 'S%' THEN 'SO'
              ELSE 'Store'
          END AS "Location Type"
   FROM lr
   GROUP BY 1,
            2),
     t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "ID",
          t.title AS "Title",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
         TRIM((REGEXP_MATCH(coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name'), E'^Safety Incident - (.+?)(?: \\( |$)'))[1]) AS "Category",
          coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Form KNID",
          coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Form Submission KNID",
          coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Form Submission No",
          initcap(t.details->>'authorName') AS "Assigned By",
          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
   cu.identifier as emp_id,
                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Overdue Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'notStarted'
                                                                                                                                                                                    OR t.status ILIKE 'started'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   WHERE t.is_deleted = 'false'
     AND t.created_at BETWEEN extract(epoch
                                      FROM @{{:Date Range.START}}::TIMESTAMP)*1000 AND extract(epoch
                                                                                     FROM @{{:Date Range.END}}::TIMESTAMP)*1000
     AND t.organization = 'croma-coma'
     AND coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE 'Safety Incident%'
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
  26),
     fs AS
  (SELECT DISTINCT ON (response_id) response_id,
                      sno,
                      id
   FROM form_submissions fs
   WHERE fs.response_id IN
       (SELECT "Form Submission KNID"
        FROM t)
   ORDER BY response_id,
            id DESC),
     sc AS
  (SELECT DISTINCT ON (response_id) response_id,
                      response->'selected'->>0 AS "Sub Category"
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'dropdown'
   ORDER BY response_id,
            fr.id),
     fl AS
  (SELECT response_id,
          response->>'name' AS "Store",
                     response->>'id' AS store_id
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'location'),
    ds as
   (
   select response_id,
	 response->>0 as "Description"
	 FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'long_text_field'
   )
SELECT t.*,
       sc."Sub Category",
	   ds."Description",
       fl."Store",
       lm."Location Type",
       lm."Head",
       lm."ZM",
       lm."RM",
       lm."CM"
FROM t
LEFT OUTER JOIN fl ON t."Form Submission KNID" = fl.response_id
LEFT OUTER JOIN lm ON fl.store_id = lm.store_id
JOIN acl on fl.store_id = acl.store_id
LEFT OUTER JOIN sc ON t."Form Submission KNID" = sc.response_id
LEFT OUTER JOIN ds ON t."Form Submission KNID" = ds.response_id
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
			26,
			27,
			28,
			29,
			30,
			31,
			32,
			33,
			34
```

---

## Croma Safety Obs and Inc Tables_Safety Obs and Inc Tables.sql

**Tables referenced:** ROLES, acl, agg, fl, form_responses, form_submissions, fs, lm, locations, lr, organizations, role_holders, sc, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Safety Obs and Inc Tables
-- Dashboard: Safety Obs and Inc Tables
-- Category: Croma
-- Extracted: 2026-01-29 16:54:20
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store_id
  FROM (
    -- Direct user role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    WHERE rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
      )

    UNION

    -- Group role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND role_holder_type = 'group'
      AND ug.is_active = TRUE
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
      )

    UNION

    -- Job location
    SELECT job_location AS store_id
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = TRUE
      AND (
        substring(job_location FROM 2 FOR 3) ~ '^\d{3}$'
        OR job_location ILIKE '%SO%'
        OR job_location ILIKE '%DC%'
      )
      AND (
        (SELECT is_super_admin
         FROM user_details
         WHERE uuid = @{{:UuidParameter}})
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
  ) l
),
td AS
  (SELECT id AS organization, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma' ),
     lr AS
  (SELECT l.id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name || ' ' || ud.last_name AS holder,
          ud."division"
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager',
                  'Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = 'true'
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true' ),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
          MAX("division") AS division,
          MAX(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
              END) AS "CM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'Head' THEN holder
              END) AS "Head",
          CASE
              WHEN lr.id ILIKE 'D%' THEN 'DC'
              WHEN lr.id ILIKE 'S%' THEN 'SO'
              WHEN lr.id ILIKE '%i - SO%' THEN 'SO'
              ELSE 'Store'
          END AS "Location Type"
   FROM lr
   GROUP BY 1,
            2),
     t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "ID",
          t.title AS "Title",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   CASE
              WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' THEN 'Observation'
              WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' THEN 'Incident'
              ELSE NULL
          END AS "Type",
          CASE
              WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' THEN TRIM((REGEXP_MATCH(coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name'), E'^Safety Observation - (.+?)(?: \\( |$)'))[1])
              WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' THEN TRIM((REGEXP_MATCH(coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name'), E'^Safety Incident - (.+?)(?: \\( |$)'))[1])
              ELSE NULL
          END AS "Category",
          coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Form KNID",
          coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Form Submission KNID",
          coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Form Submission No",
          initcap(t.details->>'authorName') AS "Assigned By",
          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' and t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Observation Beyond TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' and t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Incident Beyond TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' and t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Observation Within TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' and t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) >= CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Incident Within TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' and t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Closed Observation Within TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' and t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Closed Incident Within TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%' and t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at > deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Closed Observation Beyond TAT Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%' and t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at > deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Closed Incident Beyond TAT Count"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   WHERE t.is_deleted = 'false'
     AND t.created_at BETWEEN
    extract(epoch FROM @{{:Date Range.START}}::timestamp) * 1000 AND
    extract(epoch FROM @{{:Date Range.END}}::timestamp + interval '1 day') * 1000
     AND t.organization = 'croma-coma'
     AND (coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Observation%'
          OR coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '%Incident%')
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
  27),
     fs AS
  (SELECT DISTINCT ON (response_id) response_id,
                      sno,
                      id
   FROM form_submissions fs
   WHERE fs.response_id IN
       (SELECT "Form Submission KNID"
        FROM t)
   ORDER BY response_id,
            id DESC),
     sc AS
  (SELECT DISTINCT ON (response_id) response_id,
                      response->'selected'->>0 AS "Sub Category"
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'dropdown'
   ORDER BY response_id,
            fr.id),
     fl AS
  (SELECT response_id,
          response->>'name' AS "Store",
                     response->>'id' AS store_id
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'location'),
   agg AS (
  SELECT
    fl.store_id,

    -- type-specific denominators (distinct task count by type)
    COUNT(DISTINCT t."Task KNID") FILTER (WHERE t."Type" = 'Observation') AS obs_count,
    COUNT(DISTINCT t."Task KNID") FILTER (WHERE t."Type" = 'Incident')    AS inc_count,

    -- observation numerators
    SUM(t."Closed Observation Within TAT Count")  FILTER (WHERE t."Type" = 'Observation') AS closed_obs_within_cnt,
    SUM(t."Closed Observation Beyond TAT Count")  FILTER (WHERE t."Type" = 'Observation') AS closed_obs_beyond_cnt,
    SUM(t."Open Observation Within TAT Count")    FILTER (WHERE t."Type" = 'Observation') AS open_obs_within_cnt,
    SUM(t."Open Observation Beyond TAT Count")    FILTER (WHERE t."Type" = 'Observation') AS open_obs_beyond_cnt,

    -- incident numerators
    SUM(t."Closed Incident Within TAT Count")    FILTER (WHERE t."Type" = 'Incident') AS closed_inc_within_cnt,
    SUM(t."Closed Incident Beyond TAT Count")    FILTER (WHERE t."Type" = 'Incident') AS closed_inc_beyond_cnt,
    SUM(t."Open Incident Within TAT Count")      FILTER (WHERE t."Type" = 'Incident') AS open_inc_within_cnt,
    SUM(t."Open Incident Beyond TAT Count")      FILTER (WHERE t."Type" = 'Incident') AS open_inc_beyond_cnt

  FROM t
  LEFT JOIN fl ON t."Form Submission KNID" = fl.response_id
  GROUP BY fl.store_id
)

SELECT
  t.*,
  sc."Sub Category",
  left(fl."Store", 4) as "Store Code",
  right(fl."Store", length(fl."Store")-5) as "Store Name",
  lm."Location Type",
  lm."Head",
  lm."ZM",
  lm."RM",
  lm."CM",

  -- raw counts (useful for debugging / validation)
  COALESCE(agg.obs_count, 0) AS "Observation Task Count",
  COALESCE(agg.inc_count, 0) AS "Incident Task Count",

  -- OBSERVATION % (type-specific denominator = obs_count)
  COALESCE( ROUND(100.0 * agg.closed_obs_within_cnt  / NULLIF(agg.obs_count,0), 2), 0) AS "Closed Obs Within TAT %",
  COALESCE( ROUND(100.0 * agg.closed_obs_beyond_cnt / NULLIF(agg.obs_count,0), 2), 0) AS "Closed Obs Beyond TAT %",
  COALESCE( ROUND(100.0 * agg.open_obs_within_cnt    / NULLIF(agg.obs_count,0), 2), 0) AS "Open Obs Within TAT %",
  COALESCE( ROUND(100.0 * agg.open_obs_beyond_cnt    / NULLIF(agg.obs_count,0), 2), 0) AS "Open Obs Beyond TAT %",

  -- INCIDENT % (type-specific denominator = inc_count)
  COALESCE( ROUND(100.0 * agg.closed_inc_within_cnt  / NULLIF(agg.inc_count,0), 2), 0) AS "Closed Inc Within TAT %",
  COALESCE( ROUND(100.0 * agg.closed_inc_beyond_cnt / NULLIF(agg.inc_count,0), 2), 0) AS "Closed Inc Beyond TAT %",
  COALESCE( ROUND(100.0 * agg.open_inc_within_cnt    / NULLIF(agg.inc_count,0), 2), 0) AS "Open Inc Within TAT %",
  COALESCE( ROUND(100.0 * agg.open_inc_beyond_cnt    / NULLIF(agg.inc_count,0), 2), 0) AS "Open Inc Beyond TAT %"

FROM t
LEFT OUTER JOIN fl ON t."Form Submission KNID" = fl.response_id
JOIN acl ON fl.store_id = acl.store_id
LEFT OUTER JOIN lm ON fl.store_id = lm.store_id
LEFT OUTER JOIN sc ON t."Form Submission KNID" = sc.response_id
LEFT OUTER JOIN agg ON fl.store_id = agg.store_id
```

---

## Croma Safety Observations-copy_1754404820_Safety Audits - Tasks.sql

**Tables referenced:** ROLES, acl, analytics_requests, assignees, lm, locations, lr, nuggets, organizations, role_holders, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Safety Observations-copy_1754404820
-- Dashboard: Safety Audits - Tasks
-- Category: Croma
-- Extracted: 2026-01-29 16:54:26
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT l.location_name AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and ug.is_active = 'true'
      UNION SELECT job_location AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
td AS
  (SELECT id AS organization, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma' ),
     lr AS
  (SELECT l.id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name || ' ' || ud.last_name AS holder,
          ud."division"
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager',
                  'Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = 'true'
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true' ),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
          MAX("division") AS division,
          MAX(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
              END) AS "CM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'Head' THEN holder
              END) AS "Head",
          CASE
              WHEN lr.id ILIKE 'D%' THEN 'DC'
              WHEN lr.id ILIKE 'S%' THEN 'SO'
              WHEN lr.id ILIKE 'T%' THEN 'TRIBE'
              ELSE 'Store'
          END AS "Location Type"
   FROM lr
   GROUP BY 1,
            2),
     t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "ID",
          t.title AS "Title",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
         TRIM((REGEXP_MATCH(coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name'), E'^Safety Observation - (.+?)(?: \\( |$)'))[1]) AS "Category",
          coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Form KNID",
          coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Form Submission KNID",
          coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Form Submission No",
          initcap(t.details->>'authorName') AS "Assigned By",
          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
   cu.identifier as "Emp ID",
                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Overdue Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'notStarted'
                                                                                                                                                                                    OR t.status ILIKE 'started'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                       t.location_id
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   WHERE t.is_deleted = 'false'
     AND to_timestamp(t.created_at/1000) BETWEEN @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'

     AND t.organization = 'croma-coma'
     AND (coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE 'H&S%'
     or coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE '10-10%'
		or  coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE 'SNAP%')
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
  26,27),
  assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
       lm."Location Type",
       lm."Head",
       lm."ZM",
       lm."RM",
       lm."CM",
	   a.assignee,
	   a.department,
n.title as form_name
FROM t
LEFT OUTER JOIN lm ON t.location_id = lm.store_id
Join acl on t.location_id = acl.store_id
LEFT OUTER JOIN assignees a on t."Task KNID" = a."Task KNID"
left outer join nuggets n on n.id = t."Form KNID"
```

---

## Croma Safety Observations_Safety Observations.sql

**Tables referenced:** ROLES, acl, ds, fl, form_responses, form_submissions, fs, lm, locations, lr, organizations, role_holders, sc, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Safety Observations
-- Dashboard: Safety Observations
-- Category: Croma
-- Extracted: 2026-01-29 16:54:19
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store_id
  FROM (
    -- Direct user role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    WHERE rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
      )

    UNION

    -- Group role
    SELECT l.location_name AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND role_holder_type = 'group'
      AND ug.is_active = TRUE
      AND (
        substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
        OR l.location_name ILIKE '%SO%'
        OR l.location_name ILIKE '%DC%'
      )

    UNION

    -- Job location
    SELECT job_location AS store_id
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = TRUE
      AND (
        substring(job_location FROM 2 FOR 3) ~ '^\d{3}$'
        OR job_location ILIKE '%SO%'
        OR job_location ILIKE '%DC%'
      )
      AND (
        (SELECT is_super_admin
         FROM user_details
         WHERE uuid = @{{:UuidParameter}})
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
  ) l
),
td AS
  (SELECT id AS organization, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma' ),
     lr AS
  (SELECT l.id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name || ' ' || ud.last_name AS holder,
          ud."division"
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager',
                  'Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = 'true'
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true' ),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
          MAX("division") AS division,
          MAX(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
              END) AS "CM",
          MAX(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
              END) AS "RM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'Head' THEN holder
              END) AS "Head",
          CASE
              WHEN lr.id ILIKE 'D%' THEN 'DC'
              WHEN lr.id ILIKE 'S%' THEN 'SO'
             WHEN lr.id ILIKE '%i - SO%' THEN 'SO'
              ELSE 'Store'
          END AS "Location Type"
   FROM lr
   GROUP BY 1,
            2),
     t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "ID",
          t.title AS "Title",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Closed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
         TRIM((REGEXP_MATCH(coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name'), E'^Safety Observation - (.+?)(?: \\( |$)'))[1]) AS "Category",
          coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Form KNID",
          coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Form Submission KNID",
          coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Form Submission No",
          initcap(t.details->>'authorName') AS "Assigned By",
          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
   cu.identifier as "Emp ID",
                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                               ELSE NULL
                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Overdue Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'notStarted'
                                                                                                                                                                                    OR t.status ILIKE 'started'
                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                           CASE
                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                               ELSE 0
                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   WHERE t.is_deleted = 'false'
     AND t.created_at BETWEEN extract(epoch
                                      FROM @{{:Date Range.START}}::TIMESTAMP)*1000 AND extract(epoch
                                                                                     FROM @{{:Date Range.END}}::TIMESTAMP)*1000
     AND t.organization = 'croma-coma'
     AND coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') ILIKE 'Safety Observation%'
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
  26),
     fs AS
  (SELECT DISTINCT ON (response_id) response_id,
                      sno,
                      id
   FROM form_submissions fs
   WHERE fs.response_id IN
       (SELECT "Form Submission KNID"
        FROM t)
   ORDER BY response_id,
            id DESC),
     sc AS
  (SELECT DISTINCT ON (response_id) response_id,
                      response->'selected'->>0 AS "Sub Category"
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'dropdown'
   ORDER BY response_id,
            fr.id),
     fl AS
  (SELECT response_id,
          response->>'name' AS "Store",
                     response->>'id' AS store_id
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'location'),
   ds as
   (
   select response_id,
	 response->>0 as "Description"
	 FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id
   WHERE fr.question_type = 'long_text_field'
   )
SELECT t.*,
       sc."Sub Category",
	   ds."Description",
       fl."Store",
       lm."Location Type",
       lm."Head",
       lm."ZM",
       lm."RM",
       lm."CM"
FROM t
LEFT OUTER JOIN fl ON t."Form Submission KNID" = fl.response_id
LEFT OUTER JOIN lm ON fl.store_id = lm.store_id
JOIN acl on fl.store_id = acl.store_id
LEFT OUTER JOIN sc ON t."Form Submission KNID" = sc.response_id
LEFT OUTER JOIN ds ON t."Form Submission KNID" = ds.response_id
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
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
			26,
			27,
			28,
			29,
			30,
			31,
			32,
			33,
			34
```

---

## Croma Shifts Adoption Trends_Shifts Adoption.sql

**Tables referenced:** ROLES, a, acl, att_ct, date_series, latest_shift_version, lm, locations, lr, public, role_holders, s, shifts_ct, time_events_clockin, user_details, user_groups, users, users_ct

**Original Query:**

```sql
-- Data Source: Croma Shifts Adoption Trends
-- Dashboard: Shifts Adoption
-- Category: Croma
-- Extracted: 2026-01-29 16:55:45
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and l.is_active = 'true'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
	  and l.is_active = 'true'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT acl.store_id,
          right(l.location_name, length(l.location_name)-5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store_id = left(l.location_name, 4)
  left  JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = 'true'
  left  JOIN ROLES r ON r.id = rh.role_id AND r.name IN ('Cluster Manager',
                    'Regional Manager',
                    'Zonal Manager')
   JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
     
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store_id,
          lr.store_name,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
                  ELSE NULL
              END) AS "RM",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder_id
                  ELSE NULL
              END) AS "RM KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1,
            2
   ORDER BY 1),
   users AS
  (SELECT left(job_location, 4) as store_id, uuid, initcap(department) as department, initcap(designation) as designation, created_at
   FROM user_details
   WHERE is_active = 'true'
     AND left(job_location, 4) in (select store_id from acl)),
     -- getting latest version of published shift here
     -- if it is deleted it will be directly published, so it will also get considered in this base query
     latest_shift_version as (
       select distinct on (shifts.shift_id) * from public."shifts_croma-coma" shifts
       where to_date(shift_day, 'YYYYMMDD') between date_trunc('day', current_timestamp at time zone 'Asia/Kolkata' - interval '7 days') and date_trunc('Day', current_timestamp at time zone 'Asia/Kolkata')
       and shifts.is_planning = false
       order by shifts.shift_id, shifts.created_at desc  
     ),
     s AS
  (SELECT to_date(shift_day, 'YYYYMMDD') AS shift_date,
          ud.store_id,
   ud.department,
   ud.designation,
          count(distinct(uuid)) AS users_with_roster_entry,
   count(distinct(case when leave_type_id is null then uuid else null end)) as users_with_shifts   
   FROM latest_shift_version s
   JOIN users ud ON s.user_id = ud.uuid and s.is_deleted != 'true'
   GROUP BY 1,
            2,
  3,
  4),
     a AS
  (SELECT to_date(shift_day, 'YYYYMMDD') AS shift_date,
          ud.store_id,
   ud.department,
   ud.designation,
          count(distinct(ud.uuid)) AS present_count
   FROM time_events_clockin teci
   JOIN users ud ON teci.uuid = ud.uuid
   WHERE to_date(shift_day, 'YYYYMMDD') between date_trunc('day', current_timestamp at time zone 'Asia/Kolkata' - interval '7 days')
   and current_timestamp at time zone 'Asia/Kolkata'
   GROUP BY 1,
            2,
  3,
  4),
     date_series AS
  (SELECT generate_series(date_trunc('day', current_timestamp at time zone 'Asia/Kolkata' - interval '7 days'), current_timestamp at time zone 'Asia/Kolkata' - interval '1 day', '1 day'::interval)::date AS schedule_date),
     users_ct AS
  (SELECT d.schedule_date,
          ud.store_id,
   ud.department,
   ud.designation,
          COUNT(DISTINCT ud.uuid)::numeric AS registered_users
   FROM date_series d
   LEFT JOIN users ud ON to_timestamp(ud.created_at/1000) AT TIME ZONE 'Asia/Kolkata' <= d.schedule_date
   GROUP BY 1,
            2,
  3,
  4),
     shifts_ct AS
  (SELECT d.schedule_date,
          s.store_id,
   s.department,
   s.designation,
          sum(s.users_with_roster_entry) AS users_with_roster_entry,
   sum(s.users_with_shifts) as users_with_shifts
   FROM date_series d
   LEFT JOIN s ON s.shift_date = d.schedule_date
   GROUP BY 1,
            2,
 3,
  4),
     att_ct AS
  (SELECT d.schedule_date,
          a.store_id,
   a.department,
   a.designation,
          sum(a.present_count) AS present_count
   FROM date_series d
   LEFT JOIN a ON a.shift_date = d.schedule_date
   GROUP BY 1,
            2,
  3,
  4)
SELECT ds.schedule_date as "Date",
       lm."ZM",
	   lm."RM",
	   lm."CM",
       uc.store_id as "Store ID",
       lm.store_name as "Store Name",
	   uc.department  as "Deparment",
	   uc.designation as "Designation",
       COALESCE(uc.registered_users, 0) AS "Regd Staff",
       COALESCE(sc.users_with_roster_entry, 0) AS "Scheduled Staff",
	   COALESCE(sc.users_with_shifts, 0) as "Staff with Shifts",
       COALESCE(ac.present_count, 0) AS "Attended Staff"
FROM date_series ds
LEFT JOIN users_ct uc ON ds.schedule_date = uc.schedule_date
LEFT JOIN shifts_ct sc ON ds.schedule_date = sc.schedule_date
AND sc.store_id = uc.store_id
and sc.department = uc.department
and sc.designation = uc.designation
LEFT JOIN att_ct ac ON ds.schedule_date = ac.schedule_date
AND ac.store_id = uc.store_id
and ac.department = uc.department
and ac.designation = uc.designation
left join lm on uc.store_id = lm.store_id
ORDER BY 1 desc,
         2,
         3,
         4,
		 5,
		 7,
		 8
```

---

## Croma Shifts Adoption_Shifts Adoption.sql

**Tables referenced:** LATERAL, a, acl, att_ct, date_series, latest_shift_version, leave_summary, lm, locations, lr, public, role_holders, roles, s, shifts_ct, time_events_clockin, user_details, user_groups, user_tags, users, users_ct

**Columns needing snake_case conversion:**

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Croma Shifts Adoption
-- Dashboard: Shifts Adoption
-- Category: Croma
-- Extracted: 2026-01-29 16:53:33
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store_id
  FROM (
    SELECT left(l.location_name, 4) AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = 'true'
    WHERE rh.role_holder_id = @{{:UuidParameter}}
      AND role_holder_type = 'user'
      AND substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'

    UNION

    SELECT left(l.location_name, 4) AS store_id
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = true
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}}
      AND role_holder_type = 'group'
      AND substring(l.location_name FROM 2 FOR 3) ~ '^\d{3}$'
      AND ug.is_active = 'true'

    UNION

    SELECT left(job_location, 4) AS store_id
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = 'true'
      AND substring(job_location FROM 2 FOR 3) ~ '^\d{3}$'
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
          SELECT DISTINCT user_id
          FROM user_groups ug1
          WHERE ug1.group_id IN (
            SELECT group_id FROM user_groups ug2
            WHERE ug2.user_id = @{{:UuidParameter}} AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ) l
),

lr AS (
  SELECT acl.store_id,
         right(l.location_name, length(l.location_name)-5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name||' '||ud.last_name AS holder
  FROM acl
  LEFT JOIN locations l ON acl.store_id = left(l.location_name, 4)
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id
    AND r.name IN ('Cluster Manager','Head','Zonal Manager')
  JOIN user_details ud ON rh.role_holder_id = ud.uuid
  WHERE l.organization = 'croma-coma'
    AND l.is_active = 'true'
    AND ud.is_active = 'true'
  ORDER BY 1,2
),

lm AS (
  SELECT lr.store_id,
         lr.store_name,
         max(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         max(CASE WHEN ROLE = 'Cluster Manager' THEN holder_id END) AS "CM KNID",
         max(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head",
         max(CASE WHEN ROLE = 'Head' THEN holder_id END) AS "Head KNID",
         max(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
         max(CASE WHEN ROLE = 'Zonal Manager' THEN holder_id END) AS "ZM KNID"
  FROM lr
  GROUP BY 1,2
),

-- base users for the stores in ACL
users AS (
  SELECT left(job_location, 4) as store_id,
         uuid,
         department,
         designation,
         created_at,
         profile
  FROM user_details
  WHERE is_active = 'true'
    AND left(job_location, 4) IN (SELECT store_id FROM acl)
),

-- per-user tags (category/brand)
user_tags AS (
  SELECT 
        ud.uuid,
        STRING_AGG(CASE WHEN ut.key = 'category' THEN tag.value->>'value' END, ', ')
            FILTER (WHERE ut.key = 'category') AS category,
        STRING_AGG(CASE WHEN ut.key = 'brand' THEN tag.value->>'value' END, ', ')
            FILTER (WHERE ut.key = 'brand') AS brand
    FROM users ud
    CROSS JOIN LATERAL jsonb_each(ud.profile->'userTags') ut
    CROSS JOIN LATERAL jsonb_array_elements(ut.value) AS tag
    GROUP BY ud.uuid
),

-- latest shift versions in date range
latest_shift_version AS (
  SELECT DISTINCT ON (shifts.shift_id) *
  FROM public."shifts_croma-coma" shifts
  WHERE to_date(shift_day, 'YYYYMMDD')
    BETWEEN @{{:Date Range.START}}::timestamp
        AND @{{:Date Range.END}}::timestamp + interval '1 day'
    AND shifts.is_planning = false
  ORDER BY shifts.shift_id, shifts.created_at DESC
),

s AS (
  SELECT to_date(shift_day, 'YYYYMMDD') AS shift_date,
         ud.store_id,
         ud.department,
         ud.designation,
         count(DISTINCT uuid) AS users_with_roster_entry,
         count(DISTINCT CASE WHEN leave_type_id IS NULL THEN uuid END) AS users_with_shifts
  FROM latest_shift_version s
  JOIN users ud ON s.user_id = ud.uuid AND s.is_deleted != 'true'
  GROUP BY 1,2,3,4
),

a AS (
  SELECT to_date(shift_day, 'YYYYMMDD') AS shift_date,
         ud.store_id,
         ud.department,
         ud.designation,
         count(DISTINCT ud.uuid) AS present_count
  FROM time_events_clockin teci
  JOIN users ud ON teci.uuid = ud.uuid
  WHERE to_date(shift_day, 'YYYYMMDD')
    BETWEEN @{{:Date Range.START}}::timestamp
        AND @{{:Date Range.END}}::timestamp + interval '1 day'
  GROUP BY 1,2,3,4
),

date_series AS (
  SELECT generate_series(
      @{{:Date Range.START}}::timestamp,
      @{{:Date Range.END}}::timestamp,
      '1 day'::interval
    )::date AS schedule_date
),

-- registered users and aggregated tags at the required grain
users_ct AS (
SELECT 
        d.schedule_date,
        ud.store_id,
        ud.department,
        ud.designation,
        COUNT(DISTINCT ud.uuid)::numeric AS registered_users,
        ut.category,
        ut.brand
    FROM date_series d
    LEFT JOIN users ud 
        ON to_timestamp(ud.created_at/1000) AT TIME ZONE 'Asia/Kolkata' <= d.schedule_date
    LEFT JOIN user_tags ut ON ud.uuid = ut.uuid
    GROUP BY 
        d.schedule_date, ud.store_id, ud.department, ud.designation, ut.category, ut.brand
),

shifts_ct AS (
  SELECT d.schedule_date,
         s.store_id,
         s.department,
         s.designation,
         SUM(s.users_with_roster_entry) AS users_with_roster_entry,
         SUM(s.users_with_shifts) AS users_with_shifts
  FROM date_series d
  LEFT JOIN s ON s.shift_date = d.schedule_date
  GROUP BY 1,2,3,4
),

att_ct AS (
  SELECT d.schedule_date,
         a.store_id,
         a.department,
         a.designation,
         SUM(a.present_count) AS present_count
  FROM date_series d
  LEFT JOIN a ON a.shift_date = d.schedule_date
  GROUP BY 1,2,3,4
),

leave_summary AS (
  SELECT to_date(shift_day, 'YYYYMMDD') AS shift_date,
         ud.store_id,
         ud.department,
         ud.designation,
         COUNT(DISTINCT CASE WHEN leave_type_id = 'off-day' THEN s.user_id END) AS weekly_off_count,
         COUNT(DISTINCT CASE WHEN leave_type_id IS NOT NULL AND leave_type_id <> 'off-day' THEN s.user_id END) AS leave_count
  FROM latest_shift_version s
  JOIN users ud ON s.user_id = ud.uuid
  WHERE s.is_deleted = 'false'
  GROUP BY 1,2,3,4
)

SELECT
  ds.schedule_date AS "Date",
  lm."Head",
  lm."ZM",
  lm."CM",
  uc.store_id AS "Store ID",
  lm.store_name AS "Store Name",
  uc.department AS "Deparment",
  uc.designation AS "Designation",
  COALESCE(uc.registered_users, 0) AS "Regd Staff",
  COALESCE(sc.users_with_roster_entry, 0) AS "Scheduled Staff",
  COALESCE(sc.users_with_shifts, 0) AS "Staff with Shifts",
  COALESCE(ac.present_count, 0) AS "Attended Staff",
  COALESCE(ls.weekly_off_count, 0) AS "Weekly Offs",
  COALESCE(ls.leave_count, 0) AS "Leaves",
  -- aggregated tag columns
  COALESCE(uc.category, '') AS "Category",
  COALESCE(uc.brand, '') AS "Brand",
  to_char(@{{:Date Range.START}}::date, 'DD-Mon-YYYY') AS "Start Date",
  to_char(@{{:Date Range.END}}::date, 'DD-Mon-YYYY') AS "End Date"

FROM date_series ds
LEFT JOIN users_ct uc ON ds.schedule_date = uc.schedule_date
LEFT JOIN shifts_ct sc ON ds.schedule_date = sc.schedule_date
  AND sc.store_id = uc.store_id
  AND sc.department = uc.department
  AND sc.designation = uc.designation
LEFT JOIN att_ct ac ON ds.schedule_date = ac.schedule_date
  AND ac.store_id = uc.store_id
  AND ac.department = uc.department
  AND ac.designation = uc.designation
LEFT JOIN leave_summary ls ON ds.schedule_date = ls.shift_date
  AND ls.store_id = uc.store_id
  AND ls.department = uc.department
  AND ls.designation = uc.designation
LEFT JOIN lm ON uc.store_id = lm.store_id

WHERE uc.department NOT IN (
  'Administration', 'Customer Service', 'Human Resources', 'KNOW',
  'Finance', 'Learning', 'Security', 'Supply Chain'
)
AND uc.store_id NOT IN (
  'A021','A051','A079','A114','A142','A164','A198','A267','A296','A320','A366','A375','A423','A424','A429','A443','A474','A512','A520','A554','A569','A583','A588','A594','A606','A608','A614','A615','A619','A628','A629','A631','A634','A647','A654','A657','A663','A664','A665','A671','A683','A684','A691','A704','A713','A719','A720','A722','A728','A730','A732','A733','A734','A735','A736','A737','A738','T020'
)

ORDER BY 1 DESC, 2, 3, 4, 5, 7, 8
```

---

## Croma Staff Entry and Exit Log_Entry and Exit Logs.sql

**Tables referenced:** acl, croma.entry_exit_logs, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Croma Staff Entry and Exit Log
-- Dashboard: Entry and Exit Logs
-- Category: Croma
-- Extracted: 2026-01-29 16:57:00
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  
				  select exl.* from
				  acl
				 left outer join croma.entry_exit_logs exl on acl.store_id = exl."Store ID"
				 WHERE TO_DATE(exl."Date", 'YYYY-MM-DD') 
      BETWEEN @{{:Date Range.START}}::DATE 
      AND @{{:Date Range.END}}::DATE + INTERVAL '1 day'
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7, 8,9,10,11,12,13,14,15,16,17,18
ORDER BY 1,
         2,
         3,
         4,
         5,
         6,
         7
```

---

## Croma Tasks-copy_1742185772_NSO.sql

**Tables referenced:** ROLES, acl, analytics_requests, assignees, checkpoint_master_sheet_table, lm, locations, lr, ranked, role_holders, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Croma Tasks-copy_1742185772
-- Dashboard: NSO
-- Category: Croma
-- Extracted: 2026-01-29 16:52:40
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
  lr AS
  (SELECT acl.store,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store = l.location_name
   LEFT JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
     AND r.name IN ('Cluster Manager',
                    'Head',
                    'Zonal Manager')
   JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1
   ORDER BY 1),
    t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
CASE 
    -- Extract second segment by both patterns
    WHEN COALESCE(
        NULLIF(TRIM(SPLIT_PART(ext_id, ':', 2)), ''),
        NULLIF(TRIM(SPLIT_PART(ext_id, '-', 2)), '')
    ) = 'Operational'
    AND SPLIT_PART(t.title, ':', 1) IN ('A659', 'A718', 'A721', 'A726')
    THEN 'Snaglist'
    WHEN COALESCE(
        NULLIF(TRIM(SPLIT_PART(ext_id, ':', 2)), ''),
        NULLIF(TRIM(SPLIT_PART(ext_id, '-', 2)), '')
    ) <> ''
    THEN COALESCE(
        NULLIF(TRIM(SPLIT_PART(ext_id, ':', 2)), ''),
        NULLIF(TRIM(SPLIT_PART(ext_id, '-', 2)), '')
    )
    ELSE NULL
END AS "ops",
   SPLIT_PART(t.title, ':', 1) AS "Store Code",
   SPLIT_PART(t.title, ':', 2) AS "Store Location",
    SPLIT_PART(t.title, ':', 1) || ':' || SPLIT_PART(t.title, ':', 2) AS "Task Location",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   notes as "Details",
          /*coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",*/
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							/*CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
    CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted'    																																																																											
                                                                                                                                                                                                                                                                                                     THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Not Started Task Count", 
   CASE
                                                                                                                                                                                                                                                                                               WHEN  t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                      THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Started Task Count",
                                                                                                                                                                                                                                                                                           /*CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
   ud.designation,
   COALESCE(
  NULLIF(JSON_EXTRACT_PATH_TEXT(ud.profile::json, 'userTags', 'subdepartment', '0', 'value'), ''),
  NULL
) AS subdepartment/*,
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality"*/
   FROM tasks t
   LEFT OUTER JOIN user_details ud on t.author = ud.uuid
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   /*left outer JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid*/
   WHERE t.is_deleted = 'false'
     --AND cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'croma-coma'
   and ud.designation IN ('Associate-New Store Opening',
								   'NSO Manager',
								   'Lead-NSO',
						 'Assistant Manager-NSO, Retail Services Group',
'Senior Manager-NSO, Retail Services Group',
'General Manager-NSO, Retail Services Group')
   AND SPLIT_PART(t.title, ':', 1) ~ '^[ATZ][0-9]{3}$'
  --and to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' >= '2025-01-01'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   --and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' > '2025-01-08'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23,24,25,26,27,28,29,30,31),
                           assignees AS (
  WITH ranked AS (
    SELECT
      t."Task KNID",
      initcap(ud.first_name || ' ' || ud.last_name) AS reassign_user,
      initcap(au.first_name || ' ' || au.last_name) AS author_user,
      COALESCE(ud.division, au.division) AS "State",
      COALESCE(ud.sub_division, au.sub_division) AS "City",
      COALESCE(ud.job_location, au.job_location) AS store,
      COALESCE(ud.designation, au.designation) AS designation,
      COALESCE(ud.department, au.department) AS department,
      COALESCE(
        NULLIF(JSON_EXTRACT_PATH_TEXT(ud.profile::json, 'userTags', 'subdepartment', '0', 'value'), ''),
        NULLIF(JSON_EXTRACT_PATH_TEXT(au.profile::json, 'userTags', 'subdepartment', '0', 'value'), '')
      ) AS subdepartment,
      ar.updated_at,
      ROW_NUMBER() OVER (PARTITION BY t."Task KNID" ORDER BY ar.updated_at ASC)  AS rn_first,
      ROW_NUMBER() OVER (PARTITION BY t."Task KNID" ORDER BY ar.updated_at DESC) AS rn_last
    FROM t
    LEFT JOIN analytics_requests ar 
           ON t."Task KNID" = ar.nugget_id 
          AND ar.event_id = 1
    LEFT JOIN user_details ud 
           ON ar.user_id = ud.uuid 
          AND ud.uuid != t.author
    LEFT JOIN user_details au 
           ON t.author = au.uuid
    WHERE (
      COALESCE(ud.job_location, au.job_location) IN (SELECT store FROM acl) 
      OR t.author = @{{:UuidParameter}}
    )
  )
  SELECT
    "Task KNID",
    COALESCE(MAX(CASE WHEN rn_first = 1 THEN reassign_user END), MAX(author_user)) AS old_assignee,
    COALESCE(MAX(CASE WHEN rn_last = 1 THEN reassign_user END), MAX(author_user))  AS assignee,
    MAX("State")        AS "State",
    MAX("City")         AS "City",
    MAX(store)          AS store,
    MAX(designation)    AS designation,
    MAX(department)     AS department,
    MAX(subdepartment)  AS subdepartment
  FROM ranked
  GROUP BY "Task KNID"
)
SELECT t.*,
       a.assignee             AS "Assignee",
       a.old_assignee         AS "Old Assignee",
       a."State",
       a."City",
       a.store                AS "Location",
       a.department           AS "Assignee Department",
       a.designation          AS "Assignee Designation",
       a.subdepartment        AS "Assignee Subdepartment"
FROM t
LEFT JOIN assignees a ON t."Task KNID" = a."Task KNID"
LEFT JOIN lm
  ON lm.store =
       t."Store Code" || '-' || t."Store Location"
--WHERE a.store IN (SELECT store FROM acl) OR author = @{{:UuidParameter}}
--AND "Planned Start" >= '2025-01-01'
WHERE 1=1
AND NOT (
       ("Store Code" = 'A588' AND "ops" IN ('Fitout', 'Trigger'))
    OR ("Store Code" = 'A629' AND "ops" = 'Snaglist')
    OR ("Store Code" = 'A631' AND "ops" = 'Snaglist')
    OR ("Store Code" = 'A664' AND "ops" = 'Fitout')
    OR ("Store Code" = 'A665' AND "ops" = 'Fitout')
    OR ("Store Code" = 'A683' AND "ops" IN ('Fitout', 'Snaglist'))
)
ORDER BY 12 DESC, 25, 26, 27, 28, 29, 30, 24, 4
```

---

## Croma Tasks_Tasks.sql

**Tables referenced:** ROLES, acl, analytics_requests, assignees, checkpoint_master_sheet_table, lm, locations, lr, role_holders, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Croma Tasks
-- Dashboard: Tasks
-- Category: Croma
-- Extracted: 2026-01-29 16:56:55
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
  lr AS
  (SELECT acl.store,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store = l.location_name
   LEFT JOIN role_holders rh ON l.id = rh.location_id and rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
     AND r.name IN ('Cluster Manager',
                    'Head',
                    'Zonal Manager')
   JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.store,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lr
   GROUP BY 1
   ORDER BY 1),
    t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   notes as "Details",
          /*coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",*/
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AT TIME ZONE 'Asia/Kolkata' AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) AT TIME ZONE 'Asia/Kolkata'
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							/*CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           /*CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",*/
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image"/*,
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at at time zone 'Asia/Dubai' as "Audited At",
   cms.checkpoint as "Checkpoint",
   cms.criticality as "Criticality"*/
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   /*left outer JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid*/
   WHERE t.is_deleted = 'false'
     --AND cms.audit_submitted_at BETWEEN @{{:Date Range.START}}::timestamp AND @{{:Date Range.END}}::timestamp + interval '1 day'
     AND t.organization = 'croma-coma'
  and to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' >= '2025-01-01'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
   and to_timestamp(t.created_at/1000) AT TIME ZONE 'Asia/Kolkata' > '2025-01-08'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
   ud.division as "State",
   ud.sub_division as "City",
                      ud.job_location as store,
   ud.designation,
   ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
       assignees.assignee AS "Assignee",
		   lm."ZM",
		   lm."CM",
		   lm."Head",
	   assignees."State",
	   assignees."City",
	   assignees.store as "Location",
	   	   assignees.department AS "Assignee Department",
		   assignees.designation as "Assignee Designation"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
left outer join lm on assignees.store = lm.store
where assignees.store in (select store from acl) or author = @{{:UuidParameter}}
--and "Planned Start" >= '2025-01-01'
order by 12 desc, 25, 26, 27, 28, 29, 30, 31,24, 4
```

---

## Issues Dump_Croma Issues Dump.sql

**Tables referenced:** DATE_TRUNC, NOW, issues, user_details

**Original Query:**

```sql
-- Data Source: Issues Dump
-- Dashboard: Croma Issues Dump
-- Category: Croma
-- Extracted: 2026-01-29 16:54:00
-- ============================================================

SELECT 
    CONCAT(uda.first_name, ' ', uda.last_name) AS reporter,
    uda.identifier AS "Reporter Identifier",
    uda.designation AS "Reporter Designation",
    uda.department AS "Reporter Department",
    uda.division AS "Reporter Division",
    uda.sub_division AS "Reporter Sub Division",
    uda.job_location AS "Reporter Location",
    TO_CHAR(TO_TIMESTAMP(i.created_at / 1000) AT TIME ZONE 'Asia/Kolkata', 'DD-MM-YYYY') AS "Reported At",
    i.sno AS "Issue ID",
    i.title AS "Issue Title",
    i.category_name AS "Issue Type",
    i.severity AS Severity,
    i.status AS "Current Status",
    i.location_id AS "Issue Location",
    i.description AS "Issue Description",
    CONCAT(udr.first_name, ' ', udr.last_name) AS Resolver,
    udr.identifier AS "Resolver Identifier",
    udr.designation AS "Resolver Designation",
    udr.department AS "Resolver Department",
    udr.division AS "Resolver Division",
    udr.sub_division AS "Resolver Sub Division",
    udr.job_location AS "Resolver Location",
    TO_CHAR(TO_TIMESTAMP(i.closed_at / 1000) AT TIME ZONE 'Asia/Kolkata', 'DD-MM-YYYY') AS "Resolved At"
FROM issues AS i
JOIN user_details AS uda 
    ON i.author = uda.uuid
LEFT JOIN user_details AS udr 
    ON i.closed_by = udr.uuid
WHERE i.organization = 'croma-coma'
  AND i.is_deleted = FALSE
  AND i.created_at >= EXTRACT(EPOCH FROM DATE_TRUNC('year', CURRENT_DATE)) * 1000
  AND i.created_at <= EXTRACT(EPOCH FROM NOW()) * 1000
```

---

## Maintainence-req-croma_Maintenance Requests.sql

**Tables referenced:** ROLES, acl, completed_status, costs, form_responses, form_submissions, issue_list, issues, issues_expanded, issues_q, jsonb_each, lm, locations, lrn, nuggets, question_definitions, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Maintainence-req-croma
-- Dashboard: Maintenance Requests
-- Category: Croma
-- Extracted: 2026-01-29 16:55:51
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store
  FROM (
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = 'true'
    WHERE rh.role_holder_id = @{{:UuidParameter}} AND role_holder_type = 'user'
    UNION
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}} AND role_holder_type = 'group'
    UNION
    SELECT job_location AS store
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = 'true'
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
          SELECT DISTINCT user_id
          FROM user_groups ug1
          WHERE ug1.group_id IN (
            SELECT group_id
            FROM user_groups ug2
            WHERE ug2.user_id = @{{:UuidParameter}} AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ) l
),
lrn AS (
  SELECT acl.store,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name||' '||ud.last_name AS holder
  FROM acl
  LEFT OUTER JOIN locations l ON acl.store = l.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN ROLES r ON r.id = rh.role_id AND r.name IN ('Regional Maintenance', 'Cluster Maintenance')
  JOIN user_details ud ON rh.role_holder_id = ud.uuid
  WHERE l.organization = 'croma-coma'
    AND l.is_active = 'true'
    AND ud.is_active = 'true'
  ORDER BY 1,2
),
lm AS (
  SELECT lrn.store,
         max(CASE WHEN ROLE = 'Cluster Maintenance' THEN holder ELSE NULL END) AS "CMM",
         max(CASE WHEN ROLE = 'Cluster Maintenance' THEN holder_id ELSE NULL END) AS "CMM KNID",
         max(CASE WHEN ROLE = 'Regional Maintenance' THEN holder ELSE NULL END) AS "RMM",
         max(CASE WHEN ROLE = 'Regional Maintenance' THEN holder_id ELSE NULL END) AS "RMM KNID"
  FROM lrn
  GROUP BY 1
  ORDER BY 1
),
issue_list AS (
    SELECT issues.sno AS "Ticket No",
           reporter.division AS "Region",
  issues.title as "Issues",
           reporter.sub_division AS "City",
           issues.location AS "Location",
           issues.severity AS "Severity",
           reporter.first_name || ' ' || reporter.last_name AS "Requester",
           reporter.identifier AS "Requested ID",
           reporter.uuid AS "Requester UUID",
           issues.category_name AS "Request Type",
           CASE 
               WHEN issues.status = 'open' THEN 'Pending' 
               ELSE 'Store Acknowledged' 
           END AS "Current Status",
           to_timestamp(issues.created_at::bigint/1000)  AS "Requested At",
           to_timestamp(issues.closed_at::bigint/1000)  AS "Responded At",
           to_timestamp(issues.closed_at::bigint/1000)  AS "Acknowledged At",
           issues.id AS issue_knid,
           issues.category_id AS issue_category_knid
    FROM issues
    LEFT OUTER JOIN user_details reporter ON issues.author = reporter.uuid
    LEFT OUTER JOIN user_details resolver ON issues.closed_by = resolver.uuid
    WHERE issues.organization = 'croma-coma'
      AND issues.is_deleted != 'true'
)/*
issues_q AS (
    SELECT nugget_id, def.key AS qid
    FROM question_definitions qds
    JOIN nuggets n ON qds.nugget_id = n.id
    CROSS JOIN jsonb_each(definition) AS def
    WHERE n.title ILIKE 'Issue Creation Form%'
      AND n.organization = 'croma-coma'
      AND def.value->>'question' ILIKE '%Issue%'
    GROUP BY 1, 2
),
issues_expanded AS (
    SELECT issues.id AS issue_knid,
           jsonb_array_elements_text(fr.response->'selected') AS "Issues"
    FROM issues
    JOIN form_submissions fs ON issues.open_form_response_id = fs.response_id
    JOIN form_responses fr ON fs.id = fr.form_submit_id
    JOIN issues_q ON fr.question_id = issues_q.qid
),
cost_q AS (
    SELECT nugget_id, def.key AS qid
    FROM question_definitions qds
    JOIN nuggets n ON qds.nugget_id = n.id
    CROSS JOIN jsonb_each(definition) AS def
    WHERE n.title ILIKE 'Issue Closure Form%'
      AND n.organization = 'croma-coma'
      AND def.value->>'question' ILIKE 'Cost%'
    GROUP BY 1, 2
),
costs AS (
    SELECT issues.id AS issue_knid,
           CASE
               WHEN fr.response->>0 ~ '^[-+]?\d+(\.\d+)?$' THEN (fr.response->>0)::numeric
               ELSE NULL
           END AS "Cost"
    FROM issues
    JOIN form_submissions fs ON issues.close_form_response_id = fs.response_id
    JOIN form_responses fr ON fs.id = fr.form_submit_id
    JOIN issues_q ON fr.question_id = issues_q.qid
),
completed_q AS (
    SELECT nugget_id, def.key AS qid
    FROM question_definitions qds
    JOIN nuggets n ON qds.nugget_id = n.id
    CROSS JOIN jsonb_each(definition) AS def
    WHERE n.title ILIKE 'Issue Closure Form%'
      AND n.organization = 'croma-coma'
      AND def.value->>'question' ILIKE '%completed?'
    GROUP BY 1, 2
)
completed_status AS (
    SELECT issues.id AS issue_knid,
           fr.response->'selected'->>0 AS "Were All Tasks Completed"
    FROM issues
    JOIN form_submissions fs ON issues.close_form_response_id = fs.response_id
    JOIN form_responses fr ON fs.id = fr.form_submit_id
    JOIN issues_q ON fr.question_id = issues_q.qid
)*/
SELECT issue_list."Ticket No",
       issue_list."Region",
       issue_list."City",
       issue_list."Requester",
       issue_list."Requested ID",
       issue_list."Requester UUID",
	   issue_list."Issues",
	   lm."CMM",
	   lm."RMM",
       CASE 
  WHEN issue_list."Request Type" IN (
     'Safety - Others',
     'Safety - Fire',
     'Safety - Electrical',
     'Maintenance - Others',
     'Maintenance - CCTV and DVR',
     'Maintenance - Plumbing',
     'Maintenance - Civil',
     'Maintenance - Mechanical',
     'Maintenance - Electrical'
  ) THEN issue_list."Request Type"
  ELSE 'Others'
END AS "Request Type",
       issue_list."Current Status",
       --costs."Cost",
       --completed_status."Were All Tasks Completed",
       issue_list."Requested At",
       issue_list."Responded At",
       issue_list."Acknowledged At",
       issue_list."Location",
       issue_list."Severity",
       issue_list.issue_knid
FROM issue_list
LEFT OUTER JOIN lm on issue_list."Location" = lm.store
--LEFT OUTER JOIN issues_expanded ON issue_list.issue_knid = issues_expanded.issue_knid
--LEFT OUTER JOIN costs ON issue_list.issue_knid = costs.issue_knid
--LEFT OUTER JOIN completed_status ON issue_list.issue_knid = completed_status.issue_knid
where  issue_list."City" NOT IN ('KNOW')
```

---

## Shop Floor - Tasks_Shop floor checklist.sql

**Tables referenced:** analytics_requests, assignees, checkpoint_master_sheet_table, lm, locations, lr, role_holders, roles, t, tasks, user_details

**Columns needing snake_case conversion:**

- `auditDetails` -> `audit_details` (alias: `audit_details AS "auditDetails"`)

- `authorName` -> `author_name` (alias: `author_name AS "authorName"`)

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `notStarted` -> `not_started` (alias: `not_started AS "notStarted"`)

- `plannedStartDate` -> `planned_start_date` (alias: `planned_start_date AS "plannedStartDate"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `resolvedPayload` -> `resolved_payload` (alias: `resolved_payload AS "resolvedPayload"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Shop Floor - Tasks
-- Dashboard: Shop floor checklist
-- Category: Croma
-- Extracted: 2026-01-29 16:54:20
-- ============================================================

WITH lr AS (
    SELECT
        l.id AS store_id,
        RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
        r.name AS role,
        ud.first_name || ' ' || ud.last_name AS holder
    FROM locations l
    LEFT JOIN role_holders rh ON rh.location_id = l.id AND rh.is_active = true
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager','Zonal Manager','Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = true
    WHERE l.organization = 'croma-coma' AND l.is_active = true
),
lm AS (
    SELECT
        store_id,
        store_name,
        MAX(CASE WHEN role = 'Cluster Manager' THEN holder END) AS "CM",
        MAX(CASE WHEN role = 'Zonal Manager' THEN holder END) AS "ZM",
        MAX(CASE WHEN role = 'Head' THEN holder END) AS "Head"
    FROM lr
    GROUP BY store_id, store_name
), t AS
  (SELECT t.id AS "Task KNID",
          t.ext_id AS "Task ID",
          t.title AS "Task",
          CASE
              WHEN t.status ILIKE 'completed' THEN 'Completed'
              WHEN t.status ILIKE 'notStarted' THEN 'Not Started'
              WHEN (t.status ILIKE 'started'
                    OR t.status ILIKE 'reopened') THEN 'In Progress'
          END AS "Status",
   CASE 
    WHEN t.status ILIKE 'completed' THEN 0
    ELSE DATE_PART('day', CURRENT_TIMESTAMP - to_timestamp(t.created_at/1000))
END AS "Aging",
          coalesce(t.details->'auditDetails'->>'name', t.details->'formDetails'->>'name') AS "Audit",
                                      coalesce(t.details->'auditDetails'->>'formId', t.details->'formDetails'->>'formId') AS "Audit KNID",
                                                                  coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') AS "Audit Report KNID",
                                                                                              coalesce(t.details->'auditDetails'->>'sno', t.details->'formDetails'->>'sno') AS "Audit Report No",
                                                                                                                          initcap(t.details->>'authorName') AS "Assigned By",
                                                                                                                          author,
                                                                                                                          to_timestamp((t.details->>'plannedStartDate')::bigint/1000) AS "Planned Start",
                                                                                                                                                                                                   initcap(su.first_name||' '||su.last_name) AS "Started By",
                                                                                                                                                                                                   initcap(cu.first_name||' '||cu.last_name) AS "Completed By",
                                                                                                                                                                                                   initcap(ru.first_name||' '||ru.last_name) AS "Reopened By",
                                                                                                                                                                                                   to_timestamp(t.created_at/1000) AS "Assigned At",
                                                                                                                                                                                                                                                to_timestamp(t.deadline/1000) AS "Deadline",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'notStarted' THEN to_timestamp(t.started_at/1000)
                                                                                                                                                                                                                                                                                           END AS "Started At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN to_timestamp(t.completed_at/1000)
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Completed At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    OR t.status ILIKE 'reopened' THEN to_timestamp(t.reopened_at/1000) 
                                                                                                                                                                                                                                                                                               ELSE NULL
                                                                                                                                                                                                                                                                                           END AS "Reopened At",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Overdue Task Count",
   																																																																							CASE
                                                                                                                                                                                                                                                                                               WHEN t.status NOT ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND to_timestamp(t.deadline/1000) < CURRENT_TIMESTAMP AND cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Overdue Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN (t.status ILIKE 'notStarted' 
   																																																																											or t.status ILIKE 'started'
                                                                                                                                                                                                                                                                                                     OR t.status ILIKE 'reopened') 
																																																																									 and cms.criticality = 'Critical' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Critical Open Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed' THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.status ILIKE 'completed'
                                                                                                                                                                                                                                                                                                    AND completed_at <= deadline THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "On Time Completed Task Count",
                                                                                                                                                                                                                                                                                           CASE
                                                                                                                                                                                                                                                                                               WHEN t.reopened_at IS NOT NULL THEN 1
                                                                                                                                                                                                                                                                                               ELSE 0
                                                                                                                                                                                                                                                                                           END AS "Reopened Task Count",
                                                                                                                                                                                                                                                                                           t.details->>'comment' AS "Completion Comment",
                                                                                                                                                                                                                                                                                                       t.details->'resolvedPayload'->'images'->0->>'url' AS "Completion Image",
                                                                                                                                                                                                                                                                                                                                                   coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) AS checkpoint_knid,
                                                                                                                                                                                                                                                                                                                                                                               cms.auditor_observations AS "Auditor Comment",
   cms.store_id as "Store",
   cms.theme as "Theme",
   cms.auditor_name as "Auditor",
   cms.audit_type as "Audit Type",
   cms.audit_submitted_at as "Audited At",
   replace(cms.CHECKPOINT, left(cms.checkpoint, position(':' in cms.checkpoint)+1), '') as "Checkpoint",
   left(cms.checkpoint, position(':' in cms.checkpoint)-1) as "Criticality",
    CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE result_score::numeric
                               END AS "Actual Score",
                               CASE
                                   WHEN result_score = '' THEN NULL
                                   ELSE max_score::numeric
                               END AS "Max Score"
   FROM tasks t
   LEFT OUTER JOIN user_details su ON t.started_by = su.uuid
   LEFT OUTER JOIN user_details cu ON t.completed_by = cu.uuid
   LEFT OUTER JOIN user_details ru ON t.reopened_by = ru.uuid
   JOIN checkpoint_master_sheet_table cms ON coalesce(t.details->'auditDetails'->>'questionId', split_part(t.details->'formDetails'->>'path', '/', 2)) = cms.checkpoint_knid
   AND coalesce(t.details->'auditDetails'->>'responseId', t.details->'formDetails'->>'responseId') = cms.audit_submission_knid
   WHERE t.is_deleted = 'false'
   and cms.audit_main_theme = 'Shop Floor Checklist'
     AND cms.audit_submitted_at BETWEEN @{{:Shop floor checklist - Croma.Date Range.START}}::timestamp AND @{{:Shop floor checklist - Croma.Date Range.END}}::timestamp + interval '1 day'
  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 ,17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40),
                            assignees AS
  (SELECT DISTINCT ON (t."Task KNID") t."Task KNID",
                      ud.first_name||' '||ud.last_name AS assignee,
                      ud.department
   FROM t
   JOIN analytics_requests ar ON t."Task KNID" = ar.nugget_id
   JOIN user_details ud ON ar.user_id = ud.uuid
   WHERE ar.event_id = 1
     AND ud.uuid != t.author
   ORDER BY 1,
            ar.updated_at)
SELECT t.*,
	   assignees.assignee AS "Assigneee",
       assignees.department AS "Assignee Department",
	   CASE 
    WHEN t."Status" ILIKE 'completed' THEN DATE_PART('day', "Completed At" - "Assigned At")
    ELSE NULL
END AS "TAT (Days)",
lm."Head",
lm."ZM",
lm."CM"
FROM t
LEFT OUTER JOIN assignees ON t."Task KNID" = assignees."Task KNID"
LEFT OUTER JOIN lm on t."Store" = lm.store_id
```

---

## Shop Floor Checklist - Detailed_Shop floor checklist.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, form_submissions, lm, locations, lr, role_holders, roles, user_details

**Original Query:**

```sql
-- Data Source: Shop Floor Checklist - Detailed
-- Dashboard: Shop floor checklist
-- Category: Croma
-- Extracted: 2026-01-29 16:54:14
-- ============================================================

WITH lr AS (
    SELECT
        l.id AS store_id,
        RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
        r.name AS role,
        ud.first_name || ' ' || ud.last_name AS holder
    FROM locations l
    LEFT JOIN role_holders rh ON rh.location_id = l.id AND rh.is_active = true
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager','Zonal Manager','Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = true
    WHERE l.organization = 'croma-coma' AND l.is_active = true
),
lm AS (
    SELECT
        store_id,
        store_name,
        MAX(CASE WHEN role = 'Cluster Manager' THEN holder END) AS "CM",
        MAX(CASE WHEN role = 'Zonal Manager' THEN holder END) AS "ZM",
        MAX(CASE WHEN role = 'Head' THEN holder END) AS "Head"
    FROM lr
    GROUP BY store_id, store_name
),
cms AS
  (SELECT store_id,
          REGEXP_REPLACE(audit_main_theme, '\s*[-(].*$', '', 'g') AS "Audit",
          audit_submitted_at AS "Audited At",
          TO_CHAR(TO_TIMESTAMP(fs.started_at / 1000) AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata', 'DD/MM/YY HH24:MI') AS "Started_at",
          auditor_name AS "Auditor",
          audit_submission_number AS "Audit Report No",
          audit_submission_knid AS "Audit Report KNID",
          theme AS "Theme",
          checkpoint_knid AS "Checkpoint KNID",
          CHECKPOINT AS "Checkpoint",
                        RESULT AS "Result",
                                  criticality AS "Criticality",
                                  CASE
                                      WHEN result_score = '' THEN NULL
                                      ELSE result_score::numeric
                                  END AS "Actual Score",
                                  CASE
                                      WHEN result_score = '' THEN NULL
                                      ELSE max_score::numeric
                                  END AS "Max Score",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL THEN 1
                                      ELSE 0
                                  END AS "Checked Count",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL
                                           AND result_score < max_score THEN 1
                                      ELSE 0
                                  END AS "Failed Count",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL
                                           AND result_score < max_score
                                           AND criticality = 'Critical' THEN 1
                                      ELSE 0
                                  END AS "Critical Failed Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0 THEN 1
                                      ELSE 0
                                  END AS "Followup Points Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1
                                      ELSE 0
                                  END AS "Closed Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND (total_follow_up_tasks > total_closed_follow_up_tasks
                                                OR total_closed_follow_up_tasks IS NULL) THEN 1
                                      ELSE 0
                                  END AS "Open Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND (total_follow_up_tasks > total_closed_follow_up_tasks
                                                OR total_closed_follow_up_tasks IS NULL)
                                           AND criticality = 'Critical' THEN 1
                                      ELSE 0
                                  END AS "Critical Open Count",
                                  fs.approx_distance_in_km
   FROM checkpoint_master_sheet_table cms
   JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
   WHERE organization_id = 'croma-coma'
     AND store_id NOT ILIKE '%HO'
AND audit_submitted_at between @{{:Shop floor checklist - Croma.Date Range.START}}::timestamp and @{{:Shop floor checklist - Croma.Date Range.END}}::timestamp + interval '1 day'
     AND audit_main_theme = 'Shop Floor Checklist')
SELECT cms.*,
lm."Head",
lm."ZM",
lm."CM"
FROM cms
join lm on cms.store_id = lm.store_id
WHERE cms."Audit" IS NOT NULL
ORDER BY cms."Audit Report No",cms."Audited At"
```

---

## Shop Floor Compliance_Shop floor checklist.sql

**Tables referenced:** active_locations, checkpoint_master_sheet_table, lm, locations, lr, quarters, role_holders, roles, store_quarters, stores, submissions, user_details

**Original Query:**

```sql
-- Data Source: Shop Floor Compliance
-- Dashboard: Shop floor checklist
-- Category: Croma
-- Extracted: 2026-01-29 16:53:43
-- ============================================================


WITH
-- 1️⃣ Active store list
active_locations AS (
  SELECT
    l.id::text AS store_id,
    RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
    max(ud.division) as division
  FROM locations l
 join user_details ud on ud.job_location = l.id
  WHERE l.organization = 'croma-coma'
    AND l.is_active = TRUE
    AND l.location_name NOT ILIKE '%HO%'
  AND l.location_name NOT ILIKE '%ZO%'
    AND l.location_name NOT ILIKE '%Support%'
  group by 1,2
),

lr AS (
  SELECT
    l.id::text AS store_id,
    r.name AS role,
    ud.first_name || ' ' || ud.last_name AS holder
  FROM locations l
  LEFT JOIN role_holders rh ON rh.location_id = l.id AND rh.is_active = true
  LEFT JOIN roles r ON r.id = rh.role_id
    AND r.name IN ('Cluster Manager','Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = true
  WHERE l.organization = 'croma-coma' AND l.is_active = true
),
lm AS (
  SELECT
    store_id,
    MAX(CASE WHEN role = 'Cluster Manager' THEN holder END) AS CM,
    MAX(CASE WHEN role = 'Zonal Manager' THEN holder END) AS ZM,
    MAX(CASE WHEN role = 'Head' THEN holder END) AS Head
  FROM lr
  GROUP BY store_id
),

submissions AS (
  SELECT
    cms.store_id AS store_id,
    date_trunc('quarter', cms.audit_submitted_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') AS quarter_start
  FROM checkpoint_master_sheet_table cms
  WHERE cms.organization_id = 'croma-coma'
    AND cms.store_id NOT ILIKE '%HO%'
    AND cms.audit_main_theme = 'Shop Floor Checklist'
    AND cms.audit_submitted_at BETWEEN @{{:Shop floor checklist - Croma.Date Range.START}}::timestamp
                                  AND (@{{:Shop floor checklist - Croma.Date Range.END}}::timestamp + INTERVAL '1 day')
  GROUP BY store_id, date_trunc('quarter', cms.audit_submitted_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')
),

quarters AS (
  SELECT
    generate_series(
      date_trunc('quarter', @{{:Date Range.START}}::timestamp),
      date_trunc('quarter', @{{:Date Range.END}}::timestamp),
      interval '3 months'
    ) AS quarter_start
),

-- 5️⃣ Cross-join stores × quarters
store_quarters AS (
  SELECT
    al.store_id,
    al.store_name,
    al.division,
    q.quarter_start,
    TO_CHAR(q.quarter_start, 'YYYY-"Q"Q') AS quarter_label
  FROM active_locations al
  CROSS JOIN quarters q
)

-- 6️⃣ Final compliance result
SELECT
  sq.store_id,
  sq.store_name,
  sq.division,
  lm.ZM,
  lm.CM,
  lm.Head,
  sq.quarter_label,
  CASE 
    WHEN s.store_id IS NOT NULL THEN 'Filled'
    ELSE 'Not Filled'
  END AS compliance_status,
   SUM(CASE WHEN s.store_id IS NOT NULL THEN 1 ELSE 0 END) AS filled_count
FROM store_quarters sq
LEFT JOIN submissions s
  ON s.store_id = sq.store_id
 AND s.quarter_start = sq.quarter_start
LEFT JOIN lm
  ON lm.store_id = sq.store_id
  group by 1,2,3,4,5,6,7,s.store_id
ORDER BY sq.store_name
```

---

## Shop floor checklist - Croma_Shop floor checklist.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, form_submissions, lm, locations, lr, role_holders, roles, user_details

**Original Query:**

```sql
-- Data Source: Shop floor checklist - Croma
-- Dashboard: Shop floor checklist
-- Category: Croma
-- Extracted: 2026-01-29 16:53:42
-- ============================================================

WITH lr AS (
    SELECT
        l.id AS store_id,
        RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
        r.name AS role,
        ud.first_name || ' ' || ud.last_name AS holder
    FROM locations l
    LEFT JOIN role_holders rh ON rh.location_id = l.id AND rh.is_active = true
    LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager','Zonal Manager','Head')
    LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = true
    WHERE l.organization = 'croma-coma' AND l.is_active = true
),
lm AS (
    SELECT
        store_id,
        store_name,
        MAX(CASE WHEN role = 'Cluster Manager' THEN holder END) AS "CM",
        MAX(CASE WHEN role = 'Zonal Manager' THEN holder END) AS "ZM",
        MAX(CASE WHEN role = 'Head' THEN holder END) AS "Head"
    FROM lr
    GROUP BY store_id, store_name
),
cms AS
  (SELECT store_id,
          REGEXP_REPLACE(audit_main_theme, '\s*[-(].*$', '', 'g') AS "Audit",
          audit_submitted_at AS "Audited At",
          TO_CHAR(TO_TIMESTAMP(fs.started_at / 1000) AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata', 'DD/MM/YY HH24:MI') AS "Started_at",
          auditor_name AS "Auditor",
          audit_submission_number AS "Audit Report No",
          audit_submission_knid AS "Audit Report KNID",
          theme AS "Theme",
          ud.division,
          checkpoint_knid AS "Checkpoint KNID",
          CHECKPOINT AS "Checkpoint",
                        RESULT AS "Result",
                                  criticality AS "Criticality",
                                  CASE
                                      WHEN result_score = '' THEN NULL
                                      ELSE result_score::numeric
                                  END AS "Actual Score",
                                  CASE
                                      WHEN result_score = '' THEN NULL
                                      ELSE max_score::numeric
                                  END AS "Max Score",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL THEN 1
                                      ELSE 0
                                  END AS "Checked Count",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL
                                           AND result_score < max_score THEN 1
                                      ELSE 0
                                  END AS "Failed Count",
                                  CASE
                                      WHEN result_score != ''
                                           AND result_score IS NOT NULL
                                           AND result_score < max_score
                                           AND criticality = 'Critical' THEN 1
                                      ELSE 0
                                  END AS "Critical Failed Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0 THEN 1
                                      ELSE 0
                                  END AS "Followup Points Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND total_follow_up_tasks = total_closed_follow_up_tasks THEN 1
                                      ELSE 0
                                  END AS "Closed Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND (total_follow_up_tasks > total_closed_follow_up_tasks
                                                OR total_closed_follow_up_tasks IS NULL) THEN 1
                                      ELSE 0
                                  END AS "Open Count",
                                  CASE
                                      WHEN total_follow_up_tasks > 0
                                           AND (total_follow_up_tasks > total_closed_follow_up_tasks
                                                OR total_closed_follow_up_tasks IS NULL)
                                           AND criticality = 'Critical' THEN 1
                                      ELSE 0
                                  END AS "Critical Open Count",
                                  fs.approx_distance_in_km
   FROM checkpoint_master_sheet_table cms
   JOIN user_details ud ON ud.job_location = cms.store_id
   JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
   WHERE organization_id = 'croma-coma'
     AND store_id NOT ILIKE '%HO'
AND audit_submitted_at between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day'
     AND audit_main_theme = 'Shop Floor Checklist')
SELECT DISTINCT ON (cms."Audit Report No")cms."Audit",
lm."Head",
lm."ZM",
lm."CM",
cms.store_id,
       "Started_at",
       cms."Audited At",
       cms."Auditor",
       max(cms.division) AS division,
       cms."Audit Report No",
       ROUND((sum(cms."Actual Score") / NULLIF(sum(cms."Max Score"), 0)) * 100, 2) AS "Total Score%", -- Total Score%
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Inventory Management' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Inventory Management' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Inventory Management %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Merchandising' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Merchandising' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Merchandising %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Process awareness' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Process awareness' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Process awareness %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Finance' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Finance' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Finance %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Records' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Records' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Records %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Ticketing' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Ticketing' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Ticketing %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Marketing' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Marketing' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Marketing %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Hygiene & Cleaning' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Hygiene & Cleaning' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Hygiene & Cleaning %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Grooming Standard' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Grooming Standard' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Grooming Standard %",
							   ROUND((SUM(CASE
                WHEN cms."Theme" = 'Customer Service' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Customer Service' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Customer Service %"
FROM cms
join lm on TRANSLATE(cms.store_id, '. -', '') = TRANSLATE(lm.store_id, '. -', '')
WHERE cms."Audit" IS NOT NULL
GROUP BY cms."Audit",
         "Started_at",
         cms.store_id,
         cms."Audited At",
         cms."Auditor",
         cms."Audit Report No",
		 lm."Head",
		 lm."ZM",
		 lm."CM"
ORDER BY cms."Audit Report No",cms."Audited At"
```

---

## Store Dashboard Compliance_Store Dashboard.sql

**Tables referenced:** compliance_flat, form_responses, form_submissions, forms, locations, nuggets, question_definitions, role_holders, roles, roles_mapping, store_roles, store_submissions, user_details

**Original Query:**

```sql
-- Data Source: Store Dashboard Compliance
-- Dashboard: Store Dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:21
-- ============================================================

WITH roles_mapping AS (
    SELECT 
        l.id AS store_id,
        l.location_name AS store_name,
        MAX(CASE WHEN r.name = 'ASM' THEN ud.first_name || ' ' || ud.last_name END) AS asm_name,
        MAX(CASE WHEN r.name = 'RSM' THEN ud.first_name || ' ' || ud.last_name END) AS rsm_name,
        MAX(CASE WHEN r.name = 'Zonal Manager' THEN ud.first_name || ' ' || ud.last_name END) AS zm_name,
        MAX(CASE WHEN r.name = 'Cluster Manager' THEN ud.first_name || ' ' || ud.last_name END) AS cm_name,
        MAX(ud.division) AS division
    FROM locations l
    LEFT JOIN role_holders rh 
        ON rh.location_id = l.id AND rh.is_active = TRUE
    LEFT JOIN roles r 
        ON r.id = rh.role_id 
       AND r.name IN ('ASM', 'RSM', 'Zonal Manager', 'Cluster Manager')
    LEFT JOIN user_details ud 
        ON ud.uuid = rh.role_holder_id AND ud.is_active = TRUE
    WHERE l.organization = 'croma-coma' 
      AND l.is_active = TRUE
    GROUP BY l.id, l.location_name
),

forms AS (
    SELECT id AS form_id
    FROM nuggets
    WHERE organization = 'croma-coma'
      AND is_deleted = FALSE
      AND title IN ('OL Store Checklist', 'Own Label Store Checklist')
),

store_submissions AS (
    SELECT DISTINCT
        COALESCE(l.id, NULL) AS store_id,
        date_trunc('month', fs.submit_date at time zone 'Asia/Kolkata')::date AS month_start
    FROM form_submissions fs
    JOIN forms f ON f.form_id = fs.form_id
    JOIN form_responses fr ON fr.form_submit_id = fs.id
    JOIN question_definitions qd
      ON qd.nugget_id = f.form_id
     AND LOWER(qd.question) LIKE '%store code%'
    LEFT JOIN locations l
      ON l.id::text = fr.response ->> 'id'
      OR l.location_name = fr.response ->> 'name'
    WHERE l.organization = 'croma-coma'
      AND fs.submit_date at time zone 'Asia/Kolkata' BETWEEN CAST(@{{:Store Dashboard.Date Range.START}} AS date)
                       AND CAST(@{{:Store Dashboard.Date Range.END}} AS date) + INTERVAL '1 day'
),

-- Map each store to its ASM, RSM, ZM, CM, and Division
store_roles AS (
    SELECT 
        rm.store_id,
        rm.store_name AS location,
        rm.asm_name AS asm,
        rm.rsm_name AS rsm,
        rm.zm_name AS zm,
        rm.cm_name AS cm,
        rm.division
    FROM roles_mapping rm
    WHERE rm.asm_name IS NOT NULL 
       OR rm.rsm_name IS NOT NULL
       OR rm.zm_name IS NOT NULL
       OR rm.cm_name IS NOT NULL
),

-- Combine with submissions to mark compliance
compliance_flat AS (
    SELECT 
        sr.store_id,
        sr.location,
        sr.asm,
        sr.rsm,
        sr.zm,
        sr.cm,
        sr.division,
        m.month_start,
        CASE WHEN ss.store_id IS NOT NULL THEN 1 ELSE 0 END AS compliant
    FROM store_roles sr
    CROSS JOIN (
        SELECT DISTINCT date_trunc('month', submit_date)::date AS month_start
        FROM form_submissions
        WHERE form_id IN (SELECT form_id FROM forms)
          AND submit_date at time zone 'Asia/Kolkata' BETWEEN CAST(@{{:Store Dashboard.Date Range.START}} AS date)
                       AND CAST(@{{:Store Dashboard.Date Range.END}} AS date) + INTERVAL '1 day'
    ) m
    LEFT JOIN store_submissions ss
      ON ss.store_id = sr.store_id
     AND ss.month_start = m.month_start
)

SELECT 
    TO_CHAR(month_start, 'YYYY-MM') AS month,
    division,
    rsm AS "RSM",
    asm AS "ASM",
    zm  AS "ZM",
    cm  AS "CM",
    location AS store,
    compliant
FROM compliance_flat
ORDER BY month_start DESC, division, rsm, asm, zm, cm, location
```

---

## Store Dashboard Questions_Store Dashboard.sql

**Tables referenced:** FINAL, FINAL_DEDUP, RAW, ROLES, _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, task_responses, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Store Dashboard Questions
-- Dashboard: Store Dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:11
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:Store Dashboard.UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:Store Dashboard.UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:Store Dashboard.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:Store Dashboard.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('ASM',
                  'Zonal Manager',
                  'RSM')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'croma-coma'
     AND l.is_active = TRUE ),
     lm AS
  (SELECT store_id,
          store_name,
          MAX(CASE
                  WHEN ROLE = 'ASM' THEN holder
              END) AS "ASM",
          MAX(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
              END) AS "ZM",
          MAX(CASE
                  WHEN ROLE = 'RSM' THEN holder
              END) AS "RSM"
   FROM lr
   GROUP BY store_id,
            store_name),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title IN ('OL Store Checklist','Own Label Store Checklist')
     AND organization = 'croma-coma'
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
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date AT TIME ZONE 'ASIA/KOLKATA' BETWEEN @{{:Store Dashboard.Date Range.START}}::TIMESTAMP AND @{{:Store Dashboard.Date Range.END}}::TIMESTAMP + interval '1 day' ),
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
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as ( select distinct on (nugget_id) nugget_id, question_id from question_definitions qd where nugget_id in (select form_knid from forms) and question_type = 'location' order by nugget_id, section_id, sqno ), location_response as ( select form_submit_id, (response ->> 'name')::text location_name from form_responses fr where question_id in (select question_id from location_questions) and form_submit_id in (select id from fs) ),*/ RAW AS
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
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            3), FINAL AS
  (SELECT submit_date,
          form_name,
          sno,
          first_name AS "Submitter",
          department,
          MAX(CASE
                  WHEN question = 'Store code' THEN response
              END) AS store,
          MAX(CASE
                  WHEN question = 'Check and Upload Quick Pick Art Work and Execution ticket (Ensure Quick Pick Stand is placed at the main Aisle of the Store)' THEN response
              END) AS "Art Work",
          MAX(CASE
                  WHEN question = 'Check and Upload Dumpbin execution (Ensure dumpbin stand should have minimum qty)' THEN response
              END) AS dumpbin,
          MAX(CASE
                  WHEN question = 'Check and Upload Bulk stack execution' THEN response
              END) AS bulk_stack,
          MAX(CASE
                  WHEN question = 'Check and Upload Endcap execution' THEN response
              END) AS endcap,
          MAX(CASE
                  WHEN question = 'Check and Upload New launch line execution' THEN response
              END) AS launch_line,
          MAX(CASE
                  WHEN question = 'Check and Upload own label specific offers' THEN response
              END) AS label,
          MAX(CASE
                  WHEN question = 'Check if all offer color posters for own label are executed on the shopfloor?' THEN response
              END) AS colour,
          MAX(CASE
                  WHEN question = 'Check and Upload own label fixture' THEN response
              END) AS label_fixture
   FROM RAW
   GROUP BY submit_date,
            sno,
            first_name,
            department,
            form_name),
			FINAL_DEDUP AS (
    SELECT *
    FROM (
        SELECT
            f.*,
            ROW_NUMBER() OVER (
                PARTITION BY f.store, date_trunc('month', f.submit_date)
                ORDER BY f.submit_date ASC
            ) AS rn
        FROM FINAL f
    ) x
    WHERE x.rn = 1
),
			task_responses AS (
    SELECT 
        'Quick Pick Execution' AS task,
        LOWER("Art Work") AS response
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Dumpbin Execution',
        LOWER(dumpbin)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Bulk Stack Execution',
        LOWER(bulk_stack)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Endcap Execution',
        LOWER(endcap)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'New Launch Line',
        LOWER(launch_line)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Own Label Specific Offers',
        LOWER(label)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Offer Posters on Shop Floor',
        LOWER(colour)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
    UNION ALL
    SELECT 
        'Own Label Fixture',
        LOWER(label_fixture)
    FROM FINAL_DEDUP f
    JOIN acl a ON f.store = a.store
)
SELECT 
    task,
    ROUND(100.0 * COUNT(CASE WHEN response = 'yes' THEN 1 END) / COUNT(*), 0) AS "Yes",
    ROUND(100.0 * COUNT(CASE WHEN response = 'no' THEN 1 END) / COUNT(*), 0) AS "No",
    ROUND(100.0 * COUNT(CASE WHEN response = 'na' THEN 1 END) / COUNT(*), 0) AS "N/A"
FROM task_responses
GROUP BY task
ORDER BY
    CASE task
        WHEN 'Quick Pick Execution' THEN 1
        WHEN 'Dumpbin Execution' THEN 2
        WHEN 'Bulk Stack Execution' THEN 3
        WHEN 'Endcap Execution' THEN 4
        WHEN 'New Launch Line' THEN 5
        WHEN 'Own Label Specific Offers' THEN 6
        WHEN 'Offer Posters on Shop Floor' THEN 7
        WHEN 'Own Label Fixture' THEN 8
    END
```

---

## Store Dashboard_Store Dashboard.sql

**Tables referenced:** FINAL, FINAL_DEDUP, RAW, ROLES, _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, location_questions, locations, lr, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Store Dashboard
-- Dashboard: Store Dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:53:11
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id and rh.is_active = true
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l), lr AS
  (SELECT l.id AS store_id,
          RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
          r.name AS ROLE,
          ud.first_name || ' ' || ud.last_name AS holder,
   max(ud.division) as division
   FROM locations l
   LEFT JOIN role_holders rh ON rh.location_id = l.id
   AND rh.is_active = TRUE
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('ASM',
                  'Zonal Manager',
                  'RSM',
				 'Cluster Manager')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   AND ud.is_active = TRUE
   WHERE l.organization = 'croma-coma'
     AND l.is_active = TRUE
  group by 1,2,3,4),
     lm AS
  ( SELECT 
      store_id,
      store_name,
      MAX(division) AS division,  -- Ensures single row per store
      MAX(CASE WHEN ROLE = 'ASM' THEN holder END) AS "ASM",
      MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
      MAX(CASE WHEN ROLE = 'RSM' THEN holder END) AS "RSM",
      MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM"
  FROM lr
  GROUP BY store_id, store_name),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title IN ('OL Store Checklist', 'Own Label Store Checklist')
     AND organization = 'croma-coma'
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
     fs AS
  (SELECT *
   FROM _fs
   WHERE submit_date at time zone 'Asia/Kolkata' between @{{:Date Range.START}}::timestamp and @{{:Date Range.END}}::timestamp + interval '1 day' ),
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
      WHERE question_type = 'table') base1
   CROSS JOIN jsonb_each(base1.value) res), /*location_questions as (
select distinct on (nugget_id) nugget_id, question_id from question_definitions qd
where nugget_id in (select form_knid from forms)
and question_type = 'location'
order by nugget_id, section_id, sqno
),
location_response as (
select form_submit_id, (response ->> 'name')::text location_name from form_responses fr
where question_id in (select question_id from location_questions)
and form_submit_id in (select id from fs)
),*/ RAW AS
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
          fr.location,
          ud.first_name,
          ud.department
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON ud.uuid = fr.user_id
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
            3), FINAL AS
  (SELECT submit_date,
          form_name,
          sno,
          first_name AS "Submitter",
          department,
          MAX(CASE
                  WHEN question = 'Store code' THEN response
              END) AS store,
          MAX(CASE
                  WHEN question = 'Check and Upload Quick Pick Art Work and Execution ticket (Ensure Quick Pick Stand is placed at the main Aisle of the Store)' THEN response
              END) AS "Art Work",
          MAX(CASE
                  WHEN question = 'Check and Upload Dumpbin execution (Ensure dumpbin stand should have minimum qty)' THEN response
              END) AS dumpbin,
          MAX(CASE
                  WHEN question = 'Check and Upload Bulk stack execution' THEN response
              END) AS bulk_stack,
          MAX(CASE
                  WHEN question = 'Check and Upload Endcap execution' THEN response
              END) AS endcap,
          MAX(CASE
                  WHEN question = 'Check and Upload New launch line execution' THEN response
              END) AS launch_line,
          MAX(CASE
                  WHEN question = 'Check and Upload own label specific offers' THEN response
              END) AS label,
          MAX(CASE
                  WHEN question = 'Check if all offer color posters for own label are executed on the shopfloor?' THEN response
              END) AS colour,
          MAX(CASE
                  WHEN question = 'Check and Upload own label fixture' THEN response
              END) AS label_fixture
   FROM RAW
   GROUP BY submit_date,
            sno,
            first_name,
            department,
            form_name),
FINAL_DEDUP AS (
    SELECT *
    FROM (
        SELECT
            f.*,
            ROW_NUMBER() OVER (
                PARTITION BY f.store, date_trunc('month', f.submit_date)
                ORDER BY f.submit_date ASC
            ) AS rn
        FROM FINAL f
    ) x
    WHERE x.rn = 1
)
SELECT lm."ZM",
       lm."ASM",
       lm."RSM",
	   lm."CM",
	   lm."division",
       f.*,
	   (
        (CASE WHEN LOWER(f."Art Work") = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.dumpbin) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.bulk_stack) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.endcap) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.launch_line) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.colour) = 'yes' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label_fixture) = 'yes' THEN 1 ELSE 0 END)
    ) AS yes_count,
    -- Count No responses
    (
        (CASE WHEN LOWER(f."Art Work") = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.dumpbin) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.bulk_stack) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.endcap) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.launch_line) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.colour) = 'no' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label_fixture) = 'no' THEN 1 ELSE 0 END)
    ) AS no_count,
    -- Count NA responses
    (
        (CASE WHEN LOWER(f."Art Work") = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.dumpbin) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.bulk_stack) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.endcap) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.launch_line) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.colour) = 'na' THEN 1 ELSE 0 END) +
        (CASE WHEN LOWER(f.label_fixture) = 'na' THEN 1 ELSE 0 END)
    ) AS na_count,
	ROUND(
        100.0 *
        (
            (CASE WHEN LOWER(f."Art Work") = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.dumpbin) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.bulk_stack) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.endcap) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.launch_line) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.colour) = 'yes' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label_fixture) = 'yes' THEN 1 ELSE 0 END)
        )::numeric
        /
        NULLIF(
            (
                (CASE WHEN LOWER(f."Art Work") IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.dumpbin) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.bulk_stack) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.endcap) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.launch_line) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.colour) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label_fixture) IN ('yes','no','na') THEN 1 ELSE 0 END)
            )::numeric, 0
        ), 2
    ) AS pct_yes,

    ROUND(
        100.0 *
        (
            (CASE WHEN LOWER(f."Art Work") = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.dumpbin) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.bulk_stack) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.endcap) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.launch_line) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.colour) = 'no' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label_fixture) = 'no' THEN 1 ELSE 0 END)
        )::numeric
        /
        NULLIF(
            (
                (CASE WHEN LOWER(f."Art Work") IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.dumpbin) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.bulk_stack) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.endcap) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.launch_line) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.colour) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label_fixture) IN ('yes','no','na') THEN 1 ELSE 0 END)
            )::numeric, 0
        ), 2
    ) AS pct_no,

    ROUND(
        100.0 *
        (
            (CASE WHEN LOWER(f."Art Work") = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.dumpbin) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.bulk_stack) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.endcap) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.launch_line) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.colour) = 'na' THEN 1 ELSE 0 END) +
            (CASE WHEN LOWER(f.label_fixture) = 'na' THEN 1 ELSE 0 END)
        )::numeric
        /
        NULLIF(
            (
                (CASE WHEN LOWER(f."Art Work") IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.dumpbin) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.bulk_stack) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.endcap) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.launch_line) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.colour) IN ('yes','no','na') THEN 1 ELSE 0 END) +
                (CASE WHEN LOWER(f.label_fixture) IN ('yes','no','na') THEN 1 ELSE 0 END)
            )::numeric, 0
        ), 2
    ) AS pct_na
FROM FINAL_DEDUP f
JOIN acl ON f.store = acl.store
LEFT JOIN lm ON f.store = lm.store_id
```

---

## croma announcements_Announcements.sql

**Tables referenced:** analytics_requests, event_types, filtered_nuggets, nuggets, user_details

**Original Query:**

```sql
-- Data Source: croma announcements
-- Dashboard: Announcements
-- Category: Croma
-- Extracted: 2026-01-29 16:56:25
-- ============================================================

WITH filtered_nuggets AS (
  SELECT id, title, author
  FROM nuggets
  WHERE classification_type = 'general'
    AND sub_type NOT IN ('quiz')
)
SELECT
 ar.location as "Store",
  TO_CHAR(TO_TIMESTAMP(ar.created_at / 1000), 'DD-MM-YYYY') AS created_date,
  fn.title as "Announcement title",
  ud.first_name as "Announcement Author",
  ud.department as "Author Department",
SUM(CASE WHEN et.event_type = 'sent' THEN 1 ELSE 0 END) AS sent_count,
    SUM(CASE WHEN et.event_type = 'received' THEN 1 ELSE 0 END) AS received_count,
    SUM(CASE WHEN et.event_type = 'consumed' THEN 1 ELSE 0 END) AS viewed_count,
      ROUND(
    100.0 * SUM(CASE WHEN event_type = 'consumed' THEN 1 ELSE 0 END) 
      / NULLIF(SUM(CASE WHEN event_type = 'sent' THEN 1 ELSE 0 END), 0),
    2
  ) AS viewed_percentage
FROM analytics_requests ar
JOIN event_types et ON et.id = ar.event_id
LEFT JOIN filtered_nuggets fn ON ar.nugget_id = fn.id
LEFT JOIN user_details ud ON fn.author = ud.uuid
WHERE TO_TIMESTAMP(ar.created_at / 1000) >= '2025-04-21'
AND ud.first_name IN (
    'Consumer Finance', 'Incentives', 'Newlaunches', 'POS', 'Price Change',
    'Promotion', 'Stock Updates - Communication', 'Trade-in', 'HR', 'Report',
    'Learning', 'Shibashish', 'SOH', 'Proccess', 'SCM'
  )
GROUP BY 1, 2, 3, 4,5
order by 1,2,3
```

---

## croma safety summary_Safety KPI Tracker.sql

**Tables referenced:** acl, croma.croma_safety, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: croma safety summary
-- Dashboard: Safety KPI Tracker
-- Category: Croma
-- Extracted: 2026-01-29 16:55:14
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (l.location_name ILIKE 'A%'
             OR l.location_name ILIKE 'D%'
						OR l.location_name ILIKE 'T%')
        AND l.is_active = 'true'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (l.location_name ILIKE 'A%'
             OR l.location_name ILIKE 'D%'
						OR l.location_name ILIKE 'T%')
        AND l.is_active = 'true'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (job_location ILIKE 'A%'
             OR job_location ILIKE 'D%'
						OR job_location ILIKE 'T%')
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)
				  select cs.* from croma.croma_safety cs
				  join acl on cs."Store ID" = acl.store_id
				  where cs."Period Start"::date >= @{{:Date Range.START}}::date at time zone 'Asia/Kolkata' - interval '1 day' and cs."Period End"::date <= @{{:Date Range.END}}::date at time zone 'Asia/Kolkata' + interval '1 day'
ORDER BY 1,
         8,
         7
```

---

## croma safety ytd_Safety KPI Tracker.sql

**Tables referenced:** acl, croma.croma_safety, locations, role_holders, user_details, user_groups

**Original Query:**

```sql
-- Data Source: croma safety ytd
-- Dashboard: Safety KPI Tracker
-- Category: Croma
-- Extracted: 2026-01-29 16:55:14
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store_id
   FROM
     (SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:croma safety summary.UuidParameter}}
        AND role_holder_type = 'user'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (l.location_name ILIKE 'A%'
             OR l.location_name ILIKE 'D%'
						OR l.location_name ILIKE 'T%')
        AND l.is_active = 'true'
      UNION SELECT left(l.location_name, 4) AS store_id
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:croma safety summary.UuidParameter}}
        AND role_holder_type = 'group'
        AND substring(l.location_name
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (l.location_name ILIKE 'A%'
             OR l.location_name ILIKE 'D%'
						OR l.location_name ILIKE 'T%')
        AND l.is_active = 'true'
      UNION SELECT left(job_location, 4) AS store_id
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
        AND substring(job_location
                      FROM 2
                      FOR 3) ~ '^\d{3}$'
        AND (job_location ILIKE 'A%'
             OR job_location ILIKE 'D%'
						OR  job_location  ILIKE 'T%')
        AND (
               (SELECT is_super_admin
                FROM user_details
                WHERE uuid = @{{:croma safety summary.UuidParameter}})
             OR uuid IN
               (SELECT DISTINCT user_id
                FROM user_groups ug1
                WHERE ug1.group_id IN
                    (SELECT group_id
                     FROM user_groups ug2
                     WHERE ug2.user_id = @{{:croma safety summary.UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l)select cs.* from croma.croma_safety cs
				  join acl on cs."Store ID" = acl.store_id
				  where cs."Period Start"::date >= date_trunc('year', current_timestamp at time zone 'Asia/Kolkata' - interval '3 months') + interval '3 months' and cs."Period End"::date <= current_timestamp at time zone 'Asia/Kolkata' + interval '1 month'
ORDER BY 1,
         8,
         7
```

---

## croma_attendance_sync_results_daily-copy_1757925709_Weekly User Attendance sync report.sql

**Tables referenced:** croma_results.attendance_sync_result

**Original Query:**

```sql
-- Data Source: croma_attendance_sync_results_daily-copy_1757925709
-- Dashboard: Weekly User Attendance sync report
-- Category: Croma
-- Extracted: 2026-01-29 16:54:18
-- ============================================================

SELECT identifier,
       ci_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' AS check_in,
       co_time AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata' AS check_out,
       error_message
FROM croma_results.attendance_sync_result
WHERE run_at > now() - interval '7 days'
ORDER BY identifier
```

---

## croma_attendance_sync_results_daily_Daily User Attendance sync report.sql

**Tables referenced:** croma_results.attendance_sync_result

**Original Query:**

```sql
-- Data Source: croma_attendance_sync_results_daily
-- Dashboard: Daily User Attendance sync report
-- Category: Croma
-- Extracted: 2026-01-29 16:56:07
-- ============================================================

select identifier, ci_time at time zone 'UTC' at time zone 'Asia/Kolkata' "check_in",
co_time at time zone 'UTC' at time zone 'Asia/Kolkata' "check_out",
error_message
from croma_results.attendance_sync_result
where run_at > now() - interval '1 day'
order by identifier
```

---

## croma_defect_form_Location Transfer.sql

**Tables referenced:** ROLES, _fs, acl, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, locations, lrn, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, role_holders, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)


**Original Query:**

```sql
-- Data Source: croma_defect_form
-- Dashboard: Location Transfer
-- Category: Croma
-- Extracted: 2026-01-29 16:56:58
-- ============================================================

WITH acl AS
  (SELECT DISTINCT store
   FROM
     (SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = 'true'
      WHERE rh.role_holder_id = @{{:UuidParameter}}
        AND role_holder_type = 'user'
      UNION SELECT l.location_name AS store
      FROM role_holders rh
      JOIN locations l ON rh.location_id = l.id
      AND rh.is_active = TRUE
      JOIN user_groups ug ON rh.role_holder_id = ug.group_id
      WHERE ug.user_id = @{{:UuidParameter}}
        AND role_holder_type = 'group'
      UNION SELECT job_location AS store
      FROM user_details
      WHERE organization = 'croma-coma'
        AND is_active = 'true'
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
                     WHERE ug2.user_id = @{{:UuidParameter}}
                       AND ug2.has_access = TRUE)
                  AND ug1.is_active = TRUE))) l),
     lrn AS
  (SELECT acl.store,
          r.name AS ROLE,
          ud.uuid AS holder_id,
          ud.first_name||' '||ud.last_name AS holder
   FROM acl
   LEFT OUTER JOIN locations l ON acl.store = l.location_name
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Head',
                  'Zonal Manager')
   JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lrn.store,
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Head' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID"
   FROM lrn
   GROUP BY 1
   ORDER BY 1),
td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-OIzPMy629u7dFjNX_t6','-OJ1yo6uy2DLEjGQnfm5')
     AND organization = 'croma-coma'
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
        where submit_date BETWEEN @{{:startDate}}::timestamp AND @{{:endDate}}::timestamp + INTERVAL '1 day'
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
          location,
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
                location,
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
	         location,
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
          fr.location,
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
          "CM",
          "ZM"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN lm on lm.store = fr.location
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
            14,15,16
   ORDER BY 1,
            2,
            3)
SELECT response_id,
form_name,
submit_date,
location,
MAX(
Case when question = 'Category' Then Response END) as "Category",
MAX(
CASE when parent_question = 'CM Approval' Then Response END) as Approvals,
"CM",
"ZM",
MAX(
  CASE 
    WHEN form_id = '-OIzPMy629u7dFjNX_t6' THEN 'DC'
    WHEN form_id = '-OJ1yo6uy2DLEjGQnfm5' THEN 'SHOP'
    ELSE NULL
  END
) AS type
FROM raw
group by 1,2,3,4,"CM","ZM"
```

---

## croma_rgp_RGP Dashboard 1.sql

**Tables referenced:** RAW, ROLES, _fs, acl, filtered_sent_at, final, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, lm, location_questions, location_response, locations, lrn, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, role_holders, td, user_details, user_groups

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)


**Original Query:**

```sql
-- Data Source: croma_rgp
-- Dashboard: RGP Dashboard 1
-- Category: Croma
-- Extracted: 2026-01-29 16:56:59
-- ============================================================

WITH acl AS (
  SELECT DISTINCT store
  FROM (
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = 'true'
    WHERE rh.role_holder_id = @{{:UuidParameter}} AND role_holder_type = 'user'
    UNION
    SELECT l.location_name AS store
    FROM role_holders rh
    JOIN locations l ON rh.location_id = l.id AND rh.is_active = TRUE
    JOIN user_groups ug ON rh.role_holder_id = ug.group_id
    WHERE ug.user_id = @{{:UuidParameter}} AND role_holder_type = 'group'
    UNION
    SELECT job_location AS store
    FROM user_details
    WHERE organization = 'croma-coma'
      AND is_active = 'true'
      AND (
        (SELECT is_super_admin FROM user_details WHERE uuid = @{{:UuidParameter}})
        OR uuid IN (
          SELECT DISTINCT user_id
          FROM user_groups ug1
          WHERE ug1.group_id IN (
            SELECT group_id
            FROM user_groups ug2
            WHERE ug2.user_id = @{{:UuidParameter}} AND ug2.has_access = TRUE
          )
          AND ug1.is_active = TRUE
        )
      )
  ) l
),
lrn AS (
  SELECT acl.store,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name||' '||ud.last_name AS holder
  FROM acl
  LEFT OUTER JOIN locations l ON acl.store = l.location_name
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN ROLES r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Head', 'Zonal Manager')
  JOIN user_details ud ON rh.role_holder_id = ud.uuid
  WHERE l.organization = 'croma-coma'
    AND l.is_active = 'true'
    AND ud.is_active = 'true'
  ORDER BY 1,2
),
lm AS (
  SELECT lrn.store,
         max(CASE WHEN ROLE = 'Cluster Manager' THEN holder ELSE NULL END) AS "CM",
         max(CASE WHEN ROLE = 'Cluster Manager' THEN holder_id ELSE NULL END) AS "CM KNID",
         max(CASE WHEN ROLE = 'Head' THEN holder ELSE NULL END) AS "Head",
         max(CASE WHEN ROLE = 'Head' THEN holder_id ELSE NULL END) AS "Head KNID",
         max(CASE WHEN ROLE = 'Zonal Manager' THEN holder ELSE NULL END) AS "ZM",
         max(CASE WHEN ROLE = 'Zonal Manager' THEN holder_id ELSE NULL END) AS "ZM KNID"
  FROM lrn
  GROUP BY 1
  ORDER BY 1
),
td AS (
  SELECT id AS organization, tzoffset, interval '1 min'*tzoffset AS diff
  FROM organizations
  WHERE id = 'croma-coma'
  GROUP BY 1,2
),
forms AS (
  SELECT id AS form_knid, title AS form_name
  FROM nuggets n
  WHERE id = '-ODt4n0Z74vO5cIpjg0n'
    AND organization = 'croma-coma'
    AND is_deleted = false
  GROUP BY 1,2
),
-- New CTE to filter responses based on sentAt in section-1 within date range
filtered_sent_at AS (
  SELECT fs.response_id 
  FROM form_submissions fs
  JOIN form_responses fr on fr.form_submit_id = fs.id
  --JOIN forms ON fr.form_id = forms.form_knid
  WHERE fr.question_id = 'section-1'
    AND to_timestamp((fr.response->>'sentAt')::BIGINT / 1000) BETWEEN @{{:Date Range.START}}::date AND @{{:Date Range.END}}::date + interval '1 day'
),
-- Modified to get latest submissions only for filtered responses
_fs AS (
  SELECT DISTINCT ON (fs.response_id) fs.*, forms.form_name
  FROM form_submissions fs
  JOIN forms ON fs.form_id = forms.form_knid
  WHERE fs.response_id IN (SELECT response_id FROM filtered_sent_at)
  ORDER BY fs.response_id, fs.id DESC
),
fs AS (
  SELECT * FROM _fs
),
qd_non_table_non_logic AS (
  SELECT nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
         CASE WHEN qd.question_type = 'section' THEN 0 ELSE sqno::integer*10000 END AS q_no,
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
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
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
  WHERE definition ->>'logic' IS NOT NULL
),
qd_table AS (
  SELECT nugget_id AS form_knid,
         CASE WHEN qd.section_id = 'section' THEN 1 ELSE replace(section_id, 'section-', '')::integer END AS section_no,
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
  WHERE qd.question_type IN ('table')
),
final_definition AS (
  SELECT * FROM qd_non_table_non_logic
  UNION
  SELECT * FROM qd_non_table_with_logic
  UNION
  SELECT * FROM qd_table
  ORDER BY 1,2,3,5 DESC,7 DESC
),
fr AS (
  SELECT 
    fs.organization,
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
    to_timestamp((response->>'sentAt')::BIGINT / 1000) AS sent_at_timestamp,
    1 AS rn
  FROM form_responses fr
  JOIN fs ON fs.id = fr.form_submit_id
  JOIN td ON fs.organization = td.organization
  WHERE question_type NOT IN ('table', 'nested')

  UNION 

  SELECT 
    organization,
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
    to_timestamp((base1.response->>'sentAt')::BIGINT / 1000) AS sent_at_timestamp,
    rn
  FROM (
    SELECT 
      fs.organization,
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
      response, 
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
  SELECT form_submit_id, (response ->> 'name')::text location_name
  FROM form_responses fr 
  WHERE question_id IN (SELECT question_id FROM location_questions)
    AND form_submit_id IN (SELECT id FROM fs)
),
RAW AS (
  SELECT 
    fr.sno,
    fd.section_no,
    fd.q_no,
    fd.parent_question,
    fr.parent_qid,
    fd.question,
    sent_at_timestamp,
    q_type,
    CASE
      WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
      WHEN fd.q_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit') THEN fr.response -> 'selected'->>0
      WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY(
        SELECT jsonb_array_elements_text(fr.response->'selected')
        UNION
        SELECT CASE WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText' END
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
    fr.form_id,
    fr.response_id,
    fr.submit_date AS submit_date,
    lr.location_name as submission_location,
    "CM",
    "ZM",
  "Head"
  FROM final_definition fd
  JOIN fr ON fr.qid = fd.qid AND fr.form_id = fd.form_knid
  JOIN location_response lr ON lr.form_submit_id = fr.form_submit_id
  JOIN td ON fr.organization = td.organization
  JOIN lm ON lm.store = lr.location_name
  GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19
  ORDER BY 1,2,3
),
final AS (
  SELECT 
    sno,
  "Head",
    "ZM",
    "CM",
    MAX(response) FILTER (WHERE parent_question = 'RGP Number') AS rgp_number,
    MAX(response) FILTER (WHERE parent_question = 'Store') AS store_name,
    MAX(CASE WHEN parent_qid = 'section-1' THEN sent_at_timestamp END) AS stage1_date,
    MAX(CASE WHEN parent_qid = 'section-2' THEN sent_at_timestamp END) AS stage2_date,
    MAX(TO_CHAR(response::TIMESTAMP, 'DD/MM/YY HH24:MI')) FILTER (WHERE parent_qid = '-ODt4n0_upNa5zigUdWh') AS expected_return_date
  FROM RAW
  GROUP BY 1,2,3,4
)
SELECT *,
  CASE 
    WHEN stage1_date IS NOT NULL AND stage2_date IS NULL THEN 'Open'
    ELSE 'Closed'
  END as status
FROM final
```

---

## process_kpi-copy_1744141315_Process Dashboard.sql

**Tables referenced:** audit_submitted_at, base, checkpoint_master_sheet_table, lm, locations, lr, monthly_audit_score, organizations, pivot_final, pivoted_monthly_scores, role_holders, roles, td, user_details, ytd_scores

**Original Query:**

```sql
-- Data Source: process_kpi-copy_1744141315
-- Dashboard: Process Dashboard
-- Category: Croma
-- Extracted: 2026-01-29 16:56:27
-- ============================================================

WITH td AS (
  SELECT id AS organization, interval '1 min' * tzoffset AS diff
  FROM organizations
  WHERE id = 'croma-coma'
),
lr AS (
  SELECT l.id,
         RIGHT(l.location_name, LENGTH(l.location_name) - 5) AS store_name,
         r.name AS ROLE,
         ud.uuid AS holder_id,
         ud.first_name || ' ' || ud.last_name AS holder,
  ud."division"
  FROM locations l
  LEFT JOIN role_holders rh ON l.id = rh.location_id AND rh.is_active = 'true'
  LEFT JOIN roles r ON r.id = rh.role_id AND r.name IN ('Cluster Manager', 'Regional Manager', 'Zonal Manager','Head')
  LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid AND ud.is_active = 'true'
  WHERE l.organization = 'croma-coma' AND l.is_active = 'true'
),
lm AS (
  SELECT lr.id AS store_id,
         lr.store_name,MAX("division") AS division,
         MAX(CASE WHEN ROLE = 'Cluster Manager' THEN holder END) AS "CM",
         MAX(CASE WHEN ROLE = 'Regional Manager' THEN holder END) AS "RM",
         MAX(CASE WHEN ROLE = 'Zonal Manager' THEN holder END) AS "ZM",
  MAX(CASE WHEN ROLE = 'Head' THEN holder END) AS "Head"
  FROM lr
  GROUP BY 1, 2
),
base AS (
  SELECT organization_id,
         CASE WHEN result_score = '' THEN NULL ELSE result_score::numeric END AS result_score,
         CASE WHEN max_score = '' THEN NULL ELSE max_score::numeric END AS max_score,
         cms.store_id,
         REGEXP_REPLACE(audit_main_theme, '\s*\(.*$', '', 'g') AS audit_main_theme,
         theme,
         (audit_submitted_at + td.diff) AS audit_submitted_at,
         audit_submission_number,
         audit_submission_knid,
         auditor_name,
         checkpoint_knid,
         checkpoint,
         result,
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
         ROW_NUMBER() OVER (PARTITION BY cms.store_id, audit_main_theme, theme, checkpoint_knid, EXTRACT(YEAR FROM audit_submitted_at) ORDER BY audit_submitted_at) AS "Audit No in Year",
         "CM",
         "RM",
         "ZM",
  "Head","division"
  FROM checkpoint_master_sheet_table cms
  JOIN td ON cms.organization_id = td.organization
  JOIN lm ON cms.store_id = lm.store_id
  WHERE organization_id = 'croma-coma'
    AND audit_submitted_at >= @{{:Date Range.START}}
    AND audit_main_theme ILIKE ANY (ARRAY['%Process Excellence%', '%SMART Audit%', '%SOP Audit%'])
),
monthly_audit_score AS (
  SELECT 
    store_id as "Location" ,
   audit_main_theme as  "Audit" ,
   DATE_TRUNC('month', audit_submitted_at) as "Month" ,
    "CM", "RM", "ZM","Head","division",
    SUM(result_score) / SUM(CASE WHEN result_score IS NOT NULL THEN max_score ELSE 0 END) AS "Score"
  FROM base
  GROUP BY 1, 2, 3, 4, 5, 6,7,8
),
pivoted_monthly_scores AS (
  SELECT
    "Location",
    "CM", "RM", "ZM","Head","division",
    TO_CHAR("Month", 'YYYY-MM') AS month_text,
    MAX(CASE WHEN "Audit" ILIKE '%SMART Audit%' THEN "Score" END) AS "SMART_Audit",
    MAX(CASE WHEN "Audit" ILIKE '%SOP Audit%' THEN "Score" END) AS "SOP_Audit",
    MAX(CASE WHEN "Audit" ILIKE 'Process Excellence%' THEN "Score" END) AS "Process_Excellence"
  FROM monthly_audit_score
  GROUP BY 1, 2, 3, 4, 5,6,7
),
pivot_final AS (
  SELECT
    "Location",
    "CM", "RM", "ZM","Head","division",
    MAX(CASE WHEN month_text = '2025-01' THEN "SMART_Audit" END) AS "SMART_Audit_Jan",
    MAX(CASE WHEN month_text = '2025-01' THEN "SOP_Audit" END) AS "SOP_Audit_Jan",
    MAX(CASE WHEN month_text = '2025-01' THEN "Process_Excellence" END) AS "Process_Excellence_Jan",
    MAX(CASE WHEN month_text = '2025-02' THEN "SMART_Audit" END) AS "SMART_Audit_Feb",
    MAX(CASE WHEN month_text = '2025-02' THEN "SOP_Audit" END) AS "SOP_Audit_Feb",
    MAX(CASE WHEN month_text = '2025-02' THEN "Process_Excellence" END) AS "Process_Excellence_Feb",
    MAX(CASE WHEN month_text = '2025-03' THEN "SMART_Audit" END) AS "SMART_Audit_Mar",
    MAX(CASE WHEN month_text = '2025-03' THEN "SOP_Audit" END) AS "SOP_Audit_Mar",
    MAX(CASE WHEN month_text = '2025-03' THEN "Process_Excellence" END) AS "Process_Excellence_Mar",
COALESCE(MAX(CASE WHEN month_text = '2025-04' THEN "SMART_Audit" END), 0) AS "SMART_Audit_Apr",
COALESCE(MAX(CASE WHEN month_text = '2025-04' THEN "SOP_Audit" END), 0) AS "SOP_Audit_Apr",
COALESCE(MAX(CASE WHEN month_text = '2025-04' THEN "Process_Excellence" END), 0) AS "Process_Excellence_Apr",
  COALESCE(MAX(CASE WHEN month_text = '2025-05' THEN "SMART_Audit" END), 0) AS "SMART_Audit_May",
COALESCE(MAX(CASE WHEN month_text = '2025-05' THEN "SOP_Audit" END), 0) AS "SOP_Audit_May",
COALESCE(MAX(CASE WHEN month_text = '2025-05' THEN "Process_Excellence" END), 0) AS "Process_Excellence_May",
    MAX(CASE WHEN month_text = '2025-06' THEN "SMART_Audit" END) AS "SMART_Audit_Jun",
    MAX(CASE WHEN month_text = '2025-06' THEN "SOP_Audit" END) AS "SOP_Audit_Jun",
    MAX(CASE WHEN month_text = '2025-06' THEN "Process_Excellence" END) AS "Process_Excellence_Jun",
    MAX(CASE WHEN month_text = '2025-07' THEN "SMART_Audit" END) AS "SMART_Audit_Jul",
    MAX(CASE WHEN month_text = '2025-07' THEN "SOP_Audit" END) AS "SOP_Audit_Jul",
    MAX(CASE WHEN month_text = '2025-07' THEN "Process_Excellence" END) AS "Process_Excellence_Jul",
    MAX(CASE WHEN month_text = '2025-08' THEN "SMART_Audit" END) AS "SMART_Audit_Aug",
    MAX(CASE WHEN month_text = '2025-08' THEN "SOP_Audit" END) AS "SOP_Audit_Aug",
    MAX(CASE WHEN month_text = '2025-08' THEN "Process_Excellence" END) AS "Process_Excellence_Aug",
    MAX(CASE WHEN month_text = '2025-09' THEN "SMART_Audit" END) AS "SMART_Audit_Sep",
    MAX(CASE WHEN month_text = '2025-09' THEN "SOP_Audit" END) AS "SOP_Audit_Sep",
    MAX(CASE WHEN month_text = '2025-09' THEN "Process_Excellence" END) AS "Process_Excellence_Sep",
    MAX(CASE WHEN month_text = '2025-10' THEN "SMART_Audit" END) AS "SMART_Audit_Oct",
    MAX(CASE WHEN month_text = '2025-10' THEN "SOP_Audit" END) AS "SOP_Audit_Oct",
    MAX(CASE WHEN month_text = '2025-10' THEN "Process_Excellence" END) AS "Process_Excellence_Oct",
    MAX(CASE WHEN month_text = '2025-11' THEN "SMART_Audit" END) AS "SMART_Audit_Nov",
    MAX(CASE WHEN month_text = '2025-11' THEN "SOP_Audit" END) AS "SOP_Audit_Nov",
    MAX(CASE WHEN month_text = '2025-11' THEN "Process_Excellence" END) AS "Process_Excellence_Nov",
    MAX(CASE WHEN month_text = '2025-12' THEN "SMART_Audit" END) AS "SMART_Audit_Dec",
    MAX(CASE WHEN month_text = '2025-12' THEN "SOP_Audit" END) AS "SOP_Audit_Dec",
    MAX(CASE WHEN month_text = '2025-12' THEN "Process_Excellence" END) AS "Process_Excellence_Dec"
  FROM pivoted_monthly_scores
  GROUP BY 1, 2, 3, 4,5,6
),
ytd_scores AS (
  SELECT 
    "Location",
    "CM", "RM", "ZM","Head","division",
    AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') AS "SMART_Audit_YTD",
    AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') AS "SOP_Audit_YTD",
    AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') AS "Process_Excellence_YTD",
    ROUND(
      (
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') * 0.2, 0) +
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') * 0.4, 0) +
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') * 0.4, 0)
      ) / NULLIF(
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') IS NOT NULL THEN 0.2 ELSE 0 END) +
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') IS NOT NULL THEN 0.4 ELSE 0 END) +
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') IS NOT NULL THEN 0.4 ELSE 0 END)
      , 0) * 100, 1
    ) AS "Process_KPI_YTD"
  FROM monthly_audit_score
  WHERE "Month" >= DATE_TRUNC('year', CURRENT_DATE)
  GROUP BY 1, 2, 3, 4,5,6
)

SELECT 
  y.*,
  p."SMART_Audit_Jan", p."SOP_Audit_Jan", p."Process_Excellence_Jan",
  p."SMART_Audit_Feb", p."SOP_Audit_Feb", p."Process_Excellence_Feb",
  p."SMART_Audit_Mar", p."SOP_Audit_Mar", p."Process_Excellence_Mar",
  p."SMART_Audit_Apr", p."SOP_Audit_Apr", p."Process_Excellence_Apr",
  p."SMART_Audit_May", p."SOP_Audit_May", p."Process_Excellence_May",
  p."SMART_Audit_Jun", p."SOP_Audit_Jun", p."Process_Excellence_Jun",
  p."SMART_Audit_Jul", p."SOP_Audit_Jul", p."Process_Excellence_Jul",
  p."SMART_Audit_Aug", p."SOP_Audit_Aug", p."Process_Excellence_Aug",
  p."SMART_Audit_Sep", p."SOP_Audit_Sep", p."Process_Excellence_Sep",
  p."SMART_Audit_Oct", p."SOP_Audit_Oct", p."Process_Excellence_Oct",
  p."SMART_Audit_Nov", p."SOP_Audit_Nov", p."Process_Excellence_Nov",
  p."SMART_Audit_Dec", p."SOP_Audit_Dec", p."Process_Excellence_Dec"
FROM ytd_scores y
LEFT JOIN pivot_final p ON y."Location" = p."Location"
where y."Location" IS NOT NULL
    AND y."CM" IS NOT NULL
	AND y."ZM" IS NOT NULL
	AND y."Head" IS NOT NULL
ORDER BY y."CM", y."Location"
```

---

## process_kpi_Process KPII.sql

**Tables referenced:** FINAL, ROLES, audit_submitted_at, base, checkpoint_master_sheet_table, croma.checklist_completions, lm, location_acl, locations, lr, monthly_audit_score, monthly_checklist_scores, organizations, role_holders, td, user_details, ytd_scores

**Original Query:**

```sql
-- Data Source: process_kpi
-- Dashboard: Process KPII
-- Category: Croma
-- Extracted: 2026-01-29 16:56:32
-- ============================================================

WITH td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'croma-coma'),
     lr AS
  (SELECT l.id,
          right(l.location_name, length(l.location_name)-5) AS store_name,
          r.name AS ROLE,
          ud.uuid AS holder_id,
ud.first_name || ' ' || ud.last_name AS holder
   --,ud.division
   FROM locations l
   LEFT JOIN role_holders rh ON l.id = rh.location_id
   AND rh.is_active = 'true'
   LEFT JOIN ROLES r ON r.id = rh.role_id
   AND r.name IN ('Cluster Manager',
                  'Regional Manager',
                  'Zonal Manager','Head')
   LEFT JOIN user_details ud ON rh.role_holder_id = ud.uuid
   WHERE l.organization = 'croma-coma'
     AND l.is_active = 'true'
     AND ud.is_active = 'true'
   ORDER BY 1,
            2),
     lm AS
  (SELECT lr.id AS store_id,
          lr.store_name,
   --,"division",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder
                  ELSE NULL
              END) AS "CM",
          max(CASE
                  WHEN ROLE = 'Cluster Manager' THEN holder_id
                  ELSE NULL
              END) AS "CM KNID",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder
                  ELSE NULL
              END) AS "RM",
          max(CASE
                  WHEN ROLE = 'Regional Manager' THEN holder_id
                  ELSE NULL
              END) AS "RM KNID",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder
                  ELSE NULL
              END) AS "ZM",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "ZM KNID",
   max(CASE
                  WHEN ROLE = 'Head' THEN holder
                  ELSE NULL
              END) AS "Head",
          max(CASE
                  WHEN ROLE = 'Zonal Manager' THEN holder_id
                  ELSE NULL
              END) AS "Head KNID"
   FROM lr
   GROUP BY 1,
            2
   --,3
   ORDER BY 1),
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
          cms.store_id,
          regexp_replace(audit_main_theme, '\s*\(.*$', '', 'g') as audit_main_theme,
          theme,
          (audit_submitted_at + td.diff) AS audit_submitted_at,
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
          row_number() OVER (PARTITION BY cms.store_id,
                                          audit_main_theme,
                                          theme,
                                          checkpoint_knid,
                                          extract('Year'
                                                  FROM audit_submitted_at)
                             ORDER BY audit_submitted_at) AS "Audit No in Year",
                            "CM",
                            "RM",
                            "ZM",
   "Head"
   --,"division"
   FROM checkpoint_master_sheet_table cms
   JOIN td ON cms.organization_id = td.organization
   JOIN lm ON cms.store_id = lm.store_id --JOIN location_acl ON cms.store_id = location_acl.job_location

   WHERE organization_id = 'croma-coma'
   and audit_submitted_at >= @{{:Date Range.START}} 
     AND (audit_main_theme ILIKE ('%Process Excellence%') 
          OR audit_main_theme ILIKE ('%SMART Audit%')
          OR audit_main_theme ILIKE ('%SOP Audit%')
          OR audit_main_theme ILIKE '%BDC%'
          OR audit_main_theme ILIKE '%DM-AA%'
          OR audit_main_theme ILIKE '%CSD Checklist%'
          OR audit_main_theme ILIKE '%Cashier%'
          OR audit_main_theme ILIKE '%VM Checklist%'
          OR audit_main_theme ILIKE '%Maintenance%') 
          and audit_main_theme not ilike '%TRiBE%'),
     FINAL AS
  (SELECT organization_id AS "Org",
          store_id AS "Location",
          audit_main_theme AS "Audit",
          audit_submitted_at AS "Audit Date",
          audit_submission_number AS "Audit Report No",
          audit_submission_knid AS "Audit Report KNID",
          auditor_name AS "Auditor",
          theme AS "Theme",
          checkpoint_knid AS "Checkpoint KNID",
          CHECKPOINT AS "Checkpoint",
                        RESULT AS "Result",
                                  status AS "Checkpoint Status",
                                  auditor_observations AS "Auditor Notes",
                                  result_score AS "Actual Score",
                                  max_score AS "Max Score",
                                  criticality AS "Criticality",
                                  total_follow_up_tasks AS "Total Follow Ups",
                                  total_closed_follow_up_tasks AS "Total Closed Follow Ups",
                                  "Audit No in Year", --"Year",
 -- "Month",
 date_trunc('Month',audit_submitted_at) AS "Month",
 "CM",
 "RM",
 "ZM",
   "Head"
   --,"division"
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
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,24
   --,25
   ORDER BY 1,
            2,
            4), monthly_audit_score AS
  (SELECT "Audit",
          "Audit Report KNID",
          "Location",
          "Month" AS "Period",
          "CM",
          "RM",
          "ZM",
   "Head",
   --"division",
          sum("Actual Score")/Sum(CASE WHEN "Actual Score" IS NOT NULL then "Max Score" else 0 end ) AS "Score",
          NULL::numeric AS "Process KPI Score"
   FROM FINAL
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,8
   --,9
  ),
               ytd_scores AS (
  SELECT 
    "CM",
    "RM",
    "ZM","Head",
				 --"division",
  AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') AS "SMART Audit Score (YTD)",
    AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') AS "SOP Audit Score (YTD)",
    AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') AS "Process Excellence Score (YTD)",
  ROUND(
      (
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') * 0.2, 0) +
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') * 0.4, 0) +
        COALESCE(AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') * 0.4, 0)
      ) / NULLIF(
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE '%SMART Audit%') IS NOT NULL THEN 0.2 ELSE 0 END) +
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE '%SOP Audit%') IS NOT NULL THEN 0.4 ELSE 0 END) +
        (CASE WHEN AVG("Score") FILTER (WHERE "Audit" ILIKE 'Process Excellence%') IS NOT NULL THEN 0.4 ELSE 0 END)
      , 0) * 100
    , 1)AS "Process KPI Score (YTD)"
  FROM monthly_audit_score
  WHERE "Period" >= date_trunc('year', CURRENT_DATE) AND "Period" <= CURRENT_DATE
  GROUP BY "CM", "RM", "ZM","Head"
				 --,"division"
),

monthly_checklist_scores AS (
 SELECT 
    mc."CM",
    mc."RM",
    mc."ZM",
  mc."Head",
    to_char(date_trunc('month', "Date"), 'YYYY-MM') AS "Month",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%BDC%') AS "BDC Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%DM-AA%') AS "DM-AA Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%CSD Checklist%') AS "CSD Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%Cashier%') AS "Cashier Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%VM Checklist%') AS "VM Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%Maintenance%') AS "Maintenance Checklist Score (Monthly)",
    AVG("Completion Score") FILTER (WHERE "Routine Name" ILIKE '%SM%') AS "SM Checklist Score (Monthly)"
  FROM croma.checklist_completions mc
  WHERE (
    "Routine Name" ILIKE '%BDC%' OR
    "Routine Name" ILIKE '%DM-AA%' OR
    "Routine Name" ILIKE '%CSD Checklist%' OR
    "Routine Name" ILIKE '%Cashier%' OR
    "Routine Name" ILIKE '%VM Checklist%' OR
    "Routine Name" ILIKE '%Maintenance%' OR
    "Routine Name" ILIKE '%VM%' OR
    "Routine Name" ILIKE '%SM%'
  )
  AND "Routine Name" NOT ILIKE '%Tribe%'
  AND "Date" >= date_trunc('year', CURRENT_DATE) AND "Date" <= CURRENT_DATE
  GROUP BY mc."CM",mc. "RM", mc."ZM",mc."Head", to_char(date_trunc('month', "Date"), 'YYYY-MM')
)
SELECT 
  mc."CM",
  mc."RM",
  mc."ZM",
  mc."Head",
  --y."division",
  mc."Month",
  y."SMART Audit Score (YTD)",
  y."SOP Audit Score (YTD)",
  y."Process Excellence Score (YTD)",
  y."Process KPI Score (YTD)",
  COALESCE(mc."BDC Checklist Score (Monthly)", 0) AS "BDC Checklist Score (Monthly)",
  COALESCE(mc."DM-AA Checklist Score (Monthly)", 0) AS "DM-AA Checklist Score (Monthly)",
  COALESCE(mc."CSD Checklist Score (Monthly)", 0) AS "CSD Checklist Score (Monthly)",
  COALESCE(mc."Cashier Checklist Score (Monthly)", 0) AS "Cashier Checklist Score (Monthly)",
  COALESCE(mc."VM Checklist Score (Monthly)", 0) AS "VM Checklist Score (Monthly)",
  COALESCE(mc."Maintenance Checklist Score (Monthly)", 0) AS "Maintenance Checklist Score (Monthly)"
FROM monthly_checklist_scores mc
LEFT JOIN ytd_scores y 
  ON LOWER(COALESCE(mc."CM", '')) = LOWER(COALESCE(y."CM", ''))
 AND LOWER(COALESCE(mc."RM", '')) = LOWER(COALESCE(y."RM", ''))
 AND LOWER(COALESCE(mc."ZM", '')) = LOWER(COALESCE(y."ZM", ''))
 AND LOWER(COALESCE(mc."Head", '')) = LOWER(COALESCE(y."Head", ''))
ORDER BY mc."CM", mc."Month"
```

---
