# Chili Padi

> Auto-generated on 2026-03-04 08:13

**Total queries:** 2

---

## Chili Padi Driver Payment Report_Chili Padi Driver Payment Report.sql

**Tables referenced:** adhoc, delivery, final_adhoc, final_regular, form_responses, form_submissions, frt, fs, full_data, jsonb_each, organizations, pincodes, qd, qdnt, qdt, question_definitions, responses, section_data, td

**Columns needing snake_case conversion:**

- `endDate` -> `end_date` (alias: `end_date AS "endDate"`)

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `startDate` -> `start_date` (alias: `start_date AS "startDate"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Chili Padi Driver Payment Report
-- Dashboard: Chili Padi Driver Payment Report
-- Category: Chili Padi
-- Extracted: 2026-01-29 16:55:46
-- ============================================================

/*
    Current form: -NhAHGUSccJMc3JW4QIe, -Ni3ii6Rj1clB7KVtcKD.,-OP-Jd03TZdGHs6ps5t-,-OPcV-WJAMmVkS7TqeO6,-OPe3WKjAz68d1G7g2sa Find all and add more if needed
    Current question Ids to check: -NhAHGUSccJMc3JW4QIf, -Ni3ii6Rj1clB7KVtcKE. We are using question ids to check the date range filter since they want to filter date range based on the response of this question.
*/ WITH td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations o
   WHERE id = 'Chilli-Padi-Holding-fireworks'), /*Form Submission Data*/ fs AS
  (SELECT DISTINCT ON (response_id) fs.organization,
                      form_id,
                      id,
                      response_id AS submission_knid,
                      sno
   FROM form_submissions fs
   JOIN td ON td.organization = fs.organization /* get all the form submit ID first then use that to filter out the desire response*/
   WHERE fs.id IN
       (SELECT form_submit_id
        FROM form_responses fr,
             td
        WHERE question_id IN ('-NhAHGUSccJMc3JW4QIf',
                              '-Ni3ii6Rj1clB7KVtcKE',
                              '-OP-Jd03TZdGHs6ps5t1',
                              '-OPcV-WJAMmVkS7TqeO6',
                              '-OPcV-WKMW1bIMJ0UHB_',
                              '-OPe3WKjAz68d1G7g2sc')
          AND (to_timestamp(response::varchar::bigint/1000) + td.diff) BETWEEN @{{:startDate}}::timestamp AND @{{:endDate}}::timestamp + interval '1 day' - interval '1 second' )
   ORDER BY response_id,
            submit_date DESC, id DESC), /*Get Questions Information and Definition*/ qdnt AS
  (/*Non Table type Questions in Forms*/ SELECT nugget_id AS form_knid,
                                                replace(section_id, 'section-', '')::integer AS section_no,
                                                section_id,
                                                question_id AS parent_qid,
                                                question_type AS parent_q_type,
                                                question_id AS qid,
                                                sqno::integer*10000 AS q_no,
                                                question_type AS q_type,
                                                question AS question
   FROM question_definitions qd
   WHERE nugget_id IN
       (SELECT DISTINCT form_id
        FROM fs)
     AND question_type NOT IN ('table')),
                                                                                     qdt AS
  (/*Table type Questions in Forms - SqNo will be in decimals for sub questions*/ SELECT nugget_id AS form_knid,
                                                                                         replace(section_id, 'section-', '')::integer AS section_no,
                                                                                         section_id,
                                                                                         question_id AS parent_qid,
                                                                                         question_type AS parent_q_type,
                                                                                         def.key AS qid,
                                                                                         sqno::integer*10000+(def.value->>'order')::integer AS q_no,
                                                                                         def.value->>'question_type' AS q_type,
                                                                                                     def.value->>'question' AS question
   FROM question_definitions qd
   CROSS JOIN jsonb_each(definition -> 'questions') def
   WHERE nugget_id IN
       (SELECT DISTINCT form_id
        FROM fs)
     AND qd.question_type IN ('table')),
                                                                                     qd AS
  (SELECT *
   FROM qdnt
   UNION SELECT *
   FROM qdt),
                                                                                     frt AS
  (SELECT base.form_submit_id,
          qdt.parent_qid,
          qdt.qid,
          qdt.q_type,
          base.ordinality*10000 AS response_row,
          data.value AS response
   FROM
     (SELECT form_submit_id,
             question_id AS parent_qid,
             rows.ordinality AS
      ORDINALITY,
             rows.value AS value
      FROM fs
      JOIN form_responses fr ON fs.id = fr.form_submit_id,
                                jsonb_array_elements(fr.response) WITH
      ORDINALITY AS ROWS
      WHERE fr.question_type = 'table') base
   CROSS JOIN jsonb_each(base.value) DATA
   JOIN qdt ON data.key = qdt.qid),
                                                                                     responses AS
  (/*Responses for questions where multiple options are present*/SELECT form_submit_id,
                                                                        question_id AS parent_qid,
                                                                        question_id AS qid,
                                                                        question_type AS q_type,
                                                                        selected.ordinality*10000 AS response_row,
                                                                        selected.value->>0 AS response
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id,
                             jsonb_array_elements(fr.response -> 'selected') WITH
   ORDINALITY AS selected
   WHERE fr.question_type IN ('dropdown',
                              'multiple_choice',
                              'checkboes',
                              'linear_scale')
   UNION /*Responses for questions where only one data entry is possible*/ SELECT form_submit_id,
                                                                                  question_id AS parent_qid,
                                                                                  question_id AS qid,
                                                                                  question_type AS q_type,
                                                                                  10000 AS response_row,
                                                                                  CASE
                                                                                      WHEN question_type = 'date' THEN fr.response::varchar
                                                                                      ELSE fr.response->>0
                                                                                  END AS response
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type NOT IN ('nested',
                                  'section',
                                  'na',
                                  'audit',
                                  'table',
                                  'upload_file',
                                  'upload_video_file',
                                  'upload_mixed_file',
                                  'location',
                                  'user')
     AND fr.response -> 'selected' IS NULL
   UNION /* Responses for upload images, videos, files*/ SELECT form_submit_id,
                                                                question_id AS parent_qid,
                                                                question_id AS qid,
                                                                question_type AS q_type,
                                                                url.ordinality*10000 AS response_row,
                                                                (url.value->>'response')::varchar AS response
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id,
                             jsonb_array_elements(fr.response) WITH
   ORDINALITY AS url
   WHERE fr.question_type ILIKE 'upload%'
   UNION /* Responses for location type questions*/ SELECT form_submit_id,
                                                           question_id AS parent_qid,
                                                           question_id AS qid,
                                                           question_type AS q_type,
                                                           10000 AS response_row,
                                                           fr.response->>'name' AS response
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type IN ('location')
   UNION /* Responses for user type questions*/ SELECT form_submit_id,
                                                       question_id AS parent_qid,
                                                       question_id AS qid,
                                                       question_type AS q_type,
                                                       10000 AS response_row,
                                                       fr.response->'selected'->0->>'userName' AS response
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type IN ('user')
   UNION /*Responses for table type questions. Given table type can have all other sub types, we will have to write more nested queries*/
     (SELECT form_submit_id,
             parent_qid,
             qid,
             q_type,
             frt.response_row+(selected.ordinality-1) AS response_row,
             (selected.value)::varchar AS response
      FROM frt,
           jsonb_array_elements(CASE jsonb_typeof(frt.response->'selected')
                                    WHEN 'array' THEN frt.response ->'selected'
                                    ELSE '[]'
                                END) WITH
      ORDINALITY AS selected
      WHERE frt.q_type IN ('dropdown',
                           'multiple_choice',
                           'checkboes',
                           'linear_scale')
      UNION SELECT form_submit_id,
                   parent_qid,
                   qid,
                   q_type,
                   frt.response_row AS response_row,
                   CASE
                       WHEN q_type = 'date' THEN frt.response::varchar
                       ELSE frt.response->>0
                   END AS response
      FROM frt
      WHERE frt.q_type NOT IN ('nested',
                               'section',
                               'audit',
                               'table',
                               'upload_file',
                               'upload_video_file',
                               'upload_mixed_file',
                               'location',
                               'user')
        AND frt.response -> 'selected' IS NULL
      UNION -- for upload images, videos, files
 SELECT form_submit_id,
        parent_qid,
        qid,
        q_type,
        frt.response_row+(url.ordinality-1) AS response_row,
        (url.value->>'response')::varchar AS response
      FROM frt,
           jsonb_array_elements(CASE jsonb_typeof(frt.response)
                                    WHEN 'array' THEN frt.response
                                    ELSE '[]'
                                END) WITH
      ORDINALITY AS url
      WHERE frt.q_type ILIKE 'upload%'
      UNION -- for location type questions
 SELECT form_submit_id,
        parent_qid,
        qid,
        q_type,
        frt.response_row AS response_row,
        frt.response->>'name' AS response
      FROM frt
      WHERE frt.q_type = 'location')), /*Get Meta on when each stage was submitted, and by who*/ section_data AS
  (SELECT form_submit_id,
          question_id AS section_id,
          CASE
              WHEN response->>'status' IN ('sent',
                                           'submitted') THEN 'submitted'
              ELSE response->>'status'
          END AS section_status,
          response->'sender'->>'userName' AS submitted_by,
                               response->'sender'->>'identifier' AS submitter_emp_id,
                                                    response->'sender'->>'userId' AS submitter_knid,
                                                                         response->'sender'->>'location' AS submitter_location,
                                                                                              response->'sender'->>'department' AS submitter_department,
                                                                                                                   response->'sender'->>'designation' AS submitter_designation,
                                                                                                                                        to_timestamp((response->>'sentAt')::bigint/1000) AS submitted_timestamp
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE question_id ILIKE 'section%'
     AND question_type = 'na'),
                                                                                                 full_data AS
  ( SELECT fs.organization,
           fs.form_id,
           fs.submission_knid,
           fs.sno,
           qd.section_no,
           qd.section_id,
           initcap(section_data.section_status) AS section_status,
           qd.parent_qid AS parent_question_id,
           CASE
               WHEN qd.parent_q_type = 'upload_file' THEN 'image'
               WHEN qd.parent_q_type = 'upload_mixed_file' THEN 'file'
               WHEN qd.parent_q_type = 'upload_video_file' THEN 'video'
               ELSE qd.parent_q_type
           END AS parent_question_type,
           qd.q_no AS question_no,
           qd.qid AS question_id,
           qd.question,
           CASE
               WHEN qd.q_type = 'upload_file' THEN 'image'
               WHEN qd.q_type = 'upload_mixed_file' THEN 'file'
               WHEN qd.q_type = 'upload_video_file' THEN 'video'
               ELSE qd.q_type
           END AS question_type,
           responses.response_row AS response_number,
           responses.response,
           section_data.submitted_by AS responded_by,
           section_data.submitter_knid AS responder_knid,
           section_data.submitter_emp_id AS responder_emp_id,
           section_data.submitter_location AS responder_location,
           section_data.submitter_department AS responder_department,
           section_data.submitter_designation AS responder_designation,
           section_data.submitted_timestamp + td.diff AS responded_timestamp
   FROM fs
   JOIN qd ON fs.form_id = qd.form_knid
   JOIN responses ON fs.id = responses.form_submit_id
   AND qd.parent_qid = responses.parent_qid
   AND qd.qid = responses.qid
   JOIN section_data ON qd.section_id = section_data.section_id
   AND fs.id = section_data.form_submit_id
   JOIN td ON fs.organization = td.organization),
                                                                                                 delivery AS
  ( SELECT submission_knid,
           responded_by,
           responder_knid,
           responder_emp_id,
           max(CASE
                   WHEN question = 'Date of Delivery' THEN (to_timestamp(response::bigint/1000) + td.diff)::date
                   ELSE NULL
               END) AS date_of_delivery,
           max(CASE
                   WHEN question = 'Lunch / Dinner' THEN response
                   ELSE NULL
               END) AS lunch_or_dinner,
           max(CASE
                   WHEN question = 'Driver Name' THEN response
                   ELSE NULL
               END) AS driver_name
   FROM full_data
   JOIN td ON full_data.organization = td.organization
   WHERE question IN ('Date of Delivery',
                      'Lunch / Dinner',
                      'Driver Name')
   GROUP BY 1,
            2,
            3,
            4),
                                                                                                 pincodes AS
  (SELECT submission_knid,
          response::numeric AS pincode
   FROM full_data
   WHERE question ILIKE '%Postal Code'),
                                                                                                 final_regular AS
  (SELECT d.submission_knid,
          coalesce(d.driver_name, d.responded_by) AS responded_by,
          d.responder_knid,
          d.responder_emp_id,
          d.date_of_delivery,
          d.lunch_or_dinner,
          p.pincode,
          CASE
              WHEN pincode BETWEEN 460000 AND 529999 THEN 6.00
              WHEN pincode BETWEEN 580000 AND 759999
                   OR pincode BETWEEN 110000 AND 139999 THEN 7.00
              WHEN pincode NOT BETWEEN 010000 AND 829999 THEN 0
              ELSE 6.30
          END AS ideal_price,
          count(p.pincode) AS pincode_count
   FROM delivery d
   LEFT OUTER JOIN pincodes p ON d.submission_knid = p.submission_knid
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8
   ORDER BY 5,
            2,
            7),
                                                                                                 adhoc AS
  (SELECT submission_knid,
          response
   FROM full_data
   WHERE question = 'Price of this adhoc delivery'),
                                                                                                 final_adhoc AS
  (SELECT d.submission_knid,
          d.date_of_delivery,
          d.lunch_or_dinner,
          count(CASE
                    WHEN a.response IS NOT NULL THEN a.response
                    ELSE NULL
                END) AS adhoc_delivery_count,
          sum(a.response::numeric) AS adhoc_cost
   FROM delivery d
   JOIN adhoc a ON d.submission_knid = a.submission_knid
   GROUP BY 1,
            2,
            3)
SELECT fr.date_of_delivery AS "Date of Delivery",
       fr.responded_by AS "Driver Name",
       fr.responder_emp_id AS "Driver ID",
       fr.lunch_or_dinner AS "Shift",
       sum(CASE
               WHEN ideal_price = 6.00
                    AND pincode_count = 1 THEN pincode_count
               ELSE 0.00
           END) + count(CASE
                            WHEN ideal_price = 6.00
                                 AND pincode_count > 1 THEN pincode
                            ELSE NULL
                        END) AS "No of SGD 6.00 Deliveries",
       sum(CASE
               WHEN ideal_price = 6.00
                    AND pincode_count > 1 THEN pincode_count-1
               ELSE 0.00
           END) AS "No of SGD 3.00 Deliveries",
       sum(CASE
               WHEN ideal_price = 6.30
                    AND pincode_count = 1 THEN pincode_count
               ELSE 0.00
           END) + count(CASE
                            WHEN ideal_price = 6.30
                                 AND pincode_count > 1 THEN pincode
                            ELSE NULL
                        END) AS "No of SGD 6.30 Deliveries",
       sum(CASE
               WHEN ideal_price = 6.30
                    AND pincode_count > 1 THEN pincode_count-1
               ELSE 0.00
           END) AS "No of SGD 3.15 Deliveries",
       sum(CASE
               WHEN ideal_price = 7.00
                    AND pincode_count = 1 THEN pincode_count
               ELSE 0.00
           END) + count(CASE
                            WHEN ideal_price = 7.00
                                 AND pincode_count > 1 THEN pincode
                            ELSE NULL
                        END) AS "No of SGD 7.00 Deliveries",
       sum(CASE
               WHEN ideal_price = 7.00
                    AND pincode_count > 1 THEN pincode_count-1
               ELSE 0.00
           END) AS "No of SGD 3.50 Deliveries",
       sum(CASE
               WHEN pincode_count = 1 THEN ideal_price
               WHEN pincode_count > 1 THEN (pincode_count+1)*ideal_price*0.50
               ELSE 0.00
           END) AS "Regular Delivery Price",
       fa.adhoc_delivery_count AS "Adhoc Delivery Count",
       fa.adhoc_cost AS "Adhoc Delivery Price",
       count(distinct(fr.submission_knid)) AS "No of Form Submissions",
       count(distinct(fr.submission_knid))*0.50 AS "Form Submission Incentive",
       sum(CASE
               WHEN pincode_count = 1 THEN ideal_price
               WHEN pincode_count > 1 THEN (pincode_count+1)*ideal_price*0.50
               ELSE 0.00
           END) + CASE
                      WHEN fa.adhoc_cost IS NOT NULL THEN fa.adhoc_cost
                      ELSE 0
                  END + count(distinct(fr.submission_knid))*0.50 AS "Total Price"
FROM final_regular fr
LEFT OUTER JOIN final_adhoc fa ON fr.submission_knid = fa.submission_knid
AND fr.date_of_delivery = fa.date_of_delivery
AND fr.lunch_or_dinner = fa.lunch_or_dinner
GROUP BY 1,
         2,
         3,
         4,
         12,
         13
ORDER BY 1,
         2,
         4 DESC
```

---

## course_chilli_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: course_chilli
-- Dashboard: Learn
-- Category: Chili Padi
-- Extracted: 2026-01-29 16:55:28
-- ============================================================

WITH user_acl AS
  (SELECT ud.organization,
          ud.uuid,
          ud.first_name||' '||ud.last_name AS emp_name,
          ud.identifier AS emp_id,
          ud.division,
          ud.sub_division,
          ud.job_location,
          ud.department,
          ud.designation,
          ud.job_type
   FROM user_details ud
   WHERE organization = 'Chilli-Padi-Holding-fireworks'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
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
               AND ug1.is_active = TRUE))
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10),
     td AS
  (SELECT id AS organization,
          tzoffset, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'Chilli-Padi-Holding-fireworks'),
     latest_share_ids AS
  (SELECT DISTINCT ON (nugget_id,
                       user_id) nugget_id,
                      share_id,
                      user_id,
                      created_at AS sent_at
   FROM analytics.nuggets_user_share_requests nusr
   JOIN user_acl ud ON nusr.user_id = ud.uuid
   WHERE created_at BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   ORDER BY 1,
            3,
            created_at DESC),
     latest_course_shares AS
  (SELECT lsi.user_id,
          lsi.nugget_id AS course_id,
          lsi.share_id,
          lsi.sent_at,
          1 AS seq
   FROM latest_share_ids lsi
   JOIN public.courses c ON lsi.nugget_id = c.id
   WHERE c.organization = 'Chilli-Padi-Holding-fireworks'
   UNION ALL SELECT lsi.user_id,
                    ljc.course_id,
                    lsi.share_id,
                    lsi.sent_at,
                    (seq::int)+1 AS seq
   FROM latest_share_ids lsi
   JOIN public.learning_journey_courses ljc ON lsi.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id),
     latest_received AS
  (SELECT ra.user_id,
          ra.nugget_id,
          ra.share_id,
          ra.created_at AS received_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_share_ids lsi ON ra.user_id = lsi.user_id
   AND ra.nugget_id = lsi.nugget_id
   AND ra.share_id = lsi.share_id
   WHERE ra.event_id NOT IN (1,
                             7)),
     latest_course_received AS
  (SELECT lr.user_id,
          lr.nugget_id AS course_id,
          lr.share_id,
          min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.courses c ON lr.nugget_id = c.id
   WHERE c.organization = 'Chilli-Padi-Holding-fireworks'
   GROUP BY 1,
            2,
            3
   UNION ALL SELECT lr.user_id,
                    ljc.course_id,
                    lr.share_id,
                    min(lr.received_at) AS received_at
   FROM latest_received lr
   JOIN public.learning_journey_courses ljc ON lr.nugget_id = ljc.learning_journey_id
   JOIN public.courses c ON ljc.course_id = c.id
   WHERE c.organization = 'Chilli-Padi-Holding-fireworks'
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = 'Chilli-Padi-Holding-fireworks'
   GROUP BY 1,
            2),
     cards_consumed AS
  (SELECT ra.user_id,
          lcs.seq,
          ra.course_id,
          ra.share_id,
          lc.card_id,
          ra.lang,
          min(ra.created_at) AS consumed_at
   FROM analytics.nugget_analytics_raw ra
   JOIN latest_course_shares lcs ON ra.user_id = lcs.user_id
   AND ra.course_id = lcs.course_id
   AND ra.share_id = lcs.share_id
   JOIN cards lc ON lc.course_id = ra.course_id
   AND lc.card_id = ra.nugget_id
   WHERE ra.event_id = 3
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   ORDER BY 1,
            2,
            3,
            4,
            5),
     progress AS
  (SELECT cc.user_id,
          cc.course_id,
          cc.share_id,
          count(distinct(cc.card_id)) AS consumed_count
   FROM cards_consumed cc
   GROUP BY 1,
            2,
            3),
     final_quiz_cards AS
  (SELECT DISTINCT ON (c.id) c.id AS course_id,
                      lc.id AS quizcard_id,
                      jsonb_array_length(lc.payload -> 'questions') AS qCount,
                      (lc.settings->>'passMark')::numeric AS pass_mark
   FROM public.lesson_cards lc
   JOIN public.lessons l ON lc.lesson_id = l.id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = 'Chilli-Padi-Holding-fireworks'
     AND lc.type = 'quiz'
   ORDER BY c.id,
            l.seq DESC, lc.seq DESC),
     latest_attempt AS
  (SELECT qr.user_id,
          qr.course_id,
          qr.share_id,
          qr.card_id,
          qr.question_id,
          max(attempt) AS latestAttempt
   FROM quiz.quiz_responses qr
   JOIN latest_course_shares lcs ON qr.user_id = lcs.user_id
   AND qr.course_id = lcs.course_id
   AND qr.share_id = lcs.share_id
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5),
     final_scores AS
  (SELECT la.user_id,
          la.course_id,
          la.share_id,
          qc.quizcard_id,
          qc.pass_mark,
          qc.qcount,
          count(distinct(CASE
                             WHEN qr.is_correct = TRUE THEN qr.question_id
                             ELSE NULL
                         END))::numeric AS correct_count
   FROM latest_attempt la
   JOIN quiz.quiz_responses qr ON la.user_id = qr.user_id
   AND la.course_id = qr.course_id
   AND la.share_id = qr.share_id
   AND la.card_id = qr.card_id
   AND la.question_id = qr.question_id
   AND la.latestAttempt = qr.attempt
   JOIN final_quiz_cards qc ON qr.course_id = qc.course_id
   AND qr.card_id = qc.quizcard_id
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     quiz_status AS
  (SELECT fs.user_id,
          fs.course_id,
          fs.share_id,
          count(distinct(quizcard_id)) AS no_of_quizzes,
          count(distinct(CASE
                             WHEN correct_count >= pass_mark THEN quizcard_id
                             ELSE NULL
                         END)) AS passed_quizzes,
          sum(correct_count) *100 / sum(qcount) AS score_in_pct
   FROM final_scores fs
   GROUP BY 1,
            2,
            3)
SELECT ud.organization,
       c.name as course_name,
       ud.emp_name,
       ud.emp_id,
       ud.division,
       ud.sub_division,
       ud.job_location AS LOCATION,
       ud.department,
       ud.designation,
       ud.job_type,
       lcs.sent_at + td.diff AS shared_at,
       max(cc.consumed_at + td.diff) AS completed_at,
       CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards) THEN 'Completed'
           WHEN c.total_cards > 0
                AND p.consumed_count > 0
                AND p.consumed_count < c.total_cards THEN 'In Progress'
           WHEN c.total_cards > 0
                AND (p.consumed_count = 0
                     OR p.consumed_count IS NULL) THEN 'Not Started'
           ELSE NULL
       END AS course_status,
      CASE
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes = 0 THEN 'NA'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes >= s.no_of_quizzes THEN 'Pass'
           WHEN (c.total_cards > 0
                 AND p.consumed_count = c.total_cards)
                AND s.no_of_quizzes > 0
                AND s.passed_quizzes < s.no_of_quizzes THEN 'Fail'
           ELSE NULL
       END AS quiz_status,
       s.score_in_pct,
       lcs.course_id AS course_knid,
       ud.uuid AS user_knid/*,
       (p.consumed_count::numeric) / (c.total_cards::numeric) AS completion_pct,
       upper(cc.lang) AS LANGUAGE*/
FROM user_acl ud
JOIN latest_course_shares lcs ON lcs.user_id = ud.uuid
LEFT OUTER JOIN latest_course_received lcr ON lcs.user_id = lcr.user_id
AND lcs.course_id = lcr.course_id
AND lcs.share_id = lcr.share_id
LEFT OUTER JOIN progress p ON lcs.user_id = p.user_id
AND lcs.course_id = p.course_id
AND lcs.share_id = p.share_id
LEFT OUTER JOIN cards_consumed cc ON lcs.user_id = cc.user_id
AND lcs.course_id = cc.course_id
AND lcs.share_id = cc.share_id
LEFT OUTER JOIN quiz_status s ON lcs.user_id = s.user_id
AND lcs.course_id = s.course_id
AND lcs.share_id = s.share_id
LEFT OUTER JOIN public.courses c ON lcs.course_id = c.id
LEFT OUTER JOIN td ON ud.organization = td.organization
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
         13,
         14,
         15,
         16,
         17
ORDER BY 1,
         2,
         13,
         5,
         6,
         7,
         3
```

---
