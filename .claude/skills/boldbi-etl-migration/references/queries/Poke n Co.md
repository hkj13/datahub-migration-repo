# Poke n Co

> Auto-generated on 2026-03-04 08:13

**Total queries:** 8

---

## Poke Customer Complaint Tracker Incident Log_Customer Complaints - Staff Tracker.sql

**Tables referenced:** RAW, ack, ack_q, complaints, details, details_q, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, sa_check, t, tasks, user_details, user_groups

**Columns needing snake_case conversion:**

- `formDetails` -> `form_details` (alias: `form_details AS "formDetails"`)

- `linkedFormId` -> `linked_form_id` (alias: `linked_form_id AS "linkedFormId"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)


**Original Query:**

```sql
-- Data Source: Poke Customer Complaint Tracker Incident Log
-- Dashboard: Customer Complaints - Staff Tracker
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:58:16
-- ============================================================

WITH sa_check AS
  (SELECT is_super_admin is_sa
   FROM user_details ud
   WHERE uuid = @{{:UUIDParameter}}),
     location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'PokeandCo-cartwheel'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = @{{:UUIDParameter}})
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = @{{:UUIDParameter}}
                    AND ug2.has_access = TRUE )
               AND ug1.is_active = TRUE ))), 
		forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE classification_type = 'form'
     AND title ILIKE 'Customer Complaint Tracker & incident log%'
     AND is_deleted = 'false'
     AND organization = 'PokeandCo-cartwheel'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
   ORDER BY response_id,
            id DESC),
                                                                                             fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
                                                                                             RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id,
          fr.submit_date AT TIME ZONE 'Asia/Dubai' AS submit_date
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
   ORDER BY 1,
            2,
            3), complaints AS
  ( SELECT response_id AS "Complaint KNID",
           max(form_knid) AS "Form KNID",
           min(sno) AS "Complaint SNo",
           min(submit_date) AS "Complaint Date",
           max(CASE
                   WHEN question ILIKE 'Type of complaint' THEN response
                   ELSE NULL
               END) AS "Complaint Type",
           max(CASE
                                   WHEN question = 'Comments' THEN response
                                   ELSE NULL
                               END) AS "Details",
           max(CASE
                   WHEN question ILIKE 'Order No%' THEN response
                   ELSE NULL
               END) AS "Order #",
           max(CASE
                   WHEN question = 'Brand Name' THEN response
                   ELSE NULL
               END) AS "Brand",
           max(CASE
                   WHEN question ilike 'Branch Name%' THEN response
                   ELSE NULL
               END) AS "Branch",
           max(CASE
                   WHEN question ILIKE 'Menu Item%' THEN response
                   ELSE NULL
               END) AS "Menu Item",
           max(CASE
                   WHEN question ILIKE 'Platform%' THEN response
                   ELSE NULL
               END) AS "Delivery Platform",
           max(CASE
                   WHEN question ILIKE 'Recorded by%'
                        AND section_no = 1 THEN response
                   ELSE NULL
               END) AS "Recorded By",
           max(CASE
                   WHEN question = 'Details'
                        AND section_no = 2 THEN response
                   ELSE NULL
               END) AS "Investigation Findings",
           initcap(max(CASE
                   WHEN question ILIKE '%staff mistake%' THEN response
                   ELSE NULL
               END)) AS "Was it staff mistake?"
   FROM RAW
   GROUP BY 1
   ORDER BY 4,
            3),
                t AS
  (SELECT id AS task_knid,
          details->>'linkedFormId' AS staff_form
   FROM tasks t
   JOIN complaints ON t.details->'formDetails'->>'responseId' = complaints."Complaint KNID"
   GROUP BY 1,
            2),
                ack_q AS
  (SELECT nugget_id,
          question_id
   FROM question_definitions qd
   JOIN t ON qd.nugget_id = t.staff_form
   WHERE question ILIKE '%mistake%'
   GROUP BY 1,
            2),
                details_q AS
  (SELECT nugget_id,
          question_id
   FROM question_definitions qd
   JOIN t ON qd.nugget_id = t.staff_form
   WHERE question ILIKE '%details%'
   GROUP BY 1,
            2),
                ack AS
  (SELECT fs.response_id,
          fr.question_id,
          fr.response->'selected'->>0 AS response
   FROM form_responses fr
   JOIN form_submissions fs ON fr.form_submit_id = fs.id
   JOIN ack_q ON ack_q.nugget_id = fs.form_id
   AND ack_q.question_id = fr.question_id
   JOIN t ON fs.parent_nugget_id = t.task_knid),
                details AS
  (SELECT fs.response_id,
          fr.question_id,
          fr.response->'selected'->>0 AS response
   FROM form_responses fr
   JOIN form_submissions fs ON fr.form_submit_id = fs.id
   JOIN details_q ON details_q.nugget_id = fs.form_id
   AND details_q.question_id = fr.question_id
   JOIN t ON fs.parent_nugget_id = t.task_knid)
SELECT complaints.*,
       initcap(max(ack.response)) AS "Staff Acknowledged?",
       initcap(max(details.response)) AS "Staff Comments"
FROM complaints
LEFT OUTER JOIN ack ON complaints."Complaint KNID" = ack.response_id
LEFT OUTER JOIN details ON complaints."Complaint KNID" = details.response_id
LEFT OUTER JOIN sa_check ON sa_check.is_sa
JOIN location_acl acl ON (trim(acl.job_location) ILIKE '%'||trim(complaints."Branch")||'%'
                          OR sa_check.is_sa)
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
ORDER BY 4 DESC,
         5,
         8,
         9,
         10,
         3
```

---

## Poke Customer Complaints_Customer Complaints.sql

**Tables referenced:** DATA, RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_acl, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, sa_check, user_details, user_groups

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Poke Customer Complaints
-- Dashboard: Customer Complaints
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:56:22
-- ============================================================

 SELECT
		"QueryTable 1"."Complaint ID" AS "Complaint ID",
		"QueryTable 1"."Date of Complaint" AS "Date of Complaint",
		"QueryTable 1"."Status" AS "Status",
		"QueryTable 1"."Pending with" AS "Pending with",
		"QueryTable 1"."Branch Name" AS "Branch Name",
		"QueryTable 1"."Type of complaint" AS "Type of complaint",
		"QueryTable 1"."Complaint Details" AS "Complaint Details",
		"QueryTable 1"."Product" AS "Product",
		"QueryTable 1"."Platform" AS "Platform",
		"QueryTable 1"."Investigated By" AS "Investigated By",
		"QueryTable 1"."Investigated On" AS "Investigated On",
		"QueryTable 1"."Investigation Summary" AS "Investigation Summary",
		"QueryTable 1"."Proposed Actions" AS "Proposed Actions",
		"QueryTable 1"."Action taken" AS "Action taken",
		"QueryTable 1"."First Response Duration (Hrs)" AS "First Response Duration (Hrs)",
		"QueryTable 1"."Investigation Completion Duration (Hrs)" AS "Investigation Completion Duration (Hrs)",
		"QueryTable 1"."Action Taken Duration (Hrs)" AS "Action Taken Duration (Hrs)"
FROM(WITH sa_check AS
  (SELECT is_super_admin is_sa
   FROM user_details ud
   WHERE uuid = 'i8TGnaVdZfXFbRFeM5TiB3'),
     location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'PokeandCo-cartwheel'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'All')
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = 'i8TGnaVdZfXFbRFeM5TiB3')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = 'i8TGnaVdZfXFbRFeM5TiB3'
                    AND ug2.has_access = TRUE )
               AND ug1.is_active = TRUE ))), /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id in ('-O522gjRgNXGK6kqx99Q', '-NxC4OTopUqvOl5Xj2VI')), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
   ORDER BY response_id,
            id DESC),
                                                                                    fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
                                                                                    RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
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
            2,
            3), DATA AS
  (SELECT sno AS "Complaint ID",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'Date of Complaint' THEN response::TIMESTAMP WITHOUT TIME ZONE AT TIME ZONE 'Asia/Dubai'
                  ELSE NULL
              END) AS "Date of Complaint",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '4 - Closed'
                  WHEN section_no = 3
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '3 - Investigated'
                  WHEN section_no = 2
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '2 - Assigned'
                  WHEN section_no = 1
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '1 - Raised'
              END) AS "Status",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '4 - None'
                  WHEN section_no = 3
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '3 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 2
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '2 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 1
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '1 - '||(section_response -> 'receiver' ->>'userName')
              END) AS "Pending with",
          max(CASE
                  WHEN section_no = 1
                       AND question ILIKE 'Branch Name' THEN response
                  ELSE NULL
              END) AS "Branch Name",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'Type of complaint' THEN response
                  ELSE NULL
              END) AS "Type of complaint",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'Nature of Complaint and Details' THEN response
                  ELSE NULL
              END) AS "Complaint Details",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'Product Name' THEN response
                  ELSE NULL
              END) AS "Product",
          max(CASE
                  WHEN section_no = 1
                       AND question = 'Delivery Service (aggregator)' THEN response
                  ELSE NULL
              END) AS "Platform",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Investigated By' THEN response
                  ELSE NULL
              END) AS "Investigated By",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Date' THEN response::date
                  ELSE NULL
              END) AS "Investigated On",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Investigation Summary:' THEN response
                  ELSE NULL
              END) AS "Investigation Summary",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Proposed corrective actions' THEN response
                  ELSE NULL
              END) AS "Proposed Actions",
          max(CASE
                  WHEN section_no = 4
                       AND question = 'Corrective action' THEN response
                  ELSE NULL
              END) AS "Action taken",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 2
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "First Response Duration (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 3
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Investigation Completion Duration (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 4
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Action Taken Duration (Hrs)"
   FROM RAW
   GROUP BY 1)
SELECT data.*
FROM DATA
LEFT OUTER JOIN sa_check ON sa_check.is_sa
JOIN location_acl acl ON (trim(acl.job_location) ILIKE '%'||trim(data."Branch Name")||'%'
                          OR sa_check.is_sa)
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
ORDER BY 3 DESC,
         2 DESC,
         1 DESC)"QueryTable 1"
```

---

## Poke Maintenance Ticket Management_Maintenance Ticket Management.sql

**Tables referenced:** DATA, RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Poke Maintenance Ticket Management
-- Dashboard: Maintenance Ticket Management
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:58:48
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE '%-Maintenance Request Form%'
     AND is_deleted = 'false'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
   WHERE submit_date AT TIME ZONE 'Asia/Dubai' > '2024-06-20'
   ORDER BY response_id,
            id DESC),
                                                                             fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
                                                                             RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
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
            2,
            3), DATA AS
  (SELECT sno AS "Ticket ID",
          max(CASE
                  WHEN section_no = 1
                       AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                  ELSE NULL
              END) AS "Raised At",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 10000
                       AND response ILIKE 'Yes' THEN '5 - Closed'
                  WHEN section_no = 4
                       AND q_no = 10000
                       AND response ILIKE 'No' THEN '6 - Re-reported. Not resolved'
                  WHEN section_no = 3
                       AND q_no = 50000
                       AND response ILIKE 'Yes' THEN '4 - Stage 4 Pending'
                  WHEN section_no = 3
                       AND q_no = 50000
                       AND response ILIKE 'NO' THEN '3 - Stage 3 Work Incomplete'
                  WHEN section_no = 2
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '2 - Stage 3 Pending'
                  WHEN section_no = 1
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '1 - Stage 2 Pending'
			  WHEN section_no = 1
                       AND q_no = 0
                       AND response IN ('returned') THEN '0 - Returned'
                  ELSE '0 - Pending'
              END) AS "Status",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '4 - None'
                  WHEN section_no = 3
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '3 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 2
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '2 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 1
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '1 - '||(section_response -> 'receiver' ->>'userName')
              END) AS "Pending with",
          max(CASE
                  WHEN section_no = 2
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN (section_response -> 'receiver' ->>'userName')
                  ELSE NULL
              END) AS "Technician",
          initcap(max(CASE
                          WHEN section_no = 4
                               AND question = 'I acknowledge that the issue is resolved' THEN response
                          ELSE NULL
                      END)) AS "Branch Acknowledged?",
          max(CASE
                  WHEN section_no = 1
                       AND q_no = 0 THEN section_response -> 'sender' ->>'userName'
                  ELSE NULL
              END) AS "Branch",
          max(CASE
                  WHEN section_no IN (1, 2)
                       AND question ILIKE 'Severity%' THEN response
                  ELSE NULL
              END) AS "Severity",
          max(substring(form_name, position('(' IN form_name)+1, length(form_name)-position('(' IN form_name)-1)) AS "Category",
          max(CASE
                  WHEN section_no = 1
                       AND question ILIKE 'Scan Equipment QR Code%' THEN response
                  ELSE NULL
              END) AS "Equipment",
          max(CASE
                  WHEN section_no = 1
                       AND question ILIKE 'Share details%' THEN response
                  ELSE NULL
              END) AS "Details",
          max(CASE
                  WHEN section_no = 3
                       AND question ILIKE 'Details%' THEN response
                  ELSE NULL
              END) AS "Action Taken",
          max(CASE
                  WHEN section_no = 3
                       AND question ILIKE 'Cost%' THEN response::numeric
                  ELSE NULL
              END) AS "Cost Incurred",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Share details' THEN response
                  ELSE NULL
              END) AS "Remarks for incomplete work",
          max(CASE
                  WHEN section_no = 4
                       AND question = 'share details' THEN response
                  ELSE NULL
              END) AS "Branch remarks",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 2
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "First Response Duration (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 3
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Action Completion Duraton (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 4
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Request Closure Duration (Hrs)"
   FROM RAW
   GROUP BY 1)
SELECT *
FROM DATA
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
         18
HAVING "Raised At" >= '2024-06-20'
and "Status" != '0 - Returned'
ORDER BY 1,
         3 DESC,
         2
```

---

## Poke Maintenance Ticket Management_Ticket Log.sql

**Tables referenced:** DATA, RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Poke Maintenance Ticket Management
-- Dashboard: Ticket Log
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:58:48
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE '%-Maintenance Request Form%'
     AND is_deleted = 'false'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
  (/*Non Table type Questions in Forms without any Logic*/ SELECT nugget_id AS form_knid,
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
   WHERE submit_date AT TIME ZONE 'Asia/Dubai' > '2024-06-20'
   ORDER BY response_id,
            id DESC),
                                                                             fr AS
  (SELECT *
   FROM form_responses fr
   JOIN fs ON fr.form_submit_id = fs.id),
                                                                             RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'checkboxes') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Dubai', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code') THEN fr.response->>0
              WHEN fd.q_type IN ('upload_mixed') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          form_name,
          fd.form_knid,
          fr.response_id AS form_response_knid
   FROM final_definition fd
   JOIN fr ON fr.question_id = fd.qid
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
            2,
            3), DATA AS
  (SELECT sno AS "Ticket ID",
          max(CASE
                  WHEN section_no = 1
                       AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                  ELSE NULL
              END) AS "Raised At",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 10000
                       AND response ILIKE 'Yes' THEN '5 - Closed'
                  WHEN section_no = 4
                       AND q_no = 10000
                       AND response ILIKE 'No' THEN '6 - Re-reported. Not resolved'
                  WHEN section_no = 3
                       AND q_no = 50000
                       AND response ILIKE 'Yes' THEN '4 - Stage 4 Pending'
                  WHEN section_no = 3
                       AND q_no = 50000
                       AND response ILIKE 'NO' THEN '3 - Stage 3 Work Incomplete'
                  WHEN section_no = 2
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '2 - Stage 3 Pending'
                  WHEN section_no = 1
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '1 - Stage 2 Pending'
			  WHEN section_no = 1
                       AND q_no = 0
                       AND response IN ('returned') THEN '0 - Returned'
                  ELSE '0 - Pending'
              END) AS "Status",
          max(CASE
                  WHEN section_no = 4
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN '4 - None'
                  WHEN section_no = 3
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '3 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 2
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '2 - '||(section_response -> 'receiver' ->>'userName')
                  WHEN section_no = 1
                       AND q_no = 0
                       AND section_response IS NOT NULL THEN '1 - '||(section_response -> 'receiver' ->>'userName')
              END) AS "Pending with",
          max(CASE
                  WHEN section_no = 2
                       AND q_no = 0
                       AND response IN ('submitted', 'sent', 'approved') THEN (section_response -> 'receiver' ->>'userName')
                  ELSE NULL
              END) AS "Technician",
          initcap(max(CASE
                          WHEN section_no = 4
                               AND question = 'I acknowledge that the issue is resolved' THEN response
                          ELSE NULL
                      END)) AS "Branch Acknowledged?",
          max(CASE
                  WHEN section_no = 1
                       AND q_no = 0 THEN section_response -> 'sender' ->>'userName'
                  ELSE NULL
              END) AS "Branch",
          max(CASE
                  WHEN section_no IN (1, 2)
                       AND question ILIKE 'Severity%' THEN response
                  ELSE NULL
              END) AS "Severity",
          max(substring(form_name, position('(' IN form_name)+1, length(form_name)-position('(' IN form_name)-1)) AS "Category",
          max(CASE
                  WHEN section_no = 1
                       AND question ILIKE 'Scan Equipment QR Code%' THEN response
                  ELSE NULL
              END) AS "Equipment",
          max(CASE
                  WHEN section_no = 1
                       AND question ILIKE 'Share details%' THEN response
                  ELSE NULL
              END) AS "Details",
          max(CASE
                  WHEN section_no = 3
                       AND question ILIKE 'Details%' THEN response
                  ELSE NULL
              END) AS "Action Taken",
          max(CASE
                  WHEN section_no = 3
                       AND question ILIKE 'Cost%' THEN response::numeric
                  ELSE NULL
              END) AS "Cost Incurred",
          max(CASE
                  WHEN section_no = 3
                       AND question = 'Share details' THEN response
                  ELSE NULL
              END) AS "Remarks for incomplete work",
          max(CASE
                  WHEN section_no = 4
                       AND question = 'share details' THEN response
                  ELSE NULL
              END) AS "Branch remarks",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 2
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "First Response Duration (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 3
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Action Completion Duraton (Hrs)",
          extract(epoch
                  FROM (max(CASE
                                WHEN section_no = 4
                                     AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                ELSE NULL
                            END))- (max(CASE
                                            WHEN section_no = 1
                                                 AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
                                            ELSE NULL
                                        END)))/ 3600 AS "Request Closure Duration (Hrs)"
   FROM RAW
   GROUP BY 1)
SELECT *
FROM DATA
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
         18
HAVING "Raised At" >= '2024-06-20'
and "Status" != '0 - Returned'
ORDER BY 1,
         3 DESC,
         2
```

---

## Poke QHSE Audit Current Date Range_QHSE Audit.sql

**Tables referenced:** audit_location_questions, audit_locations, base, form_responses, form_submissions, location_acl, nuggets, question_definitions, user_details, user_groups

**Columns needing snake_case conversion:**

- `auditMaxScore` -> `audit_max_score` (alias: `audit_max_score AS "auditMaxScore"`)

- `auditScore` -> `audit_score` (alias: `audit_score AS "auditScore"`)

- `auditStatus` -> `audit_status` (alias: `audit_status AS "auditStatus"`)

- `criticalFailed` -> `critical_failed` (alias: `critical_failed AS "criticalFailed"`)

- `formAuditResults` -> `form_audit_results` (alias: `form_audit_results AS "formAuditResults"`)

- `isAudit` -> `is_audit` (alias: `is_audit AS "isAudit"`)


**Original Query:**

```sql
-- Data Source: Poke QHSE Audit Current Date Range
-- Dashboard: QHSE Audit
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:58:18
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
			   audit_location_questions AS
  (SELECT nugget_id,
          question_id
   FROM
     (SELECT DISTINCT ON (nugget_id) nugget_id,
                         jsonb_object_keys(definition -> 'questions') question_id,
                         definition -> 'questions' questions
      FROM question_definitions qd
	  join nuggets n on qd.nugget_id = n.id
      WHERE question_type = 'nested'
        AND sqno = '1'
	  and n.classification_type = 'form'
	  and n.details->>'isAudit' = 'true'
        AND n.title ilike 'HACCP & FOOD SAFETY WEEKLY AUDIT%'
      ORDER BY nugget_id,
               qd.created_at DESC) q
   WHERE questions -> question_id ->> 'question_type' = 'location' ),
     audit_locations AS
  (SELECT nugget_id AS form_id,
          fs.response_id,
          fr.response ->> 'name' AS audit_location
   FROM audit_location_questions alq
   JOIN form_submissions fs ON alq.nugget_id = fs.form_id
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   AND alq.question_id = fr.question_id), base as (
SELECT DISTINCT ON (fs.response_id) fs.form_id,
                   fs.response_id AS "Audit Submission KNID",
                   fs.sno AS "Audit SNo",
                   loc.job_location AS "Location",
                   ud.first_name||' '||ud.last_name AS "Auditor",
                   (fs.submit_date AT TIME ZONE 'Asia/Dubai')::date AS "Audit Submitted At",
                   initcap(fr.response ->> 'auditStatus') AS "Audit Status",
                   (fr.response ->> 'auditScore')::numeric AS "Audit Actual Score",
                   (fr.response ->> 'auditMaxScore')::numeric AS "Audit Max Score",
                   (fr.response ->> 'auditScore')::numeric/(fr.response ->> 'auditMaxScore')::numeric AS "Audit Score %",
	               case when fr.response->>'criticalFailed' IS NOT NULL then 'Critical Failed' else 'Critical Passed' end as "Critical", 
				   case when fs.submit_date at time zone 'Asia/Dubai' between @{{:Selected Date Range.START}}::timestamp and @{{:Selected Date Range.END}}::timestamp then 'Selected Period' else 'Past Period' end as "Period"
FROM location_acl loc
JOIN audit_locations al ON loc.job_location ilike '%'||al.audit_location
join form_submissions fs ON al.response_id = fs.response_id
JOIN form_responses fr ON fr.form_submit_id = fs.id
JOIN user_details ud ON fs.user_id = ud.uuid
WHERE fr.question_id = 'formAuditResults'
and fs.submit_date at time zone 'Asia/Dubai' between @{{:Selected Date Range.START}}::timestamp - (@{{:Selected Date Range.END}}::timestamp - @{{:Selected Date Range.START}}::timestamp)
													and @{{:Selected Date Range.END}}::timestamp
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
	 fr.response,
         fs.id
ORDER BY fs.response_id,
         fs.id DESC)
		 
		 select "Location",
		 @{{:Selected Date Range.START}}::date as "Selected Period Start", @{{:Selected Date Range.END}}::date as "Selected Period End",
		 (@{{:Selected Date Range.START}}::timestamp - (@{{:Selected Date Range.END}}::timestamp - @{{:Selected Date Range.START}}::timestamp))::date as "Past Period Start", @{{:Selected Date Range.START}}::timestamp - interval '1 day' as "Past Period End",
		 (coalesce(count(distinct(case when "Period" = 'Selected Period' then "Audit Submission KNID" else null end)), 0))::numeric as "Audit Count: Selected Period",
		 (count(distinct(case when "Audit Status" = 'Passed' and "Period" = 'Selected Period' then "Audit Submission KNID" else null end)))::numeric as "Passed Count: Selected Period",
		 (count(distinct(case when "Critical" = 'Critical Failed' and "Period" = 'Selected Period' then "Audit Submission KNID" else null end)))::numeric as "Critical Failed Count: Selected Period",
		 (count(distinct(case when "Period" = 'Past Period' then "Audit Submission KNID" else null end)))::numeric as "Audit Count: Past Period",
		 (count(distinct(case when "Audit Status" = 'Passed' and "Period" = 'Past Period' then "Audit Submission KNID" else null end)))::numeric as "Passed Count: Past Period",
		 (count(distinct(case when "Critical" = 'Critical Failed' and "Period" = 'Past Period' then "Audit Submission KNID" else null end)))::numeric as "Critical Failed Count: Past Period",
		 avg(case when "Period" = 'Selected Period' then "Audit Score %" else null end) as "Avg Rating: Selecting Period",
		 avg(case when "Period" = 'Past Period' then "Audit Score %" else null end) as "Avg Rating: Past Period"
		 from base
		 group by 1, 2, 3, 4, 5
		 order by 1
```

---

## Poke n Co Personal Hygiene Compliance_Personal Hygiene Compliance.sql

**Tables referenced:** form_compliance, location_acl, nuggets, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Poke n Co Personal Hygiene Compliance
-- Dashboard: Personal Hygiene Compliance
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:56:10
-- ============================================================

 SELECT
		"QueryTable 1"."Organization" AS "Organization",
		"QueryTable 1"."Date" AS "Date",
		"QueryTable 1"."Routine KNID" AS "Routine KNID",
		"QueryTable 1"."Routine Name" AS "Routine Name",
		"QueryTable 1"."Location" AS "Location",
		"QueryTable 1"."Staff Name" AS "Staff Name",
		"QueryTable 1"."Staff ID" AS "Staff ID",
		"QueryTable 1"."Reminded At" AS "Reminded At",
		"QueryTable 1"."Responded At" AS "Responded At",
		"QueryTable 1"."Compliance" AS "Compliance",
		"QueryTable 1"."Submission KNID" AS "Submission KNID"
FROM(WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'PokeandCo-cartwheel'
   and is_active = 'true'
   and job_location not in ('KNOW', 'HQ', 'Head Office', 'All')
   and job_location not ilike 'Head Office%'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = 'i8TGnaVdZfXFbRFeM5TiB3')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id ='i8TGnaVdZfXFbRFeM5TiB3'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'PokeandCo-cartwheel')
select distinct on (fc.organization, fc.form_id, fc.user_id, (fc.reminded_at + td.diff)::date) 
fc.organization as "Organization",
(fc.reminded_at + td.diff)::date as "Date",
fc.form_id as "Routine KNID",
n.title as "Routine Name",
fc.job_location as "Location",
ud.first_name||' ' ||ud.last_name as "Staff Name",
ud.identifier as "Staff ID",
(fc.reminded_at + td.diff)  as "Reminded At",
(fc.responded_at + td.diff)  as "Responded At",
case when fc.responded_at is null then 0 else 1 end as "Compliance",
fc.response_id as "Submission KNID"
from form_compliance fc
join location_acl on fc.job_location = location_acl.job_location
join td on td.organization = fc.organization
join nuggets n on fc.form_id = n.id
join user_details ud on fc.user_id = ud.uuid
where fc.form_id = '-NoakmbGqDHDTH5n4_cs'
and (fc.reminded_at + td.diff) between '2025-05-01 00:00:00'::timestamp and '2025-05-31 23:59:59'::timestamp + interval '1 day'
order by fc.organization, fc.form_id, fc.user_id, (fc.reminded_at + td.diff)::date, fc.responded_at)"QueryTable 1"
```

---

## Routine Compliance - Large Data_Personal Hygiene Compliance.sql

**Tables referenced:** form_compliance_v2, location_acl, organizations, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Routine Compliance - Large Data
-- Dashboard: Personal Hygiene Compliance
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:58:17
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
			   td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = @{{:OrganizationParameter}})
select fc.*
from form_compliance_v2 fc
join location_acl on fc."Location" = location_acl.job_location
where fc."Organization" =@{{:OrganizationParameter}}
and fc."Date" between @{{:Date Range.START}}::date and @{{:Date Range.END}}::date
order by 1, 3, 5, 2, 6
```

---

## Vehicle Ticket Management_Vehicle Ticket Management.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `eE` -> `e_e` (alias: `e_e AS "eE"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Vehicle Ticket Management
-- Dashboard: Vehicle Ticket Management
-- Category: Poke n Co
-- Extracted: 2026-01-29 16:59:08
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE n.organization ILIKE 'Pokeand%'
     AND n.title ILIKE 'Vehicle Maintenance%'
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
            13)
SELECT form_knid AS "Form KNID",
       form_response_knid AS "Ticket KNID",
       sno AS "Ticket ID",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Official Closure - Confirm that the vehicle is back in service and the ticket can be officially closed'
                    AND response = 'Yes' THEN '5. Closed'
               WHEN section_no = 3
                    AND q_no = 0
                    AND section_response->>'status' = 'approved' THEN '4. Ops Approved. Pending Action'
               WHEN section_no = 3
                    AND q_no = 0
                    AND section_response->>'status' = 'rejected' THEN '3. Ops Rejected'
               WHEN section_no = 2
                    AND q_no = 0
                    AND section_response->>'status' = 'sent' THEN '2. Supervisor Approved. Pending Ops Approval'
               WHEN section_no = 1
                    AND q_no = 0
                    AND section_response->>'status' = 'sent' THEN '1. Raised. Pending Review'
               ELSE NULL
           END) AS "Status",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN to_timestamp(((section_response->>'st')::bigint)/1000)
               ELSE NULL
           END) AS "Raised At",
		   max(CASE
               WHEN section_no = 4
                    AND q_no = 0 THEN to_timestamp(((section_response->>'st')::bigint)/1000)
               ELSE NULL
           END) AS "Closed At",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN section_response->'sender'->>'userName'
               ELSE NULL
           END) AS "Raised By",
       max(CASE
               WHEN section_no = 1
                    AND q_type = 'location' THEN response
               ELSE NULL
           END) AS "Branch",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Which vehicle (registration number) are you reporting for?' THEN response
               ELSE NULL
           END) AS "Vehicle Number",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Area of Issue' THEN response
               ELSE NULL
           END) AS "Area of Issue",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Issue Type' THEN response
               ELSE NULL
           END) AS "Issue Type",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Issue Category' THEN response
               ELSE NULL
           END) AS "Issue Category",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Urgency Level' THEN response
               ELSE NULL
           END) AS "Urgency Level",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Maintenance Team Details' THEN response
               ELSE NULL
           END) AS "Maintenance Team Details",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Cost of work done' THEN response::numeric
               ELSE NULL
           END) AS "Cost",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Quality - were the repairs and maintenance completed satisfactorily?' THEN response
               ELSE NULL
           END) AS "Quality Accepted?",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Completion - Have all the issues been resolved?' THEN response
               ELSE NULL
           END) AS "Work Completed?",
       max(CASE
               WHEN section_no = 4
                    AND question = 'Does the work come with a warranty or guarantee?' THEN response
               ELSE NULL
           END) AS "Warranty",
       max(CASE
               WHEN section_no = 4
                    AND parent_question = 'Did the maintenance team recommend any future work or monitoring for the vehicle?'
                    AND question = 'Details' THEN response
               ELSE NULL
           END) AS "Follow-up Work"
FROM RAW
GROUP BY 1,
         2,
         3
ORDER BY 3,
         4 DESC,
         5
```

---
