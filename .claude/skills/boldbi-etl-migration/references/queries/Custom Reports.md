# Custom Reports

> Auto-generated on 2026-03-04 08:13

**Total queries:** 47

---

## 1P Warehouse - New Associates Onboarding_1P Warehouse - New Associates Onboarding.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: 1P Warehouse - New Associates Onboarding
-- Dashboard: 1P Warehouse - New Associates Onboarding
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:56
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%1P Warehouse - New Associates Onboarding%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date >= date_trunc('month', current_date)
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
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name as "UserName"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join user_details ud on fr.user_id = ud.uuid
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
            16,
            17
   ORDER BY 1,
            2,
            3)
SELECT sno,submit_date,location,"UserName",
MAX(CASE WHEN question ILIKE 'New Associates Onboarding%' THEN response END) AS "New Associates Onboarding",
MAX(CASE WHEN question ILIKE 'Associate Email Address%' THEN response END) AS "Associate Email Address",
MAX(CASE WHEN question ILIKE 'Associate Employee Code%' THEN response END) AS "Associate Employee Code",
MAX(CASE WHEN question ILIKE 'Employee Type%' THEN response END) AS "Employee Type",
MAX(CASE WHEN question ILIKE 'Sourced by Vendor Name%' THEN response END) AS "Vendor Name ",
MAX(CASE WHEN question ILIKE 'Associate First Name%' THEN response END) AS "Associate First Name",
MAX(CASE WHEN question ILIKE 'Associate Middle Name%' THEN response END) AS "Associate Middle Name/ Father Name",
MAX(CASE WHEN question ILIKE 'Associate Last Name%' THEN response END) AS "Associate Last Name/ Surname",
MAX(CASE WHEN question ILIKE 'Gender%' THEN response END) AS "Gender",
MAX(CASE WHEN question ILIKE 'Date of Birth%' THEN response END) AS "Date of Birth",
MAX(CASE WHEN question ILIKE 'Associate Mobile Number%' THEN response END) AS "Associate Mobile Number",
MAX(CASE WHEN question ILIKE 'This does not look like a correct mobile number%' THEN response END) AS "This does not look like a correct mobile number, please check the number you have entered",
MAX(CASE WHEN question ILIKE 'Associate Date of Joining%' THEN response END) AS "Associate Date of Joining",
MAX(CASE WHEN question ILIKE 'City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE 'Designation%' THEN response END) AS "Designation",
MAX(CASE WHEN question ILIKE 'Reporting Manager Email ID%' THEN response END) AS "Reporting Manager Email ID",
MAX(CASE WHEN question ILIKE 'Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE 'Sourced By%' THEN response END) AS "Sourced By",
MAX(CASE WHEN question ILIKE 'Associate Mobile Type%' THEN response END) AS "Associate Mobile Type",
MAX(CASE WHEN question ILIKE 'Associate Age%' THEN response END) AS "Associate Age",
MAX(CASE WHEN question ILIKE 'Onboarding cannot happen for Age less than 18%' THEN response END) AS "Onboarding cannot happen for Age less than 18",
MAX(CASE WHEN question ILIKE 'Associate Aadhaar No.%' THEN response END) AS "Associate Aadhaar No.",
MAX(CASE WHEN question ILIKE 'Previously associate have ever worked with Zepto%' THEN response END) AS "Previously associate have ever worked with Zepto?",
MAX(CASE WHEN question ILIKE 'Previous Employee ID%' THEN response END) AS "Previous Employee ID",
MAX(CASE WHEN question ILIKE 'Previous Mobile Number%' THEN response END) AS "Previous Mobile Number",
MAX(CASE WHEN question ILIKE 'How much associates scored in the interview assessment%' THEN response END) AS "How much associates scored in the interview assessment?",
MAX(CASE WHEN question ILIKE 'Remark or Comment about associate%' THEN response END) AS "Remark or Comment about associate",
MAX(CASE WHEN question ILIKE 'Associate is Fit to Work%' THEN response END) AS "Associate is Fit to Work",
MAX(CASE WHEN question ILIKE 'Please attach the offer letter%' THEN response END) AS "Please attach the offer letter",
MAX(CASE WHEN question ILIKE 'Associate''s Net Take home salary%' THEN response END) AS "Associate's Net Take home salary (Mention as per offer letter)"
FROM raw
group by 1,2,3,4
```

---

## CK Tangs Weekly Attendance Report_CK Tangs Attendance Report.sql

**Tables referenced:** time_events_clockin, time_events_clockout, user_details

**Original Query:**

```sql
-- Data Source: CK Tangs Weekly Attendance Report
-- Dashboard: CK Tangs Attendance Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:37
-- ============================================================

SELECT lpad(base.identifier, 8, '0') AS emp_id,
       base.job_location AS LOCATION,
       to_char(base.attendance_date, 'DD-Mon-YY') AS attendance_date,
       base.event_time,
       base.event
FROM (/*this query will return the first clock in table*/
        (SELECT user_details.identifier,
                user_details.job_location,
                (time_events_clockin.ci_time AT TIME ZONE 'sgt')::date AS attendance_date,
                to_char(min(time_events_clockin.ci_time) AT TIME ZONE 'sgt', 'hh24mi') AS event_time,
                'Clock-in' AS event
         FROM time_events_clockin
         JOIN user_details ON time_events_clockin.uuid = user_details.uuid
         WHERE user_details.organization LIKE '%tang%'
           AND time_events_clockin.ci_time AT TIME ZONE 'sgt' BETWEEN current_timestamp::date - interval '7 days' AND current_timestamp::date
         GROUP BY 1,
                  2,
                  3
         ORDER BY 1,
                  3)
      UNION /*this query will return the last clock out table. Logic is to fetch the paired clock-out event of the last clock-in event for a user for a day*/
        (SELECT user_details.identifier,
                user_details.job_location,
                (time_events_clockout.co_time AT TIME ZONE 'sgt')::date AS attendance_date,
                to_char(max(time_events_clockout.co_time) AT TIME ZONE 'sgt', 'hh24mi') AS event_time,
                'Clock-out' AS event
         FROM
           (/*this sub query gets the latest clock-in for each user for each day*/SELECT check_in_rank.uuid,
                                                                                         check_in_rank.job_location,
                                                                                         check_in_rank.identifier,
                                                                                         check_in_rank.ci_time,
                                                                                         check_in_rank.event_id
            FROM
              (/*this sub query ranks the clock-in events in desc order for each user for each day*/ SELECT time_events_clockin.uuid,
                                                                                                            user_details.job_location,
                                                                                                            user_details.identifier,
                                                                                                            time_events_clockin.ci_time AT TIME ZONE 'sgt' AS ci_time,
                                                                                                                                                     time_events_clockin.event_id,
                                                                                                                                                     rank () OVER (PARTITION BY time_events_clockin.uuid,
                                                                                                                                                                                (time_events_clockin.ci_time AT TIME ZONE 'sgt')::date
                                                                                                                                                                   ORDER BY ci_time DESC) AS row_no
               FROM time_events_clockin
               JOIN user_details ON time_events_clockin.uuid = user_details.uuid
               WHERE user_details.organization LIKE '%tang%'
                 AND time_events_clockin.ci_time AT TIME ZONE 'sgt' BETWEEN current_timestamp::date - interval '7 days' AND current_timestamp::date
               ORDER BY uuid,
                        ci_time DESC) check_in_rank
            WHERE check_in_rank.row_no = 1) last_check_in
         JOIN time_events_clockout ON last_check_in.event_id = time_events_clockout.ci_event_id
         JOIN user_details ON time_events_clockout.uuid = user_details.uuid
         WHERE user_details.organization LIKE '%tang%'
         GROUP BY 1,
                  2,
                  3
         ORDER BY 1,
                  3)) base
ORDER BY 1,
         3,
         4
```

---

## Cafe - New Associate - Zepto_Zepto - Checklists Report.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Cafe - New Associate - Zepto
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:02
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Cafe - New Associates Onboarding%')
     AND organization = 'Zds-indus'
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
WHERE submit_date >= '2025-01-01'
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%Associate Email Address%' THEN response END) AS "Associate Email Address",
MAX(CASE WHEN question ILIKE '%Associate Employee Code%' THEN response END) AS "Associate Employee Code",
MAX(CASE WHEN question ILIKE '%Employee Type%' THEN response END) AS "Employee Type",
MAX(CASE WHEN question ILIKE '%Vendor Name%' THEN response END) AS "Vendor Name",
MAX(CASE WHEN question ILIKE '%Associate First Name%' THEN response END) AS "Associate First Name",
MAX(CASE WHEN question ILIKE '%Associate Middle Name%' THEN response END) AS "Associate Middle Name",
MAX(CASE WHEN question ILIKE '%Associate Last Name/ Surname%' THEN response END) AS "Associate Last Name/ Surname",
MAX(CASE WHEN question ILIKE '%Gender%' THEN response END) AS "Gender",
MAX(CASE WHEN question ILIKE '%Date of Birth%' THEN response END) AS "Date of Birth",
MAX(CASE WHEN question ILIKE '%Associate Mobile Number%' THEN response END) AS "Associate Mobile Number",
MAX(CASE WHEN question ILIKE '%Associate Date of Joining%' THEN response END) AS "Associate Date of Joining",
MAX(CASE WHEN question ILIKE '%New joiner''s Designation%' THEN response END) AS "New joiner's Designation",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Reporting Manager Email ID%' THEN response END) AS "Reporting Manager Email ID",
MAX(CASE WHEN question ILIKE '%Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE '%Sourced By%' THEN response END) AS "Sourced By",
MAX(CASE WHEN question ILIKE '%Associate Mobile Type%' THEN response END) AS "Associate Mobile Type",
MAX(CASE WHEN question ILIKE '%Associate Age%' THEN response END) AS "Associate Age",
MAX(CASE WHEN question ILIKE '%Associate Aadhaar No.%' THEN response END) AS "Associate Aadhaar No.",
MAX(CASE WHEN question ILIKE '%Previously associate have ever worked with Zepto?%' THEN response END) AS "Previously associate have ever worked with Zepto?",
MAX(CASE WHEN question ILIKE '%Previous Employee ID%' THEN response END) AS "Previous Employee ID",
MAX(CASE WHEN question ILIKE '%Previous Mobile Number%' THEN response END) AS "Previous Mobile Number",
MAX(CASE WHEN question ILIKE '%How much associates scored in the interview assessment?%' THEN response END) AS "How much associates scored in the interview assessment?",
MAX(CASE WHEN question ILIKE '%Remark or Comment about associate%' THEN response END) AS "Remark or Comment about associate",
MAX(CASE WHEN question ILIKE '%Associate is Fit to Work%' THEN response END) AS "Associate is Fit to Work",
MAX(CASE WHEN question ILIKE '%Please attach the offer letter%' THEN response END) AS "Please attach the offer letter",
MAX(CASE WHEN question ILIKE '%Associate''s Net Take home salary (Mention as per offer letter)%' THEN response END) AS "Associate's Net Take home salary (Mention as per offer letter)"
FROM RAW
group by 1,2,3
```

---

## Clean Sweep Report_Clean Sweep Report - Moved.sql

**Tables referenced:** MAX, checkpoint_master_sheet_table, location_map, pivoted_scores, user_Details

**Original Query:**

```sql
-- Data Source: Clean Sweep Report
-- Dashboard: Clean Sweep Report - Moved
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:45
-- ============================================================

WITH location_map AS
  ( SELECT DISTINCT ON (division,
                        sub_division,
                        regexp_replace(job_location, '([0-9]+).*', '\1')) division AS region,
                       sub_division AS city,
                       regexp_replace(job_location, '([0-9]+).*', '\1') AS pod
   FROM user_Details
   WHERE is_active = TRUE
     AND (regexp_replace(job_location, '([0-9]+).*', '\1') IS NOT NULL
          OR regexp_replace(job_location, '([0-9]+).*', '\1') != '')
   ORDER BY 1,
            2,
            3,
            created_at DESC),
     pivoted_scores AS
  ( SELECT lm.pod AS "POD ID",
           INITCAP(cms.store_id) AS "Pod Name",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '1)%' THEN result_score::numeric
               END) AS "1) Validate cleaning checklists of racks, chillers/freezers & toilets.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '2)%' THEN result_score::numeric
               END) AS "2) No Cockroaches, Lizards, House Flies, Mosquito, Rodent dropping, rat bites, are observed in POD at any area. Pest control shall be in place.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '3)%' THEN result_score::numeric
               END) AS "3) Functional Pest-o-Flash or Insectocutor shall be used inside the POD, positioned at the entrance of the POD and at 6-7 feet height. Glue pads shall be discarded & replaced with new as and when insects are filled up.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '4)%' THEN result_score::numeric
               END) AS "4) Dump bins & Dust bins used shall be of Cap Closure & Bins should be in clean condition. No Dump Stock have contact with Fresh and good material . Dump shall be kept seperately and discarded on time.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '5)%' THEN result_score::numeric
               END) AS "5) All Shelves are clean, no cob web, no dust, no rust, no spillage of Food & Non-food (FMCG) products on racks, chiller, freezers & Floors",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '6)%' THEN result_score::numeric
               END) AS "6) Timely removal of empty carton boxes",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '7)%' THEN result_score::numeric
               END) AS "7) Washrooms & Floors shall be kept regularly Clean & hygienic and Running water available. (Auditor must check for female restroom in case of female employees)",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '8)%' THEN result_score::numeric
               END) AS "8) No Expired articles found in racks ( F&V, Ambient, Chiller and Freezer). If 1 Expiry is seen no negotiation Score will be “0”",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '11)%' THEN result_score::numeric
               END) AS "11) Temperature checks for DSD / Warehouse F&V Products shall be in place, If DSD / Warehouse Cut F&V are not meeting <10 Degree Celcius, products must be rejected by PODs",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '12)%' THEN result_score::numeric
               END) AS "12) F&V stored as per SOP",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '13)%' THEN result_score::numeric
               END) AS "13) No F&V is overloaded in racks",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '14)%' THEN result_score::numeric
               END) AS "14) F&V Storage shall be organized at Racks, Crates, Freezers & Chillers",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '15)%' THEN result_score::numeric
               END) AS "15) Leaf articles shall be covered with Pre-pack polybags, Wet gunny bags or Muslin Cloth at PODs",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '17)%' THEN result_score::numeric
               END) AS "17) 20 SKUs (Including F&V) FIFO/FEFO check - 100% accuracy ",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '18)%' THEN result_score::numeric
               END) AS "18) The temperature of ”“Reach-In/Walk-In Freezer”“ shall me maintained between ”“-18 and -22”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '19)%' THEN result_score::numeric
               END) AS "19) The temperature of ”“Reach-In/Walk-In Chiller”“ shall me maintained between ”“0 and 5”“ degree Celsius If the ideal temperature is not attained , auditor to recheck after 1hr.”",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '20)%' THEN result_score::numeric
               END) AS "20) F&V Room shall be maintained at +18 to +22 degree Celsius throughout the F&V Storage If the ideal temperature is not attained , auditor to recheck after 1hr.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '21)%' THEN result_score::numeric
               END) AS "21) F&V Shelves are free for Rotten/Rotting Produce",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '22)%' THEN result_score::numeric
               END) AS "22) Cold room, Chiller rooms & Chest freezers are in best working condition with no ice formation, No overload of materials in it, No storage of dumps",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '23)%' THEN result_score::numeric
               END) AS "23) Temperature checks of Chillers & freezers shall be in place",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '24)%' THEN result_score::numeric
               END) AS "24) Are atta, breads, buns, and eggs stacked based on the First Expired, First Out (FEFO) method. If any SKUs found deviating the FEFO process, no negotiation Score will be “0”",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '28)%' THEN result_score::numeric
               END) AS "28) Are ice-cream SKUs packed using Insulation bag / Ice bag? - Sampling",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '29)%' THEN result_score::numeric
               END) AS "29) Calibrated and functional Thermometer is available at POD.",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '38)%' THEN result_score::numeric
               END) AS "38) POD shall have valid FSSAI License that shall be pasted on wall and visible clearly",
           MAX(CASE
                   WHEN cms.checkpoint ILIKE '39)%' THEN result_score::numeric
               END) AS "39) POD shall have updated A3 Size Coloured Food Safety Display Board, shall be pasted on wall and visible clearly", -- Calculate score from MAX() columns
 ( COALESCE(MAX(CASE
                    WHEN cms.checkpoint ILIKE '1)%' THEN result_score::numeric
                END), 0) + COALESCE(MAX(CASE
                                            WHEN cms.checkpoint ILIKE '2)%' THEN result_score::numeric
                                        END), 0) + COALESCE(MAX(CASE
                                                                    WHEN cms.checkpoint ILIKE '3)%' THEN result_score::numeric
                                                                END), 0) + COALESCE(MAX(CASE
                                                                                            WHEN cms.checkpoint ILIKE '4)%' THEN result_score::numeric
                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                    WHEN cms.checkpoint ILIKE '5)%' THEN result_score::numeric
                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                            WHEN cms.checkpoint ILIKE '6)%' THEN result_score::numeric
                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                    WHEN cms.checkpoint ILIKE '7)%' THEN result_score::numeric
                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '8)%' THEN result_score::numeric
                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '11)%' THEN result_score::numeric
                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '12)%' THEN result_score::numeric
                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '13)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '14)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '15)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '17)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '18)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '19)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '20)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '21)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '22)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '23)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '24)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '28)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '29)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            WHEN cms.checkpoint ILIKE '38)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        END), 0) + COALESCE(MAX(CASE
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    WHEN cms.checkpoint ILIKE '39)%' THEN result_score::numeric
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                END), 0) ) AS "Final Audit Score"
   FROM checkpoint_master_sheet_table cms
   LEFT JOIN location_map lm ON regexp_replace(cms.store_id, '([0-9]+).*', '\1') = lm.pod
   WHERE cms.audit_main_theme ILIKE 'Pod Compliance%'
     AND audit_submitted_at >= date_trunc('month', current_date)
   AND (
  cms.checkpoint ILIKE '1)%' OR
  cms.checkpoint ILIKE '2)%' OR
  cms.checkpoint ILIKE '3)%' OR
  cms.checkpoint ILIKE '4)%' OR
  cms.checkpoint ILIKE '5)%' OR
  cms.checkpoint ILIKE '6)%' OR
  cms.checkpoint ILIKE '7)%' OR
  cms.checkpoint ILIKE '8)%' OR
  cms.checkpoint ILIKE '11)%' OR
  cms.checkpoint ILIKE '12)%' OR
  cms.checkpoint ILIKE '13)%' OR
  cms.checkpoint ILIKE '14)%' OR
  cms.checkpoint ILIKE '15)%' OR
  cms.checkpoint ILIKE '17)%' OR
  cms.checkpoint ILIKE '18)%' OR
  cms.checkpoint ILIKE '19)%' OR
  cms.checkpoint ILIKE '20)%' OR
  cms.checkpoint ILIKE '21)%' OR
  cms.checkpoint ILIKE '22)%' OR
  cms.checkpoint ILIKE '23)%' OR
  cms.checkpoint ILIKE '24)%' OR
  cms.checkpoint ILIKE '28)%' OR
  cms.checkpoint ILIKE '29)%' OR
  cms.checkpoint ILIKE '38)%' OR
  cms.checkpoint ILIKE '39)%'
)

   GROUP BY lm.pod,
            cms.store_id )
SELECT *,
       CASE
           WHEN "Final Audit Score" >= 91 THEN 'Outstanding Performance'
           WHEN "Final Audit Score" BETWEEN 81 AND 90 THEN 'Compliant'
           WHEN "Final Audit Score" BETWEEN 71 AND 80 THEN 'Partially Compliant'
           ELSE 'Non-Compliant'
       END AS "Audit Rating"
FROM pivoted_scores
ORDER BY "POD ID"
```

---

## Closing Checklist 2.0_Zepto - Checklists Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Closing Checklist 2.0
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:40
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Closing Checklist 2.0%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%City%' THEN response END) AS "City",
MAX(CASE WHEN question ILIKE '%Café Name%' THEN response END) AS "Café Name",
MAX(CASE WHEN question ILIKE '%All machines are switched off and ready for cleaning%' THEN response END) AS "All machines are switched off and ready for cleaning",
MAX(CASE WHEN question ILIKE '%All smallware are washed, disinfected and placed accordingly%' THEN response END) AS "All smallware are washed, disinfected and placed accordingly",
MAX(CASE WHEN question ILIKE '%Any pest is observed in café%' THEN response END) AS "Any pest is observed in café",
MAX(CASE WHEN question ILIKE '%Café bins are cleaned and disinfected%' THEN response END) AS "Café bins are cleaned and disinfected",
MAX(CASE WHEN question ILIKE '%CCP 2 -Under counter chiller 1 ( 1-5°C)%' THEN response END) AS "CCP 2 -Under counter chiller 1 ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%Chest Freezer 1 cleaning is done including gasket, inside & outside deep freezer%' THEN response END) AS "Chest Freezer 1 cleaning is done including gasket, inside & outside deep freezer",
MAX(CASE WHEN question ILIKE '%Coffee Machine cleaning is done including porta filter & machine%' THEN response END) AS "Coffee Machine cleaning is done including porta filter & machine",
MAX(CASE WHEN question ILIKE '%KDS/ODS should be clean and printer roll laoded?%' THEN response END) AS "KDS/ODS should be clean and printer roll laoded?",
MAX(CASE WHEN question ILIKE '%Merry Chef or Turbo chef cleaning is done%' THEN response END) AS "Merry Chef or Turbo chef cleaning is done",
MAX(CASE WHEN question ILIKE '%All products expiry checking is done%' THEN response END) AS "All products expiry checking is done",
MAX(CASE WHEN question ILIKE '%All work stations are cleaned and disinfected (Food Preparation area & packing table)%' THEN response END) AS "All work stations are cleaned and disinfected (Food Preparation area & packing table)",
MAX(CASE WHEN question ILIKE '%CCP 2-Under counter chiller 2 ( 1-5°C)%' THEN response END) AS "CCP 2-Under counter chiller 2 ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%Chest Freezer 2 cleaning is done including gasket, inside & outside deep freezer%' THEN response END) AS "Chest Freezer 2 cleaning is done including gasket, inside & outside deep freezer",
MAX(CASE WHEN question ILIKE '%Grinder machine cleaning is done%' THEN response END) AS "Grinder machine cleaning is done",
MAX(CASE WHEN question ILIKE '%HSD device put on charging mode and clean%' THEN response END) AS "HSD device put on charging mode and clean",
MAX(CASE WHEN question ILIKE '%Microwave 1 cleaning is done%' THEN response END) AS "Microwave 1 cleaning is done",
MAX(CASE WHEN question ILIKE '%Packing stock is available and ready for PRP%' THEN response END) AS "Packing stock is available and ready for PRP",
MAX(CASE WHEN question ILIKE '%All the product has pasted MRD%' THEN response END) AS "All the product has pasted MRD",
MAX(CASE WHEN question ILIKE '%CCP 2-Visicooler ( 1-5°C)%' THEN response END) AS "CCP 2-Visicooler ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%Chiller 1 cleaning is done as per SOP including gasket, inside & outside chiller%' THEN response END) AS "Chiller 1 cleaning is done as per SOP including gasket, inside & outside chiller",
MAX(CASE WHEN question ILIKE '%Cold stock is is kept for thawing as per ROS%' THEN response END) AS "Cold stock is is kept for thawing as per ROS",
MAX(CASE WHEN question ILIKE '%Cup Sealing machine cleaning is done%' THEN response END) AS "Cup Sealing machine cleaning is done",
MAX(CASE WHEN question ILIKE '%Microwave 2 cleaning is done%' THEN response END) AS "Microwave 2 cleaning is done",
MAX(CASE WHEN question ILIKE '%Wall TV unit clean%' THEN response END) AS "Wall TV unit clean",
MAX(CASE WHEN question ILIKE '%Wash basin cleaning is done along with drainage%' THEN response END) AS "Wash basin cleaning is done along with drainage",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 1 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 1 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Chiller 2 cleaning is doneas as per SOP including gasket, inside & outside chiller%' THEN response END) AS "Chiller 2 cleaning is doneas as per SOP including gasket, inside & outside chiller",
MAX(CASE WHEN question ILIKE '%Closing stock: Food done%' THEN response END) AS "Closing stock: Food done",
MAX(CASE WHEN question ILIKE '%Floor is cleaned and disinfected%' THEN response END) AS "Floor is cleaned and disinfected",
MAX(CASE WHEN question ILIKE '%Microwave 3 cleaning is done%' THEN response END) AS "Microwave 3 cleaning is done",
MAX(CASE WHEN question ILIKE '%Veg & non veg segregation is done%' THEN response END) AS "Veg & non veg segregation is done",
MAX(CASE WHEN question ILIKE '%Waste water drain box cleaning is done%' THEN response END) AS "Waste water drain box cleaning is done",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 2 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 2 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Closing stock: Non-food done%' THEN response END) AS "Closing stock: Non-food done",
MAX(CASE WHEN question ILIKE '%Daily Cleaning checklist%' THEN response END) AS "Daily Cleaning checklist",
MAX(CASE WHEN question ILIKE '%Equipment and table behind cleaning is done%' THEN response END) AS "Equipment and table behind cleaning is done",
MAX(CASE WHEN question ILIKE '%Ice machine cleaning is done%' THEN response END) AS "Ice machine cleaning is done",
MAX(CASE WHEN question ILIKE '%Microwave 4 cleaning is done%' THEN response END) AS "Microwave 4 cleaning is done",
MAX(CASE WHEN question ILIKE '%Visi cooler cleaning is done as per SOP including gasket, inside & outside chiller%' THEN response END) AS "Visi cooler cleaning is done as per SOP including gasket, inside & outside chiller",
MAX(CASE WHEN question ILIKE '%All Cupboard Cleaning is done%' THEN response END) AS "All Cupboard Cleaning is done",
MAX(CASE WHEN question ILIKE '%Blender machine cleaning is done%' THEN response END) AS "Blender machine cleaning is done",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 3 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 3 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Cleaning equipments are washed and kept aside%' THEN response END) AS "Cleaning equipments are washed and kept aside",
MAX(CASE WHEN question ILIKE '%Food Tray & utensils trays cleaning is done%' THEN response END) AS "Food Tray & utensils trays cleaning is done",
MAX(CASE WHEN question ILIKE '%Verticle freezer should be clean including gasket.%' THEN response END) AS "Verticle freezer should be clean including gasket.",
MAX(CASE WHEN question ILIKE '%All pumps cleaning is done%' THEN response END) AS "All pumps cleaning is done",
MAX(CASE WHEN question ILIKE '%CCP 2-Verticle freezer 1 (-18-23°C)%' THEN response END) AS "CCP 2-Verticle freezer 1 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Hand wash sink should be clean and sanitized%' THEN response END) AS "Hand wash sink should be clean and sanitized",
MAX(CASE WHEN question ILIKE '%Racks and tops are cleaned and dustfree%' THEN response END) AS "Racks and tops are cleaned and dustfree",
MAX(CASE WHEN question ILIKE '%Veg & non veg chopping baord cleaning is done%' THEN response END) AS "Veg & non veg chopping baord cleaning is done",
MAX(CASE WHEN question ILIKE '%Wall cleaning is done%' THEN response END) AS "Wall cleaning is done",
MAX(CASE WHEN question ILIKE '%All Jar cleaning is done%' THEN response END) AS "All Jar cleaning is done",
MAX(CASE WHEN question ILIKE '%All receiving and stacking done as per REGBY%' THEN response END) AS "All receiving and stacking done as per REGBY",
MAX(CASE WHEN question ILIKE '%CCP 2-Verticle freezer 2 (-18-23°C)%' THEN response END) AS "CCP 2-Verticle freezer 2 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Chaipoint Machine should be clean and along with boiler & utensils%' THEN response END) AS "Chaipoint Machine should be clean and along with boiler & utensils",
MAX(CASE WHEN question ILIKE '%Wet & dry dustbin should be clean and dispose properly%' THEN response END) AS "Wet & dry dustbin should be clean and dispose properly",
MAX(CASE WHEN question ILIKE '%Any fly/lizard/rodent/cockroach observed in Roda Box%' THEN response END) AS "Any fly/lizard/rodent/cockroach observed in Roda Box",
MAX(CASE WHEN question ILIKE '%Tea machine cleaning done%' THEN response END) AS "Tea machine cleaning done",
MAX(CASE WHEN question ILIKE '%Wonder wipe and duster cleaning is done%' THEN response END) AS "Wonder wipe and duster cleaning is done",
MAX(CASE WHEN question ILIKE '%All drawer and stoarge area cleaning is done%' THEN response END) AS "All drawer and stoarge area cleaning is done",
MAX(CASE WHEN question ILIKE '%All fly catchers switched on%' THEN response END) AS "All fly catchers switched on",
MAX(CASE WHEN question ILIKE '%Fans are cleaned and dustfree%' THEN response END) AS "Fans are cleaned and dustfree",
MAX(CASE WHEN question ILIKE '%Food storage area should be clean and Fifo to be maintained%' THEN response END) AS "Food storage area should be clean and Fifo to be maintained",
MAX(CASE WHEN question ILIKE '%Garbage bin is refreshed with new liner and garbage thrown%' THEN response END) AS "Garbage bin is refreshed with new liner and garbage thrown",
MAX(CASE WHEN question ILIKE '%Packer table should be clean%' THEN response END) AS "Packer table should be clean",
MAX(CASE WHEN question ILIKE '%PRP cupeboard should be clean%' THEN response END) AS "PRP cupeboard should be clean",
MAX(CASE WHEN question ILIKE '%Piegon hole should be clean%' THEN response END) AS "Piegon hole should be clean",
MAX(CASE WHEN question ILIKE '%All boxes PRP are present as per locaton in Map%' THEN response END) AS "All boxes PRP are present as per locaton in Map",
MAX(CASE WHEN question ILIKE '%Water Storage Tank%' THEN response END) AS "Water Storage Tank"
FROM raw
group by 1,2,3
```

---

## Croma - Weekly Attendance Data_Croma - Weekly Attendance Data.sql

**Tables referenced:** shift_attendance

**Original Query:**

```sql
-- Data Source: Croma - Weekly Attendance Data
-- Dashboard: Croma - Weekly Attendance Data
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:30
-- ============================================================

SELECT "Shift ID",
       ("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date AS shift_date,
       "Status", -- Check-in split
 "Employee ID",
 "Employee Name",
 "Designation",
 "Home Location",
 "Shift Location",
 TO_CHAR("Actual Clockin Time" AT TIME ZONE 'Asia/Kolkata', 'DD/MM/YY') AS check_in_date,
 TO_CHAR("Actual Clockin Time" AT TIME ZONE 'Asia/Kolkata', 'HH24:MI') AS check_in_time, -- Check-out split
 TO_CHAR("Actual Clockout Time" AT TIME ZONE 'Asia/Kolkata', 'DD/MM/YY') AS check_out_date,
 TO_CHAR("Actual Clockout Time" AT TIME ZONE 'Asia/Kolkata', 'HH24:MI') AS check_out_time
FROM shift_attendance
WHERE ("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')::date 
      BETWEEN current_date - INTERVAL '7 days' AND current_date - INTERVAL '1 day'
ORDER BY "Employee ID",
         shift_date
```

---

## Croma MACL Report_Croma MACL Report.sql

**Tables referenced:** user_details

**Columns needing snake_case conversion:**

- `lmsCourses` -> `lms_courses` (alias: `lms_courses AS "lmsCourses"`)

- `lmsReports` -> `lms_reports` (alias: `lms_reports AS "lmsReports"`)


**Original Query:**

```sql
-- Data Source: Croma MACL Report
-- Dashboard: Croma MACL Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:52:28
-- ============================================================

SELECT uuid,
       first_name,
       last_name,
       identifier,
       division,
       sub_division,
       job_location AS outlet,
       department,
       designation,
       CASE
           WHEN is_super_admin = 'true' THEN 'Yes'
           ELSE 'No'
       END AS is_super_admin,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS announcements_polls_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS bites_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS shifts_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' IS NULL THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' IN ('255','65535') THEN 'Full Access'
           ELSE 'View'
       END AS forms_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS issues_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'tasks' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS tasks_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS lmscourses_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS lmsreports_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' IS NULL THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'sop' IN ('255','65535') THEN 'Full Access'
           ELSE 'No Access'
       END AS guides_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' IS NULL THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' IN ('255','65535') THEN 'Full Access'
           ELSE 'View'
       END AS users_access,


       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '1' THEN 'View'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' IN ('15','17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' IN ('255','65535') THEN 'Full Access'
           ELSE 'Full Access'
       END AS groups_access

FROM user_details
WHERE is_active = TRUE
  AND organization = 'croma-coma'
  AND PROFILE::jsonb ? 'ACL'
  AND PROFILE::jsonb->'ACL' ? 'dashboard'
```

---

## Croma Tags Report_Croma Live Tags.sql

**Tables referenced:** LATERAL, user_details

**Columns needing snake_case conversion:**

- `userTags` -> `user_tags` (alias: `user_tags AS "userTags"`)


**Original Query:**

```sql
-- Data Source: Croma Tags Report
-- Dashboard: Croma Live Tags
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:28
-- ============================================================

SELECT ud.uuid AS "UUID",
       first_name||' '||last_name AS "Name",
       identifier AS "Emp ID",
       phone_number AS "Phone Number",
       division AS "State",
       sub_division AS "City",
       job_location AS "Store",
       department AS "Department",
       designation AS "Designation",
	   doj,
       STRING_AGG(CASE
                      WHEN ut.key = 'category' THEN tag.value->>'value'
                  END, ', ') AS category,
       STRING_AGG(CASE
                      WHEN ut.key = 'brand' THEN tag.value->>'value'
                  END, ', ') AS brand
       FROM user_details ud
CROSS JOIN LATERAL jsonb_each(ud.profile->'userTags') ut
CROSS JOIN LATERAL jsonb_array_elements(ut.value) AS tag
WHERE organization = 'croma-coma'
  AND is_active = 'true'
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9
```

---

## Croma Weekly Incidents_Croma Weekly Incidents.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Croma Weekly Incidents
-- Dashboard: Croma Weekly Incidents
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:53
-- ============================================================

WITH td AS
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
   WHERE title ILIKE 'Safety Incident%'
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
   WHERE submit_date >= date_trunc('month', CURRENT_DATE)),
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name,
          ud.identifier,
          ud.designation,
          ud.division,
          ud.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON fr.user_id = ud.uuid
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
            20
   ORDER BY 1,
            2,
            3)
SELECT form_name AS "Form Name",
       sno AS "Submission Number",
       submit_date AS "Submit Date",
       first_name AS "Sender Name",
       identifier AS "Sender Identifier",
       designation AS "Sender Designation",
       division AS "Sender Division",
       sub_division AS "Sender Sub Division",
       MAX(CASE
               WHEN question = 'Location' THEN response
               ELSE NULL
           END) AS "Location",
       MAX(CASE
               WHEN question = 'Sub Category' THEN response
               ELSE NULL
           END) AS "Sub Category",
       MAX(CASE
               WHEN question = 'Description of the issue' THEN response
               ELSE NULL
           END) AS "Description of the issue",
       MAX(CASE
               WHEN question = 'Upload supporting evidence' THEN response
               ELSE NULL
           END) AS "Upload supporting evidence"
FROM RAW
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8
```

---

## Custom Report Alamar Dominos Maintenance Requests_Alamar Dominos Maintenance Requests.sql

**Tables referenced:** alamar_dominos_maintenance_requests_table, user_details, users

**Original Query:**

```sql
-- Data Source: Custom Report Alamar Dominos Maintenance Requests
-- Dashboard: Alamar Dominos Maintenance Requests
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:58
-- ============================================================

WITH users AS
  (SELECT uuid,
                   organization
   FROM user_details
   WHERE is_active = 'true'
  and phone_number not ilike '+9111%')
select requests."Ticket No",
requests."Country",
requests."Region",
requests."City",
requests."Requester",
requests."Requested ID",
requests."Requester UUID",
requests."Request Type",
requests."Issues",
requests."Current Status",
case when left(requests."Cost"::varchar, 1) in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')  then requests."Cost" else null end as "Cost",
requests."Were All Tasks Completed",
requests."Requested At",
requests."Responded At",
requests."Acknowledged At"
FROM alamar_dominos_maintenance_requests_table requests
join users on users.uuid = requests."Requester UUID"
where date_trunc('Year', requests."Requested At") = date_trunc('Year', current_timestamp)
```

---

## Daily Pinned Nuggets_Daily Pinned Nuggets.sql

**Tables referenced:** nuggets, pinned_nuggets, share_progress, user_details

**Columns needing snake_case conversion:**

- `isPinned` -> `is_pinned` (alias: `is_pinned AS "isPinned"`)

- `pinUntil` -> `pin_until` (alias: `pin_until AS "pinUntil"`)


**Original Query:**

```sql
-- Data Source: Daily Pinned Nuggets
-- Dashboard: Daily Pinned Nuggets
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:32
-- ============================================================

WITH pinned_nuggets AS
  (SELECT nuggets.id AS knid,
          nuggets.title,
          nuggets.details ->> 'notes' AS BODY,
                              user_details.email AS author,
                              to_timestamp(nuggets.created_at::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS created_at,
                                                                                         min(share_progress.created_at AT TIME ZONE 'Asia/Kolkata') AS pinned_at,
                                                                                         to_timestamp((nuggets.details->>'pinUntil')::bigint/1000) AT TIME ZONE 'Asia/Kolkata' AS pinned_until,
                                                                                                                                                                nuggets.sent_count
   FROM nuggets
   JOIN user_details ON nuggets.author = user_details.uuid
   JOIN share_progress ON nuggets.id = share_progress.nugget_id
   WHERE details ->> 'isPinned' = 'true'
     AND is_deleted = 'false'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            7,
            8)
SELECT pinned_nuggets.knid,
       pinned_nuggets.title,
       pinned_nuggets.body,
       pinned_nuggets.author,
       to_char(pinned_nuggets.created_at, 'YYYY-MM-DD HH24:MI') AS created_at,
       to_char(pinned_nuggets.pinned_at, 'YYYY-MM-DD HH24:MI') AS pinned_at,
       to_char(pinned_nuggets.pinned_until, 'YYYY-MM-DD HH24:MI') AS pinned_until,
       pinned_nuggets.sent_count
FROM pinned_nuggets
WHERE pinned_nuggets.pinned_until >= now() AT TIME ZONE 'Asia/Kolkata'
  AND author NOT IN ('jayakumarp@knownuggets.com',
                     'genguk@knownuggets.com',
                     'abhisheks@knownuggets.com',
                     'jayakumarp+or@knownuggets.com',
					'satyak+or@knownuggets.com',
					'alexk+or@knownuggets.com',
					'praneethtv+or@knownuggets.com')
ORDER BY pinned_until,
         sent_count DESC
```

---

## Daily Store Visit Update - Trainer Checklist_Daily Store Visit Update - Trainer Checklist Report.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Daily Store Visit Update - Trainer Checklist
-- Dashboard: Daily Store Visit Update - Trainer Checklist Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:07
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ILIKE ('Daily Store Visit Update%')
     AND organization = 'Zds-indus'
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
   WHERE submit_date >= date_trunc('week', current_date)
  AND submit_date <= current_date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name,
          ud.department,
          ud.division,
          ud.sub_division
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
            16,
            17,
            18
   ORDER BY 1,
            2,
            3)
SELECT sno,
       submit_date AS form_submit_date,
       first_name AS form_submitter,
       division AS submitter_division,
       sub_division AS submitter_sub_division,
       form_name,
       MAX(CASE
               WHEN parent_question = 'Date of Visit' THEN response
           END) AS "Date of Visit",
       MAX(CASE
               WHEN parent_question = 'Visit Type' THEN response
           END) AS "Visit Type",
       MAX(CASE
               WHEN parent_question = 'Trainer Name' THEN response
           END) AS "Trainer Name",
       MAX(CASE
               WHEN parent_question = 'Zone' THEN response
           END) AS "Zone",
       MAX(CASE
               WHEN parent_question = 'City Name' THEN response
           END) AS "City Name",
       MAX(CASE
               WHEN parent_question = 'Store Name' THEN response
           END) AS "Store Name",
       MAX(CASE
               WHEN parent_question = 'DHM Name' THEN response
           END) AS "DHM Name",
       MAX(CASE
               WHEN parent_question = 'RTM' THEN response
           END) AS "RTM",
       MAX(CASE
               WHEN parent_question = 'LC1 Planned Count (Numbers)' THEN response
           END) AS "LC1 Planned Count (Numbers)",
       MAX(CASE
               WHEN parent_question = 'LC1 Trained Count (Numbers)' THEN response
           END) AS "LC1 Trained Count (Numbers)",
       MAX(CASE
               WHEN parent_question = 'Are the associates aware on the Payout structure ?' THEN response
           END) AS "Are the associates aware on the Payout structure ?",
       MAX(CASE
               WHEN parent_question = 'Do the associates know on the monthy attendance bonus?' THEN response
           END) AS "Do the associates know on the monthy attendance bonus?",
       MAX(CASE
               WHEN parent_question = 'Are the associates aware about the Personal Hygiene standards?' THEN response
           END) AS "Are the associates aware about the Personal Hygiene standards?",
       MAX(CASE
               WHEN parent_question = 'Are the associates aware on the POC incase of Punching issue?' THEN response
           END) AS "Are the associates aware on the POC incase of Punching issue?",
       MAX(CASE
               WHEN parent_question = 'Do the associates know how to complete the announcement in the packman app?' THEN response
           END) AS "Do the associates know how to complete the announcement in the packman app?",
       MAX(CASE
               WHEN parent_question = 'Are the associates aware about the grievance handling procedure?' THEN response
           END) AS "Are the associates aware about the grievance handling procedure?",
       MAX(CASE
               WHEN parent_question = 'Do the Associates aware about the role of Picker and packer?' THEN response
           END) AS "Do the Associates aware about the role of Picker and packer?",
       MAX(CASE
               WHEN parent_question = 'Do the associates know about the significance of IPP and Defects?' THEN response
           END) AS "Do the associates know about the significance of IPP and Defects?",
       MAX(CASE
               WHEN parent_question = 'Do the associates aware about the FRESSH?' THEN response
           END) AS "Do the associates aware about the FRESSH?",
       MAX(CASE
               WHEN parent_question = 'Are the associates know on the importance of material handling?' THEN response
           END) AS "Are the associates know on the importance of material handling?",
       MAX(CASE
               WHEN parent_question = 'DHM Covered Count' THEN response
           END) AS "DHM Covered Count",
       MAX(CASE
               WHEN parent_question = 'SI Covered Count' THEN response
           END) AS "SI Covered Count",
       MAX(CASE
               WHEN parent_question = 'Associates Covered Count' THEN response
           END) AS "Associates Covered Count",
       MAX(CASE
               WHEN parent_question = 'Average Score for DHM''s' THEN response
           END) AS "Average Score for DHM's",
       MAX(CASE
               WHEN parent_question = 'Average Score for SI''s' THEN response
           END) AS "Average ScoreFOR SI's",
       MAX(CASE
               WHEN parent_question = 'Average Score for Associates' THEN response
           END) AS "Average Score for Associates",
       MAX(CASE
               WHEN parent_question = 'Upload Training Image' THEN response
           END) AS "Upload Training Image",
       MAX(CASE
               WHEN parent_question = 'Remarks (IF ANY)' THEN response
           END) AS "Remarks (If Any)"
FROM RAW
GROUP BY 1,
         2,
         3,
         4,
         5,
         6
```

---

## Franchise Associates Onboarding - Zepto_Franchise Associate Onboarding Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Franchise Associates Onboarding - Zepto
-- Dashboard: Franchise Associate Onboarding Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:39
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Franchise Associates Onboarding%')
     AND organization = 'Zds-indus'
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
       WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,location,
MAX(CASE WHEN question ILIKE '%New Associates Onboarding%' THEN response END) AS "New Associates Onboarding",
MAX(CASE WHEN question ILIKE '%Associate Email Address%' THEN response END) AS "Associate Email Address",
MAX(CASE WHEN question ILIKE '%Associate Employee Code%' THEN response END) AS "Associate Employee Code",
MAX(CASE WHEN question ILIKE '%Associate First Name%' THEN response END) AS "Associate First Name",
MAX(CASE WHEN question ILIKE '%Associate Middle Name/ Father Name%' THEN response END) AS "Associate Middle Name/ Father Name",
MAX(CASE WHEN question ILIKE '%Associate Last Name/ Surname%' THEN response END) AS "Associate Last Name/ Surname",
MAX(CASE WHEN question ILIKE '%Gender%' THEN response END) AS "Gender",
MAX(CASE WHEN question ILIKE '%Date of Birth%' THEN response END) AS "Date of Birth",
MAX(CASE WHEN question ILIKE '%Associate Mobile Number%' THEN response END) AS "Associate Mobile Number",
MAX(CASE WHEN question ILIKE '%Associate Date of Joining%' THEN response END) AS "Associate Date of Joining",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Designation%' THEN response END) AS "Designation",
MAX(CASE WHEN question ILIKE '%Reporting Manager Email ID%' THEN response END) AS "Reporting Manager Email ID",
MAX(CASE WHEN question ILIKE '%Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE '%Associate Mobile Type%' THEN response END) AS "Associate Mobile Type",
MAX(CASE WHEN question ILIKE '%Associate Age%' THEN response END) AS "Associate Age",
MAX(CASE WHEN question ILIKE '%Onboarding cannot happen for Age less than 18%' THEN response END) AS "Onboarding cannot happen for Age less than 18",
MAX(CASE WHEN question ILIKE '%Associate Aadhaar No.%' THEN response END) AS "Associate Aadhaar No.",
MAX(CASE WHEN question ILIKE '%Previously associate have ever worked with Zepto?%' THEN response END) AS "Previously associate have ever worked with Zepto?",
MAX(CASE WHEN question ILIKE '%Previous Employee ID%' THEN response END) AS "Previous Employee ID",
MAX(CASE WHEN question ILIKE '%Previous Mobile Number%' THEN response END) AS "Previous Mobile Number",
MAX(CASE WHEN question ILIKE '%Please attach the offer letter%' THEN response END) AS "Please attach the offer letter"
FROM raw
group by 1,2,3,4
```

---

## Franchise Associates Onboarding - Zepto_Zepto - Checklists Report 2.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Franchise Associates Onboarding - Zepto
-- Dashboard: Zepto - Checklists Report 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:39
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Franchise Associates Onboarding%')
     AND organization = 'Zds-indus'
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
       WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,location,
MAX(CASE WHEN question ILIKE '%New Associates Onboarding%' THEN response END) AS "New Associates Onboarding",
MAX(CASE WHEN question ILIKE '%Associate Email Address%' THEN response END) AS "Associate Email Address",
MAX(CASE WHEN question ILIKE '%Associate Employee Code%' THEN response END) AS "Associate Employee Code",
MAX(CASE WHEN question ILIKE '%Associate First Name%' THEN response END) AS "Associate First Name",
MAX(CASE WHEN question ILIKE '%Associate Middle Name/ Father Name%' THEN response END) AS "Associate Middle Name/ Father Name",
MAX(CASE WHEN question ILIKE '%Associate Last Name/ Surname%' THEN response END) AS "Associate Last Name/ Surname",
MAX(CASE WHEN question ILIKE '%Gender%' THEN response END) AS "Gender",
MAX(CASE WHEN question ILIKE '%Date of Birth%' THEN response END) AS "Date of Birth",
MAX(CASE WHEN question ILIKE '%Associate Mobile Number%' THEN response END) AS "Associate Mobile Number",
MAX(CASE WHEN question ILIKE '%Associate Date of Joining%' THEN response END) AS "Associate Date of Joining",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Designation%' THEN response END) AS "Designation",
MAX(CASE WHEN question ILIKE '%Reporting Manager Email ID%' THEN response END) AS "Reporting Manager Email ID",
MAX(CASE WHEN question ILIKE '%Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE '%Associate Mobile Type%' THEN response END) AS "Associate Mobile Type",
MAX(CASE WHEN question ILIKE '%Associate Age%' THEN response END) AS "Associate Age",
MAX(CASE WHEN question ILIKE '%Onboarding cannot happen for Age less than 18%' THEN response END) AS "Onboarding cannot happen for Age less than 18",
MAX(CASE WHEN question ILIKE '%Associate Aadhaar No.%' THEN response END) AS "Associate Aadhaar No.",
MAX(CASE WHEN question ILIKE '%Previously associate have ever worked with Zepto?%' THEN response END) AS "Previously associate have ever worked with Zepto?",
MAX(CASE WHEN question ILIKE '%Previous Employee ID%' THEN response END) AS "Previous Employee ID",
MAX(CASE WHEN question ILIKE '%Previous Mobile Number%' THEN response END) AS "Previous Mobile Number",
MAX(CASE WHEN question ILIKE '%Please attach the offer letter%' THEN response END) AS "Please attach the offer letter"
FROM raw
group by 1,2,3,4
```

---

## Fryer Cleaning process - Zepto_Zepto - Checklists Report 2.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Fryer Cleaning process - Zepto
-- Dashboard: Zepto - Checklists Report 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:41
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id in ('-OPjxcnG_ksNDdCb8O2K')
     AND organization = 'Zds-indus'
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
       WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%Standard cafe name%' THEN response END) AS "Standard cafe name",
MAX(CASE WHEN question ILIKE '%City%' THEN response END) AS "City",
MAX(CASE WHEN question ILIKE '%Form filled by%' THEN response END) AS "Form filled by",
MAX(CASE WHEN question ILIKE '%Is oil filtration done?%' THEN response END) AS "Is oil filtration done?",
MAX(CASE WHEN question ILIKE '%Upload oil filtration pictures.%' THEN response END) AS "Upload oil filtration pictures.",
MAX(CASE WHEN question ILIKE '%What is the TPM meter reading?%' THEN response END) AS "What is the TPM meter reading?",
MAX(CASE WHEN question ILIKE '%Is the TPM meter cleaned properly?%' THEN response END) AS "Is the TPM meter cleaned properly?",
MAX(CASE WHEN question ILIKE '%Is the TPM meter stored at the designated area?%' THEN response END) AS "Is the TPM meter stored at the designated area?",
MAX(CASE WHEN question ILIKE '%Is the fryer basket cleaned as per SOP?%' THEN response END) AS "Is the fryer basket cleaned as per SOP?",
MAX(CASE WHEN question ILIKE '%Upload fryer basket cleaning picture.%' THEN response END) AS "Upload fryer basket cleaning picture.",
MAX(CASE WHEN question ILIKE '%Is fryer deep cleaning done as per SOP?%' THEN response END) AS "Is fryer deep cleaning done as per SOP?",
MAX(CASE WHEN question ILIKE '%Upload fryer deep cleaning picture.%' THEN response END) AS "Upload fryer deep cleaning picture.",
MAX(CASE WHEN question ILIKE '%What is the oil MRD shelf life?%' THEN response END) AS "What is the oil MRD shelf life?",
MAX(CASE WHEN question ILIKE '%Describe the oil color. (Good/Clear/Slight dark/Dark)%' THEN response END) AS "Describe the oil color. (Good/Clear/Slight dark/Dark)",
MAX(CASE WHEN question ILIKE '%Is new oil refilled as per SOP?%' THEN response END) AS "Is new oil refilled as per SOP?",
MAX(CASE WHEN question ILIKE '%Upload picture of filled oil fryer.%' THEN response END) AS "Upload picture of filled oil fryer.",
MAX(CASE WHEN question ILIKE '%Total quantity of oil added in the both fryer (in liters):%' THEN response END) AS "Total quantity of oil added in the both fryer (in liters):",
MAX(CASE WHEN question ILIKE '%Is any foam or excess smoke observed in the oil?%' THEN response END) AS "Is any foam or excess smoke observed in the oil?",
MAX(CASE WHEN question ILIKE '%Is exhaust available and working properly?%' THEN response END) AS "Is exhaust available and working properly?",
MAX(CASE WHEN question ILIKE '%Has the exhaust been cleaned properly?%' THEN response END) AS "Has the exhaust been cleaned properly?",
MAX(CASE WHEN question ILIKE '%Is used oil disposed into the designated waste oil container?%' THEN response END) AS "Is used oil disposed into the designated waste oil container?",
MAX(CASE WHEN question ILIKE '%Upload waste oil container images.%' THEN response END) AS "Upload waste oil container images.",
MAX(CASE WHEN question ILIKE '%Is the waste oil container kept outside the café?%' THEN response END) AS "Is the waste oil container kept outside the café?",
MAX(CASE WHEN question ILIKE '%Is the area surrounding the fryer clean?%' THEN response END) AS "Is the area surrounding the fryer clean?",
MAX(CASE WHEN question ILIKE '%Upload images of fryer surroundings.%' THEN response END) AS "Upload images of fryer surroundings."
FROM raw
group by 1,2,3
```

---

## Greenology - Forms Responses_Greenology Form Responses.sql

**Tables referenced:** form_submissions, nuggets

**Original Query:**

```sql
-- Data Source: Greenology - Forms Responses
-- Dashboard: Greenology Form Responses
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:05
-- ============================================================

SELECT to_char(form_submissions.submit_date, 'DD-Mon-YYYY') AS submission_date,
       nuggets.title AS form_name,
       count(distinct(form_submissions.response_id)) AS submission_count,
       form_submissions.form_id
FROM form_submissions
JOIN nuggets ON form_submissions.form_id = nuggets.id
WHERE form_submissions.organization = 'Greenology-banyan'
  AND form_submissions.submit_date BETWEEN current_timestamp::date - interval '7 days' AND current_timestamp::date
GROUP BY 1,
         2,
         4
ORDER BY 1,
         3 DESC
```

---

## HCC Audit Zepto_Zepto - Checklists Report.sql

**Tables referenced:** form_responses, form_submissions, public.Zepto_QMS_Checkpoint_Master_Sheet_table, question_definitions

**Original Query:**

```sql
-- Data Source: HCC Audit Zepto
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:40
-- ============================================================

SELECT 
  store_id,
  MAX(CASE WHEN question ILIKE '%Write The Standard Café Name%' THEN response::text END) AS "Write The Standard Café Name",
  city_id,
  audit_main_theme,
  theme,
  audit_date,
  audit_submission_number,
  auditor_name,
  checkpoint,
  result,
  auditor_observations
FROM public.Zepto_QMS_Checkpoint_Master_Sheet_table cms
JOIN form_submissions fs 
  ON cms.audit_submission_knid = fs.response_id
JOIN form_responses fr 
  ON fs.id = fr.form_submit_id
Join  question_definitions qd on fr.question_id = qd.question_id
WHERE audit_main_theme ilike ('%HCC%')
  AND audit_date >= date_trunc('week', CURRENT_DATE)
GROUP BY 
  store_id,
  city_id,
  audit_main_theme,
  theme,
  audit_date,
  audit_submission_number,
  auditor_name,
  checkpoint,
  result,
  auditor_observations
```

---

## KNOW X CYC Certification Expiry Alert_CYC Certification Expiry Alert.sql

**Tables referenced:** user_details

**Original Query:**

```sql
-- Data Source: KNOW X CYC Certification Expiry Alert
-- Dashboard: CYC Certification Expiry Alert
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:36
-- ============================================================

SELECT emp_name AS "Employee Name",
       identifier AS "Employee ID",
       division AS "Division",
       sub_division AS "Sub Division",
       job_location AS "Location",
       designation AS "Designation",
       department AS "Department",
       job_type AS "Job Type",
       certification_details ->> 'name' AS "Certification",
                                 certification_details ->> 'value' AS "Expiry"
FROM
  (SELECT first_name||' '||last_name AS emp_name,
          identifier,
          division,
          sub_division,
          job_location,
          job_type,
          designation,
          department,
          jsonb_array_elements(PROFILE -> 'certifications') AS certification_details
   FROM user_details
   WHERE is_active = 'true'
     AND organization ILIKE '%cyc%'
     AND PROFILE -> 'certifications' IS NOT NULL
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            user_details.profile) base
WHERE certification_details ->> 'type' = 'certifications'
  AND certification_details ->> 'value'IS NOT NULL
  AND to_date(certification_details ->> 'value', 'YYYY-MM-DD') BETWEEN '1900-01-01' and CURRENT_DATE + interval '2 months'
ORDER BY 1,
         2,
         10
```

---

## Key Arabia Weekly shifts report_Talabat - Key Arabia Report.sql

**Tables referenced:** params, per_day, pivot_base, shift_attendance, shifts, users_in_week, week_dates, weekly_totals

**Original Query:**

```sql
-- Data Source: Key Arabia Weekly shifts report
-- Dashboard: Talabat - Key Arabia Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:27
-- ============================================================

WITH params AS (
    SELECT
        (date_trunc('week', CURRENT_DATE)::date + 7) AS week_monday,  -- next Monday
        (date_trunc('week', CURRENT_DATE)::date + 13) AS week_sunday  -- next Sunday
),
week_dates AS (
    SELECT g::date AS shift_date
    FROM params p,
         generate_series(p.week_monday, p.week_sunday, interval '1 day') g
),
shifts AS (
    SELECT
        s."Employee ID" AS employee_id,
        s."Employee Name" AS name,
        s."Shift Name" AS shift_name,
        s."Scheduled Start Time" AS start_time,
        s."Scheduled End Time" AS end_time,
        s."Shift Location" AS shift_location,
        COALESCE(NULLIF(s."Scheduled Break Hours",0),1) AS break_hours, -- default 1 if null or 0
        s."Scheduled Start Time"::date AS shift_date,
        (EXTRACT(epoch FROM (s."Scheduled End Time" - s."Scheduled Start Time"))/60)::int AS minutes,
        ROW_NUMBER() OVER (PARTITION BY s."Employee ID", s."Scheduled Start Time"::date ORDER BY s."Scheduled Start Time") AS shift_num
    FROM shift_attendance s
    JOIN params p ON TRUE
    WHERE s."Department" = 'Key Arabia'
      AND s."Scheduled Start Time"::date BETWEEN p.week_monday AND p.week_sunday
),
per_day AS (
    SELECT
        employee_id,
        name,
        shift_date,
        STRING_AGG(
            shift_name || E'\n' ||
            TO_CHAR(start_time, 'HH12:MIAM') || ' - ' || TO_CHAR(end_time, 'HH12:MIAM') || E'\n' ||
            'Break: ' || (break_hours * 60)::int || ' mins' || E'\n' ||
            shift_location,
            E'\n\n' ORDER BY start_time
        ) AS day_shifts,
        SUM(minutes) AS day_minutes
    FROM shifts
    GROUP BY employee_id, name, shift_date
),
users_in_week AS (
    SELECT DISTINCT employee_id, name FROM shifts
),
weekly_totals AS (
    SELECT employee_id, COALESCE(SUM(minutes),0) AS total_minutes
    FROM shifts
    GROUP BY employee_id
),
pivot_base AS (
    SELECT
        u.employee_id,
        u.name,
        wd.shift_date,
        COALESCE(pd.day_shifts, '') AS day_shifts,
        COALESCE(wt.total_minutes, 0) AS total_minutes
    FROM users_in_week u
    CROSS JOIN week_dates wd
    LEFT JOIN per_day pd
        ON pd.employee_id = u.employee_id AND pd.shift_date = wd.shift_date
    LEFT JOIN weekly_totals wt
        ON wt.employee_id = u.employee_id
)
SELECT
    (pb.name || E'\n\n' ||
     LPAD(((pb.total_minutes/60))::text, 2, '0') || ':' ||
     LPAD(((pb.total_minutes%60))::text, 2, '0') || ' hrs/40:00 hrs'
    ) AS "Name",

    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 0 THEN pb.day_shifts END) AS "Mon",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 1 THEN pb.day_shifts END) AS "Tue",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 2 THEN pb.day_shifts END) AS "Wed",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 3 THEN pb.day_shifts END) AS "Thu",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 4 THEN pb.day_shifts END) AS "Fri",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 5 THEN pb.day_shifts END) AS "Sat",
    MAX(CASE WHEN pb.shift_date = (SELECT week_monday FROM params) + 6 THEN pb.day_shifts END) AS "Sun"

FROM pivot_base pb
GROUP BY pb.name, pb.total_minutes
ORDER BY pb.name
```

---

## Kitopi Future Form Submission Date Alerts_Future Form Submission Date Alerts.sql

**Tables referenced:** form_submissions, nuggets, user_details

**Original Query:**

```sql
-- Data Source: Kitopi Future Form Submission Date Alerts
-- Dashboard: Future Form Submission Date Alerts
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:52:24
-- ============================================================

select fs.sno,
       fs.submit_date,
       n.title,
       ud.identifier,
       ud.division,
       fs.location,
       CURRENT_DATE as submitted_date
from form_submissions fs
JOIN user_details ud on fs.user_id = ud.uuid
JOIN nuggets n on fs.form_id = n.id
where submit_date >= CURRENT_DATE + INTERVAL '1 day'
and fs.organization = 'kitopi-pegasus'
```

---

## Kitopi_weekly_report_Kitopi Weekly Report audited by data.sql

**Tables referenced:** LATERAL, base, checkpoint_master_sheet_table, cms, f, form_responses, form_submissions, fr, nuggets, qd, question_definitions

**Columns needing snake_case conversion:**

- `canShare` -> `can_share` (alias: `can_share AS "canShare"`)

- `isAudit` -> `is_audit` (alias: `is_audit AS "isAudit"`)


**Original Query:**

```sql
-- Data Source: Kitopi_weekly_report
-- Dashboard: Kitopi Weekly Report audited by data
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:56:24
-- ============================================================

WITH base AS
  (SELECT fr.form_submit_id,
          fs.response_id
   FROM form_responses fr
   JOIN form_submissions fs ON fr.form_submit_id = fs.id
   JOIN nuggets n ON fs.form_id = n.id
   JOIN question_definitions qd ON n.id = qd.nugget_id
   AND fr.question_id = qd.question_id
   WHERE qd.question = 'First Aid box is fully stocked'
     AND fr.response->'selected'->>0 = 'No'
     AND n.title ILIKE '%Weekly Health and Safety Checklist%'
     AND n.details->>'isAudit' = 'true'
     AND fs.submit_date BETWEEN date_trunc('week', current_date - interval '7 days') 
                      AND date_trunc('week', current_date) - interval '1 second'),
     cms AS
  (SELECT store_id,
          audit_submitted_at AS audited_at,
          auditor_name AS audited_by,
          audit_submission_knid,
          cms.audit_submission_number AS sno,
          audit_main_theme
   FROM checkpoint_master_sheet_table cms
   WHERE audit_main_theme ILIKE '%Weekly Health and Safety Checklist%'
   AND cms.audit_submitted_at BETWEEN date_trunc('week', current_date - interval '7 days') 
                              AND date_trunc('week', current_date) - interval '1 second'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     f AS
  (SELECT id,
          title
   FROM nuggets
   WHERE title ILIKE '%Weekly Health and Safety Checklist%'
     AND is_deleted = 'false'
     AND details->>'canShare' = 'true'),
     qd AS
  (SELECT f.title,
          nugget_id,
          question_id,
          q.key AS aqid,
          q.value->>'question' AS aq,
                    l.key AS lqid,
                    l.value->>'question' AS lq
   FROM question_definitions qd
   JOIN f ON qd.nugget_id = f.id,
             jsonb_each(qd.definition->'questions') AS q,
             jsonb_each(q.value->'logic'->0->'questions') AS l
   WHERE qd.question ILIKE 'Health & Safety checks%'
     AND question_type = 'nested'
     AND q.value->>'question' = 'First Aid box is fully stocked'
     AND l.value->>'question' = 'Select all that are missing in your first aid box'
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7),
     fr AS
  (SELECT base.response_id,
          fr.question_id,
          fr.response
   FROM form_responses fr
   JOIN base ON fr.form_submit_id = base.form_submit_id)
SELECT
  cms.audit_main_theme AS "Audit Name",
  cms.store_id AS "Location",
  cms.audited_at AS "Audited At",
  cms.audited_by AS "Audited By",
  cms.sno AS "Audit Report Number",
  missing_item."Missing Item" AS "Missing Items",
  cms.audit_submission_knid AS "Audit Report KNID"
FROM fr
JOIN cms ON fr.response_id = cms.audit_submission_knid
JOIN qd ON fr.question_id = qd.lqid
CROSS JOIN LATERAL jsonb_array_elements_text(fr.response->'selected') AS missing_item("Missing Item")
ORDER BY 2, 3 DESC, 5, 6
```

---

## Noon Adoption Report_Noon Adoption Report.sql

**Tables referenced:** analytics_requests, ar_login, ar_read, user_details, users

**Original Query:**

```sql
-- Data Source: Noon Adoption Report
-- Dashboard: Noon Adoption Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:58
-- ============================================================

WITH users AS
  (SELECT *
   FROM user_details
   WHERE organization LIKE 'noon%'
     AND to_timestamp(created_at/1000) > CURRENT_TIMESTAMP - interval '3 months'
     AND is_active = 'true'),
     ar_login AS
  (SELECT ar.user_id,
          min(ar.updated_at) AS updated_at
   FROM analytics_requests ar
   JOIN users ON ar.user_id = users.uuid
   WHERE ar.updated_at > CURRENT_TIMESTAMP - interval '3 months'
     AND ar.event_id > 1
   GROUP BY 1),
     ar_read AS
  (SELECT ar.user_id,
          min(ar.updated_at) AS updated_at
   FROM analytics_requests ar
   JOIN users ON ar.user_id = users.uuid
   WHERE ar.updated_at > CURRENT_TIMESTAMP - interval '3 months'
     AND ar.event_id > 2
   GROUP BY 1)
SELECT users.first_name||' '||users.last_name AS "Name",
       users.phone_number as "Phone Number",
       users.identifier as "Identifier",
       users.job_location AS "Hub",
       to_timestamp(users.created_at/1000) at time zone 'Asia/Dubai' as "Registered At",
       CASE
           WHEN ar_login.updated_at IS NOT NULL THEN 'Logged In'
           ELSE 'Not logged in'
       END AS "Login Status",
       CASE
           WHEN ar_read.updated_at IS NOT NULL THEN 'Read announcements'
           ELSE 'Not read'
       END AS "Active Status"
FROM users
LEFT OUTER JOIN ar_login ON users.uuid = ar_login.user_id
LEFT OUTER JOIN ar_read ON users.uuid = ar_read.user_id
ORDER BY 4,
         6,
         7,
         1
```

---

## Noon Weekly Nuggets Report_Noon Weekly Active User Count Report.sql

**Tables referenced:** analytics_requests, event_types, nuggets, part_1, part_2, user_details

**Original Query:**

```sql
-- Data Source: Noon Weekly Nuggets Report
-- Dashboard: Noon Weekly Active User Count Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:56
-- ============================================================

WITH part_1 AS
  (SELECT ar.user_id,
          json_object_agg(et.event_type, ar.updated_at) AS analytics
   FROM analytics_requests ar
   JOIN event_types et ON et.id = ar.event_id
   JOIN nuggets ON ar.nugget_id = nuggets.id
   WHERE ar.nugget_id = '-MMFSXOgyAC1pPVupTwK'
     AND event_id IN (1,
                      2)
   GROUP BY 1),
     part_2 AS
  (SELECT DISTINCT ON (ar.user_id) ar.user_id
   FROM analytics_requests ar
   WHERE ar.event_id > 1
     AND ar.updated_at > CURRENT_TIMESTAMP - interval '1 month'
   ORDER BY ar.user_id,
            ar.updated_at DESC)
SELECT ud.job_location,
       count(distinct(part_1.user_id)) AS regd_user_count,
       count(distinct(CASE
                          WHEN part_1.analytics->>'received' IS NOT NULL THEN part_1.user_id
                          ELSE NULL
                      END)) logged_in_user_count,
       count(distinct(CASE
                          WHEN ud.is_active = 'TRUE' THEN part_1.user_id
                          ELSE NULL
                      END)) current_enabled_user_count,
       count(distinct(CASE
                          WHEN ud.is_active = 'true' THEN part_2.user_id
                          ELSE NULL
                      END)) AS last_1_month_active_user_count
FROM part_1
JOIN user_details ud ON part_1.user_id = ud.uuid
LEFT JOIN part_2 ON part_1.user_id = part_2.user_id
GROUP BY 1
ORDER BY 1
```

---

## Opening Checklist 2.0 - Zepto_Zepto - Checklists Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Opening Checklist 2.0 - Zepto
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:44
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Opening Checklist 2.0%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%Café Name%' THEN response END) AS "Café Name",
MAX(CASE WHEN question ILIKE '%Write The Standard Café Name%' THEN response END) AS "Write The Standard Café Name",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Is all PRP done?? (Condiment tray with Ice cube, Onion slice with ice cube, 700ml and 1100ml food boxes with frill, lemon juice without seed)%' THEN response END) AS "Is all PRP done?? (Condiment tray with Ice cube, Onion slice with ice cube, 700ml and 1100ml food boxes with frill, lemon juice without seed)",
MAX(CASE WHEN question ILIKE '%CCP 2 -Under counter chiller 1 ( 1-5°C)%' THEN response END) AS "CCP 2 -Under counter chiller 1 ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%Packaging PRP is done before opening as per ROS%' THEN response END) AS "Packaging PRP is done before opening as per ROS",
MAX(CASE WHEN question ILIKE '%All equipments are turned on and connected to power source%' THEN response END) AS "All equipments are turned on and connected to power source",
MAX(CASE WHEN question ILIKE '%Cafe outside & Inside area is neat and clean%' THEN response END) AS "Cafe outside & Inside area is neat and clean",
MAX(CASE WHEN question ILIKE '%CCP 2-Under counter chiller 2 ( 1-5°C)%' THEN response END) AS "CCP 2-Under counter chiller 2 ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%WIFI is on and working%' THEN response END) AS "WIFI is on and working",
MAX(CASE WHEN question ILIKE '%Mery Chef/Turbo Chef is clean and ready for operations%' THEN response END) AS "Mery Chef/Turbo Chef is clean and ready for operations",
MAX(CASE WHEN question ILIKE '%Freezer or chiller outside the café are connected and clean%' THEN response END) AS "Freezer or chiller outside the café are connected and clean",
MAX(CASE WHEN question ILIKE '%CCP 2-Visicooler ( 1-5°C)%' THEN response END) AS "CCP 2-Visicooler ( 1-5°C)",
MAX(CASE WHEN question ILIKE '%KDS switch on, printer loaded and connected with KDS%' THEN response END) AS "KDS switch on, printer loaded and connected with KDS",
MAX(CASE WHEN question ILIKE '%Microwaves are cleaned and ready for operations%' THEN response END) AS "Microwaves are cleaned and ready for operations",
MAX(CASE WHEN question ILIKE '%Cafe door/curtains are clean and well maintained%' THEN response END) AS "Cafe door/curtains are clean and well maintained",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 1 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 1 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%HHD device switched on and ready to use for operation%' THEN response END) AS "HHD device switched on and ready to use for operation",
MAX(CASE WHEN question ILIKE '%Tea machine are cleaned and ready for operations  Chayos funnel cleaning%' THEN response END) AS "Tea machine are cleaned and ready for operations  Chayos funnel cleaning",
MAX(CASE WHEN question ILIKE '%Café bins are clean and properly tagged%' THEN response END) AS "Café bins are clean and properly tagged",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 2 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 2 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%TV is connected to internet and order screen is live%' THEN response END) AS "TV is connected to internet and order screen is live",
MAX(CASE WHEN question ILIKE '%Tea Machine is loaded/connected with water and milk%' THEN response END) AS "Tea Machine is loaded/connected with water and milk",
MAX(CASE WHEN question ILIKE '%Café is well lit and all the tubelights working.%' THEN response END) AS "Café is well lit and all the tubelights working.",
MAX(CASE WHEN question ILIKE '%CCP 2-Deep freezer 3 (-18-23°C)%' THEN response END) AS "CCP 2-Deep freezer 3 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%Packer id is logged in HHD and ready for operation (all 3)%' THEN response END) AS "Packer id is logged in HHD and ready for operation (all 3)",
MAX(CASE WHEN question ILIKE '%All required ingredients for tea is stocked appropriately%' THEN response END) AS "All required ingredients for tea is stocked appropriately",
MAX(CASE WHEN question ILIKE '%All packaging items are stored in right places%' THEN response END) AS "All packaging items are stored in right places",
MAX(CASE WHEN question ILIKE '%CCP 2-Verticle freezer 1 (-18-23°C)%' THEN response END) AS "CCP 2-Verticle freezer 1 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%AC is clean and working%' THEN response END) AS "AC is clean and working",
MAX(CASE WHEN question ILIKE '%Coffee machine are cleaned and ready for operations%' THEN response END) AS "Coffee machine are cleaned and ready for operations",
MAX(CASE WHEN question ILIKE '%All products are stored in right storage: freezer or chiller%' THEN response END) AS "All products are stored in right storage: freezer or chiller",
MAX(CASE WHEN question ILIKE '%CCP 2-Verticle freezer 2 (-18-23°C)%' THEN response END) AS "CCP 2-Verticle freezer 2 (-18-23°C)",
MAX(CASE WHEN question ILIKE '%All Barcodes are printed and able to scan.%' THEN response END) AS "All Barcodes are printed and able to scan.",
MAX(CASE WHEN question ILIKE '%Coffee bean blender is refilled%' THEN response END) AS "Coffee bean blender is refilled",
MAX(CASE WHEN question ILIKE '%Products are kept for thawing as per the ROS of the same%' THEN response END) AS "Products are kept for thawing as per the ROS of the same",
MAX(CASE WHEN question ILIKE '%CCP 3-Merry Chef (260°C)=(COOKING TEMP)%' THEN response END) AS "CCP 3-Merry Chef (260°C)=(COOKING TEMP)",
MAX(CASE WHEN question ILIKE '%Dustbin are cleared and new garbage bag inserted%' THEN response END) AS "Dustbin are cleared and new garbage bag inserted",
MAX(CASE WHEN question ILIKE '%All coffee machine accessories are available and ready for operations%' THEN response END) AS "All coffee machine accessories are available and ready for operations",
MAX(CASE WHEN question ILIKE '%All fixtures are well maintained (racks, tables, fans, ac)%' THEN response END) AS "All fixtures are well maintained (racks, tables, fans, ac)",
MAX(CASE WHEN question ILIKE '%CCP 3- Turbo chef (260°C)=(COOKING TEMP)%' THEN response END) AS "CCP 3- Turbo chef (260°C)=(COOKING TEMP)",
MAX(CASE WHEN question ILIKE '%Water cans are setup and extra can are kept (atleast 2)%' THEN response END) AS "Water cans are setup and extra can are kept (atleast 2)",
MAX(CASE WHEN question ILIKE '%Chaipoint  =(COOKING TEMP)%' THEN response END) AS "Chaipoint  =(COOKING TEMP)",
MAX(CASE WHEN question ILIKE '%Packing table and working table are cleaned and disinfected%' THEN response END) AS "Packing table and working table are cleaned and disinfected",
MAX(CASE WHEN question ILIKE '%Coffee Machine Astoria (Water Pressure while dispensing :- 8-10 Bar, Steam:- 1 Bar)=(COOKING TEMP)%' THEN response END) AS "Coffee Machine Astoria (Water Pressure while dispensing :- 8-10 Bar, Steam:- 1 Bar)=(COOKING TEMP)",
MAX(CASE WHEN question ILIKE '%CCTV camera is connected and working%' THEN response END) AS "CCTV camera is connected and working",
MAX(CASE WHEN question ILIKE '%Fruit & vegetable should be sanitize with 50 PPM chlorine solution%' THEN response END) AS "Fruit & vegetable should be sanitize with 50 PPM chlorine solution",
MAX(CASE WHEN question ILIKE '%Wash Basin is connected to water source and drainge is cleaned%' THEN response END) AS "Wash Basin is connected to water source and drainge is cleaned",
MAX(CASE WHEN question ILIKE '%Check MRD on all products in Under counter chiller%' THEN response END) AS "Check MRD on all products in Under counter chiller",
MAX(CASE WHEN question ILIKE '%Ice Machine is connected and ready for operations%' THEN response END) AS "Ice Machine is connected and ready for operations",
MAX(CASE WHEN question ILIKE '%Check MRD on all products in visicooler chiller%' THEN response END) AS "Check MRD on all products in visicooler chiller",
MAX(CASE WHEN question ILIKE '%Roaster, Function chart, Cafe tracker is displayed and updated%' THEN response END) AS "Roaster, Function chart, Cafe tracker is displayed and updated",
MAX(CASE WHEN question ILIKE '%Check MRD on all products outside chiller (All syrup,Lemon, Coriander, pomegranate ,Mint, Ginger,Mint etc.j%' THEN response END) AS "Check MRD on all products outside chiller (All syrup,Lemon, Coriander, pomegranate ,Mint, Ginger,Mint etc.j",
MAX(CASE WHEN question ILIKE '%AII company approved chemicals available in store%' THEN response END) AS "AII company approved chemicals available in store",
MAX(CASE WHEN question ILIKE '%AII equipment separate and available for veg and non-veg fillings%' THEN response END) AS "AII equipment separate and available for veg and non-veg fillings",
MAX(CASE WHEN question ILIKE '%2 sink ready with MRD%' THEN response END) AS "2 sink ready with MRD",
MAX(CASE WHEN question ILIKE '%Spray Gun ready with MRD%' THEN response END) AS "Spray Gun ready with MRD",
MAX(CASE WHEN question ILIKE '%AII products within shelf life%' THEN response END) AS "AII products within shelf life",
MAX(CASE WHEN question ILIKE '%Product shelflife chart updated%' THEN response END) AS "Product shelflife chart updated",
MAX(CASE WHEN question ILIKE '%shoud be checked and recorded (Lux should be 540 in food preparation area and 150 in non food Prep area Like (dry stock,3 sink, counter,etc)%' THEN response END) AS "shoud be checked and recorded (Lux should be 540 in food preparation area and 150 in non food Prep area Like (dry stock,3 sink, counter,etc)",
MAX(CASE WHEN question ILIKE '%Room temperature of the cafe should be recorded.%' THEN response END) AS "Room temperature of the cafe should be recorded.",
MAX(CASE WHEN question ILIKE '%Frozen product maintained as per REGBY process%' THEN response END) AS "Frozen product maintained as per REGBY process"
FROM raw
group by 1,2,3
```

---

## Process Excellence Audit - Croma_Croma Audit Reports.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, form_submissions, user_details

**Original Query:**

```sql
-- Data Source: Process Excellence Audit - Croma
-- Dashboard: Croma Audit Reports
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:56:06
-- ============================================================

WITH cms AS
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
AND audit_submitted_at >= date_trunc('month', CURRENT_DATE)
     AND audit_main_theme NOT ILIKE '%tribe%'
     AND audit_main_theme ILIKE ANY (ARRAY[ '%Process Excellence%']))
SELECT DISTINCT ON (cms."Audit Report No")cms."Audit",
cms.store_id,
       "Started_at",
       cms."Audited At",
       cms."Auditor",
       max(cms.division) AS division,
       cms."Audit Report No",
       ROUND((sum(cms."Actual Score") / NULLIF(sum(cms."Max Score"), 0)) * 100, 2) AS "Total Score%", -- Total Score%
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Safety' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Safety' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Safety %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Inventory' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Inventory' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Inventory %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Registers & Checklist' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Registers & Checklist' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Registers & Checklist %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Maintenance' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Maintenance' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Maintenance %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Zip Services' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Zip Services' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Zip Services %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Marketing and Visual Merchandising' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Marketing and Visual Merchandising' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Marketing and Visual Merchandising %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Hygiene' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Hygiene' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Hygiene %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'People' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'People' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "People %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Ticketing' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Ticketing' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Ticketing %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'Customer Service' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'Customer Service' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "Customer Service %",
 ROUND((SUM(CASE
                WHEN cms."Theme" = 'General' THEN cms."Actual Score"
                ELSE 0
            END) / NULLIF(SUM(CASE
                                  WHEN cms."Theme" = 'General' THEN cms."Max Score"
                                  ELSE 0
                              END), 0)) * 100, 2) AS "General %",
 COALESCE(ROUND((sum(cms."Closed Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Task Completion %",
 COALESCE(ROUND((sum(cms."Open Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Overdue Task %",
 cms.approx_distance_in_km
FROM cms
WHERE cms."Audit" IS NOT NULL
GROUP BY cms."Audit",
         "Started_at",
         cms.store_id,
         cms."Audited At",
         cms."Auditor",
         cms."Audit Report No",
         cms.approx_distance_in_km
ORDER BY cms."Audit Report No",cms."Audited At"
```

---

## RES PM Master Sheet-copy_1719812176_RES PM Master Sheet 2.sql

**Tables referenced:** accountability, acknowledged_at, assigned_at, completed_at, first_attended_at, form_responses, form_submissions, internal_status, issue_questions, issues, metadata, nuggets, question_definitions, requested_at, stage_timeline, user_details

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: RES PM Master Sheet-copy_1719812176
-- Dashboard: RES PM Master Sheet 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:05
-- ============================================================

WITH metadata AS
  (SELECT DISTINCT ON (fs.response_id) fs.id AS form_submit_id,
                      fs.sno,
                      CASE
                          WHEN n.title ILIKE '[Scheduled%' THEN 'Non-urgent'
                          WHEN n.title ILIKE '[Urgent%' THEN 'Urgent'
                          ELSE NULL
                      END AS severity,
                      ud.division AS ops,
                      fr.response-> 'selected' ->> 0 AS outlet
   FROM form_responses fr
   JOIN form_submissions fs ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fs.form_id = qd.nugget_id
   AND fr.question_id = qd.question_id
   JOIN nuggets n ON fs.form_id = n.id
   JOIN user_details ud ON fs.user_id = ud.uuid
   WHERE qd.section_id = 'section-1'
     AND qd.question = 'Store Outlet'
     AND fs.form_id IN ('-NGnz5oKr5VEyobRe8_X',
                        '-NTxAVlQKVSXEIR-M7Ot',
                        '-NGnz5YO4NSAtoB0YurL',
                        '-NTxBRS12o8lY8Bpw3yr',
                        '-Na5Q19nO2iUU8VFuGU4',
                        '-Na5Ozbu8OfdWqt8iOT6',
                        '-NiDKJ7Dnnij6KDUBEJx',
                        '-NiDKIiVOGQy5Sdnthbh',
					   '-NyZxOkPmnh0R9QP4S9A',
					   '-NyZxO41GJg3yM46f-ue')
     AND fs.submit_date AT TIME ZONE 'cct' > '2022-11-01'
   ORDER BY fs.response_id,
            fs.id DESC),
     issue_questions AS
  (SELECT nugget_id,
          question_id,
          question_details.key AS sub_question_id
   FROM
     (SELECT qd.nugget_id,
             qd.question_id,
             fields.value AS questions
      FROM question_definitions qd,
           jsonb_each(qd.definition::jsonb) fields
      WHERE qd.nugget_id IN ('-NGnz5oKr5VEyobRe8_X',
                        '-NTxAVlQKVSXEIR-M7Ot',
                        '-NGnz5YO4NSAtoB0YurL',
                        '-NTxBRS12o8lY8Bpw3yr',
                        '-Na5Q19nO2iUU8VFuGU4',
                        '-Na5Ozbu8OfdWqt8iOT6',
                        '-NiDKJ7Dnnij6KDUBEJx',
                        '-NiDKIiVOGQy5Sdnthbh',
					   '-NyZxOkPmnh0R9QP4S9A',
					   '-NyZxO41GJg3yM46f-ue')
        AND qd.section_id = 'section-1'
        AND qd.question_type = 'table'
        AND fields.key = 'questions')base,
        jsonb_each(base.questions) question_details
   WHERE question_details.value->>'question' = 'What is/are the issue(s)?'),
     issues AS
  (SELECT form_submit_id,
          string_agg(issue, chr(10)) AS issue
   FROM
     (SELECT form_submit_id,
             jsonb_array_elements(fr.response)->>iq.sub_question_id AS issue
      FROM issue_questions iq
      JOIN form_responses fr ON fr.question_id = iq.question_id
      JOIN form_submissions fs ON fr.form_submit_id = fs.id
      AND fs.submit_date AT TIME ZONE 'cct' > '2022-11-01')base
   GROUP BY 1),
     stage_timeline AS
  (SELECT fs.id AS form_submit_id,
          fr.question_id,
          qd.sqno,
          qd.question,
          fr.response -> 'sender' ->> 'userName' AS sender,
                                      (fr.response ->> 'sentAt')::bigint AS sent_at
   FROM form_responses fr
   JOIN form_submissions fs ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fs.form_id = qd.nugget_id
   AND fr.question_id = qd.question_id
   JOIN nuggets n ON fs.form_id = n.id
   JOIN user_details ud ON fs.user_id = ud.uuid
   WHERE qd.question_type = 'section'
     AND fs.form_id IN ('-NGnz5oKr5VEyobRe8_X',
                        '-NTxAVlQKVSXEIR-M7Ot',
                        '-NGnz5YO4NSAtoB0YurL',
                        '-NTxBRS12o8lY8Bpw3yr',
                        '-Na5Q19nO2iUU8VFuGU4',
                        '-Na5Ozbu8OfdWqt8iOT6',
                        '-NiDKJ7Dnnij6KDUBEJx',
                        '-NiDKIiVOGQy5Sdnthbh',
					   '-NyZxOkPmnh0R9QP4S9A',
					   '-NyZxO41GJg3yM46f-ue')
     AND fs.submit_date AT TIME ZONE 'cct' > '2022-11-01'
     AND fr.response ->> 'status' IN ('sent',
                                      'Sent',
                                      'submitted',
                                      'Submitted')),
     accountability AS
  (SELECT form_submit_id,
          sender
   FROM stage_timeline
   WHERE sqno = '3'),
     requested_at AS
  (SELECT form_submit_id,
          sent_at
   FROM stage_timeline
   WHERE sqno = '1'),
     assigned_at AS
  (SELECT form_submit_id,
          sent_at
   FROM stage_timeline
   WHERE sqno = '2'),
     first_attended_at AS
  (SELECT form_submit_id,
          sent_at
   FROM stage_timeline
   WHERE sqno = '3'),
     completed_at AS
  (SELECT form_submit_id,
          sent_at
   FROM stage_timeline
   WHERE sqno = '5'),
     acknowledged_at AS
  (SELECT form_submit_id,
          sent_at
   FROM stage_timeline
   WHERE sqno = '6'),
     internal_status AS
  (SELECT fs.id AS form_submit_id,
          fr.response -> 'selected' ->> 0 AS internal_status
   FROM form_responses fr
   JOIN form_submissions fs ON fs.id = fr.form_submit_id
   JOIN question_definitions qd ON fs.form_id = qd.nugget_id
   AND fr.question_id = qd.question_id
   JOIN nuggets n ON fs.form_id = n.id
   JOIN user_details ud ON fs.user_id = ud.uuid
   WHERE fs.form_id IN ('-NGnz5oKr5VEyobRe8_X',
                        '-NTxAVlQKVSXEIR-M7Ot',
                        '-NGnz5YO4NSAtoB0YurL',
                        '-NTxBRS12o8lY8Bpw3yr',
                        '-Na5Q19nO2iUU8VFuGU4',
                        '-Na5Ozbu8OfdWqt8iOT6',
                        '-NiDKJ7Dnnij6KDUBEJx',
                        '-NiDKIiVOGQy5Sdnthbh',
					   '-NyZxOkPmnh0R9QP4S9A',
					   '-NyZxO41GJg3yM46f-ue')
     AND fs.submit_date AT TIME ZONE 'cct' > '2022-11-01'
     AND qd.question = 'Status of Job')
SELECT metadata.sno AS "PM ID",
       metadata.severity AS "Severity",
       metadata.ops AS "OPS",
       metadata.outlet AS "Outlet",
       issues.issue AS "Issue",
       CASE
           WHEN max(stage_timeline.sqno) = '6' THEN 'Closed'
           WHEN max(stage_timeline.sqno) = '5' THEN 'Waiting for Outlet Acknowledgement'
           WHEN max(stage_timeline.sqno) IN ('4',
                                             '3') THEN 'Follow-up Needed'
           WHEN max(stage_timeline.sqno) = '2' THEN 'Job Assigned'
           WHEN max(stage_timeline.sqno) = '1' THEN 'Request Received'
           ELSE 'Cancelled'
       END AS "Current Status",
       accountability.sender AS "Accountability",
       internal_status.internal_status AS "Internal PM Status",
       to_timestamp(requested_at.sent_at/1000) AT TIME ZONE 'cct' AS "Requested At",
                                                            to_timestamp(assigned_at.sent_at/1000) AT TIME ZONE 'cct' AS "Assigned At",
                                                                                                                to_timestamp(first_attended_at.sent_at/1000) AT TIME ZONE 'cct' AS "First Attended At",
                                                                                                                                                                          to_timestamp(completed_at.sent_at/1000) AT TIME ZONE 'cct' AS "PM Completed At",
                                                                                                                                                                                                                               to_timestamp(acknowledged_at.sent_at/1000) AT TIME ZONE 'cct' AS "Outlet Acknowledged At"
FROM metadata
LEFT OUTER JOIN issues ON metadata.form_submit_id = issues.form_submit_id
LEFT OUTER JOIN stage_timeline ON metadata.form_submit_id = stage_timeline.form_submit_id
LEFT OUTER JOIN accountability ON metadata.form_submit_id = accountability.form_submit_id
LEFT OUTER JOIN internal_status ON metadata.form_submit_id = internal_status.form_submit_id
LEFT OUTER JOIN requested_at ON metadata.form_submit_id = requested_at.form_submit_id
LEFT OUTER JOIN assigned_at ON metadata.form_submit_id = assigned_at.form_submit_id
LEFT OUTER JOIN first_attended_at ON metadata.form_submit_id = first_attended_at.form_submit_id
LEFT OUTER JOIN completed_at ON metadata.form_submit_id = completed_at.form_submit_id
LEFT OUTER JOIN acknowledged_at ON metadata.form_submit_id = acknowledged_at.form_submit_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         7,
         8,
         9,
         10,
         11,
         12,
         13
ORDER BY 9,
         8
```

---

## SOP Audit - Croma_Croma Audit Reports.sql

**Tables referenced:** ThemeLevel, ThemePivot, checkpoint_master_sheet_table, cms, form_submissions, user_details

**Original Query:**

```sql
-- Data Source: SOP Audit - Croma
-- Dashboard: Croma Audit Reports
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:16
-- ============================================================

WITH cms AS
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
AND audit_submitted_at >= date_trunc('month', CURRENT_DATE)
     AND audit_main_theme NOT ILIKE '%tribe%'
     AND audit_main_theme ILIKE ANY (ARRAY[ '%SOP Audit%'])),
     ThemeLevel AS (
  SELECT
    cms."Audit",
    cms.store_id,
    cms."Started_at",
    cms."Audited At",
    cms."Auditor",
    cms."Audit Report No",
    MAX(cms.division) AS division,
    cms."Theme",
    SUM(cms."Actual Score") AS actual_score,
    SUM(cms."Max Score") AS max_score
  FROM cms
  WHERE cms."Audit" IS NOT NULL
    AND cms."Started_at" IS NOT NULL
  GROUP BY cms."Audit", cms.store_id, cms."Started_at", cms."Audited At", cms."Auditor", cms."Audit Report No", cms."Theme"
),


ThemePivot AS (
  SELECT
    "Audit",
    store_id,
    "Started_at",
    "Audited At",
    "Auditor",
    "Audit Report No",
    division,

    SUM(actual_score) * 100.0 / NULLIF(SUM(max_score), 0) AS "Total Score%",

    -- Finance Themes
    SUM(CASE WHEN "Theme" = 'Finance - Cashiers' THEN actual_score ELSE 0 END) AS finance_cashiers_actual,
    SUM(CASE WHEN "Theme" = 'Finance - Cashiers' THEN max_score ELSE 0 END) AS finance_cashiers_max,
    SUM(CASE WHEN "Theme" = 'Finance - Reconciliation' THEN actual_score ELSE 0 END) AS finance_recon_actual,
    SUM(CASE WHEN "Theme" = 'Finance - Reconciliation' THEN max_score ELSE 0 END) AS finance_recon_max,
    SUM(CASE WHEN "Theme" = 'Finance - General Records' THEN actual_score ELSE 0 END) AS finance_records_actual,
    SUM(CASE WHEN "Theme" = 'Finance - General Records' THEN max_score ELSE 0 END) AS finance_records_max,

    -- Inventory Themes
    SUM(CASE WHEN "Theme" = 'Inventory - Delivery' THEN actual_score ELSE 0 END) AS inv_delivery_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - Delivery' THEN max_score ELSE 0 END) AS inv_delivery_max,
    SUM(CASE WHEN "Theme" = 'Inventory - RPA Related' THEN actual_score ELSE 0 END) AS inv_rpa_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - RPA Related' THEN max_score ELSE 0 END) AS inv_rpa_max,
    SUM(CASE WHEN "Theme" = 'Inventory - Hygiene' THEN actual_score ELSE 0 END) AS inv_hygiene_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - Hygiene' THEN max_score ELSE 0 END) AS inv_hygiene_max,
    SUM(CASE WHEN "Theme" = 'Inventory - Store Merchandise receiving' THEN actual_score ELSE 0 END) AS inv_merch_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - Store Merchandise receiving' THEN max_score ELSE 0 END) AS inv_merch_max,
    SUM(CASE WHEN "Theme" = 'Inventory - Trade-in' THEN actual_score ELSE 0 END) AS inv_tradein_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - Trade-in' THEN max_score ELSE 0 END) AS inv_tradein_max,
    SUM(CASE WHEN "Theme" = 'Inventory - Hygiene Requirements' THEN actual_score ELSE 0 END) AS inv_hyg_req_actual,
    SUM(CASE WHEN "Theme" = 'Inventory - Hygiene Requirements' THEN max_score ELSE 0 END) AS inv_hyg_req_max,

    -- Customer Service
    SUM(CASE WHEN "Theme" = 'Customer Service - Service Request Resolution' THEN actual_score ELSE 0 END) AS cs_sr_actual,
    SUM(CASE WHEN "Theme" = 'Customer Service - Service Request Resolution' THEN max_score ELSE 0 END) AS cs_sr_max,
    SUM(CASE WHEN "Theme" = 'Customer Service - Hygiene Standards' THEN actual_score ELSE 0 END) AS cs_hyg_actual,
    SUM(CASE WHEN "Theme" = 'Customer Service - Hygiene Standards' THEN max_score ELSE 0 END) AS cs_hyg_max,
    SUM(CASE WHEN "Theme" = 'Customer Service - GAN Facilitation' THEN actual_score ELSE 0 END) AS cs_gan_actual,
    SUM(CASE WHEN "Theme" = 'Customer Service - GAN Facilitation' THEN max_score ELSE 0 END) AS cs_gan_max,

    -- Key Processes
    SUM(CASE WHEN "Theme" = 'Key Processes - Operations Basics' THEN actual_score ELSE 0 END) AS kp_ops_actual,
    SUM(CASE WHEN "Theme" = 'Key Processes - Operations Basics' THEN max_score ELSE 0 END) AS kp_ops_max,
    SUM(CASE WHEN "Theme" = 'Key Processes - Merchandising' THEN actual_score ELSE 0 END) AS kp_merch_actual,
    SUM(CASE WHEN "Theme" = 'Key Processes - Merchandising' THEN max_score ELSE 0 END) AS kp_merch_max,
    SUM(CASE WHEN "Theme" = 'Key Processes - Audits' THEN actual_score ELSE 0 END) AS kp_audits_actual,
    SUM(CASE WHEN "Theme" = 'Key Processes - Audits' THEN max_score ELSE 0 END) AS kp_audits_max,
    SUM(CASE WHEN "Theme" = 'Key Processes - Store Layout' THEN actual_score ELSE 0 END) AS kp_layout_actual,
    SUM(CASE WHEN "Theme" = 'Key Processes - Store Layout' THEN max_score ELSE 0 END) AS kp_layout_max,

    -- Others
    SUM(CASE WHEN "Theme" = 'Own Brand Service - RPA Management of OB Products' THEN actual_score ELSE 0 END) * 100.0 /
    NULLIF(SUM(CASE WHEN "Theme" = 'Own Brand Service - RPA Management of OB Products' THEN max_score ELSE 0 END), 0) AS "Own Brand Service Score",

    SUM(CASE WHEN "Theme" = 'Formats & Checklists - Loss Prevention' THEN actual_score ELSE 0 END) * 100.0 /
    NULLIF(SUM(CASE WHEN "Theme" = 'Formats & Checklists - Loss Prevention' THEN max_score ELSE 0 END), 0) AS "Formats & Checklists Score"

  FROM ThemeLevel
  GROUP BY "Audit", store_id, "Started_at", "Audited At", "Auditor", "Audit Report No", division
)

SELECT
 DISTINCT ON (tp."Audit Report No", tp.store_id, tp."Audited At", tp."Started_at")tp."Audit",
  tp.store_id,
  tp."Started_at",
  tp."Audited At",
  tp."Auditor",
  tp.division,
  tp."Audit Report No",
  ROUND(tp."Total Score%", 2) AS "Total Score%",
  
  -- Finance Weighted Score
  ROUND((
    COALESCE(tp.finance_cashiers_actual, 0) + COALESCE(tp.finance_recon_actual, 0) + COALESCE(tp.finance_records_actual, 0)
  ) * 100.0 /
  NULLIF(
    COALESCE(tp.finance_cashiers_max, 0) + COALESCE(tp.finance_recon_max, 0) + COALESCE(tp.finance_records_max, 0), 0), 2) AS "Finance Score",

  -- Inventory Weighted Score
  ROUND((
    COALESCE(tp.inv_delivery_actual, 0) + COALESCE(tp.inv_rpa_actual, 0) + COALESCE(tp.inv_hygiene_actual, 0) +
    COALESCE(tp.inv_merch_actual, 0) + COALESCE(tp.inv_tradein_actual, 0) + COALESCE(tp.inv_hyg_req_actual, 0)
  ) * 100.0 /
  NULLIF(
    COALESCE(tp.inv_delivery_max, 0) + COALESCE(tp.inv_rpa_max, 0) + COALESCE(tp.inv_hygiene_max, 0) +
    COALESCE(tp.inv_merch_max, 0) + COALESCE(tp.inv_tradein_max, 0) + COALESCE(tp.inv_hyg_req_max, 0), 0), 2) AS "Inventory Score",

  -- Customer Service Weighted Score
  ROUND((
    COALESCE(tp.cs_sr_actual, 0) + COALESCE(tp.cs_hyg_actual, 0) + COALESCE(tp.cs_gan_actual, 0)
  ) * 100.0 /
  NULLIF(
    COALESCE(tp.cs_sr_max, 0) + COALESCE(tp.cs_hyg_max, 0) + COALESCE(tp.cs_gan_max, 0), 0), 2) AS "Customer Service Score",

  -- Key Processes Weighted Score
  ROUND((
    COALESCE(tp.kp_ops_actual, 0) + COALESCE(tp.kp_merch_actual, 0) + COALESCE(tp.kp_audits_actual, 0) + COALESCE(tp.kp_layout_actual, 0)
  ) * 100.0 /
  NULLIF(
    COALESCE(tp.kp_ops_max, 0) + COALESCE(tp.kp_merch_max, 0) + COALESCE(tp.kp_audits_max, 0) + COALESCE(tp.kp_layout_max, 0), 0), 2) AS "Key Processes Score",
  tp."Own Brand Service Score",
  tp."Formats & Checklists Score",
  COALESCE(ROUND((sum(cms."Closed Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Task Completion %",
 COALESCE(ROUND((sum(cms."Open Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Overdue Task %",
 cms.approx_distance_in_km
  
FROM ThemePivot tp
join cms on tp."Audit Report No" = cms."Audit Report No"
group by 1,2,3,4,5,6,7,8,9,10,11,12,13,14,cms.approx_distance_in_km
ORDER BY tp."Audit Report No", tp.store_id, tp."Audited At", tp."Started_at"
```

---

## Shift Handover Checklist - Zepto_Zepto - Checklists Report 2.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Shift Handover Checklist - Zepto
-- Dashboard: Zepto - Checklists Report 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:43
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Shift Handover Checklist%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,location,
MAX(CASE WHEN question ILIKE '%Any Pending Putaway%' THEN response END) AS "Any Pending Putaway",
MAX(CASE WHEN question ILIKE '%Please mention the ASN number%' THEN response END) AS "Please mention the ASN number",
MAX(CASE WHEN question ILIKE '%Any receiving pending for the day%' THEN response END) AS "Any receiving pending for the day",
MAX(CASE WHEN question ILIKE '%Mention the PO number / LPN Number%' THEN response END) AS "Mention the PO number / LPN Number",
MAX(CASE WHEN question ILIKE '%Any new joiners of the day%' THEN response END) AS "Any new joiners of the day",
MAX(CASE WHEN question ILIKE '%New joiner added in PackMan > Yes , No  >If No > Reason%' THEN response END) AS "New joiner added in PackMan > Yes , No  >If No > Reason",
MAX(CASE WHEN question ILIKE '%Any Machine banner?%' THEN response END) AS "Any Machine banner?",
MAX(CASE WHEN question ILIKE '%Select the machine > Ticket Raised > Yes , No%' THEN response END) AS "Select the machine > Ticket Raised > Yes , No",
MAX(CASE WHEN question ILIKE '%Did PRP done?%' THEN response END) AS "Did PRP done?",
MAX(CASE WHEN question ILIKE '%Reason of PRP not done%' THEN response END) AS "Reason of PRP not done",
MAX(CASE WHEN question ILIKE '%Did Bin to Bin movement pending?%' THEN response END) AS "Did Bin to Bin movement pending?",
MAX(CASE WHEN question ILIKE '%Reason of Bin Moment not done%' THEN response END) AS "Reason of Bin Moment not done",
MAX(CASE WHEN question ILIKE '%Is the movement of SKU''s in Damage, Quality and expiry bins if any%' THEN response END) AS "Is the movement of SKU's in Damage, Quality and expiry bins if any",
MAX(CASE WHEN question ILIKE '%Reason of DEQ not marked%' THEN response END) AS "Reason of DEQ not marked",
MAX(CASE WHEN question ILIKE '%Any Inventory adjustment pending%' THEN response END) AS "Any Inventory adjustment pending",
MAX(CASE WHEN question ILIKE '%Reason of Adjustment pending%' THEN response END) AS "Reason of Adjustment pending",
MAX(CASE WHEN question ILIKE '%Any Stock kept in Grocery freezer%' THEN response END) AS "Any Stock kept in Grocery freezer",
MAX(CASE WHEN question ILIKE '%What all SKU''s are in Grocery Freezer%' THEN response END) AS "What all SKU's are in Grocery Freezer",
MAX(CASE WHEN question ILIKE '%Scrap clearence to be cleared till time%' THEN response END) AS "Scrap clearence to be cleared till time",
MAX(CASE WHEN question ILIKE '%Reason%' THEN response END) AS "Reason",
MAX(CASE 
  WHEN question ILIKE '%Any important communication of the day (Like SKU''s on hold due to QA issue, Veg and Non veg complaint, Gov officer visit)%' 
  THEN response 
END) AS "Any important communication of the day (Like SKU's on hold due to QA issue, Veg and Non veg complaint, Gov officer visit)",
MAX(CASE WHEN question ILIKE '%What is the communication%' THEN response END) AS "What is the communication",
MAX(CASE WHEN question ILIKE '%New product launches for the day%' THEN response END) AS "New product launches for the day",
MAX(CASE WHEN question ILIKE '%What all SKU''s%' THEN response END) AS "What all SKU's",
MAX(CASE WHEN question ILIKE '%Opening / Closing checklist Completed%' THEN response END) AS "Opening / Closing checklist Completed",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 1",
MAX(CASE WHEN question ILIKE '%SKU 1: Did physical quantity and System quantity is matching%' THEN response END) AS "SKU 1: Did physical quantity and System quantity is matching",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 2",
MAX(CASE WHEN question ILIKE '%SKU 2: Did physical quantity and System quantity is matching%' THEN response END) AS "SKU 2: Did physical quantity and System quantity is matching",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 3",
MAX(CASE WHEN question ILIKE '%SKU 3: Did physical quantity and System quantity is matching%' THEN response END) AS "SKU 3: Did physical quantity and System quantity is matching",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 4",
MAX(CASE WHEN question ILIKE '%SKU 4: Did physical quantity and System quantity is matching%' THEN response END) AS "SKU 4: Did physical quantity and System quantity is matching",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 5",
MAX(CASE WHEN question ILIKE '%SKU 5: Did physical quantity and System quantity is matching%' THEN response END) AS "SKU 5: Did physical quantity and System quantity is matching",
MAX(CASE WHEN question ILIKE '%Reasoning%' THEN response END) AS "Reasoning 6",
MAX(CASE WHEN question ILIKE '%Is the Diesel level is more than 30%%' THEN response END) AS "Is the Diesel level is more than 30%",
MAX(CASE WHEN question ILIKE '%Inform DHM for refueling%' THEN response END) AS "Inform DHM for refueling"
FROM raw
group by 1,2,3,4
```

---

## Smart Audit - Croma_Croma Audit Reports.sql

**Tables referenced:** checkpoint_master_sheet_table, cms, form_submissions, user_details

**Original Query:**

```sql
-- Data Source: Smart Audit - Croma
-- Dashboard: Croma Audit Reports
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:56:06
-- ============================================================

WITH cms AS
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
AND audit_submitted_at >= date_trunc('month', CURRENT_DATE)
     AND audit_main_theme NOT ILIKE '%tribe%'
     AND audit_main_theme ILIKE ANY (ARRAY[ '%SMART Audit%']))
SELECT DISTINCT ON (cms."Audit Report No")cms."Audit",
                   cms.store_id,
                   "Started_at",
                   cms."Audited At",
                   cms."Auditor",
                   max(cms.division) AS division,
                   cms."Audit Report No",
                   ROUND((sum(cms."Actual Score") / NULLIF(sum(cms."Max Score"), 0)) * 100, 2) AS "Total Score%",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Customer Service' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Customer Service' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Customer Service %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Digital Transformation' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Digital Transformation' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Digital Transformation %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Finance' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Finance' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Finance %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Inventory Management' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Inventory Management' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Inventory Management %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Key Processes' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Key Processes' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Key Processes %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Learning & Development' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Learning & Development' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Learning & Development %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Marketing' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Marketing' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Marketing %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'People' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'People' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "People %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Safety' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Safety' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Safety %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Value Added Services' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Value Added Services' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Value Added Services %",
                   ROUND((SUM(CASE
                                  WHEN cms."Theme" = 'Zip Services' THEN cms."Actual Score"
                                  ELSE 0
                              END) / NULLIF(SUM(CASE
                                                    WHEN cms."Theme" = 'Zip Services' THEN cms."Max Score"
                                                    ELSE 0
                                                END), 0)) * 100, 2) AS "Zip Services %",
                   COALESCE(ROUND((sum(cms."Closed Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Task Completion %",
                   COALESCE(ROUND((sum(cms."Open Count") / NULLIF(sum(cms."Followup Points Count"), 0)) * 100, 2), 0) AS "Overdue Task %",
                   cms.approx_distance_in_km
FROM cms
WHERE cms."Audit" IS NOT NULL
GROUP BY cms."Audit",
         "Started_at",
         cms.store_id,
         cms."Audited At",
         cms."Auditor",
         cms."Audit Report No",
         cms.approx_distance_in_km
ORDER BY cms."Audit Report No",
         cms."Audited At"
```

---

## Training Audit 2.0 Report_Zepto - Checklists Report.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Training Audit 2.0 Report
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:06
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Training Audit 2.0%')
     AND organization = 'Zds-indus'
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
WHERE submit_date::date >= date_trunc('week', current_date)
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%Audited Location%' THEN response END) AS "Audited Location",
MAX(CASE WHEN question ILIKE '%Audited Cafe%' THEN response END) AS "Audited Cafe",
MAX(CASE WHEN question ILIKE '%Are All Café partner and ICO are certified in LTO%' THEN response END) AS "Are All Café partner and ICO are certified in LTO",
MAX(CASE WHEN question ILIKE '%Write the Reasons%' THEN response END) AS "Write the Reasons 1",
MAX(CASE WHEN question ILIKE '%Are all café leads are LTO Certified%' THEN response END) AS "Are all café leads are LTO Certified",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 2",
MAX(CASE WHEN question ILIKE '%Are the café Lead & ICO aware of new product / process launched in last 30 days%' THEN response END) AS "Are the café Lead & ICO aware of new product / process launched in last 30 days",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 3",
MAX(CASE WHEN question ILIKE '%Are the café Partners aware of new product / process launched in last 30 days%' THEN response END) AS "Are the café Partners aware of new product / process launched in last 30 days",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 4",
MAX(CASE WHEN question ILIKE '%Updated Milkshake summary sheet pasted near beverage counter only ( As per latest versions)%' THEN response END) AS "Updated Milkshake summary sheet pasted near beverage counter only ( As per latest versions)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 5",
MAX(CASE WHEN question ILIKE '%Updated Cooler sheet summary sheet pasted near beverage counter only ( As per latest versions)%' THEN response END) AS "Updated Cooler sheet summary sheet pasted near beverage counter only ( As per latest versions)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 6",
MAX(CASE WHEN question ILIKE '%Updated Coffee summary sheet pasted near beverage counter ( As per latest versions)%' THEN response END) AS "Updated Coffee summary sheet pasted near beverage counter ( As per latest versions)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 7",
MAX(CASE WHEN question ILIKE '%Updated Chai point  sheet pasted near beverage counter ( As per latest versions)%' THEN response END) AS "Updated Chai point  sheet pasted near beverage counter ( As per latest versions)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 8",
MAX(CASE WHEN question ILIKE '%All Product are prepared as per sop (Observe the live order preparation. 5 Product)%' THEN response END) AS "All Product are prepared as per sop (Observe the live order preparation. 5 Product)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 9",
MAX(CASE WHEN question ILIKE '%All Product are Garnished/condiment as per sop%' THEN response END) AS "All Product are Garnished/condiment as per sop",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 10",
MAX(CASE WHEN question ILIKE '%Reassessment for failed employees is conducted or not%' THEN response END) AS "Reassessment for failed employees is conducted or not",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 11",
MAX(CASE WHEN question ILIKE '%Is sop saved in desktop/Hard copy are saved in desktop and Team are aware of this%' THEN response END) AS "Is sop saved in desktop/Hard copy are saved in desktop and Team are aware of this",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 12",
MAX(CASE WHEN question ILIKE '%All equipment are in working condition (If ticket raised will get the mark if not 0)%' THEN response END) AS "All equipment are in working condition (If ticket raised will get the mark if not 0)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 13",
MAX(CASE WHEN question ILIKE '%Is opening and closing checklist is updated as per timeline%' THEN response END) AS "Is opening and closing checklist is updated as per timeline",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 14",
MAX(CASE WHEN question ILIKE '%Is quality checklist is update as per timeline%' THEN response END) AS "Is quality checklist is update as per timeline",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 15",
MAX(CASE WHEN question ILIKE '%is prp is done for packaging material, product , small ware and  thawing (As per PRP Sheet)%' THEN response END) AS "is prp is done for packaging material, product , small ware and  thawing (As per PRP Sheet)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 16",
MAX(CASE WHEN question ILIKE '%All tenured employee within 30 days and above should know all sop (Any 5 Products- Each question will be 1 Mark)%' THEN response END) AS "All tenured employee within 30 days and above should know all sop (Any 5 Products- Each question will be 1 Mark)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 17",
MAX(CASE WHEN question ILIKE '%Are All product are properly stacked in freezer and chiller in FIFO(REGBY) Process%' THEN response END) AS "Are All product are properly stacked in freezer and chiller in FIFO(REGBY) Process",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 18",
MAX(CASE WHEN question ILIKE '%The cafe Preparation area,staging, Storage area is cleaned or not%' THEN response END) AS "The cafe Preparation area,staging, Storage area is cleaned or not",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 19",
MAX(CASE WHEN question ILIKE '%is the KDS Workflow Followed or not (Awareness of Printer calibration & Ticket raising process)%' THEN response END) AS "is the KDS Workflow Followed or not (Awareness of Printer calibration & Ticket raising process)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 20",
MAX(CASE WHEN question ILIKE '%Cafe controllable product are live or not  (OOS due to miss bin moment, inventory in wrong Bin)%' THEN response END) AS "Cafe controllable product are live or not  (OOS due to miss bin moment, inventory in wrong Bin)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 21",
MAX(CASE WHEN question ILIKE '%Updated microwave summary sheet pasted at microwave or not%' THEN response END) AS "Updated microwave summary sheet pasted at microwave or not",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 22",
MAX(CASE WHEN question ILIKE '%Did the cafe team aware about KPT, NPS & d/d% (They should know targets and D-1, MTD numbers)%' THEN response END) AS "Did the cafe team aware about KPT, NPS & d/d% (They should know targets and D-1, MTD numbers)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 23",
MAX(CASE WHEN question ILIKE '%Knowledge check specific to equipment''s (Coffee espresso, Chai machine, Turbo chef)%' THEN response END) AS "Knowledge check specific to equipment's (Coffee espresso, Chai machine, Turbo chef)",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 24",
MAX(CASE WHEN question ILIKE '%All Cafe employees enrolled and loged atleast once in Know App.%' THEN response END) AS "All Cafe employees enrolled and loged atleast once in Know App.",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 25",
MAX(CASE WHEN question ILIKE '%LTO Sheet handed over to New employee%' THEN response END) AS "LTO Sheet handed over to New employee",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 26",
MAX(CASE WHEN question ILIKE '%LTO Sheet Should be maintain in cafe with all detail and cafe pariksha score%' THEN response END) AS "LTO Sheet Should be maintain in cafe with all detail and cafe pariksha score",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 27",
MAX(CASE WHEN question ILIKE '%All Trainee employee should complete 10 days LTO Plan and cafe pariksha%' THEN response END) AS "All Trainee employee should complete 10 days LTO Plan and cafe pariksha",
MAX(CASE WHEN question ILIKE '%Write the Reason%' THEN response END) AS "Write the Reason 28",
MAX(CASE WHEN question ILIKE '%Mention the over all Observations of the Audit%' THEN response END) AS "Mention the over all Observations of the Audit",
MAX(CASE WHEN question ILIKE '%Mention the Trainings conducted.%' THEN response END) AS "Mention the Trainings conducted.",
MAX(CASE WHEN question ILIKE '%Mention Critical Issues if any%' THEN response END) AS "Mention Critical Issues if any",
MAX(CASE WHEN question ILIKE '%Upload the images or documents of any Critical issues observed in the cafe. You Can skip this if no issues found%' THEN response END) AS "Upload the images or documents of any Critical issues observed in the cafe. You Can skip this if no issues found"
FROM RAW
group by 1,2,3
```

---

## Van checklist 2.0 - Zepto_Zepto - Checklists Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Van checklist 2.0 - Zepto
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:44
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%Van Temperature Monitoring Form V.2.0%')
     AND organization = 'Zds-indus'
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
where submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date

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
                                 'upload_image') THEN (fr.response)->0->>'response'
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
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,
MAX(CASE WHEN question ILIKE '%Your Name%' THEN response END) AS "Your Name",
MAX(CASE WHEN question ILIKE '%Your Mobile Number%' THEN response END) AS "Your Mobile Number",
MAX(CASE WHEN question ILIKE '%Select Your City%' THEN response END) AS "Select Your City",
MAX(CASE WHEN question ILIKE '%Select Your  Cafe Name%' THEN response END) AS "Select Your  Cafe Name",
MAX(CASE WHEN question ILIKE '%Van Reached date and time%' THEN response END) AS "Van Reached date and time",
MAX(CASE WHEN question ILIKE '%Vehicle No%' THEN response END) AS "Vehicle No",
MAX(CASE WHEN question ILIKE '%Van Display Temperature (In degree Celsius)%' THEN response END) AS "Van Display Temperature (In degree Celsius)",
MAX(CASE WHEN question ILIKE '%Capture of the image of Van Temperature meter%' THEN response END) AS "Capture of the image of Van Temperature meter",
MAX(CASE WHEN question ILIKE '%Select the product of which temperature has been checked -1%' THEN response END) AS "Select the product of which temperature has been checked -1",
MAX(CASE WHEN question ILIKE '%Enter the Temperature of the Product -1%' THEN response END) AS "Enter the Temperature of the Product -1",
MAX(CASE WHEN question ILIKE '%Capture the image of temperature of the product -1%' THEN response END) AS "Capture the image of temperature of the product -1",
MAX(CASE WHEN question ILIKE '%Select the product of which temperature has been checked -2%' THEN response END) AS "Select the product of which temperature has been checked -2",
MAX(CASE WHEN question ILIKE '%Enter the Temperature of the Product -2%' THEN response END) AS "Enter the Temperature of the Product -2",
MAX(CASE WHEN question ILIKE '%Capture the image of temperature of the product -2%' THEN response END) AS "Capture the image of temperature of the product -2",
MAX(CASE WHEN question ILIKE '%Invoice Number%' THEN response END) AS "Invoice Number",
MAX(CASE WHEN question ILIKE '%Status of Vehicle (Accepted / Rejected)%' THEN response END) AS "Status of Vehicle (Accepted / Rejected)",
MAX(CASE WHEN question ILIKE '%Mention the reason for Rejecting the vehicle /Product%' THEN response END) AS "Mention the reason for Rejecting the vehicle /Product"
FROM raw
group by 1,2,3
```

---

## Vision Foods Routine Compliance_Vision Foods Routine Compliance.sql

**Tables referenced:** form_compliance, nuggets, organizations, td

**Original Query:**

```sql
-- Data Source: Vision Foods Routine Compliance
-- Dashboard: Vision Foods Routine Compliance
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:59:57
-- ============================================================

WITH td as (select id as organization, interval '1 min'*tzoffset as diff from organizations where id = 'Vision-Foodworks-cartwheel')
select distinct on (fc.organization, fc.form_id, fc.job_location, (fc.reminded_at + td.diff)::date) 
fc.organization as "Organization",
(fc.reminded_at + td.diff)::date as "Date",
fc.form_id as "Routine KNID",
n.title as "Routine Name",
fc.job_location as "Location",
(fc.reminded_at + td.diff)  as "Reminded At",
(fc.responded_at + td.diff)  as "Responded At",
case when fc.responded_at is null then 0 else 1 end as "Compliance",
fc.response_id as "Submission KNID"
from form_compliance fc
join td on td.organization = fc.organization
join nuggets n on fc.form_id = n.id
where fc.organization = 'Vision-Foodworks-cartwheel'
and (fc.reminded_at + td.diff)::date between (current_timestamp + td.diff - interval '7 days')::date and (current_timestamp + td.diff - interval '1 day')::date
and fc.job_location not ilike 'KNOW' and fc.job_location not ilike 'HQ'
order by fc.organization, fc.form_id, fc.job_location, (fc.reminded_at + td.diff)::date, fc.responded_at
```

---

## Watsons Weekly Chatbot Report_Watsons Weekly ChatBot Report.sql

**Tables referenced:** AggregatedAnswers, Questions, chat_messages, chats, log, organizations, td, user_details

**Original Query:**

```sql
-- Data Source: Watsons Weekly Chatbot Report
-- Dashboard: Watsons Weekly ChatBot Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:58:47
-- ============================================================

WITH chats AS
  (SELECT *
   FROM chat_messages
   WHERE (to_id ILIKE 'watsons-leo-gpt-bot-retail'
          OR from_id ILIKE 'watsons-leo-gpt-bot-retail'
          OR to_id ILIKE 'watsons-leo-gpt-bot-ops'
          OR from_id ILIKE 'watsons-leo-gpt-bot-ops')
     AND is_deleted = 'false'
     AND chat_type = 'user'
  and to_timestamp(created_at/1000) > current_timestamp - interval '7 days' ),
     td AS
  (SELECT id AS org_id, interval '1 min'*tzoffset AS diff
   FROM organizations),
     log AS
  (SELECT chats.chat_id AS "Chat ID",
          senders.uuid AS from_knid,
          receivers.uuid AS to_knid,
          senders.first_name||' '||senders.last_name||' '||senders.identifier||' '||senders.designation||'-'||senders.department||'-'||senders.job_location AS "From",
          receivers.first_name||' '||receivers.last_name||' '||receivers.identifier||' '||receivers.designation||'-'||receivers.department||'-'||receivers.job_location AS "To",
          chats.message AS "Message",
          to_timestamp(chats.created_at/1000) + td.diff AS "Sent At"
   FROM chats
   JOIN user_details senders ON chats.from_id = senders.uuid
   JOIN user_details receivers ON chats.to_id = receivers.uuid
   JOIN td ON senders.organization = td.org_id
   ORDER BY 1,
            7),
     Questions AS
  (SELECT log."From" AS Asking_User,
          log.from_knid AS asking_user_knid,
          case when log.to_knid = 'watsons-leo-gpt-bot-retail' then 'HR Bot'
          when log.to_knid = 'watsons-leo-gpt-bot-ops' then 'Store Ops Bot'
          else null end as bot,
          log."Sent At" AS Question_Asked_At,
          log."Message" AS Question,
          LEAD(log."Sent At") OVER (PARTITION BY log.from_knid
                                    ORDER BY log."Sent At") AS Next_Question_Time
   FROM log
   WHERE (log.to_knid = 'watsons-leo-gpt-bot-retail'
          OR to_knid = 'watsons-leo-gpt-bot-ops')),
     AggregatedAnswers AS
  (SELECT q.Asking_User,
          q.Question_Asked_At,
          STRING_AGG(c."Message", chr(10)||chr(10)||'-') AS Aggregated_Answer
   FROM Questions q
   LEFT JOIN log c ON c."Sent At" > q.Question_Asked_At
   AND (c."Sent At" < q.Next_Question_Time
        OR q.Next_Question_Time IS NULL)
   AND c.from_knid in ('watsons-leo-gpt-bot-retail', 'watsons-leo-gpt-bot-ops')
   AND c.to_knid = q.asking_user_knid
   GROUP BY q.Asking_User,
            q.Question_Asked_At)
SELECT q.Asking_User AS "Staff",
       q.Question_Asked_At AS "Sent At",
       q.Question AS"Question",
       a.Aggregated_Answer AS "Bot Response",
       q.bot as "Bot"
FROM Questions q
LEFT JOIN AggregatedAnswers a ON q.Question_Asked_At = a.Question_Asked_At
AND q.Asking_User = a.Asking_User
where q.Asking_user not ilike 'KNOW Support%'
ORDER BY 2 desc, 1
```

---

## Watsons Weekly Compliment Report_Watsons Weekly Compliments Reports.sql

**Tables referenced:** form_responses, form_submissions, user_details

**Columns needing snake_case conversion:**

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Watsons Weekly Compliment Report
-- Dashboard: Watsons Weekly Compliments Reports
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:52:58
-- ============================================================

SELECT base.date AS "Compliment Date",
       giver_details.first_name||giver_details.last_name AS "Compliment Giver Name",
       ''''||giver_details.identifier AS "Compliment Giver Employee ID",
       giver_details.designation as "Compliment Giver Designation",
       giver_details.job_location AS "Compliment Giver Outlet",
       base.compliment_type AS "Compliment Type",
       base.compliment AS "Compliment",
       recipient_details.first_name||recipient_details.last_name AS "Compliment Recipient Name",
       ''''||recipient_details.identifier AS "Compliment Recipient Employee ID",
       recipient_details.designation as "Compliment Recipient Designation",
       recipient_details.job_location AS "Compliment Recipient Outlet",
       base.compliment_id AS "Compliment Submit ID (KNOW Internal)",
	   giver_details.organization as "Organization"
FROM
  (SELECT (submit_date AT TIME ZONE 'Asia/Singapore')::date AS date,
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
   WHERE submit_date AT TIME ZONE 'Asia/Singapore' BETWEEN current_timestamp::date - interval '7 days' AND current_timestamp::date
     AND form_submissions.form_id = '-compliment-form'
     AND organization = 'watsons-leo'
     
   GROUP BY 1,
            form_submit_id,
            6) base
JOIN user_details giver_details ON base.giver = giver_details.uuid
JOIN user_details recipient_details ON base.recipient = recipient_details.uuid
where base.compliment_type ilike '%Internal%'
ORDER BY 1,
         2,
         8,
         6
```

---

## Watsons Weekly Leaderboard Report_Watsons Weekly Leaderboard Reports.sql

**Tables referenced:** gamification, to_timestamp, user_details

**Original Query:**

```sql
-- Data Source: Watsons Weekly Leaderboard Report
-- Dashboard: Watsons Weekly Leaderboard Reports
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:38
-- ============================================================

SELECT user_details.first_name||' '||last_name AS "Employee Name",
       ''''||user_details.identifier AS "Employee ID",
       user_details.designation AS "Designation",
       user_details.department AS "Department",
       user_details.job_location AS "Work Location",
       extract('Year' FROM to_timestamp(TRUNC(CAST(gamification.created_at AS bigint) / 1000)) AT TIME ZONE 'Asia/Singapore')||' Q'||
	   extract('Quarter' FROM to_timestamp(TRUNC(CAST(gamification.created_at AS bigint) / 1000)) AT TIME ZONE 'Asia/Singapore') AS "Quarter",
       sum(gamification.points) AS "Total Points",
	   user_details.organization as "Organization"
FROM gamification
JOIN user_details ON gamification.user_id = user_details.uuid
WHERE gamification.organization = 'watsons-leo'
  AND gamification.type = 'compliments'
  AND to_timestamp(TRUNC(CAST(gamification.created_at AS bigint) / 1000)) AT TIME ZONE 'Asia/Singapore' 
           BETWEEN CURRENT_TIMESTAMP::date - interval '7 days' AND CURRENT_TIMESTAMP::date
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
		 8
ORDER BY 6,
         7 DESC,
         1
```

---

## ZCER 4.0 Checklist_Zepto - Checklists Report.sql

**Tables referenced:** qms.Zepto_QMS_Checkpoint_Master_Sheet

**Original Query:**

```sql
-- Data Source: ZCER 4.0 Checklist
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:10
-- ============================================================

select store_id,city_id,audit_type,audit_main_theme,theme,audit_date,audit_submission_number,auditor_name,checkpoint,result,auditor_observations
from qms.Zepto_QMS_Checkpoint_Master_Sheet 
where audit_main_theme = 'ZCER 4.0 Checklist' 
and audit_date >= date_trunc('week', CURRENT_DATE)
```

---

## ZCER 7.0_Zcer 7.0.sql

**Tables referenced:** form_responses, form_submissions, public.Zepto_QMS_Checkpoint_Master_Sheet_table, question_definitions

**Original Query:**

```sql
-- Data Source: ZCER 7.0
-- Dashboard: Zcer 7.0
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:19
-- ============================================================

SELECT 
  store_id,
  MAX(CASE WHEN question ILIKE '%Write standard Café Name%' THEN response::text END) AS "Write The Standard Café Name",
  city_id,
  audit_main_theme,
  theme,
  audit_date,
  audit_submission_number,
  auditor_name,
  checkpoint,
  result,
  auditor_observations
FROM public.Zepto_QMS_Checkpoint_Master_Sheet_table cms
JOIN form_submissions fs 
  ON cms.audit_submission_knid = fs.response_id
JOIN form_responses fr 
  ON fs.id = fr.form_submit_id
Join  question_definitions qd on fr.question_id = qd.question_id
WHERE audit_main_theme ilike ('%ZCER 7.0%')
  AND audit_date  >= date_trunc('week', CURRENT_DATE)
GROUP BY 
  store_id,
  city_id,
  audit_main_theme,
  theme,
  audit_date,
  audit_submission_number,
  auditor_name,
  checkpoint,
  result,
  auditor_observations
```

---

## ZC_MH Inbound Cold	- Zepto_Zepto - Checklists Report 2.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: ZC_MH Inbound Cold	- Zepto
-- Dashboard: Zepto - Checklists Report 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:38
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%ZC_MH Inbound Cold%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,location,
MAX(CASE WHEN question ILIKE '%Your Name%' THEN response END) AS "Your Name",
MAX(CASE WHEN question ILIKE '%Your Mobile Number%' THEN response END) AS "Your Mobile Number",
MAX(CASE WHEN question ILIKE '%Select MH Name%' THEN response END) AS "Select MH Name",
MAX(CASE WHEN question ILIKE '%Vendor Name (Supplier)%' THEN response END) AS "Vendor Name (Supplier)",
MAX(CASE WHEN question ILIKE '%Invoice Number%' THEN response END) AS "Invoice Number",
MAX(CASE WHEN question ILIKE '%Vehicle Number%' THEN response END) AS "Vehicle Number",
MAX(CASE WHEN question ILIKE '%Van Display Temperature (°C) before unloading%' THEN response END) AS "Van Display Temperature (°C) before unloading",
MAX(CASE WHEN question ILIKE '%Capture the Image of Van Dispaly%' THEN response END) AS "Capture the Image of Van Dispaly",
MAX(CASE WHEN question ILIKE '%Product Van Type%' THEN response END) AS "Product Van Type",
MAX(CASE WHEN question ILIKE '%Product Name 1%' THEN response END) AS "Product Name 1",
MAX(CASE WHEN question ILIKE '%Product Temperature 1 (°C)%' THEN response END) AS "Product Temperature 1 (°C)",
MAX(CASE WHEN question ILIKE '%Capture the Image of Product Temperature 1%' THEN response END) AS "Capture the Image of Product Temperature 1",
MAX(CASE WHEN question ILIKE '%Product Name 2%' THEN response END) AS "Product Name 2",
MAX(CASE WHEN question ILIKE '%Product Temperature 2 (°C)%' THEN response END) AS "Product Temperature 2 (°C)",
MAX(CASE WHEN question ILIKE '%Product Name 3%' THEN response END) AS "Product Name 3",
MAX(CASE WHEN question ILIKE '%Product Temperature 3 (°C)%' THEN response END) AS "Product Temperature 3 (°C)",
MAX(CASE WHEN question ILIKE '%Product Name 4%' THEN response END) AS "Product Name 4",
MAX(CASE WHEN question ILIKE '%Product Temperature 4 (°C)%' THEN response END) AS "Product Temperature 4 (°C)",
MAX(CASE WHEN question ILIKE '%Capture the Image of Product Temperature 2%' THEN response END) AS "Capture the Image of Product Temperature 2",
MAX(CASE WHEN question ILIKE '%Product Accepted or Rejected%' THEN response END) AS "Product Accepted or Rejected",
MAX(CASE WHEN question ILIKE '%If Rejected, Mention Reason%' THEN response END) AS "If Rejected, Mention Reason"
FROM raw
group by 1,2,3,4
```

---

## ZC_MH Outbound Cold - Zepto_Zepto - Checklists Report 2.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: ZC_MH Outbound Cold - Zepto
-- Dashboard: Zepto - Checklists Report 2
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:40
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('%ZC_MH Outbound Cold%')
     AND organization = 'Zds-indus'
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
       WHERE submit_date::date BETWEEN date_trunc('month', current_date)::date AND current_date::date
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          ud.first_name as form_filled_by
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   join user_details ud on fr.user_id = ud.uuid
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
SELECT sno, submit_date,form_filled_by,location,
MAX(CASE WHEN question ILIKE '%Your Name%' THEN response END) AS "Your Name",
MAX(CASE WHEN question ILIKE '%Your Mobile Number%' THEN response END) AS "Your Mobile Number",
MAX(CASE WHEN question ILIKE '%Van Route (Standard Cafe name)%' THEN response END) AS "Van Route (Standard Cafe name)",
MAX(CASE WHEN question ILIKE '%Vehicle Number%' THEN response END) AS "Vehicle Number",
MAX(CASE WHEN question ILIKE '%Van Display Temperature (°C) before loading%' THEN response END) AS "Van Display Temperature (°C) before loading",
MAX(CASE WHEN question ILIKE '%Product Van Type%' THEN response END) AS "Product Van Type",
MAX(CASE WHEN question ILIKE '%Product Name 1%' THEN response END) AS "Product Name 1",
MAX(CASE WHEN question ILIKE '%Product Temperature 1 (°C)%' THEN response END) AS "Product Temperature 1 (°C)",
MAX(CASE WHEN question ILIKE '%Product Name 2%' THEN response END) AS "Product Name 2",
MAX(CASE WHEN question ILIKE '%Product Temperature 2 (°C)%' THEN response END) AS "Product Temperature 2 (°C)",
MAX(CASE WHEN question ILIKE '%Product Accepted or Rejected%' THEN response END) AS "Product Accepted or Rejected",
MAX(CASE WHEN question ILIKE '%If Rejected, Mention Reason%' THEN response END) AS "If Rejected, Mention Reason"
FROM raw
group by 1,2,3,4
```

---

## ZEPTO WAREHOUSE AUDIT CHECKLIST_MH_ZEPTO WAREHOUSE AUDIT CHECKLIST_MH Report.sql

**Tables referenced:** form_responses, form_submissions, public.Zepto_QMS_Checkpoint_Master_Sheet_table, question_definitions

**Original Query:**

```sql
-- Data Source: ZEPTO WAREHOUSE AUDIT CHECKLIST_MH
-- Dashboard: ZEPTO WAREHOUSE AUDIT CHECKLIST_MH Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:52:47
-- ============================================================

SELECT store_id,
       MAX(
    CASE 
      WHEN question ILIKE '%Audited Location%' THEN 
        COALESCE(
          response->>'name',               -- case 1: {"id": "...", "name": "..."}
          response->'selected'->>0,        -- case 2: {"selected": ["..."]}
          response::text                   -- fallback
        )
    END
  ) AS "Audited Location", -- Warehouse Name/Location
 MAX( CASE
          WHEN question ILIKE '%Warehouse Name/Location%' THEN COALESCE( response->'selected'->>0, response::text )
      END ) AS "Warehouse Name/Location",
 MAX(CASE
         WHEN question ILIKE '%Auditor Name%' THEN response::text
     END) AS "Auditor Name",
 MAX(CASE
         WHEN question ILIKE '%FSSAI License Number%' THEN response::text
     END) AS "FSSAI License Number",
 city_id,
 audit_main_theme,
 theme,
 audit_date,
 audit_submission_number,
 auditor_name,
 CHECKPOINT,
 RESULT,
 auditor_observations
FROM public.Zepto_QMS_Checkpoint_Master_Sheet_table cms
JOIN form_submissions fs ON cms.audit_submission_knid = fs.response_id
JOIN form_responses fr ON fs.id = fr.form_submit_id
JOIN question_definitions qd ON fr.question_id = qd.question_id
WHERE audit_main_theme ILIKE ('%ZEPTO WAREHOUSE AUDIT CHECKLIST_MH%')
 AND audit_date >= CURRENT_DATE - INTERVAL '7 days' AND audit_date < CURRENT_DATE
GROUP BY store_id,
         city_id,
         audit_main_theme,
         theme,
         audit_date,
         audit_submission_number,
         auditor_name,
         CHECKPOINT,
         RESULT,
         auditor_observations
```

---

## Zepto - New Associates Onboarding Report_Zepto - Checklists Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Zepto - New Associates Onboarding Report
-- Dashboard: Zepto - Checklists Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:03
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike ('New Associates Onboarding%')
     AND organization = 'Zds-indus'
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
        WHERE submit_date >= date_trunc('month', current_date)
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
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name as "UserName"
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   join user_details ud on fr.user_id = ud.uuid
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
            16,
            17
   ORDER BY 1,
            2,
            3)
SELECT sno,submit_date,location,"UserName",
MAX(CASE WHEN question ILIKE 'New Associates Onboarding%' THEN response END) AS "New Associates Onboarding",
MAX(CASE WHEN question ILIKE 'Associate Email Address%' THEN response END) AS "Associate Email Address",
MAX(CASE WHEN question ILIKE 'Associate Employee Code%' THEN response END) AS "Associate Employee Code",
MAX(CASE WHEN question ILIKE 'Employee Type%' THEN response END) AS "Employee Type",
MAX(CASE WHEN question ILIKE 'Vendor Name%' THEN response END) AS "Vendor Name 1",
MAX(CASE WHEN question ILIKE 'Associate First Name%' THEN response END) AS "Associate First Name",
MAX(CASE WHEN question ILIKE 'Associate Middle Name%' THEN response END) AS "Associate Middle Name/ Father Name",
MAX(CASE WHEN question ILIKE 'Associate Last Name%' THEN response END) AS "Associate Last Name/ Surname",
MAX(CASE WHEN question ILIKE 'Gender%' THEN response END) AS "Gender",
MAX(CASE WHEN question ILIKE 'Date of Birth%' THEN response END) AS "Date of Birth",
MAX(CASE WHEN question ILIKE 'Associate Mobile Number%' THEN response END) AS "Associate Mobile Number",
MAX(CASE WHEN question ILIKE 'This does not look like a correct mobile number%' THEN response END) AS "This does not look like a correct mobile number, please check the number you have entered",
MAX(CASE WHEN question ILIKE 'Associate Date of Joining%' THEN response END) AS "Associate Date of Joining",
MAX(CASE WHEN question ILIKE 'City Name%' THEN response END) AS "City Name",
MAX(CASE WHEN question ILIKE 'Designation%' THEN response END) AS "Designation",
MAX(CASE WHEN question ILIKE 'Reporting Manager Email ID%' THEN response END) AS "Reporting Manager Email ID",
MAX(CASE WHEN question ILIKE 'Delivery Hub Name%' THEN response END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE 'Sourced By%' THEN response END) AS "Sourced By",
MAX(CASE WHEN question ILIKE 'Associate Mobile Type%' THEN response END) AS "Associate Mobile Type",
MAX(CASE WHEN question ILIKE 'Associate Age%' THEN response END) AS "Associate Age",
MAX(CASE WHEN question ILIKE 'Onboarding cannot happen for Age less than 18%' THEN response END) AS "Onboarding cannot happen for Age less than 18",
MAX(CASE WHEN question ILIKE 'Associate Aadhaar No.%' THEN response END) AS "Associate Aadhaar No.",
MAX(CASE WHEN question ILIKE 'Previously associate have ever worked with Zepto%' THEN response END) AS "Previously associate have ever worked with Zepto?",
MAX(CASE WHEN question ILIKE 'Previous Employee ID%' THEN response END) AS "Previous Employee ID",
MAX(CASE WHEN question ILIKE 'Previous Mobile Number%' THEN response END) AS "Previous Mobile Number",
MAX(CASE WHEN question ILIKE 'How much associates scored in the interview assessment%' THEN response END) AS "How much associates scored in the interview assessment?",
MAX(CASE WHEN question ILIKE 'Remark or Comment about associate%' THEN response END) AS "Remark or Comment about associate",
MAX(CASE WHEN question ILIKE 'Associate is Fit to Work%' THEN response END) AS "Associate is Fit to Work",
MAX(CASE WHEN question ILIKE 'Please attach the offer letter%' THEN response END) AS "Please attach the offer letter",
MAX(CASE WHEN question ILIKE 'Associate''s Net Take home salary%' THEN response END) AS "Associate's Net Take home salary (Mention as per offer letter)"
FROM raw
group by 1,2,3,4
```

---

## Zepto Daily Training Update Form Report_Zepto Training Form Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: Zepto Daily Training Update Form Report
-- Dashboard: Zepto Training Form Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:41
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min' * tzoffset AS diff
   FROM organizations
   WHERE id = 'Zds-indus'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id IN ('-OWVX5Y-opgITco5A4wR')
     AND organization = 'Zds-indus'
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
  (SELECT DISTINCT ON (response_id) form_submissions.*
  from form_submissions
   where form_id IN (select form_knid from forms)
   --JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id,
            id DESC),
     fs AS
  (SELECT _fs.*,forms.form_name
   FROM _fs
   JOIN forms on _fs.form_id = forms.form_knid
   WHERE submit_date >= date_trunc('week', CURRENT_DATE) ),
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
   		  ud.identifier,
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
            17,
   			18
   ORDER BY 1,
            2,
            3
            )
select sno,
submit_date,
MAX(CASE WHEN question ILIKE '%Select Your Name%' THEN response ELSE NULL END) AS "Select Your Name",
MAX(CASE WHEN question ILIKE '%City Name%' THEN response ELSE NULL END) AS "City Name",
MAX(CASE WHEN question ILIKE '%Delivery Hub Name%' THEN response ELSE NULL END) AS "Delivery Hub Name",
MAX(CASE WHEN question ILIKE '%Select Zone%' THEN response ELSE NULL END) AS "Select Zone",
MAX(CASE WHEN question ILIKE '%Date of Visit%' THEN response ELSE NULL END) AS "Date of Visit",
MAX(CASE WHEN question ILIKE '%Select the type of training conducted%' THEN response ELSE NULL END) AS "Select the type of training conducted",
MAX(CASE WHEN question ILIKE '%Training Topic%' THEN response ELSE NULL END) AS "Training Topic",
MAX(CASE WHEN question ILIKE '%Select Mode of Training%' THEN response ELSE NULL END) AS "Select Mode of Training",
MAX(CASE WHEN question ILIKE '%Total number of people trained%' THEN response ELSE NULL END) AS "Total number of people trained",
MAX(CASE WHEN question ILIKE '%Number of batches conducted%' THEN response ELSE NULL END) AS "Number of batches conducted",
MAX(CASE WHEN question ILIKE '%Time spent on each batch (In hours)%' THEN response ELSE NULL END) AS "Time spent on each batch (In hours)",
MAX(CASE WHEN question ILIKE '%Total time spent on Training Delivery for the day on selected type & topic%' THEN response ELSE NULL END) AS "Total time spent on Training Delivery for the day on selected type & topic"
from raw
group by 1,2
```

---

## coms edge report_Coms Edge Report.sql

**Tables referenced:** _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, other, outside, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: coms edge report
-- Dashboard: Coms Edge Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:56:05
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'swiggy-mart-whirlpool'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike '%COMS EDGE%'
     AND organization = 'swiggy-mart-whirlpool'
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
        where submit_date >= date_trunc('month', current_timestamp)
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
                                 'upload_video','upload_file') THEN (fr.response)->0->>'response'
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
          ud.first_name
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   Join user_details ud on fr.user_id = ud.uuid
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
sno,TO_CHAR(submit_date, 'DD/MM/YY HH24:MI') as submit_date,first_name as form_filled_by,
MAX(CASE WHEN question ILIKE '%POD ID%' THEN response END) AS "POD ID",
MAX(CASE WHEN question ILIKE '%Capture the Image of POD Name Board with Scootsy%' THEN response END) AS "Capture the Image of POD Name Board with Scootsy",
MAX(CASE WHEN question ILIKE '%FSSAI License Is Available?%' THEN response END) AS "FSSAI License Is Available?",
MAX(CASE WHEN question ILIKE '%FSSAI License Valid Upto / Expiry Date%' THEN response END) AS "FSSAI License Valid Upto / Expiry Date",
MAX(CASE WHEN question ILIKE '%Capture the Image of FSSAI License%' THEN response END) AS "Capture the Image of FSSAI License",
MAX(CASE WHEN question ILIKE '%Is the security maintaining the register properly?%' THEN response END) AS "Is the security maintaining the register properly?",
MAX(CASE WHEN question ILIKE '%Capture the Images%' THEN response END) AS "Capture the Images",
MAX(CASE WHEN question ILIKE '%Are you using the IM COM app?%' THEN response END) AS "Are you using the IM COM app?",
MAX(CASE WHEN question ILIKE '%Capture the Image of IMCOM app logged in the Laptop%' THEN response END) AS "Capture the Image of IMCOM app logged in the Laptop",
MAX(CASE WHEN question ILIKE '%Is the daily gate meeting happening for Morning shift?%' THEN response END) AS "Is the daily gate meeting happening for Morning shift?",
MAX(CASE WHEN question ILIKE '%Is the daily gate meeting happening for Afternoon shift?%' THEN response END) AS "Is the daily gate meeting happening for Afternoon shift?",
MAX(CASE WHEN question ILIKE '%Is the daily gate meeting happening for Night shift?%' THEN response END) AS "Is the daily gate meeting happening for Night shift?",
MAX(CASE WHEN question ILIKE '%Are the SM / ASM Updating the Attendance in DWS?%' THEN response END) AS "Are the SM / ASM Updating the Attendance in DWS?",
MAX(CASE WHEN question ILIKE '%Capture the Image of DWS App%' THEN response END) AS "Capture the Image of DWS App",
MAX(CASE WHEN question ILIKE '%Is the daily recognition of good and bad performers happening?%' THEN response END) AS "Is the daily recognition of good and bad performers happening?",
MAX(CASE WHEN question ILIKE '%Mention the Name of good performer for yesterday%' THEN response END) AS "Mention the Name of good performer for yesterday",
MAX(CASE WHEN question ILIKE '%Mention the Name of Bad performer for yesterday%' THEN response END) AS "Mention the Name of Bad performer for yesterday",
MAX(CASE WHEN question ILIKE '%Did you speak to 5 store executives to understand their issues?%' THEN response END) AS "Did you speak to 5 store executives to understand their issues?",
MAX(CASE WHEN question ILIKE '%Mention the top issues which are reported by the store executives.%' THEN response END) AS "Mention the top issues which are reported by the store executives.",
MAX(CASE WHEN question ILIKE '%Elaborate the Other Issues%' THEN response END) AS "Elaborate the Other Issues",
MAX(CASE WHEN question ILIKE '%Does the pod have ideal manpower?%' THEN response END) AS "Does the pod have ideal manpower?",
MAX(CASE WHEN question ILIKE '%What is the current Manpower gap?%' THEN response END) AS "What is the current Manpower gap?",
MAX(CASE WHEN question ILIKE '%Did you speak to HRBP / TA for existing issues?%' THEN response END) AS "Did you speak to HRBP / TA for existing issues?",
MAX(CASE WHEN question ILIKE '%Is the packing table clear and free from other materials?%' THEN response END) AS "Is the packing table clear and free from other materials?",
MAX(CASE WHEN question ILIKE '%Capture the Image of Packing table%' THEN response END) AS "Capture the Image of Packing table",
MAX(CASE WHEN question ILIKE '%Is the pick path free to walk?%' THEN response END) AS "Is the pick path free to walk?",
MAX(CASE WHEN question ILIKE '%Capture the Images of paths%' THEN response END) AS "Capture the Images of paths",
MAX(CASE WHEN question ILIKE '%All FPO bins are placed in the racks?%' THEN response END) AS "All FPO bins are placed in the racks?",
MAX(CASE WHEN question ILIKE '%Capture the Images of Milk stored in the chillers%' THEN response END) AS "Capture the Images of Milk stored in the chillers",
MAX(CASE WHEN question ILIKE '%Capture the Images of Ice Cream stored in the Freezers%' THEN response END) AS "Capture the Images of Ice Cream stored in the Freezers",
MAX(CASE WHEN question ILIKE '%Are all CCTV cameras working and feed is visible on the TV?%' THEN response END) AS "Are all CCTV cameras working and feed is visible on the TV?",
MAX(CASE WHEN question ILIKE '%Capture the Images of TV%' THEN response END) AS "Capture the Images of TV",
MAX(CASE WHEN question ILIKE '%How many infra tickets were raised in the last 15 days?%' THEN response END) AS "How many infra tickets were raised in the last 15 days?",
MAX(CASE WHEN question ILIKE '%Capture the Image of Altra tech%' THEN response END) AS "Capture the Image of Altra tech",
MAX(CASE WHEN question ILIKE '%How many infra tickets are open > 3 days ?%' THEN response END) AS "How many infra tickets are open > 3 days ?",
MAX(CASE WHEN question ILIKE '%Are there any rusted /  broken racks in the pod?%' THEN response END) AS "Are there any rusted /  broken racks in the pod?",
MAX(CASE WHEN question ILIKE '%Capture the Image of Rusted / Broken Racks%' THEN response END) AS "Capture the Image of Rusted / Broken Racks",
MAX(CASE WHEN question ILIKE '%Did you find dust on non moving stock?%' THEN response END) AS "Did you find dust on non moving stock?",
MAX(CASE WHEN question ILIKE '%Did you speak to INFRA POC for existing issues?%' THEN response END) AS "Did you speak to INFRA POC for existing issues?",
MAX(CASE WHEN question ILIKE '%Did you speak to POD maintanence POC for existing issues?%' THEN response END) AS "Did you speak to POD maintanence POC for existing issues?",
MAX(CASE WHEN question ILIKE '%Have you spoken to Fleet Coach (DE Related Issues) ?%' THEN response END) AS "Have you spoken to Fleet Coach (DE Related Issues) ?",
MAX(CASE WHEN question ILIKE '%Did you speak to POD IT POC for existing issues?%' THEN response END) AS "Did you speak to POD IT POC for existing issues?",
MAX(CASE WHEN question ILIKE '%Are there any products placed near the UPS/inverter area?%' THEN response END) AS "Are there any products placed near the UPS/inverter area?",
MAX(CASE WHEN question ILIKE '%How many ladders / step tool is available in the pod?%' THEN response END) AS "How many ladders / step tool is available in the pod?",
MAX(CASE WHEN question ILIKE '%Capture the Image of Step tool / Ladder which is avilable in the pod%' THEN response END) AS "Capture the Image of Step tool / Ladder which is avilable in the pod",
MAX(CASE WHEN question ILIKE '%Are the reusable/insulation bags cleaning being done?%' THEN response END) AS "Are the reusable/insulation bags cleaning being done?",
MAX(CASE WHEN question ILIKE '%Capture the Images of reusable / insulation bags%' THEN response END) AS "Capture the Images of reusable / insulation bags",
MAX(CASE WHEN question ILIKE '%Is the POD Washroom clean?%' THEN response END) AS "Is the POD Washroom clean?",
MAX(CASE WHEN question ILIKE '%Is the DE washrooms clean?%' THEN response END) AS "Is the DE washrooms clean?",
MAX(CASE WHEN question ILIKE '%Drinking water is available for DE''s?%' THEN response END) AS "Drinking water is available for DE's?",
MAX(CASE WHEN question ILIKE '%Garbage Disposal happening on daily basis?%' THEN response END) AS "Garbage Disposal happening on daily basis?",
MAX(CASE WHEN question ILIKE '%Capture the Image of Empty dustbins%' THEN response END) AS "Capture the Image of Empty dustbins",
MAX(CASE WHEN question ILIKE '%Fire extinguishers available at the POD?%' THEN response END) AS "Fire extinguishers available at the POD?",
MAX(CASE WHEN question ILIKE '%Capture the image of Fire extinguishers%' THEN response END) AS "Capture the image of Fire extinguishers",
MAX(CASE WHEN question ILIKE '%Can we add more racks in the pod?%' THEN response END) AS "Can we add more racks in the pod?",
MAX(CASE WHEN question ILIKE '%Mention the Count of Extra Racks to be added%' THEN response END) AS "Mention the Count of Extra Racks to be added",
MAX(CASE WHEN question ILIKE '%Capture the photo of FnV empty crate stacking%' THEN response END) AS "Capture the photo of FnV empty crate stacking",
MAX(CASE WHEN question ILIKE '%Capture the photo of Ambient empty crate stacking%' THEN response END) AS "Capture the photo of Ambient empty crate stacking",
MAX(CASE WHEN question ILIKE '%Mention the 3 Action items you have assigned to SM / ASM during the pod visit%' THEN response END) AS "Mention the 3 Action items you have assigned to SM / ASM during the pod visit",
MAX(CASE WHEN question ILIKE '%SM / ASM Who is reporting in the night shift ? Mention their name%' THEN response END) AS "SM / ASM Who is reporting in the night shift ? Mention their name",
MAX(CASE WHEN question ILIKE '%Take Selfie with the team%' THEN response END) AS "Take Selfie with the team",
MAX(CASE WHEN question ILIKE '%Last visit done by me on for this pod%' THEN response END) AS "Last visit done by me on for this pod",
MAX(CASE WHEN question ILIKE '%Capture the photo of pod from outside%' THEN response END) AS "Capture the photo of pod from outside",
MAX(CASE WHEN question ILIKE '%Who is the current duty manager and his / her designation?%' THEN response END) AS "Who is the current duty manager and his / her designation?",
MAX(CASE WHEN question ILIKE '%On a scale of 5 how would you rate the duty manager on the overall shift management? (1 is Low 5 is High)%' THEN response END) AS "On a scale of 5 how would you rate the duty manager on the overall shift management? (1 is Low 5 is High)"
FROM raw
group by 1,2,3
order by submit_date,sno
```

---

## croma announcements reports_Announcement Report - Croma.sql

**Tables referenced:** analytics_requests, event_types, filtered_nuggets, nuggets, user_details

**Original Query:**

```sql
-- Data Source: croma announcements reports
-- Dashboard: Announcement Report - Croma
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:55:36
-- ============================================================

WITH filtered_nuggets AS
  (SELECT id,
          title,
          author
   FROM nuggets
   WHERE classification_type = 'general'
     AND sub_type NOT IN ('quiz') )
SELECT ar.location AS "Store",
       TO_CHAR(TO_TIMESTAMP(ar.created_at / 1000), 'DD-MM-YYYY') AS created_date,
       fn.title AS "Announcement title",
	   fn.id as "Announcement ID",
       ud.first_name AS "Announcement Author",
       ud.department AS "Author Department",
       SUM(CASE
               WHEN et.event_type = 'sent' THEN 1
               ELSE 0
           END) AS sent_count,
       SUM(CASE
               WHEN et.event_type = 'received' THEN 1
               ELSE 0
           END) AS received_count,
       SUM(CASE
               WHEN et.event_type = 'consumed' THEN 1
               ELSE 0
           END) AS viewed_count
FROM analytics_requests ar
JOIN event_types et ON et.id = ar.event_id
LEFT JOIN filtered_nuggets fn ON ar.nugget_id = fn.id
LEFT JOIN user_details ud ON fn.author = ud.uuid
WHERE TO_TIMESTAMP(ar.created_at / 1000) 
      >= CURRENT_DATE - INTERVAL '7 days'
  AND ud.email IN ('promotion@croma.com',
'posnote@croma.com',
'process@croma.com',
'ConsumerFinance@croma.com',
'newlaunches@croma.com',
'Incentives@croma.com',
'learning.desk@croma.com',
'HR.Desk@croma.com',
'reports@croma.com',
'safety@croma.com',
'stockupdates@croma.com',
'Trade-in_Finance@croma.com',
'stockupdates@croma.com',
'SOH.revenue@croma.com',
'scmprocess@croma.com',
'sohimplementation@croma.com',
'contactunboxed@croma.com',
'sustainability@croma.com',
'shibashish.roy@croma.com')
GROUP BY 1,
         2,
         3,
         4,
         5,
		 6
ORDER BY 1,
         2,
         3
```

---

## croma_weekly_observation_Croma Weekly Observation.sql

**Tables referenced:** RAW, _fs, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, location_questions, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, user_details

**Columns needing snake_case conversion:**

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: croma_weekly_observation
-- Dashboard: Croma Weekly Observation
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:54:52
-- ============================================================

WITH td AS
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
   WHERE title ILIKE 'Safety Observation%'
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
   WHERE submit_date >= date_trunc('month', CURRENT_DATE)),
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
          form_name,
          fr.form_id,
          fr.response_id,
          fr.submit_date AS submit_date,
          fr.location,
          fr.user_id,
          ud.first_name,
          ud.identifier,
          ud.designation,
          ud.division,
          ud.sub_division
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
   AND fr.form_id = fd.form_knid
   JOIN td ON fr.organization = td.organization
   JOIN user_details ud ON fr.user_id = ud.uuid
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
            20
   ORDER BY 1,
            2,
            3)
SELECT form_name AS "Form Name",
       sno AS "Submission Number",
       submit_date AS "Submit Date",
       first_name AS "Sender Name",
       identifier AS "Sender Identifier",
       designation AS "Sender Designation",
       division AS "Sender Division",
       sub_division AS "Sender Sub Division",
       MAX(CASE
               WHEN question = 'Location' THEN response
               ELSE NULL
           END) AS "Location",
       MAX(CASE
               WHEN question = 'Sub Category' THEN response
               ELSE NULL
           END) AS "Sub Category",
       MAX(CASE
               WHEN question = 'Description of the issue' THEN response
               ELSE NULL
           END) AS "Description of the issue",
       MAX(CASE
               WHEN question = 'Upload supporting evidence' THEN response
               ELSE NULL
           END) AS "Upload supporting evidence"
FROM RAW
GROUP BY 1,
         2,
         3,
         4,
         5,
         6,
         7,
         8
```

---

## ddt sytems multi attendance report_DDT- Custom Attendance Report.sql

**Tables referenced:** base, base_sum, sa, shift_attendance, user_details

**Columns needing snake_case conversion:**

- `otherDetails` -> `other_details` (alias: `other_details AS "otherDetails"`)


**Original Query:**

```sql
-- Data Source: ddt sytems multi attendance report
-- Dashboard: DDT- Custom Attendance Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:53:17
-- ============================================================

WITH base AS (
    SELECT 
        sa."Shift ID",
        sa."UUID",
        sa."Employee Name",
        sa."Division",
        sa."Sub Division",
        sa."Employee ID",
        sa."Job Type",
        ud.job_location AS "Home Location",
        sa."Shift Location",
        sa."Department" AS "Role",
        sa."Designation",
        ud.profile -> 'otherDetails' -> 'ID' ->> 'type' AS "Local / Foreign",
        ud.profile -> 'otherDetails' -> 'ID' ->> 'number' AS "NRIC",

        extract('week' FROM "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') AS "Week No",

        CASE
            WHEN to_char("Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore', 'Dy') IN ('Sat','Sun') 
            THEN 'Weekend'
            ELSE NULL
        END AS "Special Rates",

        sa."Status",

        sm.comments AS "Leave Tags",

        "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore' AS "Scheduled Start for Date Filter",

        CASE WHEN sa."Status" NOT IN ('On Leave')
            THEN "Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
            ELSE NULL
        END AS "Scheduled In",

        CASE WHEN sa."Status" NOT IN ('On Leave')
            THEN "Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
            ELSE NULL
        END AS "Scheduled Out",

        CASE WHEN sa."Status" NOT IN ('On Leave','Absent')
            THEN "Actual Clockin Time" AT TIME ZONE 'Asia/Singapore'
            ELSE NULL
        END AS "Time In",

        CASE WHEN sa."Status" NOT IN ('On Leave','Absent')
            THEN "Actual Clockout Time" AT TIME ZONE 'Asia/Singapore'
            ELSE NULL
        END AS "Time Out",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins')
                    THEN sa."Actual Clockin Time" AT TIME ZONE 'Asia/Singapore'
                ELSE sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
            END
        END AS "Adjusted Time In",

        CASE WHEN sa."Status" NOT IN ('On Leave','Absent')
            THEN sa."Actual Break Hours"
            ELSE NULL
        END AS "Unpaid Break",

        CASE WHEN sa."Status" NOT IN ('On Leave')
            THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Scheduled Start Time" AT TIME ZONE 'UTC' 
                     - interval '1 hour'*sa."Scheduled Break Hours"))/3600
            ELSE NULL
        END AS "Scheduled Hours",

        CASE WHEN sa."Status" NOT IN ('On Leave')
            THEN sa."Scheduled Break Hours"
            ELSE NULL
        END AS "Scheduled Break Hours",

        CASE
            WHEN sa."Status" IN ('Absent') THEN NULL
            WHEN sa."Status" IN ('On Leave') 
                AND (
                    (CASE
                        WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) = '-' 
                            THEN substring("Shift ID", 13, length("Shift ID") - length("UUID") - 13)
                        WHEN "Status" = 'On Leave' AND substring("Shift ID", 12, 1) != '-' 
                            THEN substring("Shift ID", 14, length("Shift ID") - length("UUID") - 14)
                        ELSE NULL
                    END) ILIKE ANY (ARRAY['NoPay%','Unpaid%','Off-Day'])
                ) 
                THEN NULL
            WHEN sa."Status" IN ('On Leave') THEN 8
            ELSE CASE
                WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins')
                    THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Actual Clockin Time"))/3600 
                         - sa."Actual Break Hours"
                ELSE extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Scheduled Start Time" AT TIME ZONE 'UTC'))/3600 
                         - sa."Actual Break Hours"
            END
        END AS "Total Paid Hours",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins')
                    THEN extract(epoch FROM (sa."Actual Clockin Time" - sa."Scheduled Start Time" AT TIME ZONE 'UTC'))/3600
                ELSE NULL
            END
        END AS "Late In Hours",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Break Hours"*60 > sa."Scheduled Break Hours"*60 + 5
                    THEN sa."Actual Break Hours" - sa."Scheduled Break Hours"
                ELSE NULL
            END
        END AS "Excess Break Hours",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockout Time" < (sa."Scheduled End Time" AT TIME ZONE 'UTC' - interval '5 mins')
                    THEN extract(epoch FROM (sa."Scheduled End Time" AT TIME ZONE 'UTC' - sa."Actual Clockout Time"))/3600
                ELSE NULL
            END
        END AS "Early Out Hours",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockout Time" > (sa."Scheduled End Time" AT TIME ZONE 'UTC' + interval '10 mins')
                    THEN extract(epoch FROM (sa."Actual Clockout Time" - sa."Scheduled End Time" AT TIME ZONE 'UTC'))/3600
                ELSE NULL
            END
        END AS "Late Out Hours",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockin Time" > (sa."Scheduled Start Time" AT TIME ZONE 'UTC' + interval '5 mins')
                    THEN 1
                ELSE NULL
            END
        END AS "Late Shifts",

        CASE WHEN sa."Status" = 'Absent' THEN 1 ELSE NULL END AS "Absent Shifts",

        CASE 
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN sa."Actual Clockout Time" < (sa."Scheduled End Time" AT TIME ZONE 'UTC' - interval '5 mins')
                    THEN 1
                ELSE NULL
            END
        END AS "Early Out Shifts",

        CASE
            WHEN sa."Status" IN ('On Leave','Absent') THEN NULL
            ELSE CASE
                WHEN extract('day' FROM sa."Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')
                     > extract('day' FROM sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore')
                     AND extract('hour' FROM sa."Scheduled End Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore') >= 4
                THEN 1
                ELSE NULL
            END
        END AS "Night Shift Allowance"

    FROM shift_attendance sa
    JOIN user_details ud ON sa."UUID" = ud.uuid
    JOIN "shifts_DDT-Systems-multi" sm on sa."Shift ID" = sm.shift_id
    WHERE sa.organization = 'DDT-Systems-multi'
      AND sa."Scheduled Start Time" AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Singapore'
          BETWEEN @{{:Date Range.START}}::timestamp 
          AND @{{:Date Range.END}}::timestamp + interval '1 day'
          and sm.is_deleted = false
          and sm.is_planning = true
),

base_sum AS (
    SELECT *,
        SUM("Total Paid Hours") OVER (
            PARTITION BY "UUID", "Week No"
            ORDER BY "Scheduled Start for Date Filter"
        ) AS total_week_hours_to_date
    FROM base
)

SELECT
    "Employee Name" AS "Name",
    "Shift ID" AS "Shift Name",
    "Role" AS "Dept",
    "Designation",
    "Leave Tags" AS "Shift Notes",

    DATE("Scheduled Start for Date Filter") AS "Shift Date",

    "Scheduled In" AS "Shift Scheduled Start Time",
    "Scheduled Out" AS "Shift Scheduled End Time",

    "Time In" AS "Actual Check-in Time",
    "Time Out" AS "Actual Check-out Time",

    "Scheduled Hours" AS "Total Hours In Shift (hrs)",
    "Total Paid Hours" AS "Actual Work Duration (hrs)",

    CASE
        WHEN "Total Paid Hours" >= 5 THEN 1
        WHEN "Total Paid Hours" < 5 AND "Total Paid Hours" IS NOT NULL THEN 0.5
        ELSE NULL
    END AS "Man Day"

FROM base_sum
```

---

## watsons User Groups_Watsons Monthly User Report.sql

**Tables referenced:** user_details

**Columns needing snake_case conversion:**

- `lmsCourses` -> `lms_courses` (alias: `lms_courses AS "lmsCourses"`)

- `lmsReports` -> `lms_reports` (alias: `lms_reports AS "lmsReports"`)


**Original Query:**

```sql
-- Data Source: watsons User Groups
-- Dashboard: Watsons Monthly User Report
-- Category: Custom Reports
-- Extracted: 2026-01-29 16:56:24
-- ============================================================

 SELECT uuid,
       first_name,
       last_name,
       identifier,
       division,
       sub_division,
       job_location AS outlet,
       department,
       designation,
       CASE
           WHEN is_super_admin = 'true' THEN 'Yes'
           ELSE 'No'
       END AS is_super_admin,
       CASE
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' IS NULL THEN 'Full Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '0' THEN 'No Access'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '1' THEN 'View Only'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' IN ('15',
                                                                        '17') THEN 'View Create & Edit'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '49' THEN 'View and Publish'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '63' THEN 'View, Create, Edit and Publisher'
           WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'announcements' = '65535' THEN 'Full Access'
           ELSE 'View & Edit'
       END AS announcements_polls_access,
     CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'bites' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS bites_access,

-- Shifts Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'roster' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS shifts_access,

-- Forms Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'forms' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS forms_access,

-- Issues Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'issues' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS issues_access,

-- LMS Courses Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsCourses' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS lmscourses_access,

/*-- LMS Reports Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'lmsReports' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS lmsreports_access,*/

-- Guides Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'guide' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS guides_access,

-- Users Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'users' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS users_access,

-- Groups Access
CASE
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' IS NULL THEN 'Full Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '0' THEN 'No Access'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '1' THEN 'View Only'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' IN ('15', '17') THEN 'View Create & Edit'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '49' THEN 'View and Publish'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '63' THEN 'View, Create, Edit and Publisher'
    WHEN PROFILE -> 'ACL' -> 'dashboard' ->> 'groups' = '65535' THEN 'Full Access'
    ELSE 'View & Edit'
END AS groups_access
FROM user_details
WHERE is_active = TRUE
and is_admin = true
  AND organization = 'watsons-leo'
  
 -- AND PROFILE::jsonb ? 'ACL'
  --AND PROFILE::jsonb->'ACL' ? 'dashboard'
```

---
