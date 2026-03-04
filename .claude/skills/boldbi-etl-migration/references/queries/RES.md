# RES

> Auto-generated on 2026-03-04 08:13

**Total queries:** 6

---

## RES Classroom Training Attendance_Classroom Training Attendance.sql

**Tables referenced:** RAW, attendance, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, td, training_list, user_details

**Columns needing snake_case conversion:**

- `otherDetails` -> `other_details` (alias: `other_details AS "otherDetails"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)


**Original Query:**

```sql
-- Data Source: RES Classroom Training Attendance
-- Dashboard: Classroom Training Attendance
-- Category: RES
-- Extracted: 2026-01-29 16:54:39
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'RESE-banyan'
   GROUP BY 1,
            2),
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
  WHERE (title ILIKE '%In-house Training%'
    OR title ILIKE '%WSQ FSC L1 / WSH L2%'
    OR title ILIKE '%WSQ FSC L1 Refresher%')
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
                                                                                    END), ' ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula', 'time') THEN fr.response->>0
              WHEN fd.q_type IN ('user') THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed',
                                 'upload_image',
                                 'upload_video') THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature') THEN fr.response->'response'->>0
              WHEN fd.q_type IN ('location',
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
            3), training_list AS
  (SELECT response_id AS "Trainer Form Response KNID",
          sno AS "Trainer Form Response No",
          submit_date::date||'-'||sno AS "Training ID",
          max(CASE
                  WHEN question = 'Name of Trainer:' THEN response
                  ELSE NULL
              END) AS "Trainer",
  max(CASE
                  WHEN question = 'Session' THEN response
                  ELSE NULL
              END) AS "Session" ,
          max(CASE
                  WHEN question = 'Course Name' THEN response
                  ELSE NULL
              END) AS "Course",
          trim(max(CASE
                  WHEN question = 'Course Code' THEN replace(response, ', ', '')
                  ELSE NULL
              END)) AS "Code",
          max(CASE
                  WHEN question = 'Classroom Code:' THEN response
                  ELSE NULL
              END) AS "Venue",
          max(CASE
                  WHEN question = 'Training Dates:' THEN to_date(response, 'YYYY-MM-DD HH24:MI:SS')
                  ELSE NULL
              END) AS "Course Date",
          max(CASE
                  WHEN question = 'Training Time (Start):' THEN response
                  ELSE NULL
              END) AS "Start Time",
          max(CASE
                  WHEN question = 'Training Time (End):' THEN response
                  ELSE NULL
              END) AS "End Time",
          max(CASE
                  WHEN question = 'Assessment Date:' THEN to_date(response, 'YYYY-MM-DD HH24:MI:SS')
                  ELSE NULL
              END) AS "Assessment Date",
          max(CASE
                  WHEN question = 'Course Training Duration (Hours):' THEN response
                  ELSE NULL
              END) AS "Course Duration",
          max(CASE
                  WHEN question = 'Assessment Duration (Hours):' THEN response
                  ELSE NULL
              END) AS "Assessment Duration",
          max(CASE
                  WHEN raw.question = 'Signature' THEN response
                  ELSE NULL
              END) AS "Trainer Signature",
max(CASE
                  WHEN raw.question = 'Course Run:' THEN response
                  ELSE NULL
              END) AS "Course Run",
   max(CASE
                  WHEN raw.question = 'Remarks:' THEN response
                  ELSE NULL
              END) AS "Remarks",
   max(CASE
                  WHEN raw.question = 'Enrolment Created By:' THEN response
                  ELSE NULL
              END) AS "Enrolment Created By",
   max(CASE
                  WHEN raw.question = 'Enrolment Verified By:' THEN response
                  ELSE NULL
              END) AS "Enrolment Verified By",
   max(CASE
                  WHEN raw.question = 'Downloading of E- Cert:' THEN response
                  ELSE NULL
              END) AS "Downloading of E- Cert",
   max(CASE
                  WHEN raw.question = 'Course Medium' THEN response
                  ELSE NULL
              END) AS "Course Medium"
   
   FROM RAW
   WHERE form_name ILIKE '%Trainer%'
   GROUP BY 1,
            2,
            3),
                attendance AS
  (SELECT raw.response_id AS "Trainee Form Response KNID",
          raw.sno AS "Trainee Form Response No",
          raw.submit_date::date AS "Course Date",
          fs.user_id,
          max(CASE
                  WHEN raw.question = 'Course Name' THEN raw.response
                  ELSE NULL
              END) AS "Course",
  max(CASE
                  WHEN raw.question = 'Session' THEN raw.response
                  ELSE NULL
              END) AS "Session" ,
          trim(max(CASE
                  WHEN raw.question = 'Course Code' THEN replace(raw.response, ', ', '')
                  ELSE NULL
              END)) AS "Code",
          max(CASE
                  WHEN raw.question = 'Signature' THEN response
                  ELSE NULL
              END) AS "Trainee Signature"
   FROM RAW
   JOIN fs ON raw.response_id = fs.response_id
   WHERE (raw.form_name ilike '%Assessment%'
		  or raw.form_name ilike '%Session%'
		 		  or raw.form_name ilike '%Training%')
   GROUP BY 1,
            2,
            3,
            4)
SELECT t."Training ID",
       'RE&S Enterprises Pte Ltd' AS "Name of Training Provider",
       t."Course" AS "Course Title",
       t."Code",
       t."Course Date"::date AS "Training Dates",
      t."Start Time"||' to '||t."End Time" AS "Training Time",
       t."Course Duration"||' hrs' AS "Classroom Training Duration",
       t."Trainer" AS "Name of Trainer",
       t."Venue" AS "Classroom Code",
       t."Course Run" As "Course Run",
       t."Assessment Date" AS "Assessment Date",
	   t."Session" as "Trainer Session",
	   a."Session" as "Trainee Session",
       case when t."Assessment Duration" is null then '' else t."Assessment Duration"||' hrs' end AS "Assessment Duration",
       t."Trainer Signature",
       a.user_id AS "User KNID",
       ud.first_name AS "Name of Trainee",
      ud.profile->'otherDetails'->'ID'->>'number'  AS "NRIC/FIN",
      ud.profile->>'DOB' AS "D.O.B",
      ud.profile->'certifications'->0->>'name' AS "Education Level",
      ud.profile->'otherDetails'->'ID'->>'type' as "Nationality",
                    ud.phone_number AS "HP No",
                    ud.department AS "Outlet",
                    ud.designation AS "Title",
                    ud.designation AS "Position",
                    ud.profile->'otherDetails'->>'gender' AS "Gender",
                                                 a."Trainee Signature",
												 t."Remarks",
												 t."Enrolment Created By",
												 t."Enrolment Verified By",
												 t."Downloading of E- Cert",
												 t."Course Medium"
FROM training_list t
LEFT OUTER JOIN attendance a ON t."Course Date" = a."Course Date"
AND t."Code" = a."Code"
AND trim(t."Session") = trim(a."Session")
LEFT OUTER JOIN user_details ud ON a.user_id = ud.uuid
where trim(t."Code") = trim(@{{:Course Code}}) and
t."Course Date" = @{{:Course Date}}::date
```

---

## RES PM Master Sheet Part 1_RES PM Master Sheet Part 1.sql

**Tables referenced:** accountability, acknowledged_at, assigned_at, completed_at, first_attended_at, form_responses, form_submissions, internal_status, issue_questions, issues, metadata, nuggets, question_definitions, requested_at, stage_timeline, user_details

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: RES PM Master Sheet Part 1
-- Dashboard: RES PM Master Sheet Part 1
-- Category: RES
-- Extracted: 2026-01-29 16:57:22
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
     AND fs.submit_date AT TIME ZONE 'cct' > current_timestamp - interval '3 month'
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
      AND fs.submit_date AT TIME ZONE 'cct' > current_timestamp - interval '3 month')base
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
     AND fs.submit_date AT TIME ZONE 'cct' > current_timestamp - interval '3 month'
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
     AND fs.submit_date AT TIME ZONE 'cct' > current_timestamp - interval '3 month'
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

## RES PM Master Sheet Part 2_RES PM Master Sheet.sql

**Tables referenced:** LATERAL, completion_data, filtered_submissions, form_responses, form_submissions, internal_status, issue_questions, issues, metadata, nuggets, outlet_ack, question_definitions, stage_data, stage_timeline, user_details

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: RES PM Master Sheet Part 2
-- Dashboard: RES PM Master Sheet
-- Category: RES
-- Extracted: 2026-01-29 16:53:03
-- ============================================================

-- ========================================================
-- Performance: ~2.3 seconds (vs 830s original)
-- OPTIMIZATIONS:
-- 1. Pre-filter form_submissions once (reduces 2.9M -> ~2K rows)
-- 2. Remove unnecessary joins from stage_timeline
-- 3. Fixed issues CTE with proper array handling
-- 4. COALESCE for sentAt/st timestamp field compatibility
-- ========================================================

WITH 
-- Step 1: Pre-filter form_submissions (small result set)
filtered_submissions AS (
    SELECT fs.id AS form_submit_id,
           fs.sno,
           fs.form_id,
           fs.response_id,
           fs.user_id
    FROM form_submissions fs
    WHERE fs.form_id IN ('-ORJg-5xZdfUkGRRLp46', '-OZO5wuKqzRrbb8WqqDK')
      --AND fs.submit_date AT TIME ZONE 'cct' > CURRENT_TIMESTAMP - interval '16 week'
),

-- Step 2: Get metadata (outlet, severity)
metadata AS (
    SELECT DISTINCT ON (fs.response_id) 
           fs.form_submit_id,
           fs.sno,
           CASE
               WHEN n.title ILIKE '[Scheduled%' THEN 'Non-urgent'
               WHEN n.title ILIKE '[Urgent%' THEN 'Urgent'
               ELSE NULL
           END AS severity,
           ud.division AS ops,
           fr.response->>'name' AS outlet
    FROM filtered_submissions fs
    JOIN nuggets n ON fs.form_id = n.id
    JOIN user_details ud ON fs.user_id = ud.uuid
    JOIN form_responses fr ON fr.form_submit_id = fs.form_submit_id
    JOIN question_definitions qd ON fs.form_id = qd.nugget_id
        AND fr.question_id = qd.question_id
        AND qd.section_id = 'section-1'
        AND qd.question = 'Store Outlet'
    ORDER BY fs.response_id, fs.form_submit_id DESC
),

-- Step 3: Get issue sub-question IDs for both forms
issue_questions AS (
    SELECT nugget_id, question_id, question_details.key AS sub_question_id
    FROM (
        SELECT qd.nugget_id, qd.question_id, fields.value AS questions
        FROM question_definitions qd,
             jsonb_each(qd.definition::jsonb) fields
        WHERE qd.nugget_id IN ('-ORJg-5xZdfUkGRRLp46', '-OZO5wuKqzRrbb8WqqDK')
          AND qd.section_id = 'section-1'
          AND qd.question_type = 'table'
          AND fields.key = 'questions'
    ) base,
    jsonb_each(base.questions) question_details
    WHERE question_details.value->>'question' = 'What is/are the issue(s)?'
),

-- Step 4: Extract issues with proper array handling
issues AS (
    SELECT fs.form_submit_id,
           string_agg(DISTINCT elem->>iq.sub_question_id, chr(10)) as issue
    FROM filtered_submissions fs
    JOIN form_responses fr ON fr.form_submit_id = fs.form_submit_id
    JOIN issue_questions iq ON fs.form_id = iq.nugget_id 
        AND fr.question_id = iq.question_id
    CROSS JOIN LATERAL jsonb_array_elements(
        CASE WHEN jsonb_typeof(fr.response) = 'array' THEN fr.response ELSE '[]'::jsonb END
    ) AS elem
    GROUP BY fs.form_submit_id
),

-- Step 5: Get stage timeline
stage_timeline AS (
    SELECT fs.form_submit_id,
           qd.sqno,
           fr.response -> 'receiver' ->> 'userName' AS receiver,
           COALESCE(
               (fr.response ->> 'sentAt')::bigint,
               (fr.response ->> 'st')::bigint
           ) AS sent_at
    FROM filtered_submissions fs
    JOIN form_responses fr ON fr.form_submit_id = fs.form_submit_id
    JOIN question_definitions qd ON fs.form_id = qd.nugget_id
        AND fr.question_id = qd.question_id
    WHERE qd.question_type = 'section'
      AND fr.response ->> 'status' IN ('sent', 'Sent', 'submitted', 'Submitted', 'Approved', 'approved')
),

-- Step 6: Extract all stage data in single pass
stage_data AS (
    SELECT form_submit_id,
           MAX(CASE WHEN sqno = '1' THEN sent_at END) AS requested_at,
           MAX(CASE WHEN sqno = '2' THEN sent_at END) AS approved_at,
           MAX(CASE WHEN sqno = '3' THEN sent_at END) AS assigned_at,
           MAX(CASE WHEN sqno = '3' THEN receiver END) AS accountability,
           MAX(CASE WHEN sqno = '4' THEN sent_at END) AS first_attended_at,
           MAX(sqno::int) AS max_sqno
    FROM stage_timeline
    GROUP BY form_submit_id
),

-- Step 7: Get completion timestamps (severity-dependent)
completion_data AS (
    SELECT st.form_submit_id,
           MAX(CASE 
               WHEN (m.severity = 'Non-urgent' AND st.sqno = '6') 
                 OR (m.severity = 'Urgent' AND st.sqno = '5') 
               THEN st.sent_at 
           END) AS completed_at,
           MAX(CASE 
               WHEN (m.severity = 'Non-urgent' AND st.sqno = '7') 
                 OR (m.severity = 'Urgent' AND st.sqno = '6') 
               THEN st.sent_at 
           END) AS acknowledged_at
    FROM stage_timeline st
    JOIN metadata m ON st.form_submit_id = m.form_submit_id
    GROUP BY st.form_submit_id
),

-- Step 8: Outlet acknowledgement status
outlet_ack AS (
    SELECT fs.form_submit_id,
           MAX(CASE WHEN fr.response ->> 'status' IN ('Approved', 'approved', 'Submitted', 'submitted') 
                    THEN 1 ELSE 0 END) AS is_approved
    FROM filtered_submissions fs
    JOIN form_responses fr ON fr.form_submit_id = fs.form_submit_id
    JOIN question_definitions qd ON fs.form_id = qd.nugget_id
        AND fr.question_id = qd.question_id
    WHERE qd.question_type = 'section'
      AND qd.sqno IN ('6', '7')
    GROUP BY fs.form_submit_id
),

-- Step 9: Internal status
internal_status AS (
    SELECT form_submit_id,
           response -> 'selected' ->> 0 AS internal_status
    FROM (
        SELECT fs.form_submit_id,
               fr.response,
               ROW_NUMBER() OVER (PARTITION BY fs.form_submit_id ORDER BY qd.sqno DESC, fr.id DESC) AS rn
        FROM filtered_submissions fs
        JOIN form_responses fr ON fr.form_submit_id = fs.form_submit_id
        JOIN question_definitions qd ON fs.form_id = qd.nugget_id
            AND fr.question_id = qd.question_id
        WHERE qd.question = 'Status of Job'
    ) ranked
    WHERE rn = 1
)

-- Final SELECT
SELECT 
    m.sno AS "PM ID",
    m.severity AS "Severity",
    m.ops AS "OPS",
    m.outlet AS "Outlet",
    i.issue AS "Issue",
    CASE 
        -- NON-URGENT
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno = 7 AND COALESCE(oa.is_approved, 0) = 1 THEN 'Closed'
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno >= 6 THEN 'Waiting for Outlet Acknowledgement'
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno IN (4, 5) THEN 'Follow-up Needed'
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno = 3 THEN 'Job Assigned'
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno = 2 THEN 'VPO/VPA Approved'
        WHEN m.severity = 'Non-urgent' AND sd.max_sqno = 1 THEN 'Request Received'
        -- URGENT
        WHEN m.severity = 'Urgent' AND sd.max_sqno = 6 AND COALESCE(oa.is_approved, 0) = 1 THEN 'Closed'
        WHEN m.severity = 'Urgent' AND sd.max_sqno >= 5 THEN 'Waiting for Outlet Acknowledgement'
        WHEN m.severity = 'Urgent' AND sd.max_sqno = 4 THEN 'Follow-up Needed'
        WHEN m.severity = 'Urgent' AND sd.max_sqno = 3 THEN 'Job Assigned'
        WHEN m.severity = 'Urgent' AND sd.max_sqno = 2 THEN 'VPO/VPA Approved'
        WHEN m.severity = 'Urgent' AND sd.max_sqno = 1 THEN 'Request Received'
        ELSE 'Cancelled'
    END AS "Current Status",
    CASE
        WHEN sd.accountability ILIKE '%Team A%' THEN 'Team A'
        WHEN sd.accountability ILIKE '%Team B%' THEN 'Team B'
        WHEN sd.accountability ILIKE '%Team C%' THEN 'Team C'
        WHEN sd.accountability ILIKE '%Manager%' THEN 'PM'
        ELSE sd.accountability
    END AS "Accountability",
    ist.internal_status AS "Internal PM Status",
    to_timestamp(sd.requested_at/1000) AT TIME ZONE 'cct' AS "Requested At",
    to_timestamp(sd.approved_at/1000) AT TIME ZONE 'cct' AS "VPO/VPA Approved At",
    to_timestamp(sd.assigned_at/1000) AT TIME ZONE 'cct' AS "Assigned At",
    to_timestamp(sd.first_attended_at/1000) AT TIME ZONE 'cct' AS "First Attended At",
    to_timestamp(cd.completed_at/1000) AT TIME ZONE 'cct' AS "PM Completed At",
    to_timestamp(cd.acknowledged_at/1000) AT TIME ZONE 'cct' AS "Outlet Acknowledged At"
FROM metadata m
JOIN stage_data sd ON m.form_submit_id = sd.form_submit_id
LEFT JOIN issues i ON m.form_submit_id = i.form_submit_id
LEFT JOIN completion_data cd ON m.form_submit_id = cd.form_submit_id
LEFT JOIN outlet_ack oa ON m.form_submit_id = oa.form_submit_id
LEFT JOIN internal_status ist ON m.form_submit_id = ist.form_submit_id
WHERE sd.approved_at IS NOT NULL
ORDER BY sd.requested_at, ist.internal_status
```

---

## RES Skills Inventory_Skill Inventory.sql

**Tables referenced:** RAW, attendance, attendance_ca01, attendance_ob02, attendance_soj, base, base_2, base_ca01, base_non_ob02, base_ob02, base_soj, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_each, nuggets, organizations, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw, res_skills_inventory_archive, td, training_list, user_details

**Columns needing snake_case conversion:**

- `otherDetails` -> `other_details` (alias: `other_details AS "otherDetails"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: RES Skills Inventory
-- Dashboard: Skill Inventory
-- Category: RES
-- Extracted: 2026-01-29 16:53:22
-- ============================================================

WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'RESE-banyan'
   GROUP BY 1, 2),
     
     forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE ( title ilike '%(OPS) Onboarding Checklist%'
	OR  title ILIKE '%In-house Training%'
    OR title ILIKE '%WSQ FSC L1 / WSH L2%'
    OR title ILIKE '%WSQ FSC L1 Refresher%'
	OR title ILIKE '%Service On-The-Job-Training (SOJT)%'
	OR title ILIKE '%Confirmation assessment%'
	OR title ILIKE '%Conversion Assessment Form%'
	OR title ILIKE '%Conversion & Transition / Promotion%')
   GROUP BY 1, 2),
     
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
   UNION
   SELECT *
   FROM qd_non_table_with_logic
   UNION
   SELECT *
   FROM qd_table
   ORDER BY 1, 2, 3, 5 DESC, 7 DESC),
     
   fs AS
  (SELECT DISTINCT ON (response_id) form_submissions.*,
                      form_name
   FROM forms
   JOIN form_submissions ON forms.form_knid = form_submissions.form_id
   ORDER BY response_id, id ASC) ,
     
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
   WHERE question_type NOT IN ('table', 'nested')
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
                 jsonb_array_elements(response) WITH ORDINALITY AS base
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
              WHEN fd.q_type IN ('dropdown', 'multiple_choice', 'linear_scale', 'audit', 'user')
                THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes')
                THEN array_to_string(ARRAY(SELECT jsonb_array_elements_text(fr.response->'selected')
                                             UNION SELECT CASE
                                                            WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                            ELSE NULL
                                                        END), ', ')
              WHEN fd.q_type IN ('date', 'datetime')
                THEN to_char(to_timestamp((fr.response::bigint)/1000) + td.diff, 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field', 'single_text_field', 'qr_code', 'formula')
                THEN fr.response->>0
              WHEN fd.q_type IN ('user')
                THEN fr.response::text
              WHEN fd.q_type IN ('upload_mixed', 'upload_image', 'upload_video')
                THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature', 'location', 'division', 'sub_division')
                THEN fr.response ->> 'name'
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
   GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
   ORDER BY 1, 2, 3),
     
     training_list AS
  (SELECT form_id,
          response_id AS "Trainer Form Response KNID",
          sno AS "Trainer Form Response No",
          submit_date::date||'-'||sno AS "Training ID",
          max(CASE WHEN question = 'Name of Trainer:' THEN response ELSE NULL END) AS "Trainer",
          max(CASE WHEN question = 'Course Name' THEN response ELSE NULL END) AS "Course",
          max(CASE WHEN question = 'Session' THEN response ELSE NULL END) AS "Session",
          max(CASE WHEN question = 'Course Code' THEN replace(response, ', ', '') ELSE NULL END) AS "Code",
          max(CASE WHEN question = 'Classroom Code:' THEN response ELSE NULL END) AS "Venue",
          max(CASE WHEN question = 'Training Dates:' THEN to_date(response, 'YYYY-MM-DD HH24:MI:SS') ELSE NULL END) AS "Course Date",
          max(CASE WHEN question = 'Training Time (Start):' THEN response ELSE NULL END) AS "Start Time",
          max(CASE WHEN question = 'Training Time (End):' THEN response ELSE NULL END) AS "End Time",
          max(CASE WHEN question = 'Assessment Date:' THEN to_date(response, 'YYYY-MM-DD HH24:MI:SS') ELSE NULL END) AS "Assessment Date",
          max(CASE WHEN question = 'Course Training Duration (Hours):' THEN response ELSE NULL END) AS "Course Duration",
          max(CASE WHEN question = 'Assessment Duration (Hours):' THEN response ELSE NULL END) AS "Assessment Duration"
   FROM RAW
  WHERE form_name IN (
    'In-house Training (Trainer form)',
    'WSQ FSC L1 / WSH L2 (Trainer form)',
    'WSQ FSC L1 Refresher (Trainer form)'
)
   GROUP BY 1, 2, 3, 4),
     
     attendance AS
  (SELECT raw.response_id AS "Trainee Form Response KNID",
          raw.sno AS "Trainee Form Response No",
          fs.user_id,
          raw.submit_date::date AS "Course Date",
          ud.first_name AS "Staff Name",
          ud.designation AS "Designation",
          ud.identifier AS "Batch ID",
   ud.department AS "Department",
          MAX(CASE WHEN raw.question = 'Course Name' THEN raw.response ELSE NULL END) AS "Course",
          MAX(CASE WHEN raw.question = 'Session' THEN response ELSE NULL END) AS "Session",
          MAX(CASE WHEN raw.question = 'Course Code' THEN REPLACE(raw.response, ', ', '') ELSE NULL END) AS "Code"
   FROM RAW
   JOIN fs ON raw.response_id = fs.response_id
   JOIN user_details ud ON fs.user_id = ud.uuid
  WHERE (
     raw.form_name ILIKE 'In-house Training'
  OR raw.form_name ILIKE 'WSQ FSC L1 / WSH L2 (Session %'
  OR raw.form_name ILIKE 'WSQ FSC L1 / WSH L2 (Assessment%'
)
   GROUP BY raw.response_id, raw.sno, raw.submit_date::date, fs.user_id, ud.first_name, ud.designation, ud.identifier,ud.department),
     
     base_non_ob02 AS
  (SELECT ud.last_name AS "EE Code",
          ud.identifier AS "Badge No",
          ud.first_name AS "EE Name",
          ud.division AS "Division",
          ud.job_location AS "Outlet",
   ud.department AS "Department",
          ud.designation AS "Occupation",
          to_date(ud.profile->'otherDetails'->>'DOJ', 'YYYY-MM-DD') AS "Hired Date",
          t."Training ID",
          t.form_id,
          t."Course",
          t."Code",
          t."Trainer",
          t."Session" AS "Trainer Session",
          a."Session" AS "Trainee Session",
          t."Course Date"::date AS "Course Date",
          t."Start Time",
          t."End Time",
          t."Assessment Date",
          t."Course Duration",
          t."Assessment Duration"
   FROM user_details ud
   LEFT OUTER JOIN attendance a ON a.user_id = ud.uuid
   LEFT OUTER JOIN training_list t ON t."Course Date" = a."Course Date"
                              AND t."Code" = a."Code"
   WHERE ud.is_active = 'true'
     AND ud.organization = 'RESE-banyan'),
     
     attendance_ob02 AS
  (SELECT response_id,
          submit_date||'-'||sno AS "Training ID",
          form_id,
          max(CASE WHEN qid = 'section-1'
                   THEN to_timestamp((section_response->>'sentAt')::bigint/1000)
                   ELSE NULL END) AS "Course Date",
          max(CASE WHEN question ILIKE 'Search for the New Hire Full Name as per NRIC 查找员工全名 (依据身份证)%'
                   THEN (raw.response::jsonb)->>'userId'
                   ELSE NULL END) AS user_id,
          COALESCE(MAX(CASE WHEN question ILIKE 'Search for the New Hire Full Name as per NRIC 查找员工全名 (依据身份证)%'
                            THEN (raw.response::jsonb)->>'userName'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE 'New Hire Full Name as per NRIC 员工全名 (依据身份证)%'
                            THEN raw.response
                            ELSE NULL END)) AS name,
          COALESCE(MAX(CASE WHEN question ILIKE 'Search for the New Hire Full Name as per NRIC 查找员工全名 (依据身份证)%'
                            THEN (raw.response::jsonb)->>'designation'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE 'Designation 职位%'
                            THEN raw.response
                            ELSE NULL END)) AS designation,
          COALESCE(MAX(CASE WHEN question ILIKE 'Search for the New Hire Full Name as per NRIC 查找员工全名 (依据身份证)%'
                            THEN (raw.response::jsonb)->>'identifier'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE 'New Hire TMS Batch number 新员工TMS号码%'
                            THEN raw.response
                            ELSE NULL END)) AS identifier,
          max(CASE WHEN q_type = 'location'
                   THEN response
                   ELSE NULL END) AS outlet
   FROM RAW
   WHERE raw.form_name ILIKE '%(OPS) Onboarding Checklist%'
   GROUP BY 1, 2, 3),
     
attendance_soj AS (
SELECT response_id,
          submit_date||'-'||sno AS "Training ID",
          form_id,
  max(CASE WHEN qid = 'section-2'
                   THEN to_timestamp((section_response->>'sentAt')::bigint/1000)
                   ELSE NULL END) AS "Course Date",
  MAX(CASE WHEN question ILIKE '%Name of trainer%'
                            THEN (raw.response::jsonb)->>'userId'
                            ELSE NULL END) AS user_id,
		     MAX(CASE WHEN question ILIKE '%Name of trainer%'
                            THEN (raw.response::jsonb)->>'userName'
                            ELSE NULL END) AS name,
  MAX(CASE WHEN question ILIKE '%Name of trainer%'
                            THEN (raw.response::jsonb)->>'designation'
                            ELSE NULL END) AS designation,
  MAX(CASE WHEN question ILIKE '%Name of trainer%'
                            THEN (raw.response::jsonb)->>'identifier'
                            ELSE NULL END) AS identifier,
  MAX(CASE WHEN question ILIKE '%Name of trainer%'
                            THEN (raw.response::jsonb)->>'location'
                            ELSE NULL END) AS outlet,
  MAX(CASE WHEN q_type = 'multiple_choice'
                            THEN raw.response
                            ELSE NULL END) AS Code
  from RAW
  WHERE raw.form_name ILIKE '%Service On-The-Job-Training%'
  group by 1,2,3
),
	 
attendance_ca01 AS
  (SELECT response_id,
          submit_date||'-'||sno AS "Training ID",
          form_id,
           MAX(CASE WHEN question ILIKE '%Date%'
                            THEN raw.response
                            ELSE NULL END) AS "Course Date",
    COALESCE(MAX(CASE WHEN question ILIKE '%Name of Employee being assess%'
                            THEN (raw.response::jsonb)->>'userName'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE '%Employee Name%'
                            THEN (raw.response::jsonb)->>'userName' 
                            ELSE NULL END),
		MAX(CASE WHEN question ILIKE '%Candidate Name%'
                            THEN (raw.response::jsonb)->>'userName' 
                            ELSE NULL END)) AS name,
   
           COALESCE(MAX(CASE WHEN question ILIKE '%Name of Employee being assess%'
                            THEN (raw.response::jsonb)->>'userId'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE '%Employee Name%'
                            THEN (raw.response::jsonb)->>'userId' 
                            ELSE NULL END),
		MAX(CASE WHEN question ILIKE '%Candidate Name%'
                            THEN (raw.response::jsonb)->>'userId' 
                            ELSE NULL END)) AS user_id,
          COALESCE(MAX(CASE WHEN question ILIKE '%Name of Employee being assess%'
                            THEN (raw.response::jsonb)->>'designation'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE '%Employee Name%'
                            THEN (raw.response::jsonb)->>'designation' 
                            ELSE NULL END),
		MAX(CASE WHEN question ILIKE '%Candidate Name%'
                            THEN (raw.response::jsonb)->>'designation' 
                            ELSE NULL END))  AS designation,
     COALESCE(MAX(CASE WHEN question ILIKE '%Name of Employee being assess%'
                            THEN (raw.response::jsonb)->>'identifier'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE '%Employee Name%'
                            THEN (raw.response::jsonb)->>'identifier' 
                            ELSE NULL END),
		MAX(CASE WHEN question ILIKE '%Candidate Name%'
                            THEN (raw.response::jsonb)->>'identifier' 
                            ELSE NULL END))  AS identifier,
         COALESCE(MAX(CASE WHEN question ILIKE '%Name of Employee being assess%'
                            THEN (raw.response::jsonb)->>'location'
                            ELSE NULL END),
                   MAX(CASE WHEN question ILIKE '%Employee Name%'
                            THEN (raw.response::jsonb)->>'location' 
                            ELSE NULL END),
		MAX(CASE WHEN question ILIKE '%Candidate Name%'
                            THEN (raw.response::jsonb)->>'location' 
                            ELSE NULL END)) AS outlet
   FROM RAW
   WHERE raw.form_name ILIKE '%Confirmation assessment%'
   AND EXISTS (
      SELECT 1
      FROM raw r2
      WHERE r2.response_id = raw.response_id
        AND r2.question ILIKE '%Assessment%'
        AND r2.response ILIKE '%Competent%'
  )
   GROUP BY 1, 2, 3
  ),
	 
	 base_ca01 as
(
 SELECT ud.last_name AS "EE Code",
          a2.identifier AS "Badge No",
          a2.name AS "EE Name",
          ud.division AS "Division",
          coalesce(ud.job_location, a2.outlet) AS "Outlet",
          ud.department AS "Department",
          a2.designation AS "Occupation",
          to_date(ud.profile->'otherDetails'->>'DOJ', 'YYYY-MM-DD') AS "Hired Date",
          "Training ID",
          form_id,
          'Confirmation Assessment' AS "Course",
          'CA01' AS "Code",
          NULL AS "Trainer",
          NULL AS "Trainer Session",
          NULL AS "Trainee Session",
          "Course Date"::date AS "Course Date",
          NULL AS "Start Time",
          NULL AS "End Time",
          NULL::Date AS "Assessment Date",
          NULL AS "Course Duration",
          NULL AS "Assessment Duration"
   FROM attendance_ca01 a2
   LEFT OUTER JOIN user_details ud ON ud.uuid = a2.user_id
) ,
	 
	 
	 base_soj AS (
	   SELECT ud.last_name AS "EE Code",
          a2.identifier AS "Badge No",
          a2.name AS "EE Name",
          ud.division AS "Division",
          coalesce(ud.job_location, a2.outlet) AS "Outlet",
   ud.department AS "Department",
          a2.designation AS "Occupation",
          to_date(ud.profile->'otherDetails'->>'DOJ', 'YYYY-MM-DD') AS "Hired Date",
          "Training ID",
          form_id,
          Code AS "Course",
          Code AS "Code",
          NULL AS "Trainer",
          NULL AS "Trainer Session",
          NULL AS "Trainee Session",
          "Course Date"::date AS "Course Date",
          NULL AS "Start Time",
          NULL AS "End Time",
          NULL::Date AS "Assessment Date",
          NULL AS "Course Duration",
          NULL AS "Assessment Duration"
   FROM attendance_soj a2
   LEFT OUTER JOIN user_details ud ON ud.uuid = a2.user_id
	   ),
	 
	 
     base_ob02 AS
  (SELECT ud.last_name AS "EE Code",
          a2.identifier AS "Badge No",
          a2.name AS "EE Name",
          ud.division AS "Division",
          coalesce(ud.job_location, a2.outlet) AS "Outlet",
  ud.department AS "Department",
          a2.designation AS "Occupation",
          to_date(ud.profile->'otherDetails'->>'DOJ', 'YYYY-MM-DD') AS "Hired Date",
          "Training ID",
          form_id,
          'OB02 - Onboarding Checklist' AS "Course",
          'OB02' AS "Code",
          NULL AS "Trainer",
          NULL AS "Trainer Session",
          NULL AS "Trainee Session",
          "Course Date"::date AS "Course Date",
          NULL AS "Start Time",
          NULL AS "End Time",
          NULL::Date AS "Assessment Date",
          NULL AS "Course Duration",
          NULL AS "Assessment Duration"
   FROM attendance_ob02 a2
   LEFT OUTER JOIN user_details ud ON ud.uuid = a2.user_id),
     
     base AS
  (SELECT *
   FROM base_non_ob02
   UNION ALL
   SELECT *
   FROM base_ob02
  UNION ALL
  select *
  from base_soj
   UNION ALL
  select *
  from base_ca01),
     
     base_2 AS (
       SELECT 
         "EE Code",
         "Badge No",
         TRIM(REGEXP_REPLACE("EE Name", '\s+\d+$', '')) AS "EE Name",
         "Division",
         "Outlet",
         "Occupation",
         "Hired Date",
	   "Department",
         MAX(CASE WHEN "Code" = 'OB01' THEN "Course Date" ELSE NULL END) AS "OB01 - New Hire Orientation",
MAX(CASE WHEN "Code" = 'OB02' THEN "Course Date" ELSE NULL END) AS "OB02 - Onboarding Checklist",
MAX(CASE WHEN "Code" = 'OB03' THEN "Course Date" ELSE NULL END) AS "OB03 - Follow-up Orientation",
MAX(CASE WHEN "Code" = 'WSQFSC01' THEN "Course Date" ELSE NULL END) AS "WSQFSC01 - Food Safety Course Level 1",
MAX(CASE WHEN "Code" = 'WSQFSC02' THEN "Course Date" ELSE NULL END) AS "WSQFSC02 - Food Safety Course Level 1 (Refresher 1)",
MAX(CASE WHEN "Code" = 'WSQWSH01' THEN "Course Date" ELSE NULL END) AS "WSQWSH01 - Workplace Safety Level 2",
MAX(CASE WHEN "Code" = 'NHKTIBB01' THEN "Course Date" ELSE NULL END) AS "NHKTIBB01 - Ichiban Boshi / Sushi Kaiten Station New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTIBB02' THEN "Course Date" ELSE NULL END) AS "NHKTIBB02 - Ichiban Boshi / Sushi Hot Station New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTIBB03' THEN "Course Date" ELSE NULL END) AS "NHKTIBB03 - Ichiban Boshi / Sushi Age Station New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTKJM01' THEN "Course Date" ELSE NULL END) AS "NHKTKJM01 - Kuriya Japanese Market New hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTYYB01' THEN "Course Date" ELSE NULL END) AS "NHKTYYB01 - Yaki Yaki Bo New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTYNG01' THEN "Course Date" ELSE NULL END) AS "NHKTYNG01 - Yakiniku-GO New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTIBT01' THEN "Course Date" ELSE NULL END) AS "NHKTIBT01 - Ichiban Bento New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTSSG01' THEN "Course Date" ELSE NULL END) AS "NHKTSSG01 - Sushi-Go Kaiten Station New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTSSG02' THEN "Course Date" ELSE NULL END) AS "NHKTSSG02 - Sushi-Go Kitchen Station New Hire Kitchen Training",
MAX(CASE WHEN "Code" = 'NHKTIDU01' THEN "Course Date" ELSE NULL END) AS "NHKTIDU01 - Idaten Udon New Hire Kitchen Training",
MAX(CASE WHEN "Code" ILIKE '%S1%' THEN "Course Date" ELSE NULL END) AS "SOJT01 - S1 - Orientation",
MAX(CASE WHEN "Code" ILIKE '%S2%' THEN "Course Date" ELSE NULL END) AS "SOJT02 - S2 - Culture",
MAX(CASE WHEN "Code" ILIKE '%S3%' THEN "Course Date" ELSE NULL END) AS "SOJT03 - S3 - Server",
MAX(CASE WHEN "Code" ILIKE '%S4%' THEN "Course Date" ELSE NULL END) AS "SOJT04 - S4 - Busser",
MAX(CASE WHEN "Code" ILIKE '%S5%' THEN "Course Date" ELSE NULL END) AS "SOJT05 - S5 - Order Taker",
MAX(CASE WHEN "Code" ILIKE '%S6%' THEN "Course Date" ELSE NULL END) AS "SOJT06 - S6 - Ocha",
MAX(CASE WHEN "Code" ILIKE '%S7%' THEN "Course Date" ELSE NULL END) AS "SOJT07 - S7 - Cashier",
MAX(CASE WHEN "Code" ILIKE '%S8%' THEN "Course Date" ELSE NULL END) AS "SOJT08 - S8 - Greeter",
MAX(CASE WHEN "Code" ILIKE '%S9%' THEN "Course Date" ELSE NULL END) AS "SOJT09 - S9 - Opening",
MAX(CASE WHEN "Code" ILIKE '%S10%' THEN "Course Date" ELSE NULL END) AS "SOJT10 - S10 - Closing",
MAX(CASE WHEN "Code" ILIKE '%S11%' THEN "Course Date" ELSE NULL END) AS "SOJT11 - S11 - Retail",
MAX(CASE WHEN "Code" ILIKE '%S12%' THEN "Course Date" ELSE NULL END) AS "SOJT12 - S12 - Toast Slicer",
MAX(CASE WHEN "Code" = 'KOJT01' THEN "Course Date" ELSE NULL END) AS "KOJT01 - K1 - Orientation",
MAX(CASE WHEN "Code" = 'KOJT02' THEN "Course Date" ELSE NULL END) AS "KOJT02 - K2 - Age",
MAX(CASE WHEN "Code" = 'KOJT03' THEN "Course Date" ELSE NULL END) AS "KOJT03 - K3 - Hot",
MAX(CASE WHEN "Code" = 'KOJT04' THEN "Course Date" ELSE NULL END) AS "KOJT04 - K4 - Setter",
MAX(CASE WHEN "Code" = 'KOJT05' THEN "Course Date" ELSE NULL END) AS "KOJT05 - K5 - Sashimi",
MAX(CASE WHEN "Code" = 'KOJT06' THEN "Course Date" ELSE NULL END) AS "KOJT06 - K6 - Sushi",
MAX(CASE WHEN "Code" = 'KOJT07' THEN "Course Date" ELSE NULL END) AS "KOJT07 - K7 - Maki",
MAX(CASE WHEN "Code" = 'KOJT08' THEN "Course Date" ELSE NULL END) AS "KOJT08 - K8 - Noodle",
MAX(CASE WHEN "Code" = 'KOJT09' THEN "Course Date" ELSE NULL END) AS "KOJT09 - K9 - Soup",
MAX(CASE WHEN "Code" = 'KOJT10' THEN "Course Date" ELSE NULL END) AS "KOJT10 - K10 - Meat",
MAX(CASE WHEN "Code" = 'KOJT11' THEN "Course Date" ELSE NULL END) AS "KOJT11 - K11 - Vege",
MAX(CASE WHEN "Code" = 'KOJT12' THEN "Course Date" ELSE NULL END) AS "KOJT12 - K12 - Teppan",
MAX(CASE WHEN "Code" = 'KOJT13' THEN "Course Date" ELSE NULL END) AS "KOJT13 - K13 - Bento",
MAX(CASE WHEN "Code" = 'KOJT14' THEN "Course Date" ELSE NULL END) AS "KOJT14 - K14 - Baker",
MAX(CASE WHEN "Code" = 'KOJT15' THEN "Course Date" ELSE NULL END) AS "KOJT15 - K15 - Sandwich",
MAX(CASE WHEN "Code" = 'KOJT16' THEN "Course Date" ELSE NULL END) AS "KOJT16 - K16 - Kushi Yaki",
MAX(CASE WHEN "Code" = 'KOJT17' THEN "Course Date" ELSE NULL END) AS "KOJT17 - K17 - Showcase",
MAX(CASE WHEN "Code" = 'KOJT18' THEN "Course Date" ELSE NULL END) AS "KOJT18 - K18 - Mixing & Proofing",
MAX(CASE WHEN "Code" = 'KOJT19' THEN "Course Date" ELSE NULL END) AS "KOJT19 - K19 - Garnishing",
MAX(CASE WHEN "Code" = 'KOJT20' THEN "Course Date" ELSE NULL END) AS "KOJT20 - K20 - Soba",
MAX(CASE WHEN "Code" = 'KOJT21' THEN "Course Date" ELSE NULL END) AS "KOJT21 - K21 - Dessert",
MAX(CASE WHEN "Code" = 'MOJT01' THEN "Course Date" ELSE NULL END) AS "MOJT01 - M1 - General Admin",
MAX(CASE WHEN "Code" = 'MOJT02' THEN "Course Date" ELSE NULL END) AS "MOJT02 - M2 - Technology & Equipment",
MAX(CASE WHEN "Code" = 'MOJT03' THEN "Course Date" ELSE NULL END) AS "MOJT03 - M3 - Customer Service Excellence",
MAX(CASE WHEN "Code" = 'MOJT04' THEN "Course Date" ELSE NULL END) AS "MOJT04 - M4 - Effective Shift Management",
MAX(CASE WHEN "Code" = 'MOJT05' THEN "Course Date" ELSE NULL END) AS "MOJT05 - M5 - Health & Safety Compliance",
MAX(CASE WHEN "Code" = 'MOJT06' THEN "Course Date" ELSE NULL END) AS "MOJT06 - M6 - Procurement & Inventory Management",
MAX(CASE WHEN "Code" = 'MOJT07' THEN "Course Date" ELSE NULL END) AS "MOJT07 - M7 - Leadership Transformation",
MAX(CASE WHEN "Code" = 'MOJT08' THEN "Course Date" ELSE NULL END) AS "MOJT08 - M8 - Staff Engagement & Training",
MAX(CASE WHEN "Code" = 'MOJT09' THEN "Course Date" ELSE NULL END) AS "MOJT09 - M9 - Conflict Resolution & Problem Solving",
MAX(CASE WHEN "Code" = 'MOJT10' THEN "Course Date" ELSE NULL END) AS "MOJT10 - M10 - Financial Management",
MAX(CASE WHEN "Code" = 'IHT01' THEN "Course Date" ELSE NULL END) AS "IHT01 - Basic Service Training",
MAX(CASE WHEN "Code" = 'IHT02' THEN "Course Date" ELSE NULL END) AS "IHT02 - Basic Coaching Level 1",
MAX(CASE WHEN "Code" = 'IHT03' THEN "Course Date" ELSE NULL END) AS "IHT03 - Human Relation Skill",
MAX(CASE WHEN "Code" = 'IHT04' THEN "Course Date" ELSE NULL END) AS "IHT04 - Shaping Leaders for tomorrow",
MAX(CASE WHEN "Code" = 'IHT05' THEN "Course Date" ELSE NULL END) AS "IHT05 - Stress Management",
MAX(CASE WHEN "Code" = 'IHT06' THEN "Course Date" ELSE NULL END) AS "IHT06 - Re-DISCover Yourself to Build a More Effective Team",
MAX(CASE WHEN "Code" = 'IHT07' THEN "Course Date" ELSE NULL END) AS "IHT07 - Leading Your Team With Confidence",
MAX(CASE WHEN "Code" = 'IHT08' THEN "Course Date" ELSE NULL END) AS "IHT08 - OJT Blueprint Briefing",
MAX(CASE WHEN "Code" = 'IHT09' THEN "Course Date" ELSE NULL END) AS "IHT09 - Workplace Safety Workshop (With A&C)",
MAX(CASE WHEN "Code" = 'IHT10' THEN "Course Date" ELSE NULL END) AS "IHT10 - Be A Service Coach (Level 2)",
MAX(CASE WHEN "Code" = 'IHT11' THEN "Course Date" ELSE NULL END) AS "IHT11 - Coaching (Level 3)",
MAX(CASE WHEN "Code" = 'IHT12' THEN "Course Date" ELSE NULL END) AS "IHT12 - Train The Trainer",
MAX(CASE WHEN "Code" = 'IHT13' THEN "Course Date" ELSE NULL END) AS "IHT13 - P&L Training",
MAX(CASE WHEN "Code" = 'IHT14' THEN "Course Date" ELSE NULL END) AS "IHT14 - Presenting With Impact",
MAX(CASE WHEN "Code" = 'IHT15' THEN "Course Date" ELSE NULL END) AS "IHT15 - Basic English Class",
MAX(CASE WHEN "Code" = 'IHT16' THEN "Course Date" ELSE NULL END) AS "IHT16 - Advance English Class",
MAX(CASE WHEN "Code" = 'CA01' THEN "Course Date" ELSE NULL END) AS "CA01 - Confirmation Assessment",
MAX(CASE WHEN "Code" = 'A01' THEN "Course Date" ELSE NULL END) AS "A01 - Senior Service Staff Assessment",
MAX(CASE WHEN "Code" = 'A02' THEN "Course Date" ELSE NULL END) AS "A02 - Senior Kitchen Staff Assessment",
MAX(CASE WHEN "Code" = 'A03' THEN "Course Date" ELSE NULL END) AS "A03 - Senior Bakery Staff Assessment",
MAX(CASE WHEN "Code" = 'A04' THEN "Course Date" ELSE NULL END) AS "A04 - Management Trainee (Service) Assessment",
MAX(CASE WHEN "Code" = 'A05' THEN "Course Date" ELSE NULL END) AS "A05 - Management Trainee (Kitchen) Assessment",
MAX(CASE WHEN "Code" = 'A06' THEN "Course Date" ELSE NULL END) AS "A06 - Management Trainee (Baker) Assessment",
MAX(CASE WHEN "Code" = 'A07' THEN "Course Date" ELSE NULL END) AS "A07 - Assistant Manager Assessment",
MAX(CASE WHEN "Code" = 'A08' THEN "Course Date" ELSE NULL END) AS "A08 - Assistant Chef Assessment",
MAX(CASE WHEN "Code" = 'A09' THEN "Course Date" ELSE NULL END) AS "A09 - Restaurant Manager Assessment",
MAX(CASE WHEN "Code" = 'A10' THEN "Course Date" ELSE NULL END) AS "A10 - Chef Assessment",
MAX(CASE WHEN "Code" = 'A11' THEN "Course Date" ELSE NULL END) AS "A11 - Senior Restaurant Manager Assessment",
MAX(CASE WHEN "Code" = 'A12' THEN "Course Date" ELSE NULL END) AS "A12 - Senior Chef Assessment",
MAX(CASE WHEN "Code" = 'EXT01' THEN "Course Date" ELSE NULL END) AS "EXT01 - Responder Plus Programme (RPP)",
MAX(CASE WHEN "Code" = 'EXT02' THEN "Course Date" ELSE NULL END) AS "EXT02 - Food Safety Course L3 (FHO)"
       FROM base
       GROUP BY "EE Code",
                "Badge No",
                TRIM(REGEXP_REPLACE("EE Name", '\s+\d+$', '')),
                "Division",
                "Outlet",
                "Occupation",
                "Hired Date",
	   "Department"
     ) 
SELECT
  b."Badge No",
  max(b."EE Code") as "EE Code" ,
  max(b."EE Name") as "EE Name",
  max(b."Division") as "Division",
  max(b."Outlet") as "Outlet",
  max(b."Occupation") as "Occupation",
  max(b."Department") as "Department",

  -- Hired Date
  max(greatest(r."Hired Date",b."Hired Date")) AS "Hired Date",

  -- OB Courses
MAX(COALESCE(Greatest(r."OB01 - New Hire Orientation", b."OB01 - New Hire Orientation"), r."OB01 - New Hire Orientation", b."OB01 - New Hire Orientation")) AS "OB01 - New Hire Orientation",
MAX(COALESCE(Greatest(r."OB02 - Onboarding Checklist", b."OB02 - Onboarding Checklist"), r."OB02 - Onboarding Checklist", b."OB02 - Onboarding Checklist")) AS "OB02 - Onboarding Checklist",
MAX(COALESCE(Greatest(r."OB03 - Follow-up Orientation", b."OB03 - Follow-up Orientation"), r."OB03 - Follow-up Orientation", b."OB03 - Follow-up Orientation")) AS "OB03 - Follow-up Orientation",

-- WSQ Courses
MAX(COALESCE(Greatest(r."WSQFSC01 - Food Safety Course Level 1", b."WSQFSC01 - Food Safety Course Level 1"), r."WSQFSC01 - Food Safety Course Level 1", b."WSQFSC01 - Food Safety Course Level 1")) AS "WSQFSC01 - Food Safety Course Level 1",
MAX(COALESCE(Greatest(r."WSQFSC02 - Food Safety Course Level 1 (Refresher 1)", b."WSQFSC02 - Food Safety Course Level 1 (Refresher 1)"), r."WSQFSC02 - Food Safety Course Level 1 (Refresher 1)", b."WSQFSC02 - Food Safety Course Level 1 (Refresher 1)")) AS "WSQFSC02 - Food Safety Course Level 1 (Refresher 1)",
MAX(COALESCE(Greatest(r."WSQWSH01 - Workplace Safety Level 2", b."WSQWSH01 - Workplace Safety Level 2"), r."WSQWSH01 - Workplace Safety Level 2", b."WSQWSH01 - Workplace Safety Level 2")) AS "WSQWSH01 - Workplace Safety Level 2",

-- IHT Courses
MAX(COALESCE(Greatest(r."IHT01 - Basic Service Training", b."IHT01 - Basic Service Training"), r."IHT01 - Basic Service Training", b."IHT01 - Basic Service Training")) AS "IHT01 - Basic Service Training",
MAX(COALESCE(Greatest(r."IHT02 - Basic Coaching Level 1", b."IHT02 - Basic Coaching Level 1"), r."IHT02 - Basic Coaching Level 1", b."IHT02 - Basic Coaching Level 1")) AS "IHT02 - Basic Coaching Level 1",
MAX(COALESCE(Greatest(r."IHT03 - Human Relation Skill", b."IHT03 - Human Relation Skill"), r."IHT03 - Human Relation Skill", b."IHT03 - Human Relation Skill")) AS "IHT03 - Human Relation Skill",
MAX(COALESCE(Greatest(r."IHT04 - Shaping Leaders for tomorrow", b."IHT04 - Shaping Leaders for tomorrow"), r."IHT04 - Shaping Leaders for tomorrow", b."IHT04 - Shaping Leaders for tomorrow")) AS "IHT04 - Shaping Leaders for tomorrow",
MAX(COALESCE(Greatest(r."IHT05 - Stress Management", b."IHT05 - Stress Management"), r."IHT05 - Stress Management", b."IHT05 - Stress Management")) AS "IHT05 - Stress Management",
MAX(COALESCE(Greatest(r."IHT06 - Re-DISCover Yourself to Build a More Effective Team", b."IHT06 - Re-DISCover Yourself to Build a More Effective Team"), r."IHT06 - Re-DISCover Yourself to Build a More Effective Team", b."IHT06 - Re-DISCover Yourself to Build a More Effective Team")) AS "IHT06 - Re-DISCover Yourself to Build a More Effective Team",
MAX(COALESCE(Greatest(r."IHT07 - Leading Your Team With Confidence", b."IHT07 - Leading Your Team With Confidence"), r."IHT07 - Leading Your Team With Confidence", b."IHT07 - Leading Your Team With Confidence")) AS "IHT07 - Leading Your Team With Confidence",
MAX(COALESCE(Greatest(r."IHT08 - OJT Blueprint Briefing", b."IHT08 - OJT Blueprint Briefing"), r."IHT08 - OJT Blueprint Briefing", b."IHT08 - OJT Blueprint Briefing")) AS "IHT08 - OJT Blueprint Briefing",
MAX(COALESCE(Greatest(r."IHT09 - Workplace Safety Workshop (With A&C)", b."IHT09 - Workplace Safety Workshop (With A&C)"), r."IHT09 - Workplace Safety Workshop (With A&C)", b."IHT09 - Workplace Safety Workshop (With A&C)")) AS "IHT09 - Workplace Safety Workshop (With A&C)",
MAX(COALESCE(Greatest(r."IHT10 - Be A Service Coach (Level 2)", b."IHT10 - Be A Service Coach (Level 2)"), r."IHT10 - Be A Service Coach (Level 2)", b."IHT10 - Be A Service Coach (Level 2)")) AS "IHT10 - Be A Service Coach (Level 2)",
MAX(b."IHT11 - Coaching (Level 3)")AS "IHT11 - Coaching (Level 3)",
MAX(b."IHT12 - Train The Trainer") AS "IHT12 - Train The Trainer",
MAX(b."IHT13 - P&L Training") AS "IHT13 - P&L Training",
MAX(b."IHT14 - Presenting With Impact") AS "IHT14 - Presenting With Impact",
MAX(b."IHT15 - Basic English Class") AS "IHT15 - Basic English Class",
MAX(b."IHT16 - Advance English Class") AS "IHT16 - Advance English Class",
	 
-- EXT Courses
MAX(COALESCE(Greatest(r."EXT01 - Responder Plus Programme (RPP)", b."EXT01 - Responder Plus Programme (RPP)"), r."EXT01 - Responder Plus Programme (RPP)", b."EXT01 - Responder Plus Programme (RPP)")) AS "EXT01 - Responder Plus Programme (RPP)",
MAX(COALESCE(Greatest(r."EXT02 - Food Safety Course L3 (FHO)", b."EXT02 - Food Safety Course L3 (FHO)"), r."EXT02 - Food Safety Course L3 (FHO)", b."EXT02 - Food Safety Course L3 (FHO)")) AS "EXT02 - Food Safety Course L3 (FHO)",
	 
--SOJT Courses
MAX(b."SOJT01 - S1 - Orientation") AS "SOJT01 - S1 - Orientation",
MAX(b."SOJT02 - S2 - Culture") AS "SOJT02 - S2 - Culture",
MAX(b."SOJT03 - S3 - Server") AS "SOJT03 - S3 - Server",
MAX(b."SOJT04 - S4 - Busser") AS "SOJT04 - S4 - Busser",
MAX(b."SOJT05 - S5 - Order Taker") AS "SOJT05 - S5 - Order Taker",
MAX(b."SOJT06 - S6 - Ocha") AS "SOJT06 - S6 - Ocha",
MAX(b."SOJT07 - S7 - Cashier") AS "SOJT07 - S7 - Cashier",
MAX(b."SOJT08 - S8 - Greeter") AS "SOJT08 - S8 - Greeter",
MAX(b. "SOJT09 - S9 - Opening") AS "SOJT09 - S9 - Opening",
MAX(b."SOJT10 - S10 - Closing") AS "SOJT10 - S10 - Closing",
MAX(b."SOJT11 - S11 - Retail") AS "SOJT11 - S11 - Retail",
MAX(b."SOJT12 - S12 - Toast Slicer") AS "SOJT12 - S12 - Toast Slicer",

--MOJT Courses
MAX(b."MOJT01 - M1 - General Admin") AS "MOJT01 - M1 - General Admin",
MAX(b."MOJT02 - M2 - Technology & Equipment") AS "MOJT02 - M2 - Technology & Equipment",
MAX(b."MOJT03 - M3 - Customer Service Excellence") AS "MOJT03 - M3 - Customer Service Excellence",
 MAX(b."MOJT04 - M4 - Effective Shift Management") AS "MOJT04 - M4 - Effective Shift Management",
MAX(b."MOJT05 - M5 - Health & Safety Compliance") AS "MOJT05 - M5 - Health & Safety Compliance",
MAX(b."MOJT06 - M6 - Procurement & Inventory Management") AS "MOJT06 - M6 - Procurement & Inventory Management",
MAX(b."MOJT07 - M7 - Leadership Transformation") AS "MOJT07 - M7 - Leadership Transformation",
MAX(b."MOJT08 - M8 - Staff Engagement & Training") AS "MOJT08 - M8 - Staff Engagement & Training",
 MAX(b."MOJT09 - M9 - Conflict Resolution & Problem Solving") AS "MOJT09 - M9 - Conflict Resolution & Problem Solving",
MAX(b."MOJT10 - M10 - Financial Management") AS "MOJT10 - M10 - Financial Management",

--A Series
MAX(b."CA01 - Confirmation Assessment") AS "CA01 - Confirmation Assessment",
MAX(b."A01 - Senior Service Staff Assessment") AS "A01 - Senior Service Staff Assessment",
 MAX(b."A02 - Senior Kitchen Staff Assessment") AS "A02 - Senior Kitchen Staff Assessment",
MAX(b."A03 - Senior Bakery Staff Assessment") AS "A03 - Senior Bakery Staff Assessment",
 MAX(b."A04 - Management Trainee (Service) Assessment") AS "A04 - Management Trainee (Service) Assessment",
MAX(b."A05 - Management Trainee (Kitchen) Assessment") AS "A05 - Management Trainee (Kitchen) Assessment",
MAX("A06 - Management Trainee (Baker) Assessment") AS "A06 - Management Trainee (Baker) Assessment",
MAX(b."A07 - Assistant Manager Assessment") AS "A07 - Assistant Manager Assessment",
MAX(b."A08 - Assistant Chef Assessment") AS "A08 - Assistant Chef Assessment",
MAX(b."A09 - Restaurant Manager Assessment") AS "A09 - Restaurant Manager Assessment",
MAX(b."A10 - Chef Assessment") AS "A10 - Chef Assessment",
MAX(b."A11 - Senior Restaurant Manager Assessment") AS "A11 - Senior Restaurant Manager Assessment",
MAX(b."A12 - Senior Chef Assessment") AS "A12 - Senior Chef Assessment",

-- KOJT Courses
MAX(b."KOJT01 - K1 - Orientation") AS "KOJT01 - K1 - Orientation",
MAX(b."KOJT02 - K2 - Age") AS "KOJT02 - K2 - Age",
MAX(b."KOJT03 - K3 - Hot") AS "KOJT03 - K3 - Hot",
MAX(b."KOJT04 - K4 - Setter") AS "KOJT04 - K4 - Setter",
MAX(b."KOJT05 - K5 - Sashimi") AS "KOJT05 - K5 - Sashimi",
MAX(b."KOJT06 - K6 - Sushi") AS "KOJT06 - K6 - Sushi",
MAX(b."KOJT07 - K7 - Maki") AS "KOJT07 - K7 - Maki",
MAX(b."KOJT08 - K8 - Noodle") AS "KOJT08 - K8 - Noodle",
MAX(b."KOJT09 - K9 - Soup") AS "KOJT09 - K9 - Soup",
MAX(b."KOJT10 - K10 - Meat") AS "KOJT10 - K10 - Meat",
MAX(b."KOJT11 - K11 - Vege") AS "KOJT11 - K11 - Vege",
MAX(b."KOJT12 - K12 - Teppan") AS "KOJT12 - K12 - Teppan",
MAX(b."KOJT13 - K13 - Bento") AS "KOJT13 - K13 - Bento",
MAX(b."KOJT14 - K14 - Baker") AS "KOJT14 - K14 - Baker",
MAX(b."KOJT15 - K15 - Sandwich") AS "KOJT15 - K15 - Sandwich",
MAX(b."KOJT16 - K16 - Kushi Yaki") AS "KOJT16 - K16 - Kushi Yaki",
MAX(b."KOJT17 - K17 - Showcase") AS "KOJT17 - K17 - Showcase",
MAX(b."KOJT18 - K18 - Mixing & Proofing") AS "KOJT18 - K18 - Mixing & Proofing",
MAX(b."KOJT19 - K19 - Garnishing") AS "KOJT19 - K19 - Garnishing",
MAX(b."KOJT20 - K20 - Soba") AS "KOJT20 - K20 - Soba",
MAX(b."KOJT21 - K21 - Dessert") AS "KOJT21 - K21 - Dessert",

--NHKT Courses
MAX(b."NHKTIBB01 - Ichiban Boshi / Sushi Kaiten Station New Hire Kitchen Training") AS "NHKTIBB01 - Ichiban Boshi / Sushi Kaiten Station New Hire Kitchen Training",
MAX(b."NHKTIBB02 - Ichiban Boshi / Sushi Hot Station New Hire Kitchen Training") AS "NHKTIBB02 - Ichiban Boshi / Sushi Hot Station New Hire Kitchen Training",
MAX(b."NHKTIBB03 - Ichiban Boshi / Sushi Age Station New Hire Kitchen Training") AS "NHKTIBB03 - Ichiban Boshi / Sushi Age Station New Hire Kitchen Training",
MAX(b."NHKTKJM01 - Kuriya Japanese Market New hire Kitchen Training") AS "NHKTKJM01 - Kuriya Japanese Market New hire Kitchen Training",
 MAX(b."NHKTYYB01 - Yaki Yaki Bo New Hire Kitchen Training") AS "NHKTYYB01 - Yaki Yaki Bo New Hire Kitchen Training",
MAX(b."NHKTYNG01 - Yakiniku-GO New Hire Kitchen Training") AS "NHKTYNG01 - Yakiniku-GO New Hire Kitchen Training",
MAX(b."NHKTIBT01 - Ichiban Bento New Hire Kitchen Training") AS "NHKTIBT01 - Ichiban Bento New Hire Kitchen Training",
MAX(b."NHKTSSG01 - Sushi-Go Kaiten Station New Hire Kitchen Training") AS "NHKTSSG01 - Sushi-Go Kaiten Station New Hire Kitchen Training",
MAX(b."NHKTSSG02 - Sushi-Go Kitchen Station New Hire Kitchen Training") AS "NHKTSSG02 - Sushi-Go Kitchen Station New Hire Kitchen Training",
MAX(b."NHKTIDU01 - Idaten Udon New Hire Kitchen Training") AS "NHKTIDU01 - Idaten Udon New Hire Kitchen Training"

FROM base_2 b
LEFT JOIN res_skills_inventory_archive r
  ON r."EE Code" = b."EE Code"
WHERE b."Occupation" NOT IN ('Store')
  AND b."Badge No" NOT ILIKE '%KN%'
  AND b."Badge No" NOT IN ('-', 'IT SUPPORT', '93263317', 'sdk-user', '6511111374', 
                           'CCC', 'CHQS', 'PM-367', '1121121007', '1234', '6650', '58924')
                           group by 1
ORDER BY b."Badge No"
```

---

## RES Staff Claim Form_Staff Claim List.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, metadata, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions, raw

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `isTotal` -> `is_total` (alias: `is_total AS "isTotal"`)

- `otherText` -> `other_text` (alias: `other_text AS "otherText"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: RES Staff Claim Form
-- Dashboard: Staff Claim List
-- Category: RES
-- Extracted: 2026-01-29 16:58:00
-- ============================================================

WITH forms AS
  (SELECT id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE id = @{{:formId}}),
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
   where submit_date at time zone 'Asia/Singapore' between @{{:startDate}}::timestamp and @{{:endDate}}::timestamp + interval '1 day'
   ORDER BY response_id,
            id DESC),
     fr AS
  (SELECT form_submit_id,
          form_id,
          form_name,
          sno,
          submit_date,
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
     (SELECT form_submit_id,
             form_id,
             form_name,
             sno,
             submit_date,
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
      WHERE question_type = 'table'
        AND base.value->>'isTotal' IS NULL) base1
   CROSS JOIN jsonb_each(base1.value) res),
     RAW AS
  (SELECT fr.sno,
          fd.section_no,
          fd.q_no,
          fd.parent_question,
          fd.question,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response ->> 'status'
              WHEN fd.q_type IN ('dropdown',
                                 'multiple_choice',
                                 'linear_scale') THEN fr.response -> 'selected'->>0
              WHEN fd.q_type IN ('checkboxes') THEN array_to_string(ARRAY
                                                                      (SELECT jsonb_array_elements_text(fr.response->'selected')
                                                                       UNION SELECT CASE
                                                                                        WHEN fr.response->>'otherText' IS NOT NULL THEN fr.response->>'otherText'
                                                                                        ELSE NULL
                                                                                    END), ', ')
              WHEN fd.q_type IN ('date',
                                 'datetime') THEN to_char(to_timestamp((fr.response::bigint)/1000) AT TIME ZONE 'Asia/Singapore', 'YYYY-MM-DD HH24:MI:SS')
              WHEN fd.q_type IN ('long_text_field',
                                 'single_text_field',
                                 'qr_code',
                                 'formula') THEN fr.response->>0
              WHEN fd.q_type ilike 'upload%' THEN (fr.response)->0->>'response'
              WHEN fd.q_type IN ('signature',
                                 'location') THEN fr.response ->> 'name'
              ELSE NULL
          END AS response,
          CASE
              WHEN fd.q_type = 'section' THEN fr.response
              ELSE NULL
          END AS section_response,
          rn,
          form_name,
          fd.form_knid,
          fr.response_id,
          fr.submit_date AT TIME ZONE 'Asia/Singapore' AS submit_date
   FROM final_definition fd
   JOIN fr ON fr.qid = fd.qid
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
            12
   ORDER BY 1,
            2,
            3),
			metadata as (
			  select form_name, form_knid, response_id, submit_date, sno, max(CASE
               WHEN question = 'Claimant' THEN section_response->'sender'->>'userName'
               ELSE NULL
           END) AS "Claimant",
		   max(CASE
               WHEN question = 'Claimant' THEN section_response->'sender'->>'department'
               ELSE NULL
           END) AS "Department"
			  from raw
			  group by 1, 2, 3, 4, 5)
SELECT md.form_knid AS "Form KNID",
       md.form_name AS "Form Name",
       md.response_id AS "Submission KNID",
       md.sno AS "Submission No",
       md.submit_date AS "Submitted At",
	   md."Claimant",
	   md."Department",
       raw.rn AS "Item No",
      max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Date%' THEN response
               ELSE NULL
           END) AS "Car Transport Date",
       max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Location (From)%' THEN response
               ELSE NULL
           END) AS "Car Transport From",
       max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Location (To)%' THEN response
               ELSE NULL
           END) AS "Car Transport To",
       sum(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Distance%' THEN response::numeric
               ELSE NULL
           END) AS "Car Mileage",
       sum(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Total Amount%' THEN response::numeric
               ELSE NULL
           END) AS "Car Amount",
       max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Motorbike)%'
                    AND question ILIKE 'Date%' THEN response
               ELSE NULL
           END) AS "Motorbike Transport Date",
       max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Motorbike)%'
                    AND question ILIKE 'Location (From)%' THEN response
               ELSE NULL
           END) AS "Motorbike Transport From",
       max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Motorbike)%'
                    AND question ILIKE 'Location (To)%' THEN response
               ELSE NULL
           END) AS "Motorbike Transport To",
       sum(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Motorbike)%'
                    AND question ILIKE 'Distance%' THEN response::numeric
               ELSE NULL
           END) AS "Motorbike Mileage",
       sum(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Motorbike)%'
                    AND question ILIKE 'Total Amount%' THEN response::numeric
               ELSE NULL
           END) AS "Motorbike Amount",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Category%' THEN response
               ELSE NULL
           END) AS "Expense Category",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Claim description%' THEN response
               ELSE NULL
           END) AS "Claim Description",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Claim purpose%' THEN response
               ELSE NULL
           END) AS "Claim Purpose",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Receipt Date%' THEN response
               ELSE NULL
           END) AS "Receipt Date",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Cost center%' THEN response
               ELSE NULL
           END) AS "Cost Center",
       sum(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Amount (Before GST)%' THEN response::numeric
               ELSE NULL
           END) AS "Amount Before GST",
       sum(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'GST%' THEN response::numeric
               ELSE NULL
           END) AS "GST",
       sum(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Sub Total%' THEN response::numeric
               ELSE NULL
           END) AS "Sub Total",
       max(CASE
               WHEN parent_question ILIKE 'Claim Details%'
                    AND question ILIKE 'Receipt' THEN response
               ELSE NULL
           END) AS "Receipt",
		   max(CASE
               WHEN parent_question ILIKE 'Transport Mileage Claim (Car)%'
                    AND question ILIKE 'Car Plate' THEN response
               ELSE NULL
           END) AS "Car Plate"
FROM RAW
join metadata md on raw.response_id = md.response_id
GROUP BY 1,
         2,
         3,
         4,
         5,
         6, 7, 8
ORDER BY 2,
         5,
         6
```

---

## REs weekly report needed for Preventive Maintenance Team_RES PM Master Sheet - Weekly Parts.sql

**Tables referenced:** data_team.res_pm_report

**Original Query:**

```sql
-- Data Source: REs weekly report needed for Preventive Maintenance Team
-- Dashboard: RES PM Master Sheet - Weekly Parts
-- Category: RES
-- Extracted: 2026-01-29 16:54:07
-- ============================================================

 select * from data_team.res_pm_report
```

---
