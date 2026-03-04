# Dev Testing

> Auto-generated on 2026-03-04 08:13

**Total queries:** 12

---

## AI Verification Demo in KN Prod_AI Image Verification.sql

**Tables referenced:** form_responses, form_submissions, fs, image_response, loc, nuggets, question_definitions, user_details

**Columns needing snake_case conversion:**

- `nuggetCategories` -> `nugget_categories` (alias: `nugget_categories AS "nuggetCategories"`)


**Original Query:**

```sql
-- Data Source: AI Verification Demo in KN Prod
-- Dashboard: AI Image Verification
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:57:08
-- ============================================================

WITH fs AS
  (SELECT DISTINCT ON (fs.response_id) response_id,
                      fs.id,
                      form_id,
                      n.title,
                      sno,
                      submit_date AT TIME ZONE 'Asia/Singapore' AS submit_date, --ud.first_name||' '||ud.last_name AS submitter,
 fs.user_id,
 fs.location
   FROM form_submissions fs
   LEFT OUTER JOIN nuggets n ON fs.form_id = n.id --left outer JOIN user_details ud ON fs.user_id = ud.uuid

   WHERE n.details->'nuggetCategories'->>'5e6478a8e441048ff4cc83a5598b4f25' = 'true'
     AND n.is_deleted = 'false'
   ORDER BY response_id,
            id DESC),
     loc AS
  (SELECT fs.response_id,
          coalesce(fr.response->>'name', fs.location) AS LOCATION
   FROM fs
   JOIN form_responses fr ON fs.id = fr.form_submit_id
   WHERE fr.question_type = 'location'
   GROUP BY 1,
            2),
     image_response AS
  (SELECT *
   FROM form_responses fr
   WHERE question_type IN ('upload_file',
                           'upload_image')
     AND form_submit_id IN
       (SELECT id
        FROM fs))
SELECT fs.title AS "Form",
       fs.sno AS "Submission No",
       loc.location AS "Store",
       fs.submit_date AS "Submitted At",
       qd.question AS "Checkpoint",
       elements->>'response' AS "Image URL",
                  CASE
                      WHEN ai_verify_passed = TRUE THEN 'Verified'
                      ELSE 'Rejected'
                  END AS "Status",
                  CASE
                      WHEN ai_verify_passed = TRUE THEN 1
                      ELSE 0
                  END AS "Verified Count",
                  fs.response_id AS "Submission KNID",
                  fs.user_id AS "Submitter KNID",
                  fs.form_id AS "Form KNID"
FROM image_response fr
JOIN fs ON fr.form_submit_id = fs.id
JOIN loc ON fs.response_id = loc.response_id
JOIN question_definitions qd ON fr.question_id = qd.question_id
AND fs.form_id = qd.nugget_id,
    jsonb_array_elements(fr.response) AS elements
ORDER BY 1,
         2,
         3,
         4,
         5
```

---

## Course Report-copy_1729125105_Learn.sql

**Tables referenced:** analytics.nugget_analytics_raw, analytics.nuggets_user_share_requests, cards, cards_consumed, final_quiz_cards, final_scores, latest_attempt, latest_course_received, latest_course_shares, latest_received, latest_share_ids, organizations, progress, public.courses, public.learning_journey_courses, public.lesson_cards, public.lessons, quiz.quiz_responses, quiz_status, td, user_acl, user_details, user_groups

**Columns needing snake_case conversion:**

- `latestAttempt` -> `latest_attempt` (alias: `latest_attempt AS "latestAttempt"`)

- `passMark` -> `pass_mark` (alias: `pass_mark AS "passMark"`)

- `qCount` -> `q_count` (alias: `q_count AS "qCount"`)


**Original Query:**

```sql
-- Data Source: Course Report-copy_1729125105
-- Dashboard: Learn
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:10
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
   WHERE organization = @{{:OrganizationParameter}}
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
   WHERE id = @{{:OrganizationParameter}}),
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
   WHERE c.organization = @{{:OrganizationParameter}}
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
   WHERE c.organization = @{{:OrganizationParameter}}
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
   WHERE c.organization = @{{:OrganizationParameter}}
   GROUP BY 1,
            2,
            3),
     cards AS
  (SELECT l.course_id,
          lc.id AS card_id
   FROM public.lesson_cards lc
   JOIN public.lessons l ON l.id = lc.lesson_id
   JOIN public.courses c ON l.course_id = c.id
   WHERE c.organization = @{{:OrganizationParameter}}
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
   WHERE c.organization = @{{:OrganizationParameter}}
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

## Instamart Impact Daily Report-copy_1735005782_IMPACT Report Daily Emailer.sql

**Tables referenced:** active_locations_pods, base_forms, filtered_lfr, form_responses, form_submissions, forms, fr, fs, lfr, lm, looker.locations_map_orange_mart, public.form_reminders, public.location_form_reminders, public.locations, public.nuggets

**Original Query:**

```sql
-- Data Source: Instamart Impact Daily Report-copy_1735005782
-- Dashboard: IMPACT Report Daily Emailer
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:57:18
-- ============================================================

WITH lm AS (
  SELECT * 
  FROM looker.locations_map_orange_mart
),
active_locations_pods AS (
  SELECT id, location_name 
  FROM public.locations l
  WHERE l.organization = 'swiggy-mart-whirlpool' 
    AND l.is_active = true
    AND regexp_replace(l.location_name, '([0-9]+).*', '\1') IN (SELECT pod_id FROM lm)
),
base_forms AS (
  SELECT 
    id,
    regexp_replace(title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '') AS title
  FROM public.nuggets
  WHERE is_deleted = false
    AND id IN (
      '-OC37vPYSTaYpa6rNk7y', '-OB4CVmT_YAytFR2fty7', '-OB4xcGu1NqT84w0lAWQ', '-O9U1GGkwZWt_Vs6okDW', '-OB4z2473dKeZ34McBIV',
      '-OB4zWin85ZrjPUjH0RV', '-OB4zm7TVqXaKK3J0vAX', '-OB5-5PzkC26eek0Bk-1', '-OB5-Q1oguPmrJlRlBnH', '-OBPR5RTpUGaHJsVJFZH',
      '-OB5-kLCkZWwy65-Ek6h', '-OB505iZAJ8wJ0zZxcFM', '-OB525WEclHOXV6JYtJn', '-OB51wGxzBWxhStUNtqv', '-OB52IvLT3rJTvAM7wLT',
      '-OB52TuE5WfUdYkJdmrE', '-OB52jx59NEjUjPBixqy', '-OB52ttmR2iTHizVPXwE', '-OB55VCsN1K47jdOc-N2', '-OB5622pYYZHwe2fCC1W',
      '-OB56cNfUDEhTxUPhJ4S', '-OB56mQetguLSxb-mTv6', '-OB57bk-9BG-rX7wAceu', '-OAIJndZxwVht8750Zc6', '-OAIsM27j29lvnM9Br5O',
      '-OAIx7irPIBo-9cKLh_y', '-OALkeIDkVHTQtxyEVne', '-OAvN4-5jv-XvXPhQEeM', '-OAvPLR9pQLC_wvRpX0Y', '-OAvQgdymG5aSTHcrVQR',
      '-OAvVUTteJqBgqdYYJgq', '-OAvVhmAOQCKn9Ln_JC-', '-OAvVvs7yNtCfVItyUr4', '-OAvWIJh_dc1cSU8uJgq', '-OAvWV2dPw9S0L6KWBlb',
      '-OAvb8LGJYxjlH_YrSRb', '-OAvWvojjYv0Cxl9uTai', '-OBAL68W_bLx6qrgfVjm', '-OB0_uO6Q4lBeasMViQT', '-OB56yx-t8HP7oBY0JQX',
      '-OB0_OEwgHSkOq9KOr7P', '-OBZLlW2pRYqtVoLwUJq', '-OBdNIXxFdIQrGnbqESi', '-OBdNs7lzEaEIhrrlwHk', '-OC351d72Tg3nF69kF0Z',
      '-O5vnwzkiszWtqSl6QGF', '-O73HoSK3DHguZxXg_q0'
    )
),
forms AS (
  SELECT n.id, bf.title
  FROM public.nuggets n
  join base_forms bf on bf.title = regexp_replace(n.title, '\s\(\d{2}-[A-Za-z]{3}-\d{4} to \d{2}-[A-Za-z]{3}-\d{4}\)$', '')
  WHERE n.classification_type = 'form'
    AND n.organization = 'swiggy-mart-whirlpool'
    AND n.is_deleted = false
),
filtered_lfr AS (
  SELECT 
    lfr.reminder_id,
    lfr.reminded_at,
    lfr.reminder_window_end,
    lfr.form_response_id,
    lfr.responded_at,
    lfr.location_id,
    fr.organization,
    fr.tz_offset,
    fr.form_id,
    fn.title,
    alp.location_name AS "location"
  FROM public.form_reminders fr 
  JOIN forms fn on fn.id = fr.form_id 
  JOIN public.location_form_reminders lfr ON fr.id = lfr.reminder_id
  JOIN active_locations_pods alp ON lfr.location_id = alp.id
  WHERE to_timestamp(lfr.reminded_at/1000) at time zone 'Asia/Kolkata' between date_trunc('Day', current_timestamp at time zone 'Asia/Kolkata' - interval '1 day') and date_trunc('Day', current_timestamp at time zone 'Asia/Kolkata')),
lfr AS (
  SELECT 
    lfr.reminder_id,
    lfr.organization,
    lfr.tz_offset AS tz_offset_sec,
    lfr.form_id,
    lfr.title,
    lfr.location,
    regexp_replace(lfr."location", '([0-9]+).*', '\1') as pod_id,
    (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date AS reminded_date,
    row_number() OVER (
      PARTITION BY lfr.form_id, alp.location_name, (to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset)::date
      ORDER BY to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset
    ) AS reminder_no,
    to_timestamp(lfr.reminded_at/1000) + interval '1 sec'*lfr.tz_offset AS reminded_at,
    to_timestamp(lfr.reminder_window_end/1000) + interval '1 sec'*lfr.tz_offset AS reminder_window_end,
    lfr.form_response_id,
    CASE
      WHEN lfr.responded_at = 0 THEN NULL
      ELSE to_timestamp(lfr.responded_at/1000) + interval '1 sec'*lfr.tz_offset
    END AS responded_at
  FROM filtered_lfr lfr
  JOIN active_locations_pods alp ON lfr.location_id = alp.id
),
fs AS (
  SELECT fs.*
  FROM form_submissions fs
  WHERE fs.submit_date at time zone 'Asia/Kolkata' between date_trunc('Day', current_timestamp at time zone 'Asia/Kolkata' - interval '1 day') and date_trunc('Day', current_timestamp at time zone 'Asia/Kolkata')
    AND fs.form_id IN (select id from forms)
    and fs.location in (select location_name from active_locations_pods)
),
fr AS (
  SELECT 
    fs.form_id,
    fs.submit_date at time zone 'Asia/Kolkata' as submit_date,
    fs.response_id,
    fr.response->>'name' AS LOCATION,
    row_number() OVER (
      PARTITION BY fs.form_id, (fs.submit_date AT TIME ZONE 'Asia/Kolkata')::date, fr.response->>'name'
      ORDER BY fs.submit_date
    ) AS submission_no
  FROM fs
  JOIN form_responses fr ON fs.id = fr.form_submit_id
  WHERE fr.question_type = 'location'
    AND regexp_replace(fr.response->>'name', '([0-9]+).*', '\1') IN (SELECT pod_id FROM lm)
)
SELECT 
  lfr.organization AS "Organization",
  lm.cluster AS "Cluster",
  lm.city AS "City",
  coalesce(lm.pod_id, lfr.pod_id) AS "Pod ID",
  lm.pod_name AS "Pod Name",
  lm.com AS "COM",
  lm.dch AS "DCH",
  (lfr.reminded_at)::date AS "Date",
  lfr.form_id AS "Routine KNID",
  lfr.title AS "Routine Name",
  lfr.reminded_at AS "Reminded At",
  lfr.reminder_window_end as "Due At",
  CASE
    WHEN (lfr.reminded_at)::TIME BETWEEN '06:00:01' AND '12:00:01' THEN '1 - Morning'
    WHEN (lfr.reminded_at)::TIME BETWEEN '12:00:01' AND '20:00:01' THEN '2 - Afternoon'
    ELSE '3 - Night'
  END AS "Shift",
  CASE
    WHEN lfr.form_response_id IS NOT NULL THEN 'Compliant'
    WHEN fr.response_id IS NULL THEN 'Missed'
    ELSE 'Done Late'
  END AS "Status",
  CASE
    WHEN lfr.form_response_id IS NOT NULL THEN 1
    WHEN fr.response_id IS NULL THEN 0
    ELSE 0.5
  END AS "Compliance Score",
  CASE
    WHEN coalesce(lfr.form_response_id, fr.response_id) IS NULL THEN 0.0
    ELSE 1.0
  END AS "Completion Score",
  coalesce(lfr.form_response_id, fr.response_id) AS "Submission KNID"
FROM lfr
LEFT OUTER JOIN fr ON fr.form_id = lfr.form_id
  AND (fr.submit_date)::date = (lfr.reminded_at)::date
  AND fr.location = lfr.location
  AND fr.submission_no = lfr.reminder_no
LEFT OUTER JOIN lm ON lfr.pod_id = lm.pod_id
GROUP BY 
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
ORDER BY 
  11 DESC, 10, 1, 2, 3, 4
```

---

## KNUat-16_Users List.sql

**Tables referenced:** public.user_details

**Original Query:**

```sql
-- Data Source: KNUat-16
-- Dashboard: Users List
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:28
-- ============================================================

select * from public.user_details
```

---

## Kitopi Routine Compliance-copy_1724729876_Test Kitopi Compliance.sql

**Tables referenced:** base, form_compliance, location_acl, location_map, location_off_days, nuggets, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Kitopi Routine Compliance-copy_1724729876
-- Dashboard: Test Kitopi Compliance
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:24
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
     AND is_active = 'true'
     AND job_location NOT IN ('KNOW',
                              'HQ',
                              'Head Office',
                              'All')
     AND job_location NOT ILIKE 'Head Office%'
     AND (
            (SELECT is_super_admin
             FROM user_details
             WHERE uuid = '2CnoAWPZf7LApMqFaiuiFo')
          OR uuid IN
            (SELECT DISTINCT user_id
             FROM user_groups ug1
             WHERE ug1.group_id IN
                 (SELECT group_id
                  FROM user_groups ug2
                  WHERE ug2.user_id = '2CnoAWPZf7LApMqFaiuiFo'
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse')
   ORDER BY job_location,
            created_at ASC),
     location_off_days AS
  (SELECT 'KUW CK1' AS LOCATION,
          'Mon' AS off_day
   UNION SELECT 'BAH CK' AS LOCATION,
                'Wed' AS off_day
   UNION SELECT 'KSA CK1' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA CK2' AS LOCATION,
                'Thu' AS off_day
   UNION SELECT 'KUW Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Bahrain Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Riyadh Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA Nakheel CK' AS LOCATION,
                'Fri' AS off_day),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     base AS
  (SELECT DISTINCT ON (fc.organization,
                       split_part(n.title, ' - ', 1),
                       fc.job_location, (fc.reminded_at + td.diff)) fc.organization AS "Organization",
                      (fc.reminded_at + td.diff)::date AS "Date",
                      to_char(fc.reminded_at + td.diff, 'Dy') AS "Reminded Day",
                      location_map.country AS "Country",
                      location_map.team AS "Team",
   location_map.cluster as "Cluster",
   					  fc.job_location AS "Location",
                      split_part(n.title, ' - ', 1) AS "Routine Name",
                      row_number() OVER (PARTITION BY (fc.reminded_at + td.diff)::date,
                                                      split_part(n.title, ' - ', 1),
                                                      fc.job_location
                                         ORDER BY (fc.reminded_at + td.diff)) AS "Routine #",
                      (fc.reminded_at + td.diff) AS "Reminded At",
                                        (fc.responded_at + td.diff) AS "Responded At",
                                        CASE
                                            WHEN fc.responded_at IS NULL or fc.responded_at < '1970-01-01 01:00:00' THEN 0
                                            ELSE 1
                                        END AS "Compliance",
                                        fc.response_id AS "Submission KNID"
   FROM form_compliance fc
   JOIN location_acl ON fc.job_location = location_acl.job_location
    JOIN td ON td.organization = fc.organization
    JOIN nuggets n ON fc.form_id = n.id
    JOIN location_map ON fc.job_location = location_map.job_location
     WHERE fc.organization ='kitopi-pegasus'
     AND fc.reminded_At + td.diff BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   ORDER BY fc.organization,
            split_part(n.title, ' - ', 1),
            fc.job_location, (fc.reminded_at + td.diff), fc.responded_at)
SELECT base.*
FROM base
LEFT OUTER JOIN location_off_days lod ON base."Location" = lod.location
AND base."Reminded Day" = lod.off_day
WHERE lod.location IS NULL
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
         12, 13
		 ORDER by 1, 4, 5, 6, 7, 2, 10, 8
```

---

## Maintenance Ticket Management-copy_1705496334-copy_1709030164_Testing for Akhil Training.sql

**Tables referenced:** RAW, final_definition, form_responses, form_submissions, forms, fr, fs, jsonb_Each, jsonb_each, nuggets, qd_non_table_non_logic, qd_non_table_with_logic, qd_table, qdntwl_prework, question_definitions

**Columns needing snake_case conversion:**

- `sentAt` -> `sent_at` (alias: `sent_at AS "sentAt"`)

- `userName` -> `user_name` (alias: `user_name AS "userName"`)


**Original Query:**

```sql
-- Data Source: Maintenance Ticket Management-copy_1705496334-copy_1709030164
-- Dashboard: Testing for Akhil Training
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:59:26
-- ============================================================

WITH /* Get Form List*/ forms AS
  (SELECT organization,
          id AS form_knid,
          title AS form_name
   FROM nuggets n
   WHERE title ilike '%-Maintenance Request Form%'), /*Get Questions Information and Definition*/ qd_non_table_non_logic AS
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
            3)
SELECT sno AS "Ticket ID",
       max(CASE
               WHEN section_no = 1
                    AND q_no = 0 THEN to_timestamp((section_response ->> 'sentAt')::bigint/1000) AT TIME ZONE 'Asia/Dubai'
               ELSE NULL
           END) AS "Raised At",
       max(CASE
               WHEN section_no = 4
                    AND q_no = 10000
                    AND response ILIKE 'Yes' THEN '4 - Closed'
               WHEN section_no = 3
                    AND q_no = 40000
                    AND response ILIKE 'Yes' THEN '3 - Work Complete'
               WHEN section_no = 3
                    AND q_no = 40000
                    AND response ILIKE 'NO' THEN '3 - Work Incomplete'
               WHEN section_no = 2
                    AND q_no = 0
                    AND response IN ('submitted', 'sent', 'approved') THEN '2 - Work Pending'
               WHEN section_no = 1
                    AND q_no = 0
                    AND response IN ('submitted', 'sent', 'approved') THEN '1 - Response Pending'
               ELSE '0 - Pending'
           END) AS "Status",
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
               WHEN section_no = 1
                    AND question = 'Severity' THEN response
               ELSE NULL
           END) AS "Severity",
       max(substring(form_name, position('(' IN form_name)+1, length(form_name)-position('(' IN form_name)-1)) AS "Category",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Scan Equipment QR Code' THEN response
               ELSE NULL
           END) AS "Equipment",
       max(CASE
               WHEN section_no = 1
                    AND question = 'Share details about the issue' THEN response
               ELSE NULL
           END) AS "Details",
       max(CASE
               WHEN section_no = 3
                    AND question = 'Details of work done' THEN response
               ELSE NULL
           END) AS "Action Taken",
       max(CASE
               WHEN section_no = 3
                    AND question = 'Cost of work done' THEN response::numeric
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
GROUP BY 1
ORDER BY 1,
         3 DESC,
         2
```

---

## Shift Report v2_Attendance v2.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Shift Report v2
-- Dashboard: Attendance v2
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:59:02
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
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
and shift_attendance."Scheduled Start Time" > @{{:StartDate}}
and shift_attendance."Scheduled Start Time" < @{{:EndDate}}
```

---

## Shift Report-copy_1720602804_Attendance with Cache.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Shift Report-copy_1720602804
-- Dashboard: Attendance with Cache
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:59:02
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
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
```

---

## Shift Report-copy_1720696118_Attendance v3.sql

**Tables referenced:** location_acl, organizations, shift_attendance, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: Shift Report-copy_1720696118
-- Dashboard: Attendance v3
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:59:01
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
SELECT shift_attendance."Shift ID",
shift_attendance."UUID",
shift_attendance."Employee Name",
shift_attendance."Employee ID",
shift_attendance."Designation",
shift_attendance."Department",
shift_attendance."Division",
shift_attendance."Sub Division",
shift_attendance."Home Location",
shift_attendance."Job Type",
shift_attendance."organization",
shift_attendance."Employee Status",
(shift_attendance."Scheduled Start Time" + td.diff) as "Scheduled Start Time",
(shift_attendance."Scheduled End Time" + td.diff) as "Scheduled End Time",
shift_attendance."Shift Location",
shift_attendance."Scheduled Break Hours",
(shift_attendance."Actual Clockin Time" + td.diff) as "Actual Clockin Time",
(shift_attendance."Actual Clockout Time" + td.diff) as "Actual Clockout Time",
shift_attendance."Clockin Beacon",
shift_attendance."Clockin Geofence",
shift_attendance."ci_qr_location_id",
shift_attendance."Clockout Beacon",
shift_attendance."Clockout Geofence",
shift_attendance."co_qr_location_id",
shift_attendance."Actual Work Duration",
shift_attendance."Actual Break Hours",
shift_attendance."Status",
shift_attendance."Scheduled Count",
shift_attendance."Leave Count",
shift_attendance."Present Count",
shift_attendance."Late Count",
shift_attendance."Absent Count",
shift_attendance."Clockin QR Location",
shift_attendance."Clockout QR Location"
FROM shift_attendance
JOIN location_acl ON shift_attendance."Shift Location" = location_acl.job_location
join td on shift_attendance."organization" = td.organization
where shift_attendance."organization" = @{{:OrganizationParameter}}
and extract (epoch from shift_attendance."Scheduled Start Time") > @{{:StartDate}}
and extract (epoch from shift_attendance."Scheduled Start Time") < @{{:EndDate}}
```

---

## TEST Kitopi Routine Compliance_TEST Routine Compliance (Large).sql

**Tables referenced:** base, form_compliance, location_acl, location_map, location_off_days, nuggets, organizations, td, user_details, user_groups

**Original Query:**

```sql
-- Data Source: TEST Kitopi Routine Compliance
-- Dashboard: TEST Routine Compliance (Large)
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:27
-- ============================================================

WITH location_acl AS
  (SELECT DISTINCT job_location
   FROM user_details
   WHERE organization = 'kitopi-pegasus'
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
                  WHERE ug2.user_id = @{{:UuidParameter}}
                    AND ug2.has_access = TRUE)
               AND ug1.is_active = TRUE))),
     location_map AS
  (SELECT DISTINCT ON (job_location) job_location,
                      division AS country,
                      sub_division AS team,
   designation as cluster
   FROM user_details
   WHERE is_active = 'true'
     AND organization = 'kitopi-pegasus'
     AND job_type IN ('CK',
                      'SK',
                      'Kitchen',
                      'Warehouse')
   ORDER BY job_location,
            created_at ASC),
     location_off_days AS
  (SELECT 'KUW CK1' AS LOCATION,
          'Mon' AS off_day
   UNION SELECT 'BAH CK' AS LOCATION,
                'Wed' AS off_day
   UNION SELECT 'KSA CK1' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA CK2' AS LOCATION,
                'Thu' AS off_day
   UNION SELECT 'KUW Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Bahrain Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'Riyadh Warehouse' AS LOCATION,
                'Fri' AS off_day
   UNION SELECT 'KSA Nakheel CK' AS LOCATION,
                'Fri' AS off_day),
     td AS
  (SELECT id AS organization, interval '1 min'*tzoffset AS diff
   FROM organizations
   WHERE id = 'kitopi-pegasus'),
     base AS
  (SELECT DISTINCT ON (fc.organization,
                       split_part(n.title, ' - ', 1),
                       fc.job_location, (fc.reminded_at + td.diff)) fc.organization AS "Organization",
                      (fc.reminded_at + td.diff)::date AS "Date",
                      to_char(fc.reminded_at + td.diff, 'Dy') AS "Reminded Day",
                      location_map.country AS "Country",
                      location_map.team AS "Team",
   location_map.cluster as "Cluster",
   					  fc.job_location AS "Location",
                      split_part(n.title, ' - ', 1) AS "Routine Name",
                      row_number() OVER (PARTITION BY (fc.reminded_at + td.diff)::date,
                                                      split_part(n.title, ' - ', 1),
                                                      fc.job_location
                                         ORDER BY (fc.reminded_at + td.diff)) AS "Routine #",
                      (fc.reminded_at + td.diff) AS "Reminded At",
                                        (fc.responded_at + td.diff) AS "Responded At",
                                        CASE
                                            WHEN fc.responded_at IS NULL THEN 0
                                            ELSE 1
                                        END AS "Compliance",
                                        fc.response_id AS "Submission KNID"
   FROM form_compliance fc
   JOIN location_acl ON fc.job_location = location_acl.job_location
   JOIN location_map ON fc.job_location = location_map.job_location
   JOIN td ON td.organization = fc.organization
   JOIN nuggets n ON fc.form_id = n.id
   WHERE fc.organization ='kitopi-pegasus'
     AND fc.reminded_At + td.diff BETWEEN @{{:Date Range.START}}::TIMESTAMP AND @{{:Date Range.END}}::TIMESTAMP + interval '1 day'
   ORDER BY fc.organization,
            split_part(n.title, ' - ', 1),
            fc.job_location, (fc.reminded_at + td.diff), fc.responded_at)
SELECT base.*
FROM base
LEFT OUTER JOIN location_off_days lod ON base."Location" = lod.location
AND base."Reminded Day" = lod.off_day
WHERE lod.location IS NULL
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
         12, 13
		 ORDER by 1, 4, 5, 6, 7, 2, 10, 8
```

---

## Talabat SKU Param Details-copy_1724729900_Test Talabat Audits.sql

**Tables referenced:** add_sku, add_sku_barcode_q, add_sku_notes_q, add_sku_notes_r, add_sku_param_q, add_sku_param_r, all_sku_metadata, details, forms, fq, fr, fr_mod, fs, lq, metadata, notes_q, notes_r_with_null, param_agg, param_q, param_r, param_r_with_null, public.form_nuggets, public.form_questions, public.form_responses, public.form_submissions, scores, sku_barcode, sku_barcode_q, sku_details_q, sku_final, sku_q, sku_status

**Columns needing snake_case conversion:**

- `formID` -> `form_id` (alias: `form_id AS "formID"`)

- `formId` -> `form_id` (alias: `form_id AS "formId"`)

- `groupID` -> `group_id` (alias: `group_id AS "groupID"`)

- `groupId` -> `group_id` (alias: `group_id AS "groupId"`)

- `groupTitle` -> `group_title` (alias: `group_title AS "groupTitle"`)

- `groupType` -> `group_type` (alias: `group_type AS "groupType"`)

- `questionID` -> `question_id` (alias: `question_id AS "questionID"`)

- `questionId` -> `question_id` (alias: `question_id AS "questionId"`)

- `questionTitle` -> `question_title` (alias: `question_title AS "questionTitle"`)

- `questionType` -> `question_type` (alias: `question_type AS "questionType"`)

- `responseId` -> `response_id` (alias: `response_id AS "responseId"`)

- `rowId` -> `row_id` (alias: `row_id AS "rowId"`)

- `rowIdX` -> `row_id_x` (alias: `row_id_x AS "rowIdX"`)

- `startedAt` -> `started_at` (alias: `started_at AS "startedAt"`)

- `submissionsRefId` -> `submissions_ref_id` (alias: `submissions_ref_id AS "submissionsRefId"`)

- `submittedAt` -> `submitted_at` (alias: `submitted_at AS "submittedAt"`)

- `submittedBy` -> `submitted_by` (alias: `submitted_by AS "submittedBy"`)

- `tzOffset` -> `tz_offset` (alias: `tz_offset AS "tzOffset"`)

- `userId` -> `user_id` (alias: `user_id AS "userId"`)


**Original Query:**

```sql
-- Data Source: Talabat SKU Param Details-copy_1724729900
-- Dashboard: Test Talabat Audits
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:24
-- ============================================================

WITH forms AS
  (SELECT id AS formId,
          title
   FROM public.form_nuggets
   WHERE id IN ('-O3gqjLNcu_eM3LWfdpA',
                '-O3gs9NRAyVE8d4OTAri',
                '-O3gsd9wQID4JlQ9cL6F',
                '-O3gt7YnulgoHDIDErN1',
                '-O3gtc_uriHQojyDFvgl',
                '-O3guAzhGWctofpKNg2t',
                '-O3gugNeYHEtQ9Bv_Gh6',
                '-O3gmEPo9i_u4ZwfCA9T',
                '-O3gv94NVLIdahrw2Cjy',
                '-O3gvf5ZlolkCtNKpty2',
                '-O3gw6c0zdl1r14klDhr',
                '-O3gwXrtXxvmMP39zH81')),
     fq AS
  (SELECT fq.*
   FROM public.form_questions fq
   JOIN forms ON forms.formId = fq.formId),
     fs AS
  (SELECT fs.*
   FROM public.form_submissions fs
   JOIN forms ON forms.formId = fs.formId
   AND fs.startedAt BETWEEN cast(@{{:Date Range.START}} AS TIMESTAMP) + interval 240 MINUTE AND cast(@{{:Date Range.END}} AS TIMESTAMP) + interval 1680 MINUTE),
     fr AS
  (SELECT fr.*,
          fq.groupId,
          fq.groupType,
          fq.groupTitle
   FROM public.form_responses fr
   JOIN fs ON fs.id = fr.submissionsRefId
   JOIN fq ON fs.formID = fq.formId
   AND fr.questionId = fq.questionId),
     lq AS
  (SELECT fq.formId,
          fq.questionId
   FROM fq
   WHERE questionType = 'location'),
     metadata AS
  (SELECT fs.responseId,
          fs.formId,
          fs.sno,
          json_extract_scalar(fs.details, '$.submittedAt') AS submitted_epoch,
          json_extract_scalar(fs.details, '$.userId') AS initiator_uuid,
          timestamp_add(fs.submittedAt, interval cast(json_value(fs.details, '$.tzOffset') AS int) SECOND) AS submittedAt,
          json_value(fr.response, '$.name') AS store
   FROM lq
   JOIN fs ON lq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = lq.questionId),
     sku_q AS
  (SELECT fq.formId,
          REGEXP_EXTRACT(fq.questionTitle, r'^(.*?):') AS sku,
          fq.questionId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE '%SKU Status'
     AND questionType = 'multiple_choice'
   GROUP BY 1,
            2,
            3,
            4),
     sku_status AS
  (SELECT fs.formId,
          fs.responseId,
          sq.sku,
          json_value(fr.response.selected, '$.0') AS sku_status
   FROM sku_q sq
   JOIN fs ON sq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = sq.questionId),
     sku_barcode_q AS
  (SELECT sq.formId,
          sq.sku,
          fq.questionId
   FROM fq
   JOIN sku_q sq ON fq.groupId LIKE concat(sq.questionId, '~%')
   WHERE questionTitle = 'Scan Barcode'
     AND questionType = 'qr_code' ),
     sku_barcode AS
  (SELECT fr.responseId,
          fr.formId,
          q.sku,
          json_extract_scalar(fr.response) AS barcode
   FROM sku_barcode_q q
   JOIN fr ON q.formId = fr.formId
   AND fr.questionID = q.questionId),
     add_sku_barcode_q AS
  (SELECT fq.formId,
          fq.questionId,
          fq.groupId,
          fq.seq
   FROM fq
   WHERE questionTitle LIKE 'Scan Barcode'
     AND questionType = 'qr_code'
     AND groupTitle = 'Additional SKUs'
     AND groupType = 'table'
   GROUP BY 1,
            2,
            3,
            4),
     add_sku AS
  (SELECT fs.formId,
          fs.responseId,
          asbq.groupId,
          json_extract_scalar(fr.response) AS sku,
          json_extract_scalar(fr.response) AS barcode,
          'Additional' AS sku_status,
          fr.rowIdX AS rowId
   FROM add_sku_barcode_q asbq
   JOIN fs ON asbq.formId = fs.formId
   JOIN fr ON fs.id = fr.submissionsRefId
   AND fr.questionID = asbq.questionId
   AND fr.groupId = asbq.groupId),
     all_sku_metadata AS
  (SELECT sku_status.formId,
          sku_status.responseId,
          sku_status.sku,
          sku_barcode.barcode,
          sku_status.sku_status
   FROM sku_status
   LEFT OUTER JOIN sku_barcode ON sku_status.formID = sku_barcode.formId
   AND sku_status.responseId = sku_barcode.responseId
   AND sku_status.sku = sku_barcode.sku
   UNION ALL SELECT formId,
                    responseId,
                    sku,
                    barcode,
                    sku_status
   FROM add_sku),
     sku_details_q AS
  (SELECT sq.formId,
          sq.sku,
          fq.questionId
   FROM fq
   JOIN sku_q sq ON fq.groupId LIKE concat(sq.questionId, '~%')
   WHERE questionTitle = 'SKU Details'
     AND questionType = 'table' ),
     param_q AS
  (SELECT sdq.formId,
          sdq.sku,
          fq.questionTitle AS param,
          fq.questionId AS qid,
          fq.groupId
   FROM fq
   JOIN sku_details_q sdq ON fq.groupId = sdq.questionId
   WHERE fq.questionType IN ('dropdown',
                             'multiple_choice')),
     notes_q AS
  (SELECT sdq.formId,
          sdq.sku,
          fq.questionTitle AS param,
          fq.questionId AS qid,
          fq.groupId
   FROM fq
   JOIN sku_details_q sdq ON fq.groupId = sdq.questionId
   WHERE fq.questionTitle = 'Inspector Notes'
     AND questionType = 'long_text_field'),
     add_sku_param_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionType IN ('dropdown',
                             'multiple_choice')
     AND fq.groupTitle = 'Additional SKUs'
     AND fq.groupType = 'table'),
     add_sku_notes_q AS
  (SELECT fq.formId,
          fq.questionTitle AS param,
          fq.questionId AS qid
   FROM fq
   WHERE fq.questionTitle = 'Inspector Notes'
     AND questionType = 'long_text_field'
     AND fq.groupTitle = 'Additional SKUs'
     AND fq.groupType = 'table' ),
     add_sku_param_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_param_q.param,
          1 AS sample_no,
          json_value(fr.response['selected'], '$.0') AS response
   FROM add_sku_param_q
   JOIN fr ON add_sku_param_q.formId = fr.formId
   AND add_sku_param_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     add_sku_notes_r AS
  (SELECT fr.formId,
          fr.responseId,
          add_sku.sku,
          add_sku_notes_q.param,
          1 AS sample_no,
          json_extract_scalar(fr.response) AS response
   FROM add_sku_notes_q
   JOIN fr ON add_sku_notes_q.formId = fr.formId
   AND add_sku_notes_q.qid = fr.questionId
   JOIN add_sku ON add_sku.formId = fr.formId
   AND add_sku.responseId = fr.responseId
   AND add_sku.groupID = fr.groupId
   AND add_sku.rowId = fr.rowIdX
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6),
     fr_mod AS
  (SELECT fr.formId,
          fr.responseId,
          fr.questionId,
          arr,
          row_number() over(PARTITION BY fr.responseId, fr.formId, fr.questionid) AS rn
   FROM sku_details_q sdq
   JOIN fr ON fr.formId = sdq.formId
   AND fr.questionId = sdq.questionId,
       unnest(json_extract_array(fr.response)) AS arr),
     param_r_with_null AS
  (SELECT fr.formId,
          fr.responseId,
          q.sku,
          q.param,
          fr.rn AS sample_no,
          json_value(fr.arr[q.qid]['selected'], '$.0') AS response,
   FROM param_q q
   JOIN fr_mod fr ON q.formId = fr.formId
   AND fr.questionID = q.groupid),
     notes_r_with_null AS
  (SELECT fr.formId,
          fr.responseId,
          q.sku,
          q.param,
          fr.rn AS sample_no,
          json_extract_scalar(fr.arr[q.qid]) AS response,
   FROM notes_q q
   JOIN fr_mod fr ON q.formId = fr.formId
   AND fr.questionID = q.groupid),
     param_r AS
  (SELECT *
   FROM param_r_with_null
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   HAVING response IS NOT NULL
   UNION ALL SELECT *
   FROM notes_r_with_null
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6
   HAVING response IS NOT NULL
   UNION ALL SELECT *
   FROM add_sku_param_r
   UNION ALL SELECT *
   FROM add_sku_notes_r),
     details AS
  (SELECT md.formId AS `Form KNID`,
          md.responseId AS `Audit Report KNID`,
          md.sno AS `Audit Report No`,
          md.submittedAt AS `Audited At`, --md.submittedBy AS `Audited By`,
 md.store AS `Store`,
 asmd.sku AS `SKU`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     ELSE asmd.barcode
 END AS `Barcode`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN 'OOS'
     WHEN asmd.sku_status = 'Not completed' THEN 'Not Completed'
     WHEN asmd.sku_status = 'Additional' THEN 'Additional'
     ELSE 'In Stock'
 END AS `Stock Status`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     ELSE sample_no
 END AS `Sample No`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     ELSE param_r.param
 END AS `Parameter`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     ELSE param_r.response
 END AS `Reading`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     WHEN param_r.param NOT IN ('Inspector Decision',
                                'Inspector Notes')
          AND param_r.response IN ('Poor',
                                   'Irregular',
                                   'Not Uniform',
                                   'Soft',
                                   'Yes',
                                   'Unripe',
                                   'Overripe',
                                   'Out of range') THEN 0
     WHEN param_r.param NOT IN ('Inspector Decision',
                                'Inspector Notes')
          AND param_r.response IN ('Great',
                                   'Standard',
                                   'Uniform',
                                   'Firm',
                                   'No',
                                   'Ripe',
                                   'In range',
                                   'Not Applicable') THEN 100
     WHEN param_r.param NOT IN ('Inspector Decision',
                                'Inspector Notes')
          AND param_r.response IN ('Fair') THEN 50
     WHEN param_r.param NOT IN ('Inspector Decision',
                                'Inspector Notes')
          AND param_r.response IN ('Good') THEN 75
     ELSE NULL
 END AS `Given Score`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     WHEN param_r.param IN ('Colour',
                            'Size',
                            'Uniformity of Shape',
                            'Firmness',
                            'Absence of Scars',
                            'Bruising/ Crushing') THEN 'External'
     WHEN param_r.param IN ('Odour',
                            'Tasting (Sweetness, Bitterness, Sourness, Saltiness)',
                            'Texture (Tenderness, firmness, crispness, crunchiness, chewiness, fibrousness)') THEN 'Internal'
     WHEN param_r.param IN ('Mold or Decay or Sprouting',
                            'Maturation & Ripening') THEN 'Biological'
     WHEN param_r.param IN ('Storage Temperature',
                            'Product Temperature',
                            'Brix Level') THEN 'Measure'
     WHEN param_r.param IN ('Inedible?',
                            'Inspector Notes') THEN 'Overall'
     ELSE NULL
 END AS `Category`,
 CASE
     WHEN asmd.sku_status = 'Out of stock' THEN NULL
     WHEN param_r.param IN ('Colour',
                            'Size',
                            'Uniformity of Shape',
                            'Tasting (Sweetness, Bitterness, Sourness, Saltiness)',
                            'Texture (Tenderness, firmness, crispness, crunchiness, chewiness, fibrousness)',
                            'Odour') THEN 0.04
     WHEN param_r.param IN ('Firmness',
                            'Absence of Scars',
                            'Storage Temperature',
                            'Product Temperature') THEN 0.05
     WHEN param_r.param IN ('Bruising/ Crushing',
                            'Mold or Decay or Sprouting') THEN 0.21
     WHEN param_r.param IN ('Maturation & Ripening') THEN 0.09
     WHEN param_r.param IN ('Brix Level') THEN 0.10
     ELSE NULL
 END AS `Weightage`,
 md.submitted_epoch,
 md.initiator_uuid
   FROM metadata md
   LEFT OUTER JOIN all_sku_metadata asmd ON md.responseId = asmd.responseId
   LEFT OUTER JOIN param_r ON md.responseId = param_r.responseId
   AND param_r.sku = asmd.sku
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
            16),
     param_agg AS
  (SELECT `Form KNID`,
          `Audit Report KNID`,
          `Audit Report No`,
          `Audited At`,
          `Store`,
          `SKU`,
          `Barcode`,
          `Stock Status`,
          `Category`,
          `Parameter`,
          max(`Reading`) AS `Reading`,
          `Weightage`,
          avg(`Given Score`) AS `Avg Given Score`,
   FROM details
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
            12),
     scores AS
  (SELECT `Form KNID`,
          `Audit Report KNID`,
          `Audit Report No`,
          `Audited At`, --md.submittedBy AS `Audited By`,
 `Store`,
 `SKU`,
 `Barcode`,
 `Stock Status`,
 sum(CASE
         WHEN `Stock Status` IN ('In Stock', 'Additional') THEN `Avg Given Score`*`Weightage`
         ELSE NULL
     END)/sum(CASE
                  WHEN `Stock Status` IN ('In Stock', 'Additional') THEN 100*`Weightage`
                  ELSE NULL
              END) AS `SKU_Score`,
 max(CASE
         WHEN `Parameter` = 'Inspector Decision' THEN `Reading`
         ELSE NULL
     END) AS `Inspector Decision`,
 max(CASE
         WHEN `Parameter` = 'Inspector Notes' THEN `Reading`
         ELSE NULL
     END) AS `Inspector Notes`
   FROM param_agg
   GROUP BY 1,
            2,
            3,
            4,
            5,
            6,
            7,
            8),
     sku_final AS
  (SELECT *,
          CASE
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` >= 0.9 THEN 'Great'
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` >= 0.8
                   AND `SKU_Score` < 0.9 THEN 'Good'
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` >= 0.7
                   AND `SKU_Score` < 0.8 THEN 'Fair'
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` < 0.7 THEN 'Bad'
              ELSE NULL
          END AS `SKU Rating`,
          CASE
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` >= 0.8 THEN 'Pass'
              WHEN `Stock Status` IN ('In Stock',
                                      'Additional')
                   AND `SKU_Score` < 0.8 THEN 'Fail'
              ELSE NULL
          END AS `Pass or Fail`
   FROM scores)
SELECT d.`Form KNID`,
       d.`Audit Report KNID`,
       d.`Audit Report No`,
       d.`Audited At`,
       d.`Store`,
       left(d.`Store`, 3) AS `Region`,
       d.`SKU`,
       d.`Barcode`,
       d.`Audit Report KNID`||' - '||d.`SKU` AS `Audit Combo`,
       d.`Stock Status`,
       sf.`SKU Rating`,
       sf.`Pass or Fail`,
       sf.`Inspector Decision`,
       sf.`Inspector Notes`,
       d.`Category`,
       d.`Parameter`,
       d.`Weightage`,
       avg(CASE
               WHEN d.`Stock Status` IN ('In Stock', 'Additional') THEN d.`Given Score`*d.`Weightage`
               ELSE NULL
           END) AS `Actual Score`,
       avg(CASE
               WHEN d.`Stock Status` IN ('In Stock', 'Additional') THEN 100*d.`Weightage`
               ELSE NULL
           END) AS `Max Score`,
       d.submitted_epoch,
       d.initiator_uuid
FROM details d
LEFT OUTER JOIN sku_final sf ON d.`Audit Report KNID` = sf.`Audit Report KNID`
AND d.`SKU` = sf.`SKU`
WHERE (d.`Parameter` NOT IN ('Inspector Decision',
                             'Inspector Notes')
       OR d.`Parameter` IS NULL)
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
         20,
         21
ORDER BY 8,
         4,
         3,
         5,
         6
```

---

## Zepto Maintenance Issue Ticketing-copy_1726625147_Zepto Ticket Management.sql

**Tables referenced:** issue_ticketing_form_data

**Original Query:**

```sql
-- Data Source: Zepto Maintenance Issue Ticketing-copy_1726625147
-- Dashboard: Zepto Ticket Management
-- Category: Dev Testing
-- Extracted: 2026-01-29 16:58:18
-- ============================================================

select * from issue_ticketing_form_data
where "Raised At" > current_timestamp - interval '6 months'
order by "Raised At" desc
```

---
